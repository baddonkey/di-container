import logging
from typing import Optional

from src.interfaces.i_tape_drive import ITapeDrive

logger = logging.getLogger("tape_drive.service")


class TapeDriveService:
    """High-level tape drive service.

    Orchestrates tape operations through the injected ``ITapeDrive``
    implementation.  Business logic lives here; the concrete driver is
    supplied at construction time (dependency injection).
    """

    def __init__(self, drive: ITapeDrive) -> None:
        self._drive = drive
        logger.debug(
            "TapeDriveService created with driver: %s",
            type(drive).__name__,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_tape(self, tape_id: str) -> bool:
        """Mount a tape by its identifier."""
        logger.info("Service: load tape '%s'", tape_id)
        return self._drive.load(tape_id)

    def unload_tape(self) -> bool:
        """Eject the currently mounted tape."""
        logger.info("Service: unload tape")
        return self._drive.unload()

    def rewind_tape(self) -> bool:
        """Rewind the tape to the beginning."""
        logger.info("Service: rewind tape")
        return self._drive.rewind()

    def seek_tape(self, position: int) -> bool:
        """Move the tape head to *position*."""
        logger.info("Service: seek to position %d", position)
        return self._drive.seek(position)

    def read_data(self, num_bytes: int) -> Optional[bytes]:
        """Read *num_bytes* from the current tape position."""
        logger.info("Service: read %d bytes", num_bytes)
        return self._drive.read(num_bytes)

    def write_data(self, data: bytes) -> bool:
        """Write *data* at the current tape position."""
        logger.info("Service: write %d bytes", len(data))
        return self._drive.write(data)

    def get_status(self) -> dict:
        """Return the current drive status dictionary."""
        logger.debug("Service: get status")
        return self._drive.get_status()
