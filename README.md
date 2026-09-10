# SecureLog-Desk

Secure desktop application built with Streamlit and SQLite for streamlined shift management, audit logs, and secure local data persistence.

## Features

- **Dynamic Shift Logging**: Optimized interface for quickly recording operational events and shift notes.
- **Chronological Notebook View**: Daily ledger-style navigation with rapid forward and backward controls to review past shifts.
- **Advanced Search Engine**: Multi-criteria keyword and date filtering across historical records.
- **Permanent Reference Notes**: Dedicated repository for static operational guidelines, internal directories, and procedures.
- **Smart Recycle Bin**: Temporary retention of deleted items with automated 7-day purging.
- **Authentication**: Secure access control protected via SHA-256 hashing.

## Project Architecture

- `app.py`: Core entry point, session management, and view router.
- `views.py`: Modular user interface components and rendering logic.
- `database.py`: SQLite database configuration and automated maintenance routines.
- `bitacora_recepcion.db`: Local database instance for persistent record storage.
- `Iniciar_Bitacora.command`: Automated startup script for macOS.
- `Iniciar_Bitacora.bat`: Automated startup script for Windows.

## Portability and Deployment

The application is engineered to operate in a fully self-contained environment:
1. Ensure all system files reside in the same directory alongside the local database file.
2. **macOS**: Execute the `Iniciar_Bitacora.command` script.
3. **Windows**: Execute the `Iniciar_Bitacora.bat` script.
