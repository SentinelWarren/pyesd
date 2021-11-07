"""A simple script for automatically signing and querying invoices sent over the network via custom ESD REST web service.

TODO: Add detailed documentation.

Changelog
---------

**Version 0.3** - 2021 November 2
    Initial release.

"""

__version__ = '0.3'
__all__ = ('ESD', 'SignPayments')

from pyesd.esd_service import ESD
from pyesd.processing import SignPayments