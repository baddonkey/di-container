# di-container — Tape Drive CLI

A minimal Python CLI application demonstrating **object-oriented design**, **dependency injection**, and **TDD** with a real and simulated tape drive backend.

## Features

- Clean `ITapeDrive` interface with two interchangeable implementations
- Dependency injection via a lightweight `Container` class
- Switch between the real hardware driver and the in-memory simulator with a single flag
- JSON-configurable logging (console + rotating file)
- Full pytest suite — atomic unit tests (mocked) and integration tests (simulator)

## Project Structure

```
di-container/
├── main.py                              # CLI entry point
├── logging_config.json                  # Logging configuration
├── requirements.txt
├── pytest.ini
└── src/
    ├── interfaces/
    │   └── i_tape_drive.py              # ITapeDrive abstract interface
    ├── tape_drive.py                    # Real hardware driver (Linux mt/dev)
    ├── tape_drive_simulator.py          # In-memory simulator
    ├── tape_drive_service.py            # Service layer (receives ITapeDrive via DI)
    ├── container.py                     # DI container — wires the object graph
    └── logging_setup.py                 # Loads logging config from JSON
```

## Installation

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

## Usage

All commands accept `--driver real|simulator` (default: `simulator`) and an optional `--log-config` path.

### Mount and inspect a tape

```bash
python main.py load TAPE-001
python main.py status
```

```
OK — tape loaded.
  driver   : simulator
  tape_id  : TAPE-001
  loaded   : True
  position : 0
  capacity : 10485760
```

### Write and read back data

```bash
python main.py load TAPE-001
python main.py write "Hello, tape!"
python main.py rewind
python main.py read 12
```

```
OK — tape loaded.
OK — wrote 12 byte(s).
OK — tape rewound.
Read 12 byte(s): b'Hello, tape!'
```

### Seek to a position

```bash
python main.py load TAPE-001
python main.py seek 1024
python main.py write "offset data"
python main.py seek 1024
python main.py read 11
```

### Eject the tape

```bash
python main.py unload
```

### Switch to the real hardware driver (Linux only)

```bash
python main.py --driver real status
```

> The real driver communicates with `/dev/nst0` via the `mt` utility (`mt-st` package).  
> It requires a Linux system with a connected tape device.

### Use a custom logging configuration

```bash
python main.py --log-config /etc/tapedrive/logging.json status
```

## Running Tests

```bash
# All tests
pytest

# Unit tests only (all dependencies mocked)
pytest tests/unit/

# Integration tests only (real simulator, no mocks)
pytest tests/integration/

# With coverage report
pytest --cov=src --cov-report=term-missing
```

```
tests/unit/test_tape_drive_service.py          28 passed
tests/integration/test_tape_drive_simulator.py 41 passed
```

## Logging

Logging is configured via `logging_config.json` using the standard Python `logging.config.dictConfig` schema.

- **Console** — `INFO` and above, simple format
- **File** (`tape_drive.log`) — `DEBUG` and above, timestamped detailed format

Edit `logging_config.json` to change levels, add handlers, or switch formatters without touching the code.

```json
{
    "loggers": {
        "tape_drive": {
            "level": "DEBUG",
            "handlers": ["console", "file"]
        }
    }
}
```

## Design

| Concept | Implementation |
|---|---|
| Interface | `ITapeDrive` — Python `ABC` with `@abstractmethod` |
| Real driver | `TapeDrive` — delegates to `mt` and `/dev/nst0` |
| Simulator | `TapeDriveSimulator` — `bytearray` in memory |
| Service layer | `TapeDriveService` — business logic, no I/O |
| DI container | `Container` — constructs and wires the graph |
| Logging config | `LoggingSetup` — loads from JSON, falls back to `basicConfig` |
