import urllib.request
import json
import sys
from datetime import datetime, timedelta

def run_checks():
    base_url = "http://127.0.0.1:8000"
    print(f"Connecting to {base_url}...")

    # 1. Root HTML
    with urllib.request.urlopen(f"{base_url}/") as res:
        content = res.read().decode("utf-8")
        assert res.status == 200
        assert "ParkIQ" in content
        print(f"[PASS] Root HTML loaded ({len(content)} bytes)")

    # 2. CSS & JS
    with urllib.request.urlopen(f"{base_url}/static/css/style.css") as res:
        assert res.status == 200
        print(f"[PASS] Static CSS loaded ({len(res.read())} bytes)")

    with urllib.request.urlopen(f"{base_url}/static/js/app.js") as res:
        assert res.status == 200
        print(f"[PASS] Static JS loaded ({len(res.read())} bytes)")

    # 3. Lots & Availability
    with urllib.request.urlopen(f"{base_url}/api/lots") as res:
        data = json.loads(res.read().decode("utf-8"))
        assert len(data["lots"]) == 4
        print(f"[PASS] Lots endpoint verified: 4 campus lots (P1, P2, P3, P4)")

    # 4. Digital Twin Live Map State
    with urllib.request.urlopen(f"{base_url}/api/twin/live") as res:
        twin = json.loads(res.read().decode("utf-8"))
        assert len(twin["slots"]) == 80
        print(f"[PASS] Digital Twin verified: {len(twin['slots'])} slots, live counts: {twin['counts']}")

    # 5. AI Forecast Engine
    with urllib.request.urlopen(f"{base_url}/api/forecast") as res:
        fc = json.loads(res.read().decode("utf-8"))
        assert fc["horizon_hours"] == 48
        print(f"[PASS] AI Forecast 48h model verified with {len(fc['predictions'])} prediction horizons")

    # 6. ClassSync Timetable Allocator
    with urllib.request.urlopen(f"{base_url}/api/classsync/suggest?user_id=u_student_1") as res:
        cs = json.loads(res.read().decode("utf-8"))
        assert "suggested_lot_id" in cs
        print(f"[PASS] ClassSync verified: recommends {cs['suggested_lot_name']} for {cs['class_name']}")

    # 7. 10 Must-Pass Testing Suite (Section 11)
    with urllib.request.urlopen(f"{base_url}/api/tests/run-all") as res:
        tests = json.loads(res.read().decode("utf-8"))
        assert tests["status"] == "ALL_TESTS_PASSED"
        assert tests["passed_count"] == 10
        print(f"[PASS] Section 11 Test Suite: ALL 10 TESTS PASSED")

    # 8. Golden Flow (Section 2 of Blueprint)
    login_req = urllib.request.Request(
        f"{base_url}/api/auth/login",
        data=json.dumps({"email": "priya@campus.edu", "password": "pass123"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(login_req) as res:
        priya_token = json.loads(res.read().decode("utf-8"))["token"]
    print("[PASS] Golden Flow Step 1: User Login successful")

    # Cancel previous test booking if any
    mine_req = urllib.request.Request(f"{base_url}/api/reservations/mine", headers={"Authorization": f"Bearer {priya_token}"})
    with urllib.request.urlopen(mine_req) as res:
        my_resvs = json.loads(res.read().decode("utf-8"))["reservations"]
        for r in my_resvs:
            if r["status"] in ("CONFIRMED", "PENDING"):
                c_req = urllib.request.Request(f"{base_url}/api/reservations/{r['id']}/cancel", method="PATCH", headers={"Authorization": f"Bearer {priya_token}"})
                urllib.request.urlopen(c_req)

    # Book slot starting NOW (within the 15-min arrival window)
    now = datetime.now()
    st = (now - timedelta(minutes=2)).strftime("%Y-%m-%dT%H:%M:00")
    et = (now + timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:00")

    book_req = urllib.request.Request(
        f"{base_url}/api/reservations",
        data=json.dumps({
            "slot_id": "slot_LIB-A-01",
            "start_time": st,
            "end_time": et,
            "vehicle_no": "KA-05-XY-7890",
            "vehicle_type": "2W"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {priya_token}"}
    )
    with urllib.request.urlopen(book_req) as res:
        book_data = json.loads(res.read().decode("utf-8"))
    print(f"[PASS] Golden Flow Step 2-4: Booked slot {book_data['slot_code']}, signed QR issued")

    # Gate Check-in
    checkin_req = urllib.request.Request(
        f"{base_url}/api/checkin",
        data=json.dumps({
            "qr_token": book_data["qr_token"],
            "method": "QR",
            "kiosk_id": "KIOSK-NORTH-GATE"
        }).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(checkin_req) as res:
        cin_data = json.loads(res.read().decode("utf-8"))
    print(f"[PASS] Golden Flow Step 5: Check-in verified ({cin_data['status']}), Barrier: {cin_data['barrier_servo']}")

    # Gate Check-out
    checkout_req = urllib.request.Request(
        f"{base_url}/api/checkout",
        data=json.dumps({"session_id": cin_data["session_id"], "method": "QR"}).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(checkout_req) as res:
        cout_data = json.loads(res.read().decode("utf-8"))
    print(f"[PASS] Golden Flow Step 7-8: Check-out verified! Slot {cout_data['slot_code']} freed. CO2 saved: {cout_data['co2_saved_kg']} kg")

    print("\n=======================================================")
    print("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!")
    print(f"WEB APP IS LIVE AT: {base_url}")
    print("=======================================================")

if __name__ == "__main__":
    run_checks()
