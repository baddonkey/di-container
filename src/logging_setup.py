import json
import logging
import logging.config
from pathlib import Path

_DEFAULT_CONFIG = Path(__file__).parent.parent / "logging_config.json"


class LoggingSetup:
    """Loads Python logging configuration from a JSON file.

    The JSON schema must follow the ``logging.config.dictConfig`` format
    (https://docs.python.org/3/library/logging.config.html#logging-config-dictschema).
    Falls back to ``basicConfig`` when the file is absent.
    """

    def __init__(self, config_path: Path = _DEFAULT_CONFIG) -> None:
        self._config_path = config_path

    def configure(self) -> None:
        """Apply the logging configuration."""
        if self._config_path.exists():
            with self._config_path.open(encoding="utf-8") as fh:
                config = json.load(fh)
            logging.config.dictConfig(config)
            logging.getLogger("tape_drive").debug(
                "Logging configured from %s", self._config_path
            )
        else:
            logging.basicConfig(level=logging.INFO)
            logging.warning(
                "Logging config not found at '%s'; using defaults.",
                self._config_path,
            )
