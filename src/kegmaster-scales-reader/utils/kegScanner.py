from bleak import BleakScanner
import struct
import asyncio


def parse_beacon_data(service_data_bytes):
    try:
        # TEMPERATURE: Now correctly pulling TWO bytes starting at index 2
        # For b' \x00\x10t...', this grabs \x10t
        t_raw = struct.unpack('>H', service_data_bytes[2:4])[0]
        
        # New Calibration Formula based on your data points:
        # 4212 raw = 3.5c
        # 4234 raw = 7.0c
        # Formula: (Raw - 4190) / 6.28
        temp_c = (t_raw - 4190) / 6.28

        # WEIGHT: Final 3 Bytes (remains correct)
        w_raw = struct.unpack('>I', b'\x00' + service_data_bytes[-3:])[0]
        weight_kg = (w_raw * 0.0038) - 248.55
        
        return {
            "temp": round(temp_c, 1),
            "weight": round(weight_kg, 2),
            "raw_t": t_raw,
            "raw_w": w_raw
        }
    except Exception as e:
        return f"Error: {e}"
