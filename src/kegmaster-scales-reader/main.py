from src.kegmaster_scales_reader.utils.config import load_scales_config


def main():
    print("Kegmaster Scales Reader is running...")
    try:
        scales = load_scales_config()
    except Exception as e:
        print(f"Warning: failed to load scales config: {e}")
        scales = []

    if scales:
        print("Configured scales:")
        for s in scales:
            print(f" - {s.get('name','<unnamed>')}: {s['address']} ({s['literSize']} L)")
    else:
        print("No scales configured.")


if __name__ == "__main__":
    main()