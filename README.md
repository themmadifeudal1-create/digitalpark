# 🚀 ParkIQ — Smart Campus Parking Platform (S.M.A.R.T. Edition · 2026)

> **"Don't just book parking — predict it."**

ParkIQ is a next-generation, QR-based parking intelligence platform for academic and commercial campuses. Built with a sub-second Realtime Digital Twin, timetable-aware ClassSync booking, offline-capable EdgeGuard gate kiosks, and 48-hour AI occupancy forecasting, ParkIQ turns physical campus parking into an intelligent, self-balancing resource.

---

## 🏛️ The S.M.A.R.T. Architecture Model

| Pillar | Meaning | Implementation |
| :--- | :--- | :--- |
| **S** | **Sensing Mesh** | Per-slot IoT sensor telemetry (ESP32 simulation) reporting real ground-truth occupancy |
| **M** | **Machine Learning** | 48-hour occupancy forecasting heatmap + timetable-aware ClassSync slot allocator |
| **A** | **Assured Entry** | Cryptographic HMAC-SHA256 single-use QR passes verified at the edge kiosk |
| **R** | **Realtime Digital Twin** | Live SVG campus map with sub-second WebSocket updates (< 1s sync) & historical replay |
| **T** | **Timetable-Aware** | Integration with student timetables proposing nearest parking lot + departure buffer |

---

## ⭐ The 8 Standout Differentiators

1. **ParkIQ Forecast**: AI 48-hour occupancy prediction heatmap per lot with peak bottleneck warnings (*"P1 will be full by 9:40 — P3 has space till 11:15"*).
2. **ClassSync Allocator**: Analyzes student lecture schedules and campus distance matrices to recommend the closest parking lot with one-tap auto-booking.
3. **Realtime Digital Twin**: Interactive vector SVG map rendering all 80 physical slots with live color coding (Available, Reserved, Occupied, Maintenance), animated walking routes, and an Admin Historical Replay scrubber.
4. **EdgeGuard Gates**: Offline-capable kiosks verifying cryptographic signatures locally with cached secrets when campus WiFi is down, queueing events for cloud sync.
5. **Triple-ID Entry**: Redundant gate entry via QR Code (primary), ANPR Camera Express Lane (license plate capture), and RFID smart card fallback.
6. **Geofence Auto Check-Out**: Haversine distance tracking against the 300m campus boundary; leaving campus auto-closes sessions with a 5-minute grace period.
7. **GreenMeter Sustainability**: Calculates search-minutes avoided $\times$ fuel burn to display avoided cruising hours, fuel saved, and $\text{kg}\ \text{CO}_2$ prevented.
8. **FairFlow Off-Peak Rewards**: Gamified token points ledger rewarding commuters parking outside morning rush hours (11:00 AM – 4:00 PM).

---

## 🔒 Concurrency & Double-Booking Prevention

Double-booking is eliminated at the database engine level via SQLite/PostgreSQL triggers (`prevent_reservation_overlap_insert`) and transactional row locking (`SELECT ... FOR UPDATE`):

```sql
CREATE TRIGGER prevent_reservation_overlap_insert
BEFORE INSERT ON reservations
WHEN NEW.status IN ('CONFIRMED', 'CHECKED_IN')
BEGIN
    SELECT RAISE(ABORT, 'DOUBLE_BOOKING_PREVENTED: Slot is already reserved for this overlapping window')
    WHERE EXISTS (
        SELECT 1 FROM reservations
        WHERE slot_id = NEW.slot_id
          AND status IN ('CONFIRMED', 'CHECKED_IN')
          AND NOT (end_time <= NEW.start_time OR start_time >= NEW.end_time)
    );
END;
```

---

## 🛠️ Quickstart & Local Installation

### Prerequisites
- Python 3.10+ installed

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/parkiq.git
cd parkiq
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Web Application
```bash
python run.py
```

### 4. Access the Live Platform
- **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Interactive REST API Documentation (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Automated Test Suite Runner**: [http://127.0.0.1:8000/api/tests/run-all](http://127.0.0.1:8000/api/tests/run-all)

---

## 🧪 Section 11: 10 Must-Pass Testing Checklist

Run the automated integration test suite to verify all 10 core constraints:

```bash
python verify.py
```

- [x] **Test 1: Roles Verification** — Register/login for STUDENT, STAFF, ADMIN, and SECURITY roles.
- [x] **Test 2: Double-Booking Overlap** — Concurrent overlapping bookings; exactly one succeeds, second aborted at DB level.
- [x] **Test 3: Availability Math** — Total slots ($80$) = Available + Reserved + Occupied + Maintenance.
- [x] **Test 4: QR Forgery Rejection** — Tampered HMAC-SHA256 signature rejected locally at edge kiosk.
- [x] **Test 5: QR Expiry** — Yesterday's screenshot rejected with expired `exp` claim.
- [x] **Test 6: Single-Use Replay** — Consumed QR token rejected with 409 Conflict.
- [x] **Test 7: No-Show Auto-Expiry** — 20-minute departure worker auto-expires no-shows and frees slots.
- [x] **Test 8: Check-Out Cycle** — Slot freed back to available in $< 1\text{s}$ over WebSocket push.
- [x] **Test 9: Overstay Override** — Overstay sessions flagged with admin alert and security force-end.
- [x] **Test 10: Geofence Check-Out** — Haversine exit simulation auto-closes trip and generates sustainability receipt.

---

## 📄 Project Documentation & Hackathon Pitch PDF

A complete **Hackathon Presentation & Technical Defense Guide** is included in this repository:
- **PDF File**: [`ParkIQ_Hackathon_Pitch_and_Technical_Guide.pdf`](./ParkIQ_Hackathon_Pitch_and_Technical_Guide.pdf)
- Contains:
  - 30-Second Elevator Pitch
  - 2-Minute Demo Script with timing cues
  - 6 Technical Formulations & Algorithms
  - Us vs. Other Teams Competitive Moat Table
  - 8 Hard Evaluator Viva Questions & Complete Answers

---

## 📂 Project Structure

```
parkiq/
├── app/
│   ├── main.py                # FastAPI REST API, WebSockets & Background Workers
│   ├── database.py            # SQLite Schema, Overlap Triggers & Seed Data
│   ├── auth.py                # JWT & HMAC-SHA256 Cryptographic QR Signing
│   ├── ml_engine.py           # 48h Occupancy Forecaster & ClassSync Allocator
│   ├── models.py              # Pydantic Schemas for 16 REST API Routes
│   └── static/
│       ├── index.html         # PWA Frontend with SVG Digital Twin & Kiosk Sim
│       ├── css/style.css      # Futuristic Glassmorphic Dark-Mode Design System
│       ├── js/app.js          # WebSockets, Digital Twin, Servo Barrier & Audio
│       └── ParkIQ_Hackathon_Pitch_and_Technical_Guide.pdf
├── requirements.txt           # Python Package Dependencies
├── run.py                     # Uvicorn Server Launcher
├── verify.py                  # Integration Test Suite Runner
├── generate_pdf.py            # PDF Generation Script
└── README.md
```

---

## 📜 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
