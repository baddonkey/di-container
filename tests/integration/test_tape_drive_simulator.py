"""Integration tests for TapeDriveSimulator.

No mocking — exercises the real simulator and TapeDriveService end-to-end.
All tests run purely in memory; no OS resources are needed.
"""

import pytest

from src.tape_drive_simulator import TapeDriveSimulator
from src.tape_drive_service import TapeDriveService

_TAPE_ID = "INTG-TAPE-01"
_SMALL_TAPE = 1024  # 1 KiB — fast and deterministic


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def simulator() -> TapeDriveSimulator:
    return TapeDriveSimulator(tape_size=_SMALL_TAPE)


@pytest.fixture()
def loaded_simulator(simulator: TapeDriveSimulator) -> TapeDriveSimulator:
    """Simulator with a tape already mounted."""
    simulator.load(_TAPE_ID)
    return simulator


@pytest.fixture()
def service(simulator: TapeDriveSimulator) -> TapeDriveService:
    return TapeDriveService(simulator)


@pytest.fixture()
def loaded_service(
    loaded_simulator: TapeDriveSimulator,
) -> TapeDriveService:
    """Service whose simulator already has a tape mounted."""
    return TapeDriveService(loaded_simulator)


# ---------------------------------------------------------------------------
# Simulator: initial state
# ---------------------------------------------------------------------------


class TestInitialState:
    def test_not_loaded_on_creation(self, simulator: TapeDriveSimulator) -> None:
        assert simulator.get_status()["loaded"] is False

    def test_tape_id_is_none_on_creation(
        self, simulator: TapeDriveSimulator
    ) -> None:
        assert simulator.get_status()["tape_id"] is None

    def test_position_is_zero_on_creation(
        self, simulator: TapeDriveSimulator
    ) -> None:
        assert simulator.get_status()["position"] == 0

    def test_capacity_matches_constructor(
        self, simulator: TapeDriveSimulator
    ) -> None:
        assert simulator.get_status()["capacity"] == _SMALL_TAPE


# ---------------------------------------------------------------------------
# Simulator: load / unload
# ---------------------------------------------------------------------------


