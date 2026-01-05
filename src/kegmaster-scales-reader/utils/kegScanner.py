from bleak import BleakScanner
import struct
import asyncio

# The Eddystone Service UUID
EDDYSTONE_UUID = "0000aafe-0000-1000-8000-00805f9b34fb"

def parse_custom_tlm(data):
    """
    Parses the Service Data portion of the packet.
    Expected data starts after the 0xAAFE header.
    """
    try:
        # data[0] is usually the Frame Type (e.g., 0x20 for TLM)
        # We start parsing from the voltage (bytes 1-2)
        voltage = struct.unpack('>H', data[1:3])[0]
        
        # Temperature (8.8 fixed-point)
        temp_int, temp_frac = struct.unpack('>bb', data[4:6])
        temperature = temp_int + (temp_frac / 256.0)
        
        # Weight (The last 3 bytes of your specific packet)
        # We pad with \x00 to make it 4 bytes for unpacking
        weight_bytes = b'\x00' + data[-3:]
        weight_grams = struct.unpack('>I', weight_bytes)[0]
        
        return {
            "voltage_mv": voltage,
            "temp_c": round(temperature, 2),
            "weight_kg": weight_grams / 1000.0
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
