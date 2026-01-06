from bleak import BleakScanner
import struct
import asyncio


def parse_beacon_data(raw_bytes):
    """
    Final calibrated logic based on provided examples:
    Ex 1: 15.85kg / 7.0C
    Ex 2: 10.11kg / 3.5C
    Ex 3: 8.18kg / 5.0C
    """
    try:
        # TEMPERATURE: Bytes 15-16
        # Formula: (Raw - 4238) * 0.125
        t_raw = struct.unpack('>H', raw_bytes[15:17])[0]
        temp_c = (t_raw - 4238) * 0.125
        
        # WEIGHT: Final 3 bytes
        # Formula: (Raw * 0.0038) - 248.66
        w_raw = struct.unpack('>I', b'\x00' + raw_bytes[-3:])[0]
        weight_kg = (w_raw * 0.0038) - 248.66
        
        return {
            "temp": round(temp_c, 1),
            "weight": round(weight_kg, 2),
            "raw_t": t_raw,
            "raw_w": w_raw
        }
    except Exception as e:
        print(f"Parsing error: {e}")
        return None
