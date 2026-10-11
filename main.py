import os
from mission.drone_controller import DroneController
from mission.state_machine import CropSprayerMission

def main():
    print("=" * 60)
    print("Autonomiczny Oprysk Precyzyjny")
    print("=" * 60)

    #Sprawdzenie, czy  próbki danych istnieją
    if not os.path.exists("data/clean_field.png") or not os.path.exists("data/weed_field.png"):
        print("[SETUP] Generuję pliki testowe w data/...")
        import data.generate_samples
        data.generate_samples.generate_data()

    # Domyślne współrzędne domowe w SITL:
    # Lat: -35.363261, Lon: 149.165230
    home_lat = -35.363261
    home_lon = 149.165230

    # Trzy punkty trasy nad polem
    waypoints = [
        (home_lat + 0.0002, home_lon + 0.0002, 10),  # WP 1: czyste pole
        (home_lat + 0.0004, home_lon + 0.0002, 10),  # WP 2: wykrycie chwastu i oprysk
        (home_lat + 0.0004, home_lon + 0.0004, 10),  # WP 3: czyste pole
    ]

    # Symulowane zdjęcia przypisane do kolejnych punktów
    sample_images = [
        "data/clean_field.png",
        "data/weed_field.png",
        "data/clean_field.png"
    ]

    # Inicjalizacja kontrolera i misji
    controller = DroneController(connection_string='udpin:localhost:14551')
    mission = CropSprayerMission(controller, waypoints, sample_images)

    # Start misji
    sprayed_spots = mission.run()

    print("\n" + "=" * 60)
    print("RAPORT KOŃCOWY MISJI:")
    print(f"Liczba zlikwidowanych ognisk chwastów: {len(sprayed_spots)}")
    for i, spot in enumerate(sprayed_spots, 1):
        print(f"  [{i}] Oprysk wykonany na współrzędnych: Lat {spot[0]:.6f}, Lon {spot[1]:.6f}")
    print("=" * 60)

if __name__ == "__main__":
    main()
