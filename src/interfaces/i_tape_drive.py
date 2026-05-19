from abc import ABC, abstractmethod
from typing import Optional


class ITapeDrive(ABC):
    """Abstract interface for tape drive operations.

    All concrete tape drive implementations must satisfy this contract,
    enabling dependency injection and clean substitution between real hardware
    and the in-memory simulator.
    """

    @abstractmethod
    def load(self, tape_id: str) -> bool:
        """Load a tape identified by *tape_id*.

        Returns ``True`` on success, ``False`` otherwise.
        """

    @abstractmethod
    def unload(self) -> bool:
        """Eject / unload the currently mounted tape.

        Returns ``True`` on success, ``False`` if no tape is loaded or the
        operation fails.
        """

    @abstractmethod
    def rewind(self) -> bool:
        """Rewind the tape to its beginning (position 0).

        Returns ``True`` on success.
        """

    @abstractmethod
    def seek(self, position: int) -> bool:
        """Move the tape head to *position* (byte offset).

        Returns ``True`` on success, ``False`` if the position is out of range
        or no tape is loaded.
        """

    @abstractmethod
    def read(self, num_bytes: int) -> Optional[bytes]:
        """Read up to *num_bytes* from the current tape position.

        Advances the head by the number of bytes actually read.
        Returns ``None`` when no tape is loaded or a hardware error occurs.
        """

    @abstractmethod
    def write(self, data: bytes) -> bool:
        """Write *data* at the current tape position.

        Advances the head by ``len(data)`` bytes.
        Returns ``True`` on success.
        """

    @abstractmethod
    def get_status(self) -> dict:
        """Return a dictionary describing the current drive state."""
