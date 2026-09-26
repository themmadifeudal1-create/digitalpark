from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any

class UserRegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = Field(default="STUDENT", description="STUDENT, STAFF, ADMIN, or SECURITY")
    vehicle_no: Optional[str] = "DL-01-AB-1234"
    vehicle_type: Optional[str] = "4W"
    roll_no: Optional[str] = None

class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str

class ReservationCreateRequest(BaseModel):
    slot_id: str
    start_time: str
    end_time: str
    vehicle_no: Optional[str] = None
    vehicle_type: Optional[str] = "4W"

class CheckInRequest(BaseModel):
    qr_token: Optional[str] = None
    reservation_id: Optional[str] = None
    method: str = Field(default="QR", description="QR, ANPR, or RFID")
    vehicle_no: Optional[str] = None
    kiosk_id: str = "KIOSK-NORTH-GATE"
    offline_verified: bool = False

class CheckOutRequest(BaseModel):
    qr_token: Optional[str] = None
    session_id: Optional[str] = None
    slot_id: Optional[str] = None
    method: str = Field(default="QR", description="QR, GEOFENCE, or ADMIN")

class SlotStatusUpdateRequest(BaseModel):
    sensor_state: str = Field(description="VACANT or DETECTED")
    battery_level: Optional[int] = 95
    rssi: Optional[int] = -62

class GeofenceExitRequest(BaseModel):
    user_id: str
    lat: float
    lng: float
    distance_to_boundary_m: float = 350.0

class LotCreateRequest(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    campus_block: str
    capacity_2w: int = 10
    capacity_4w: int = 15
    lat: float = 12.9716
    lng: float = 77.5946

class SlotCreateRequest(BaseModel):
    lot_id: str
    zone: str = "A"
    slot_code: str
    type: str = "4W"
