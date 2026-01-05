"""Константы парсера."""
from pathlib import Path


MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

PEP_TYPE_STATUS_COLUMN = 0
PEP_NUMBER_COLUMN = 1
MIN_PEP_TABLE_COLUMNS = 2
PEP_STATUS_CHAR_INDEX = 1

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
