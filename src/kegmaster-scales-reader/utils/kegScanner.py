from bleak import BleakScanner
import struct
import asyncio

# The Eddystone Service UUID
EDDYSTONE_UUID = "0000aafe-0000-1000-8000-00805f9b34fb"

def parse_custom_tlm(hex_string):
    try:
        data = bytes.fromhex(hex_string)
        service_data = data[11:]

        # --- 1. Extract Raw Values ---
        # Temperature: Bytes 15-16
        t_raw = struct.unpack('>H', service_data[4:6])[0]

        # Weight: Final 3 Bytes
        w_raw = struct.unpack('>I', b'\x00' + service_data[-3:])[0]

        # --- 2. Temperature Calculation ---
        # Based on your data: 7.0C at 4240 and 3.5C at 4212
        # Slope: 8 counts per degree
        temp_c = (t_raw - 4184) / 8.0

        # --- 3. Temperature-Compensated Weight ---
        # m1 (Weight Gain), m2 (Temp Compensation Factor), and b (Intercept)
        # These constants are derived to minimize the error across all 3 examples.
        m1 = 0.00371   # Scale factor for raw weight
        m2 = -0.0512   # Correction for thermal drift (kg per raw temp count)
        b = -22.45     # Baseline offset

        # Formula: (RawWeight * Scale) + (RawTemp * DriftCorrection) + Intercept
        weight_kg = (w_raw * m1) + (t_raw * m2) + b

        return {
            "temperature_c": round(temp_c, 2),
            "weight_kg": round(weight_kg, 2),
            "raw_debug": {"t": t_raw, "w": w_raw}
        }
    except Exception as e:
        return f"Parse Error: {e}"

def detection_callback(device, advertisement_data):
    # Check if the Eddystone UUID is in the service data
    if EDDYSTONE_UUID in advertisement_data.service_data:
        raw_payload = advertisement_data.service_data[EDDYSTONE_UUID]
        
        # In your raw hex, the Service Data started with BEE4...
        # Bleak provides the value associated with the UUID key
        stats = parse_custom_tlm(raw_payload)
        
        print(f"Device: {device.address} | RSSI: {device.rssi}")
        print(f"  Payload: {raw_payload.hex().upper()}")
        print(f"  Data: {stats}")
        print("-" * 40)

async def main():
    print("Scanning for BLE Beacon packets... (Ctrl+C to stop)")
    scanner = BleakScanner(detection_callback)
    
    await scanner.start()
    try:
        while True:
            await asyncio.sleep(1.0)
    except KeyboardInterrupt:
        await scanner.stop()
        print("\nScanner stopped.")

if __name__ == "__main__":
    asyncio.run(main())
