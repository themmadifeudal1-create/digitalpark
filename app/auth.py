import json
import hmac
import hashlib
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from app.database import SERVER_SECRET, hash_password, get_db

JWT_SECRET = SERVER_SECRET
JWT_ALGORITHM = "HS256"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hash_password(plain_password) == hashed_password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=8))
    to_encode.update({"exp": int(expire.timestamp())})
    header = {"alg": JWT_ALGORITHM, "typ": "JWT"}
    
    import base64
    def b64url(s: bytes) -> str:
        return base64.urlsafe_b64encode(s).decode("utf-8").rstrip("=")

    header_b64 = b64url(json.dumps(header).encode("utf-8"))
    payload_b64 = b64url(json.dumps(to_encode).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}"
    signature = hmac.new(JWT_SECRET.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = b64url(signature)
    return f"{signing_input}.{sig_b64}"

def decode_access_token(token: str) -> Optional[dict]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        header_b64, payload_b64, sig_b64 = parts
        import base64
        def b64url_decode(s: str) -> bytes:
            rem = len(s) % 4
            if rem > 0:
                s += "=" * (4 - rem)
            return base64.urlsafe_b64decode(s)

        signing_input = f"{header_b64}.{payload_b64}"
        expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256).digest()
        actual_sig = b64url_decode(sig_b64)
        if not hmac.compare_digest(expected_sig, actual_sig):
            return None

        payload_bytes = b64url_decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))
        if payload.get("exp") and time.time() > payload["exp"]:
            return None
        return payload
    except Exception:
        return None

# --- S.M.A.R.T. Standout: QR Code Cryptographic Signing & Edge Verification ---
def generate_signed_qr_payload(reservation_id: str, user_id: str, slot_code: str, exp_timestamp: int) -> dict:
    payload = {
        "reservationId": reservation_id,
        "userId": user_id,
        "slotId": slot_code,
        "exp": exp_timestamp,
        "v": "1.0"
    }
    payload_str = json.dumps(payload, sort_keys=True)
    signature = hmac.new(SERVER_SECRET.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256).hexdigest()
    
    # Bundle into signed token string
    token_str = f"PARKIQ::{payload_str}::SIG::{signature}"
    return {
        "payload": payload,
        "signature": signature,
        "token_str": token_str
    }

def verify_signed_qr(token_str: str) -> Dict[str, Any]:
    """
    EdgeGuard Gate Kiosk verification logic.
    Rejection cases (Section 9):
    1. Forged QR (Signature check fails)
    2. Expired QR (Past exp claim)
    3. Invalid format
    """
    if not token_str or not token_str.startswith("PARKIQ::"):
        return {"valid": False, "reason": "FORGED_QR", "message": "Invalid QR signature: Unrecognized ticket structure"}

    try:
        parts = token_str.split("::")
        if len(parts) != 4 or parts[2] != "SIG":
            return {"valid": False, "reason": "FORGED_QR", "message": "Signature check failed: Malformed tamper attempt"}
        
        payload_str = parts[1]
        provided_sig = parts[3]
        expected_sig = hmac.new(SERVER_SECRET.encode("utf-8"), payload_str.encode("utf-8"), hashlib.sha256).hexdigest()
        
        if not hmac.compare_digest(expected_sig, provided_sig):
            return {"valid": False, "reason": "FORGED_QR", "message": "Signature check failed: Cryptographic signature does not match server authority"}

        payload = json.loads(payload_str)
        current_time = int(time.time())

        if payload.get("exp") and current_time > payload["exp"]:
            return {"valid": False, "reason": "EXPIRED_QR", "message": f"QR Expired: Ticket deadline passed at {datetime.fromtimestamp(payload['exp']).strftime('%H:%M:%S')}"}

        return {"valid": True, "payload": payload, "signature": provided_sig}
    except Exception as e:
        return {"valid": False, "reason": "FORGED_QR", "message": f"Cryptographic verification error: {str(e)}"}
