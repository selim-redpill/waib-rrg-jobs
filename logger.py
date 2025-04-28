"""
Logger configuration module.

Defines a custom logger with split coloring:
- The metadata part (timestamp and level) is colorized based on log severity.
- The actual log message is always white for better readability.

Available log levels:
- DEBUG (blue)
- INFO (green)
- WARNING (yellow)
- ERROR (red)
- CRITICAL (bold red)

Usage:
    from logger import logger

    logger.info("This is an info message")
    logger.error("This is an error message")
"""

import logging

class ColorFormatter(logging.Formatter):
    """
    Custom formatter that adds colors to the metadata part of log messages
    (timestamp and log level) based on their severity level.

    Attributes:
        COLORS (dict): Mapping of log levels to ANSI color codes.
        RESET (str): ANSI code to reset color to default after each message.
        WHITE (str): ANSI code for standard white color.
    """
    COLORS = {
        logging.DEBUG: "\033[94m",     # Blue
        logging.INFO: "\033[92m",      # Green
        logging.WARNING: "\033[93m",   # Yellow
        logging.ERROR: "\033[91m",     # Red
        logging.CRITICAL: "\033[1;91m" # Bold Red
    }
    RESET = "\033[0m"
    WHITE = "\033[97m"

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the given log record, applying color to metadata and keeping
        the message part in white.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted and colorized log message.
        """
        # generate timestamp manually
        asctime = self.formatTime(record, self.datefmt)
        color = self.COLORS.get(record.levelno, self.RESET)
        meta = f"{asctime} - [{record.levelname}]"
        message = record.getMessage()
        return f"{color}{meta}{self.RESET} - {self.WHITE}{message}{self.RESET}"


# --- Logger Setup ---

# Create root logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create a console handler
handler = logging.StreamHandler()

# Create and apply the custom color formatter
formatter = ColorFormatter(
    fmt="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Prevent logs from being duplicated in some environments (e.g., Jupyter, some IDEs)
logger.propagate = False