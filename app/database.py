import sqlite3
import os
import json
import hashlib
import hmac
import time
from datetime import datetime, timedelta, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "parkiq.db")
SERVER_SECRET = "parkiq-smart-campus-jwt-hmac-secret-key-2026-standout"

def get_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def create_qr_signature(payload_str: str) -> str:
    return hmac.new(SERVER_SECRET.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256).hexdigest()

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Users
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('STUDENT', 'STAFF', 'ADMIN', 'SECURITY')),
        vehicle_no TEXT,
        vehicle_type TEXT DEFAULT '4W' CHECK(vehicle_type IN ('2W', '4W', 'EV', 'ACCESSIBLE')),
        roll_no TEXT,
        fairflow_points INTEGER DEFAULT 120,
        created_at TEXT NOT NULL
    );
    """)

    # 2. Parking Lots
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parking_lots (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        campus_block TEXT NOT NULL,
        capacity_2w INTEGER DEFAULT 0,
        capacity_4w INTEGER DEFAULT 0,
        total_slots INTEGER DEFAULT 0,
        lat REAL NOT NULL,
        lng REAL NOT NULL
    );
    """)

    # 3. Parking Slots
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parking_slots (
        id TEXT PRIMARY KEY,
        lot_id TEXT NOT NULL,
        zone TEXT NOT NULL,
        slot_code TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL CHECK(type IN ('2W', '4W', 'EV', 'ACCESSIBLE')),
        status TEXT NOT NULL CHECK(status IN ('AVAILABLE', 'RESERVED', 'OCCUPIED', 'MAINTENANCE')),
        sensor_state TEXT DEFAULT 'VACANT' CHECK(sensor_state IN ('VACANT', 'DETECTED')),
        last_updated TEXT NOT NULL,
        FOREIGN KEY (lot_id) REFERENCES parking_lots(id) ON DELETE CASCADE
    );
    """)

    # 4. Reservations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        slot_id TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        status TEXT NOT NULL CHECK(status IN ('PENDING', 'CONFIRMED', 'CHECKED_IN', 'COMPLETED', 'EXPIRED', 'CANCELLED')),
        vehicle_no TEXT,
        vehicle_type TEXT DEFAULT '4W',
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (slot_id) REFERENCES parking_slots(id)
    );
    """)

    # Database-level constraint to kill double-booking (Page 10-11 of Blueprint)
    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS prevent_reservation_overlap_insert
    BEFORE INSERT ON reservations
    WHEN NEW.status IN ('CONFIRMED', 'CHECKED_IN')
    BEGIN
        SELECT RAISE(ABORT, 'DOUBLE_BOOKING_PREVENTED: Slot is already reserved for this overlapping time window')
        WHERE EXISTS (
            SELECT 1 FROM reservations
            WHERE slot_id = NEW.slot_id
              AND id != NEW.id
              AND status IN ('CONFIRMED', 'CHECKED_IN')
              AND NOT (end_time <= NEW.start_time OR start_time >= NEW.end_time)
        );
    END;
    """)

    cursor.execute("""
    CREATE TRIGGER IF NOT EXISTS prevent_reservation_overlap_update
    BEFORE UPDATE OF status, start_time, end_time ON reservations
    WHEN NEW.status IN ('CONFIRMED', 'CHECKED_IN')
    BEGIN
        SELECT RAISE(ABORT, 'DOUBLE_BOOKING_PREVENTED: Slot is already reserved for this overlapping time window')
        WHERE EXISTS (
            SELECT 1 FROM reservations
            WHERE slot_id = NEW.slot_id
              AND id != NEW.id
              AND status IN ('CONFIRMED', 'CHECKED_IN')
              AND NOT (end_time <= NEW.start_time OR start_time >= NEW.end_time)
        );
    END;
    """)

    # 5. Parking Sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS parking_sessions (
        id TEXT PRIMARY KEY,
        reservation_id TEXT,
        user_id TEXT NOT NULL,
        slot_id TEXT NOT NULL,
        check_in_at TEXT NOT NULL,
        check_out_at TEXT,
        duration_minutes INTEGER DEFAULT 0,
        status TEXT NOT NULL CHECK(status IN ('ACTIVE', 'COMPLETED', 'FORCE_ENDED')),
        overstayed INTEGER DEFAULT 0,
        co2_saved_kg REAL DEFAULT 0.0,
        minutes_saved INTEGER DEFAULT 0,
        FOREIGN KEY (reservation_id) REFERENCES reservations(id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (slot_id) REFERENCES parking_slots(id)
    );
    """)

    # 6. QR Tokens
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS qr_tokens (
        id TEXT PRIMARY KEY,
        reservation_id TEXT NOT NULL,
        token_hash TEXT NOT NULL,
        signature TEXT NOT NULL,
        issued_at TEXT NOT NULL,
        used_at TEXT,
        is_revoked INTEGER DEFAULT 0,
        FOREIGN KEY (reservation_id) REFERENCES reservations(id)
    );
    """)

    # 7. Notifications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        meta_data TEXT,
        sent_at TEXT NOT NULL,
        read INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # 8. Timetables (for ClassSync Allocator)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS timetables (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        day_of_week TEXT NOT NULL,
        class_block TEXT NOT NULL,
        class_name TEXT NOT NULL,
        start_time TEXT NOT NULL,
        end_time TEXT NOT NULL,
        recommended_lot_id TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # 9. Green Stats & FairFlow Points
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS green_stats (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        session_id TEXT,
        minutes_saved INTEGER NOT NULL,
        co2_kg REAL NOT NULL,
        points INTEGER NOT NULL,
        reason TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );
    """)

    # 10. Audit Logs
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        actor TEXT NOT NULL,
        action TEXT NOT NULL,
        entity TEXT NOT NULL,
        details TEXT,
        timestamp TEXT NOT NULL
    );
    """)

    conn.commit()
    seed_data_if_needed(cursor, conn)
    conn.close()

def seed_data_if_needed(cursor, conn):
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] > 0:
        return

    now = datetime.now(timezone.utc)
    now_str = now.isoformat()

    # Seed Default Users
    users_data = [
        ("u_student_1", "Alex Rivera (Student)", "alex@campus.edu", hash_password("pass123"), "STUDENT", "DL-01-AB-1234", "4W", "CS-2023-042", 185, now_str),
        ("u_student_2", "Priya Nair (Student)", "priya@campus.edu", hash_password("pass123"), "STUDENT", "KA-05-XY-7890", "2W", "EC-2023-108", 220, now_str),
        ("u_staff_1", "Dr. Vikram Sharma (Faculty)", "prof.sharma@campus.edu", hash_password("pass123"), "STAFF", "MH-12-DE-5678", "EV", "EMP-FAC-991", 340, now_str),
        ("u_admin_1", "Admin Security Office", "admin@campus.edu", hash_password("admin123"), "ADMIN", "KA-01-SEC-001", "4W", "EMP-SEC-001", 500, now_str),
        ("u_kiosk_1", "North Gate Edge Kiosk", "gate.north@campus.edu", hash_password("kiosk123"), "SECURITY", "KIOSK-NORTH", "4W", "GATE-01", 0, now_str)
    ]
    cursor.executemany("INSERT INTO users VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);", users_data)

    # Seed 4 Parking Lots (Blueprint Section 4 & 5)
    lots_data = [
        ("P1", "P1 · Main Block Lot", "Front courtyard parking adjacent to Academic Blocks A, B, and C", "Block C", 8, 12, 20, 12.9716, 77.5946),
        ("P2", "P2 · Library Digital Wing", "Shaded canopy lot near Central Library and Research Labs", "Library", 8, 16, 24, 12.9725, 77.5955),
        ("P3", "P3 · Hostel Complex Lot", "Spacious open lot near Student Hostels 1-4 and Canteen", "Hostels", 10, 10, 20, 12.9705, 77.5938),
        ("P4", "P4 · Sports Arena Lot", "Large arena lot adjacent to Gymnasium, Stadium, and Auditorium", "Sports Arena", 6, 10, 16, 12.9732, 77.5925)
    ]
    cursor.executemany("INSERT INTO parking_lots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);", lots_data)

    # Seed Slots for each lot
    slots = []
    # P1: 20 slots (Zone A: 10, Zone B: 10)
    for i in range(1, 21):
        zone = "A" if i <= 10 else "B"
        slot_code = f"P1-{zone}-{i:02d}"
        stype = "EV" if i in (1, 2) else ("ACCESSIBLE" if i == 3 else ("2W" if i > 12 else "4W"))
        # Make a few initial occupied/reserved to make the live map vivid on first view
        status = "AVAILABLE"
        if slot_code in ("P1-A-04", "P1-A-05", "P1-B-14"):
            status = "OCCUPIED"
        elif slot_code in ("P1-A-07", "P1-B-12"):
            status = "RESERVED"
        slots.append((f"slot_{slot_code}", "P1", zone, slot_code, stype, status, "DETECTED" if status == "OCCUPIED" else "VACANT", now_str))

    # P2: 24 slots (Library)
    for i in range(1, 25):
        zone = "A" if i <= 12 else "B"
        slot_code = f"LIB-{zone}-{i:02d}"
        stype = "EV" if i in (1, 2, 3) else ("ACCESSIBLE" if i == 4 else ("2W" if i > 16 else "4W"))
        status = "AVAILABLE"
        if slot_code in ("LIB-A-02", "LIB-A-06", "LIB-B-18"):
            status = "OCCUPIED"
        elif slot_code in ("LIB-A-08",):
            status = "RESERVED"
        slots.append((f"slot_{slot_code}", "P2", zone, slot_code, stype, status, "DETECTED" if status == "OCCUPIED" else "VACANT", now_str))

    # P3: 20 slots (Hostel)
    for i in range(1, 21):
        zone = "A" if i <= 10 else "B"
        slot_code = f"HST-{zone}-{i:02d}"
        stype = "2W" if i > 10 else ("EV" if i == 1 else "4W")
        status = "AVAILABLE"
        if slot_code in ("HST-A-03", "HST-B-12"):
            status = "OCCUPIED"
        slots.append((f"slot_{slot_code}", "P3", zone, slot_code, stype, status, "DETECTED" if status == "OCCUPIED" else "VACANT", now_str))

    # P4: 16 slots (Sports Arena)
    for i in range(1, 17):
        zone = "A" if i <= 8 else "B"
        slot_code = f"SPT-{zone}-{i:02d}"
        stype = "EV" if i == 1 else ("ACCESSIBLE" if i == 2 else ("2W" if i > 10 else "4W"))
        status = "AVAILABLE"
        if slot_code in ("SPT-A-05",):
            status = "OCCUPIED"
        slots.append((f"slot_{slot_code}", "P4", zone, slot_code, stype, status, "DETECTED" if status == "OCCUPIED" else "VACANT", now_str))

    cursor.executemany("INSERT INTO parking_slots VALUES (?, ?, ?, ?, ?, ?, ?, ?);", slots)

    # Seed Sample Timetables for Alex (Student) for ClassSync demonstration (Page 5 & 16)
    timetable_data = [
        ("tt_1", "u_student_1", "Monday", "Block C", "CS401: Distributed Cloud Systems", "10:00", "11:30", "P1"),
        ("tt_2", "u_student_1", "Monday", "Library", "CS402: Research Lab Seminar", "13:30", "15:00", "P2"),
        ("tt_3", "u_student_1", "Tuesday", "Block C", "CS405: Embedded IoT Systems", "09:30", "11:00", "P1"),
        ("tt_4", "u_student_1", "Wednesday", "Sports Arena", "PE102: Physical Athletics", "16:00", "17:30", "P4"),
        ("tt_5", "u_student_2", "Monday", "Block C", "EC302: Signal Processing Lab", "10:00", "12:00", "P1")
    ]
    cursor.executemany("INSERT INTO timetables VALUES (?, ?, ?, ?, ?, ?, ?, ?);", timetable_data)

    # Seed 6 Months of Synthetic Sessions for Analytics & GreenMeter (Blueprint Page 15)
    today = datetime.now()
    sample_sessions = []
    sample_green = []
    session_counter = 100

    for days_back in range(90, 0, -3):
        sess_date = today - timedelta(days=days_back)
        date_str = sess_date.strftime("%Y-%m-%d")
        for h in [9, 11, 14, 16]:
            session_counter += 1
            sess_id = f"sess_{session_counter}"
            in_time = f"{date_str}T{h:02d}:05:00Z"
            out_time = f"{date_str}T{h+1:02d}:45:00Z"
            duration = 100
            min_saved = 14  # avg search minutes avoided
            co2 = round(min_saved * 0.045, 2)  # ~0.63 kg
            pts = 25 if (h != 9) else 10 # off-peak reward
            overstay = 1 if (session_counter % 17 == 0) else 0

            sample_sessions.append((
                sess_id, None, "u_student_1" if (session_counter % 2 == 0) else "u_staff_1",
                f"slot_P1-A-{(session_counter % 9 + 1):02d}", in_time, out_time, duration,
                "COMPLETED", overstay, co2, min_saved
            ))

            sample_green.append((
                f"grn_{session_counter}", "u_student_1" if (session_counter % 2 == 0) else "u_staff_1",
                sess_id, min_saved, co2, pts, "Smooth Smart Parking" if pts == 10 else "FairFlow Off-Peak Bonus",
                in_time
            ))

    cursor.executemany("""
    INSERT INTO parking_sessions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, sample_sessions)

    cursor.executemany("""
    INSERT INTO green_stats VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, sample_green)

    # Seed Initial Active Reservation for Alex (Student) with signed QR
    res_start = (datetime.now() + timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:00")
    res_end = (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:00")
    res_id = "RES-1024"
    cursor.execute("""
    INSERT INTO reservations VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (res_id, "u_student_1", "slot_P1-A-07", res_start, res_end, "CONFIRMED", "DL-01-AB-1234", "4W", now_str))

    # Generate Signed JWT QR Token for this demo reservation
    exp_timestamp = int((datetime.now() + timedelta(hours=3)).timestamp())
    qr_payload = {
        "reservationId": res_id,
        "userId": "u_student_1",
        "slotId": "P1-A-07",
        "exp": exp_timestamp
    }
    payload_json = json.dumps(qr_payload, sort_keys=True)
    sig = create_qr_signature(payload_json)
    full_token = f"{payload_json}###SIG###{sig}"

    cursor.execute("""
    INSERT INTO qr_tokens VALUES (?, ?, ?, ?, ?, ?, ?);
    """, ("qr_token_1024", res_id, hashlib.sha256(full_token.encode()).hexdigest(), sig, now_str, None, 0))

    # Seed Notification
    cursor.execute("""
    INSERT INTO notifications VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        "notif_101", "u_student_1", "BOOKING_CONFIRMED", "Reservation Confirmed: Slot P1-A-07",
        "Your parking slot P1-A-07 is reserved from 10:00 AM to 12:00 PM. QR Pass is ready for gate check-in.",
        json.dumps({"reservationId": res_id, "slotCode": "P1-A-07", "lotName": "P1 · Main Block Lot"}),
        now_str, 0
    ))

    # Seed initial audit log
    cursor.execute("""
    INSERT INTO audit_logs VALUES (?, ?, ?, ?, ?, ?);
    """, ("audit_init", "SYSTEM", "SEED_INITIALIZE", "SYSTEM", "System initialized with S.M.A.R.T. baseline configuration", now_str))

    conn.commit()
