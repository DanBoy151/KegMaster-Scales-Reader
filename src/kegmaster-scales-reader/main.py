from utils.config import load_scales_config

import asyncio
from typing import Dict

try:
    from bleak import BleakScanner
except Exception:
    BleakScanner = None  # type: ignore

from utils.kegScanner import EDDYSTONE_UUID, parse_custom_tlm


def _normalize_mac(addr: str) -> str:
    # Normalize by removing separators and uppercasing hex digits
    return ''.join([c for c in addr.upper() if c in '0123456789ABCDEF'])


async def _scan_for_scales(scales_map: Dict[str, dict]):
    if BleakScanner is None:
        print("BLE scanning requires 'bleak'. Install with: pip install bleak")
        return

    seen = set()

    def _detection(device, advertisement_data):
        addr_norm = _normalize_mac(device.address)
        if addr_norm not in scales_map:
            return

        # service_data keys may be uuids; check for eddystone
        svc = advertisement_data.service_data
        if not svc:
            return

        # keys are lower-case UUIDs in Bleak
        if EDDYSTONE_UUID in svc:
            raw = svc[EDDYSTONE_UUID]
            stats = parse_custom_tlm(raw)
            scale = scales_map[addr_norm]
            print(f"== Scale: {scale.get('name','<unnamed>')} ({device.address}) ==")
            print(f"  RSSI: {device.rssi}")
            print(f"  Payload: {raw.hex().upper()}")
            print(f"  Parsed: {stats}")
            print("" + "-" * 40)
            seen.add(addr_norm)

    print("Starting scanner for configured scales... (Ctrl+C to stop)")
    scanner = BleakScanner(_detection)
    await scanner.start()
    try:
        while True:
            await asyncio.sleep(1.0)
    except KeyboardInterrupt:
        await scanner.stop()
        print("Scanner stopped.")


def main():
    print("Kegmaster Scales Reader is running...")
    try:
        scales = load_scales_config()
    except Exception as e:
        print(f"Warning: failed to load scales config: {e}")
        scales = []

    if not scales:
        print("No scales configured.")
        return

    # Build lookup by normalized MAC
    scales_map: Dict[str, dict] = {}
    print("Configured scales:")
    for s in scales:
        addr = s.get('address')
        if not addr:
            continue
        norm = _normalize_mac(addr)
        scales_map[norm] = s
        print(f" - {s.get('name','<unnamed>')}: {addr} ({s.get('literSize')} L)")

    # Start scanning loop
    try:
        asyncio.run(_scan_for_scales(scales_map))
    except Exception as e:
        print(f"Scanner error: {e}")


if __name__ == "__main__":
    main()