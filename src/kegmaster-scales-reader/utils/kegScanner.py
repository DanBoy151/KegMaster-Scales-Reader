from bleak import BleakScanner
import struct
import asyncio


def parse_beacon_data(service_data_bytes):
    try:
        # TEMPERATURE (Bytes 2 and 3)
        t_raw = struct.unpack('>H', service_data_bytes[2:4])[0]
        
        # Updated NTC Logic: 
        # Using a slope derived from your data points to get closer to your targets
        # We use a base offset of 4278 for 5.0C
        temp_c = 5.0 - (t_raw - 4278) * 0.045
        
        # WEIGHT (Final 3 Bytes)
        w_raw = struct.unpack('>I', b'\x00' + service_data_bytes[-3:])[0]
        
        # Calibrated Weight Logic (Remaining stable)
        weight_kg = (w_raw * 0.0038) - 248.55
        
        return {
            "temp": round(temp_c, 1),
            "weight": round(weight_kg, 2),
            "raw_t": t_raw,
            "raw_w": w_raw
        }
    except Exception as e:
        return f"Error: {e}"
