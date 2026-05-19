import logging
import subprocess
from typing import Optional

from src.interfaces.i_tape_drive import ITapeDrive

logger = logging.getLogger("tape_drive.real")

# Default Linux non-rewind tape device.  Adjust via constructor on other
# platforms or when multiple drives are present.
_DEFAULT_DEVICE = "/dev/nst0"


class TapeDrive(ITapeDrive):
    """Real tape drive implementation.

    Communicates with the OS through the ``mt`` utility (Linux / Unix) and
    direct character-device I/O.  A Linux system with the ``mt-st`` package
    and an accessible tape device is required.
    """

    def __init__(self, device: str = _DEFAULT_DEVICE) -> None:
        self._device = device
        self._tape_id: Optional[str] = None
        logger.info("TapeDrive initialised on device %s", self._device)

    # ------------------------------------------------------------------
    # ITapeDrive implementation
    # ------------------------------------------------------------------

    def load(self, tape_id: str) -> bool:
        logger.info("Loading tape '%s' on %s", tape_id, self._device)
        try:
            subprocess.run(
                ["mt", "-f", self._device, "load"],
                check=True,
                capture_output=True,
            )
            self._tape_id = tape_id
            logger.debug("Tape '%s' loaded successfully", tape_id)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            logger.error("Failed to load tape '%s': %s", tape_id, exc)
            return False

    def unload(self) -> bool:
        logger.info("Unloading tape from %s", self._device)
        try:
            subprocess.run(
                ["mt", "-f", self._device, "eject"],
                check=True,
                capture_output=True,
            )
            self._tape_id = None
            logger.debug("Tape unloaded successfully")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            logger.error("Failed to unload tape: %s", exc)
            return False

    def rewind(self) -> bool:
        logger.info("Rewinding tape on %s", self._device)
        try:
            subprocess.run(
                ["mt", "-f", self._device, "rewind"],
                check=True,
                capture_output=True,
            )
            logger.debug("Tape rewound successfully")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            logger.error("Failed to rewind tape: %s", exc)
            return False

    def seek(self, position: int) -> bool:
        logger.info("Seeking to block %d on %s", position, self._device)
        try:
            subprocess.run(
                ["mt", "-f", self._device, "seek", str(position)],
                check=True,
                capture_output=True,
            )
            logger.debug("Seek to block %d successful", position)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            logger.error("Failed to seek to block %d: %s", position, exc)
            return False

    def read(self, num_bytes: int) -> Optional[bytes]:
        logger.info("Reading %d bytes from %s", num_bytes, self._device)
        try:
            with open(self._device, "rb") as fh:
                data = fh.read(num_bytes)
            logger.debug("Read %d bytes", len(data))
            return data
        except OSError as exc:
            logger.error("Failed to read from tape device: %s", exc)
            return None

    def write(self, data: bytes) -> bool:
        logger.info("Writing %d bytes to %s", len(data), self._device)
        try:
            with open(self._device, "wb") as fh:
                fh.write(data)
            logger.debug("Wrote %d bytes successfully", len(data))
            return True
        except OSError as exc:
            logger.error("Failed to write to tape device: %s", exc)
            return False

    def get_status(self) -> dict:
        logger.debug("Getting status for %s", self._device)
        try:
            result = subprocess.run(
                ["mt", "-f", self._device, "status"],
                check=True,
                capture_output=True,
                text=True,
            )
            return {
                "driver": "real",
                "device": self._device,
                "tape_id": self._tape_id,
                "raw_status": result.stdout,
            }
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            logger.error("Failed to get tape status: %s", exc)
            return {
                "driver": "real",
                "device": self._device,
                "tape_id": self._tape_id,
                "error": str(exc),
            }
