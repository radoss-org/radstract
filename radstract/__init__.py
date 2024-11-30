"""
.. include:: ../README.md
"""

import logging


class TileNumberFilter(logging.Filter):
    def filter(self, record):
        return "tile number" not in record.getMessage()


# Replace 'your.logger.name' with the actual logger name
logger = logging.getLogger("openjpeg.encode")
logger.addFilter(TileNumberFilter())
