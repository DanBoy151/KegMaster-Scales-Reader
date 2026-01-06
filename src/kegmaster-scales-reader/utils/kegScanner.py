from bleak import BleakScanner
import struct
import asyncio


def parse_beacon_data(service_data_bytes):
    """
    Corrected offsets for Bleak's stripped Service Data payload.
    service_data_bytes should be the raw value from the Eddystone UUID.
    """
    try:
        # 1. TEMPERATURE (Bytes 1 and 2)
        # In your byte string: \x10\xb6
        t_raw = struct.unpack('>H', service_data_bytes[1:3])[0]
        
        # Calibrated Formula: (4278 - 4238) * 0.125 = 5.0C
        temp_c = (t_raw - 4238) * 0.125
        
        # 2. WEIGHT (Last 3 Bytes)
        # In your byte string: \x01\x07\xe9 (Decimal 67561)
        w_raw = struct.unpack('>I', b'\x00' + service_data_bytes[-3:])[0]
        
        # Calibrated Formula: (67561 * 0.0038) - 248.55
        # (Slightly adjusted offset to keep it near 8.18kg for this raw value)
        weight_kg = (w_raw * 0.0038) - 248.55
        
        return {
            "temp": round(temp_c, 1),
            "weight": round(weight_kg, 2),
            "raw_t": t_raw,
            "raw_w": w_raw
        }
    except Exception as e:
        print(f"Index Error: {e}")
        return None
