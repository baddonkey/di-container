"""Pure unit tests for TapeDriveService.

The tape drive dependency is fully mocked out — no simulator or hardware is
touched.  Each test is atomic: it exercises exactly one behaviour of the
service in isolation.
"""

import pytest
from unittest.mock import MagicMock

from src.tape_drive_service import TapeDriveService


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_drive() -> MagicMock:
    """A fresh MagicMock that satisfies the ITapeDrive interface."""
    return MagicMock()


@pytest.fixture()
def service(mock_drive: MagicMock) -> TapeDriveService:
    """TapeDriveService wired to the mock drive."""
    return TapeDriveService(mock_drive)


# ---------------------------------------------------------------------------
# load_tape
# ---------------------------------------------------------------------------


class TestLoadTape:
    def test_delegates_tape_id_to_drive(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.load.return_value = True
        service.load_tape("TAPE-001")
        mock_drive.load.assert_called_once_with("TAPE-001")

    def test_returns_true_when_drive_succeeds(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.load.return_value = True
        assert service.load_tape("TAPE-001") is True

    def test_returns_false_when_drive_fails(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.load.return_value = False
        assert service.load_tape("TAPE-001") is False

    def test_calls_drive_exactly_once(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        service.load_tape("TAPE-001")
        assert mock_drive.load.call_count == 1


# ---------------------------------------------------------------------------
# unload_tape
# ---------------------------------------------------------------------------


class TestUnloadTape:
    def test_delegates_to_drive(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.unload.return_value = True
        service.unload_tape()
        mock_drive.unload.assert_called_once_with()

    def test_returns_true_when_drive_succeeds(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.unload.return_value = True
        assert service.unload_tape() is True

    def test_returns_false_when_drive_fails(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.unload.return_value = False
        assert service.unload_tape() is False


# ---------------------------------------------------------------------------
# rewind_tape
# ---------------------------------------------------------------------------


class TestRewindTape:
    def test_delegates_to_drive(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.rewind.return_value = True
        service.rewind_tape()
        mock_drive.rewind.assert_called_once_with()

    def test_returns_true_when_drive_succeeds(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.rewind.return_value = True
        assert service.rewind_tape() is True

    def test_returns_false_when_drive_fails(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.rewind.return_value = False
        assert service.rewind_tape() is False


# ---------------------------------------------------------------------------
# seek_tape
# ---------------------------------------------------------------------------


class TestSeekTape:
    def test_delegates_position_to_drive(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.seek.return_value = True
        service.seek_tape(1024)
        mock_drive.seek.assert_called_once_with(1024)

    def test_returns_true_when_drive_succeeds(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.seek.return_value = True
        assert service.seek_tape(1024) is True

    def test_returns_false_when_drive_fails(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.seek.return_value = False
        assert service.seek_tape(1024) is False

    def test_passes_zero_position(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        service.seek_tape(0)
        mock_drive.seek.assert_called_once_with(0)


# ---------------------------------------------------------------------------
# read_data
# ---------------------------------------------------------------------------


class TestReadData:
    def test_delegates_num_bytes_to_drive(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.read.return_value = b"hello"
        service.read_data(5)
        mock_drive.read.assert_called_once_with(5)

    def test_returns_bytes_from_drive(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.read.return_value = b"hello"
        assert service.read_data(5) == b"hello"

    def test_returns_none_when_drive_fails(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.read.return_value = None
        assert service.read_data(5) is None

    def test_returns_empty_bytes_when_drive_returns_empty(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.read.return_value = b""
        assert service.read_data(0) == b""


# ---------------------------------------------------------------------------
# write_data
# ---------------------------------------------------------------------------


class TestWriteData:
    def test_delegates_bytes_to_drive(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.write.return_value = True
        service.write_data(b"world")
        mock_drive.write.assert_called_once_with(b"world")

    def test_returns_true_when_drive_succeeds(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.write.return_value = True
        assert service.write_data(b"world") is True

    def test_returns_false_when_drive_fails(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.write.return_value = False
        assert service.write_data(b"world") is False

    def test_passes_empty_bytes(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        service.write_data(b"")
        mock_drive.write.assert_called_once_with(b"")


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------


class TestGetStatus:
    def test_delegates_to_drive(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.get_status.return_value = {}
        service.get_status()
        mock_drive.get_status.assert_called_once_with()

    def test_returns_status_dict_from_drive(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        expected = {"driver": "mock", "loaded": False, "tape_id": None}
        mock_drive.get_status.return_value = expected
        assert service.get_status() == expected

    def test_returns_whatever_the_drive_provides(
        self, service: TapeDriveService, mock_drive: MagicMock
    ) -> None:
        mock_drive.get_status.return_value = {"arbitrary": "data"}
        assert service.get_status() == {"arbitrary": "data"}