class TestLoadUnload:
    def test_load_returns_true(self, simulator: TapeDriveSimulator) -> None:
        assert simulator.load(_TAPE_ID) is True

    def test_load_sets_tape_id(self, simulator: TapeDriveSimulator) -> None:
        simulator.load(_TAPE_ID)
        assert simulator.get_status()["tape_id"] == _TAPE_ID

    def test_load_marks_drive_as_loaded(
        self, simulator: TapeDriveSimulator
    ) -> None:
        simulator.load(_TAPE_ID)
        assert simulator.get_status()["loaded"] is True

    def test_second_load_without_unload_returns_false(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        assert loaded_simulator.load("OTHER-TAPE") is False

    def test_second_load_does_not_change_tape_id(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.load("OTHER-TAPE")
        assert loaded_simulator.get_status()["tape_id"] == _TAPE_ID

    def test_unload_after_load_returns_true(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        assert loaded_simulator.unload() is True

    def test_unload_clears_tape_id(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.unload()
        assert loaded_simulator.get_status()["tape_id"] is None

    def test_unload_marks_drive_as_not_loaded(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.unload()
        assert loaded_simulator.get_status()["loaded"] is False

    def test_unload_without_tape_returns_false(
        self, simulator: TapeDriveSimulator
    ) -> None:
        assert simulator.unload() is False

    def test_reload_after_unload_is_allowed(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.unload()
        assert loaded_simulator.load("NEW-TAPE") is True

    def test_load_resets_buffer(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.write(b"\xff" * 10)
        loaded_simulator.unload()
        loaded_simulator.load("FRESH-TAPE")
        loaded_simulator.rewind()
        data = loaded_simulator.read(10)
        assert data == b"\x00" * 10


# ---------------------------------------------------------------------------
# Simulator: rewind
# ---------------------------------------------------------------------------


class TestRewind:
    def test_rewind_without_tape_returns_false(
        self, simulator: TapeDriveSimulator
    ) -> None:
        assert simulator.rewind() is False

    def test_rewind_returns_true_when_loaded(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        assert loaded_simulator.rewind() is True

    def test_rewind_resets_position_to_zero(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.seek(512)
        loaded_simulator.rewind()
        assert loaded_simulator.get_status()["position"] == 0


# ---------------------------------------------------------------------------
# Simulator: seek
# ---------------------------------------------------------------------------


class TestSeek:
    def test_seek_without_tape_returns_false(
        self, simulator: TapeDriveSimulator
    ) -> None:
        assert simulator.seek(0) is False

    def test_seek_to_valid_position_returns_true(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        assert loaded_simulator.seek(100) is True

    def test_seek_updates_position(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.seek(256)
        assert loaded_simulator.get_status()["position"] == 256

    def test_seek_to_zero_is_valid(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.seek(512)
        assert loaded_simulator.seek(0) is True

    def test_seek_to_negative_returns_false(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        assert loaded_simulator.seek(-1) is False

    def test_seek_beyond_capacity_returns_false(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        assert loaded_simulator.seek(_SMALL_TAPE) is False

    def test_seek_beyond_capacity_does_not_change_position(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.seek(100)
        loaded_simulator.seek(_SMALL_TAPE + 1)
        assert loaded_simulator.get_status()["position"] == 100


# ---------------------------------------------------------------------------
# Simulator: read / write
# ---------------------------------------------------------------------------


class TestReadWrite:
    def test_read_without_tape_returns_none(
        self, simulator: TapeDriveSimulator
    ) -> None:
        assert simulator.read(10) is None

    def test_write_without_tape_returns_false(
        self, simulator: TapeDriveSimulator
    ) -> None:
        assert simulator.write(b"data") is False

    def test_write_returns_true(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        assert loaded_simulator.write(b"OK") is True

    def test_write_advances_position(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.write(b"ABCDE")
        assert loaded_simulator.get_status()["position"] == 5

    def test_read_advances_position(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.write(b"ABCDE")
        loaded_simulator.rewind()
        loaded_simulator.read(3)
        assert loaded_simulator.get_status()["position"] == 3

    def test_write_read_roundtrip(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        payload = b"Hello, Tape!"
        loaded_simulator.write(payload)
        loaded_simulator.rewind()
        assert loaded_simulator.read(len(payload)) == payload

    def test_partial_read_returns_available_bytes(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.seek(_SMALL_TAPE - 3)
        data = loaded_simulator.read(100)
        assert len(data) == 3

    def test_write_beyond_capacity_returns_false(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        oversized = bytes(_SMALL_TAPE + 1)
        assert loaded_simulator.write(oversized) is False

    def test_write_beyond_capacity_does_not_corrupt_position(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.seek(10)
        loaded_simulator.write(bytes(_SMALL_TAPE + 1))  # fails
        assert loaded_simulator.get_status()["position"] == 10

    def test_seek_then_write_then_read(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.seek(50)
        loaded_simulator.write(b"XYZ")
        loaded_simulator.seek(50)
        assert loaded_simulator.read(3) == b"XYZ"

    def test_multiple_writes_accumulate(
        self, loaded_simulator: TapeDriveSimulator
    ) -> None:
        loaded_simulator.write(b"AB")
        loaded_simulator.write(b"CD")
        loaded_simulator.rewind()
        assert loaded_simulator.read(4) == b"ABCD"


# ---------------------------------------------------------------------------
# Service + Simulator: end-to-end workflows
# ---------------------------------------------------------------------------


class TestServiceWithSimulator:
    def test_full_load_write_read_unload_workflow(
        self, service: TapeDriveService
    ) -> None:
        assert service.load_tape(_TAPE_ID) is True
        assert service.write_data(b"integration test") is True
        assert service.rewind_tape() is True
        result = service.read_data(16)
        assert result == b"integration test"
        assert service.unload_tape() is True

    def test_status_shows_correct_driver(
        self, loaded_service: TapeDriveService
    ) -> None:
        assert loaded_service.get_status()["driver"] == "simulator"

    def test_status_shows_tape_loaded(
        self, loaded_service: TapeDriveService
    ) -> None:
        assert loaded_service.get_status()["loaded"] is True

    def test_status_shows_tape_id(
        self, loaded_service: TapeDriveService
    ) -> None:
        assert loaded_service.get_status()["tape_id"] == _TAPE_ID

    def test_seek_write_seek_read(
        self, loaded_service: TapeDriveService
    ) -> None:
        loaded_service.seek_tape(20)
        loaded_service.write_data(b"DATA")
        loaded_service.seek_tape(20)
        assert loaded_service.read_data(4) == b"DATA"

    def test_write_after_unload_fails(
        self, loaded_service: TapeDriveService
    ) -> None:
        loaded_service.unload_tape()
        assert loaded_service.write_data(b"oops") is False

    def test_read_after_unload_fails(
        self, loaded_service: TapeDriveService
    ) -> None:
        loaded_service.unload_tape()
        assert loaded_service.read_data(4) is None

    def test_rewind_after_unload_fails(
        self, loaded_service: TapeDriveService
    ) -> None:
        loaded_service.unload_tape()
        assert loaded_service.rewind_tape() is False
