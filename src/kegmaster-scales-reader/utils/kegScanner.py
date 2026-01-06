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
        candidates = []

        # Try several possible 2-byte offsets that have been observed in packets
        possible_offsets = [(2, 4), (4, 6), (6, 8)]
        for a, b in possible_offsets:
            if b <= len(service_data_bytes):
                raw_t = struct.unpack('>H', service_data_bytes[a:b])[0]

                # Candidate temperature calculations (several heuristics):
                temp_ntc = (raw_t - 4184) / 8.0  # older NTC-based heuristic
                temp_linear_a = 5.0 - (raw_t - 4278) * 0.045  # earlier ad-hoc fit
                temp_linear_b = 5.0 + (raw_t - 4228) * 0.01  # gentle slope fallback

                candidates.append({
                    "offset": (a, b),
                    "raw_t": raw_t,
                    "temps": {
                        "ntc": round(temp_ntc, 2),
                        "fit_a": round(temp_linear_a, 2),
                        "fit_b": round(temp_linear_b, 2),
                    },
                })

        # Choose the best candidate by simple heuristic:
        # - prefer temperatures in a reasonable range ([-20, 60])
        # - pick the candidate whose median temperature is closest to that range center (20C)
        picked = None
        best_score = None
        for c in candidates:
            temps = list(c["temps"].values())
            median_temp = sorted(temps)[len(temps) // 2]
            # score = distance from 20C (prefer realistic sensor temps)
            score = abs(median_temp - 20.0)
            if best_score is None or score < best_score:
                best_score = score
                picked = c

        # Fall back: if nothing picked, use first candidate
        if picked is None and candidates:
            picked = candidates[0]

        # Weight parsing (final 3 bytes)
        w_raw = struct.unpack('>I', b'\x00' + service_data_bytes[-3:])[0]
        weight_kg = (w_raw * 0.0038) - 248.55

        result = {
            "raw_w": w_raw,
            "weight": round(weight_kg, 2),
        }

        if picked:
            # Use the 'fit_a' heuristic by default as it was tuned previously;
            # expose raw_t and candidates for debugging/validation.
            result["raw_t"] = picked["raw_t"]
            result["temp"] = round(picked["temps"]["fit_a"], 1)
            if debug:
                result["candidates"] = candidates

        if debug:
            return result

        return result
    except Exception as e:
        return f"Error: {e}"
