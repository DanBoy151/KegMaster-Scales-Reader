from bleak import BleakScanner
import struct
import asyncio


def parse_beacon_data(service_data_bytes, debug: bool = True):
    """Parse the provided service data bytes and return temperature/weight info.

    This parser computes temperature candidates from a few likely offsets
    (based on observed packets) and returns the most plausible value. When
    `debug=True` it includes all candidate values to help determine the
    correct offset/calibration.
    """
    try:
        # Only use the fixed 2-byte offset (2,4) and compute a single
        # temperature using the `fit_b` linear heuristic. Candidate logic
        # and other heuristics have been removed per request.
        # fit_b used as it is closest to all expected temps with least variation. more data points would be required to updated.
        a, b = (2, 4)
        temp_linear_b = None
        raw_t = None
        if b <= len(service_data_bytes):
            raw_t = struct.unpack('>H', service_data_bytes[a:b])[0]
            temp_linear_b = 5.0 + (raw_t - 4228) * 0.01  # gentle slope fallback

        # Weight parsing (final 3 bytes)
        w_raw = struct.unpack('>I', b'\x00' + service_data_bytes[-3:])[0]
        weight_kg = (w_raw * 0.0038) - 248.55

        result = {
            "raw_w": w_raw,
            "weight": round(weight_kg, 2),
        }

        # Include temperature only from the `fit_b` heuristic (if available).
        if temp_linear_b is not None:
            result["temp"] = round(temp_linear_b, 1)
            # still include raw_t for traceability
            result["raw_t"] = raw_t

        if debug:
            return result

        return result
    except Exception as e:
        return f"Error: {e}"
