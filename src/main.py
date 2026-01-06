"""Парсер документации Python: точка входа и функции парсинга."""
import logging
import re
from collections import Counter
from typing import List, Optional, Tuple
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup, Tag
from requests_cache import CachedSession
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (
    BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, MIN_PEP_TABLE_COLUMNS,
    PEP_NUMBER_COLUMN, PEP_STATUS_CHAR_INDEX, PEP_TYPE_STATUS_COLUMN, PEP_URL,
    PEP_ZERO_PATTERNS
)
from exceptions import ParserFindTagException
from outputs import control_output
from utils import find_tag, get_response


ResultsType = List[Tuple[str, ...]]


def whats_new(session: CachedSession) -> Optional[ResultsType]:
    """Парсит страницы What's New in Python, возвращает ссылки и авторов."""
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')

    response = get_response(session, whats_new_url)
    if response is None:
        return None

    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]

    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])

        response = get_response(session, version_link)
        if response is None:
            continue

        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')

        results.append((version_link, h1.text, dl_text))

    return results


def latest_versions(session: CachedSession) -> Optional[ResultsType]:
    """Парсит список версий Python с их статусами."""
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return None

    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')

    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException('Не найден список c версиями Python')

    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)

        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''

        results.append((link, version, status))

    return results


def download(session: CachedSession) -> None:
    """Скачивает документацию Python в директорию downloads/."""
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')

    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, 'lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})

    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)

    archive_tag = table_tag.find('a', {'href': re.compile(r'.+html\.zip$')})
    if archive_tag is None:
        logging.warning('Архив не найден')
        return

    archive_link = archive_tag['href']
    archive_url = urljoin(downloads_url, archive_link)
    filename = archive_url.split('/')[-1]
    archive_path = downloads_dir / filename

    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)

    logging.info(f'Архив был загружен: {archive_path}')


def get_pep_status(session: CachedSession, pep_url: str) -> Optional[str]:
    """Извлекает статус со страницы PEP."""
    response = get_response(session, pep_url)
    if response is None:
        return None

    pep_soup = BeautifulSoup(response.text, 'lxml')
    status_dt = pep_soup.find(string='Status')

    if status_dt is None:
        return None

    status_dd = status_dt.parent.find_next_sibling('dd')
    if status_dd is None:
        return None
    return str(status_dd.string)


def get_pep_rows(soup: BeautifulSoup) -> list[Tag]:
    """Извлекает строки PEP из таблиц."""
    rows = []
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            if not row.find('th'):
                rows.append(row)
    return rows


def pep(session: CachedSession) -> Optional[ResultsType]:
    """Парсит PEP, считает статусы."""
    response = get_response(session, PEP_URL)
    if response is None:
        return None

    soup = BeautifulSoup(response.text, 'lxml')
    pep_rows = get_pep_rows(soup)

    results = [('Статус', 'Количество')]
    status_counts = Counter()

    for row in tqdm(pep_rows):
        tds = row.find_all('td')
        if len(tds) < MIN_PEP_TABLE_COLUMNS:
            continue

        status_cell = tds[PEP_TYPE_STATUS_COLUMN].text.strip()
        idx = PEP_STATUS_CHAR_INDEX
        preview_status = status_cell[idx:idx + 1]

        pep_link_tag = tds[PEP_NUMBER_COLUMN].find('a')
        if pep_link_tag is None:
            continue

        pep_link = pep_link_tag['href']
        if any(pattern in pep_link for pattern in PEP_ZERO_PATTERNS):
            continue

        pep_url = urljoin(PEP_URL, pep_link)
        actual_status = get_pep_status(session, pep_url)
        if actual_status is None:
            continue

        expected_statuses = EXPECTED_STATUS.get(preview_status, ())
        if actual_status not in expected_statuses:
            logging.warning(
                f'Несовпадающие статусы:\n'
                f'{pep_url}\n'
                f'Статус в карточке: {actual_status}\n'
                f'Ожидаемые статусы: {list(expected_statuses)}'
            )

        status_counts[actual_status] += 1

    results.extend(sorted(status_counts.items()))
    results.append(('Total', sum(status_counts.values())))

    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main() -> None:
    """Точка входа: настройка, парсинг аргументов, запуск выбранного режима."""
    configure_logging()
    logging.info('Парсер запущен!')

    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
