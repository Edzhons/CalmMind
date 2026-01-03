# CalmMind (MVP)

CalmMind is a **minimal desktop productivity and mental clarity app** designed to help you capture ideas, manage tasks, and remember important appointments — without accounts, cloud sync, or unnecessary complexity.

This repository contains the **MVP (Minimum Viable Product)** version of CalmMind.

---

## What CalmMind Is (and Isn’t)

**CalmMind is:**
- A local-first desktop app
- Focused on clarity, simplicity, and low friction
- Built for personal use and experimentation

**CalmMind is not:**
- A medical or mental health service
- A replacement for professional care
- A fully polished commercial product (yet)

---

## Core Features

- **Three entry types**
  - 💡 Ideas (no time, just capture)
  - ✅ Tasks (optional time)
  - 📅 Appointments (required time)

- **Smart views**
  - All entries
  - Upcoming (Next)
  - Ideas-only
  - Archive

- **Reminders**
  - Desktop reminder popups
  - Snooze options (5 / 10 minutes)
  - Mark as done directly from reminder

- **Automatic archiving**
  - Timed entries are archived automatically after 24 hours

- **Local-first storage**
  - All data is stored locally on your machine
  - No accounts, no cloud, no tracking

---

## Data & Privacy

CalmMind stores all user data **locally** in the system application data directory:

- **Windows:**  
  `%APPDATA%\CalmMind\data\entries.json`

No data is sent anywhere.  
Nothing is collected, tracked, or synced.

---

## Installation (MVP)

1. Download the `CalmMind.exe` from the Releases section (or the project website).
2. Run the executable.

> ⚠️ Windows may show a security warning because the app is not code-signed yet.  
> This is normal for early-stage indie applications.

No installer is required.

---

## Tech Stack

- Python
- Tkinter (GUI)
- tkcalendar
- PyInstaller (for packaging)

---

## Project Status

This project is currently in **MVP / early testing phase**.

Things intentionally **not included yet**:
- Cloud sync
- Accounts or login
- Mobile version
- Advanced analytics

Feedback and experimentation are the main goals at this stage.

---

## Disclaimer

CalmMind is **not a medical or mental health application** and should not be used as a substitute for professional mental health care.

---

## License

MIT License.
