import logging
from typing import Optional

from src.interfaces.i_tape_drive import ITapeDrive

logger = logging.getLogger("tape_drive.simulator")

# Default virtual tape capacity (10 MiB).
_DEFAULT_TAPE_SIZE = 10 * 1024 * 1024


class TapeDriveSimulator(ITapeDrive):
    """In-memory tape drive simulator.

    All state is held in a ``bytearray`` buffer so no hardware or OS
    resources are required.  Suitable for development, testing, and demos.
    """

    def __init__(self, tape_size: int = _DEFAULT_TAPE_SIZE) -> None:
        self._tape_size = tape_size
        self._tape_id: Optional[str] = None
        self._loaded: bool = False
        self._buffer: bytearray = bytearray(tape_size)
        self._position: int = 0
        logger.info(
            "TapeDriveSimulator initialised (capacity: %d bytes)", tape_size
        )

    # ------------------------------------------------------------------
    # ITapeDrive implementation
    # ------------------------------------------------------------------

    def load(self, tape_id: str) -> bool:
        if self._loaded:
            logger.warning(
                "Load rejected: tape '%s' is already mounted", self._tape_id
            )
            return False
        self._tape_id = tape_id
        self._loaded = True
        self._buffer = bytearray(self._tape_size)
        self._position = 0
        logger.info("Simulator mounted tape '%s'", tape_id)
        return True

    def unload(self) -> bool:
        if not self._loaded:
            logger.warning("Unload rejected: no tape is currently mounted")
            return False
        logger.info("Simulator ejecting tape '%s'", self._tape_id)
        self._tape_id = None
        self._loaded = False
        self._position = 0
        return True

    def rewind(self) -> bool:
        if not self._loaded:
            logger.warning("Rewind rejected: no tape is mounted")
            return False
        self._position = 0
        logger.debug("Tape rewound to position 0")
        return True

    def seek(self, position: int) -> bool:
        if not self._loaded:
            logger.warning("Seek rejected: no tape is mounted")
            return False
        if position < 0 or position >= self._tape_size:
            logger.error(
                "Seek to %d rejected: valid range is 0–%d",
                position,
                self._tape_size - 1,
            )
            return False
        self._position = position
        logger.debug("Seeked to position %d", position)
        return True

    def read(self, num_bytes: int) -> Optional[bytes]:
        if not self._loaded:
            logger.warning("Read rejected: no tape is mounted")
            return None
        end = min(self._position + num_bytes, self._tape_size)
        data = bytes(self._buffer[self._position : end])
        logger.debug(
            "Read %d bytes from position %d", len(data), self._position
        )
        self._position = end
        return data

    def write(self, data: bytes) -> bool:
        if not self._loaded:
            logger.warning("Write rejected: no tape is mounted")
            return False
        end = self._position + len(data)
        if end > self._tape_size:
            logger.error(
                "Write rejected: would exceed tape capacity (%d > %d)",
                end,
                self._tape_size,
            )
            return False
        self._buffer[self._position : end] = data
        logger.debug(
            "Wrote %d bytes at position %d", len(data), self._position
        )
        self._position = end
        return True

    def get_status(self) -> dict:
        return {
            "driver": "simulator",
            "tape_id": self._tape_id,
            "loaded": self._loaded,
            "position": self._position,
            "capacity": self._tape_size,
        }
