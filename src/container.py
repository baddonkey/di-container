import logging

from src.interfaces.i_tape_drive import ITapeDrive
from src.tape_drive import TapeDrive
from src.tape_drive_simulator import TapeDriveSimulator
from src.tape_drive_service import TapeDriveService

logger = logging.getLogger("tape_drive.container")

DRIVER_REAL = "real"
DRIVER_SIMULATOR = "simulator"


class Container:
    """Minimal dependency-injection container.

    Constructs and wires the object graph based on the chosen *driver* name.
    Consumers retrieve fully-assembled objects through factory methods; they
    never instantiate dependencies themselves.
    """

    def __init__(self, driver: str = DRIVER_SIMULATOR) -> None:
        if driver not in (DRIVER_REAL, DRIVER_SIMULATOR):
            raise ValueError(
                f"Unknown driver '{driver}'. "
                f"Valid choices: '{DRIVER_REAL}', '{DRIVER_SIMULATOR}'."
            )
        self._driver = driver
        self._tape_drive: ITapeDrive = self._build_drive()
        logger.info("Container ready — driver: %s", driver)

    # ------------------------------------------------------------------
    # Factory methods
    # ------------------------------------------------------------------

    def tape_drive(self) -> ITapeDrive:
        """Return the shared ``ITapeDrive`` instance."""
        return self._tape_drive

    def tape_drive_service(self) -> TapeDriveService:
        """Return a ``TapeDriveService`` wired to the shared drive."""
        return TapeDriveService(self._tape_drive)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_drive(self) -> ITapeDrive:
        if self._driver == DRIVER_REAL:
            logger.debug("Instantiating TapeDrive (real hardware)")
            return TapeDrive()
        logger.debug("Instantiating TapeDriveSimulator")
        return TapeDriveSimulator()
