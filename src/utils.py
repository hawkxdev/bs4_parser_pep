"""Утилиты парсера: HTTP-запросы и поиск тегов."""
import logging
from typing import Optional

from bs4 import Tag
from requests import RequestException, Response
from requests_cache import CachedSession

from exceptions import ParserFindTagException


def get_response(session: CachedSession, url: str) -> Optional[Response]:
    """Выполняет GET-запрос с обработкой ошибок."""
    try:
        response = session.get(url)
        response.raise_for_status()
        response.encoding = 'utf-8'
        return response

    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )
        return None


def find_tag(
    soup: Tag,
    tag: str,
    attrs: Optional[dict] = None
) -> Tag:
    """Ищет тег или выбрасывает исключение."""
    searched_tag = soup.find(tag, attrs=(attrs or {}))

    if searched_tag is None:
        raise ParserFindTagException(f'Не найден тег {tag} {attrs}')

    return searched_tag
