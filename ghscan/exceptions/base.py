from ghscan.exceptions import GHScanError
from ghscan.constants import ALLOWED_SEARCH


class WhereError(GHScanError):
    def __str__(self):
        return 'Wrong search type, allowed: ' + ', '.join(ALLOWED_SEARCH)
