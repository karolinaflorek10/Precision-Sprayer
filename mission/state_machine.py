import time
from enum import Enum
from mission.detector import RedTargetDetector

class MissionState(Enum):
    INIT = "INIT"
    TAKEOFF = "TAKEOFF"
    PATROL = "PATROL"
    SPRAYING = "SPRAYING"
    RTL = "RTL"
    FINISHED = "FINISHED"
    ERROR = "ERROR"

class CropSprayerMission:
    def __init__(self, controller, waypoints, sample_images):
        """
        controller: instancja DroneController
        waypoints: lista krotek (lat, lon, alt)
        sample_images: lista ścieżek do zdjęć symulujących widok z kamery w kolejnych punktach
        """
        self.controller = controller
        self.waypoints = waypoints
        self.sample_images = sample_images
        self.detector = RedTargetDetector(min_pixel_count=150)
        self.state = MissionState.INIT
        self.current_wp_index = 0
        self.sprayed_locations = []

    def run(self):
        """Główna pętla wykonawcza maszyny stanów."""
        print(f"[FSM] Rozpoczynam misję w stanie: {self.state.value}")

        while self.state != MissionState.FINISHED and self.state != MissionState.ERROR:
            
            if self.state == MissionState.INIT:
                self._handle_init()

            elif self.state == MissionState.TAKEOFF:
                self._handle_takeoff()

            elif self.state == MissionState.PATROL:
                self._handle_patrol()

            elif self.state == MissionState.SPRAYING:
                self._handle_spraying()

            elif self.state == MissionState.RTL:
                self._handle_rtl()

            time.sleep(1)

        print(f"[FSM] Misja zakończona w stanie: {self.state.value}")
        return self.sprayed_locations

    def _handle_init(self):
        try:
            self.controller.connect()
            self.controller.set_mode("GUIDED")
            self.controller.arm()
            self.state = MissionState.TAKEOFF
        except Exception as e:
            print(f"[FSM-BŁĄD] Inicjalizacja nie powiodła się: {e}")
            self.state = MissionState.ERROR

    def _handle_takeoff(self):
        try:
            target_alt = 10.0
            self.controller.takeoff(target_altitude=target_alt)
            print("[FSM] Osiągnięto pułap patrolowy. Przechodzę do PATROL.")
            self.state = MissionState.PATROL
        except Exception as e:
            print(f"[FSM-BŁĄD] Błąd podczas startu: {e}")
            self.state = MissionState.RTL

    def _handle_patrol(self):
        if self.current_wp_index >= len(self.waypoints):
            print("[FSM] Wszystkie punkty trasy odwiedzone. Powrót do bazy.")
            self.state = MissionState.RTL
            return

        lat, lon, alt = self.waypoints[self.current_wp_index]
        print(f"[FSM] Lot do punktu {self.current_wp_index + 1}/{len(self.waypoints)}...")
        self.controller.goto_location(lat, lon, alt)
        
        # Czas na dolot do punktu w symulacji
        time.sleep(6)

        # Pobranie wirtualnego zdjęcia odpowiadającego aktualnemu punktowi
        image_path = self.sample_images[self.current_wp_index]
        print(f"[SENSOR] Analiza obrazu z kamery pod dronem: {image_path}")
        
        detected, red_count = self.detector.detect(image_path)
        if detected:
            print(f"[SENSOR] WYKRYTO CHWAST! (piksele czerwone: {red_count})")
            self.state = MissionState.SPRAYING
        else:
            print("[SENSOR] Uprawa czysta, brak chwastów.")
            self.current_wp_index += 1

    def _handle_spraying(self):
        pos = self.controller.get_position()
        print(f"[ACTION] Pozycja do oprysku: {pos}")
        
        # Wykonanie oprysku
        self.controller.trigger_sprayer(duration_sec=2.0)
        
        if pos:
            self.sprayed_locations.append((pos['lat'], pos['lon']))

        # Po oprysku przechodzimy do kolejnego punktu
        self.current_wp_index += 1
        self.state = MissionState.PATROL

    def _handle_rtl(self):
        try:
            self.controller.return_to_launch()
            print("[FSM] Dron wraca i ląduje. Czekam na zakończenie...")
            time.sleep(5)
            self.state = MissionState.FINISHED
        except Exception as e:
            print(f"[FSM-BŁĄD] Błąd RTL: {e}")
            self.state = MissionState.ERROR
