import time
import math
from pymavlink import mavutil

class DroneController:
    def __init__(self, connection_string='udpin:localhost:14551'):
        self.connection_string = connection_string
        self.vehicle = None

    def connect(self):
        #Ustanawia połączenie i oczekuje na sygnał heartbeat.
        print(f"[DRONE] Łączenie przez {self.connection_string}...")
        self.vehicle = mavutil.mavlink_connection(self.connection_string)
        self.vehicle.wait_heartbeat()
        print(f"[DRONE] Połączono! SysID: {self.vehicle.target_system}, CompID: {self.vehicle.target_component}")

    def set_mode(self, mode_name="GUIDED"):
        #Zmienia tryb lotu autopilota.
        print(f"[DRONE] Zmiana trybu na {mode_name}...")
        mode_id = self.vehicle.mode_mapping().get(mode_name)
        if mode_id is None:
            raise ValueError(f"Nieznany tryb lotu: {mode_name}")
        self.vehicle.set_mode(mode_id)

    def arm(self):
        #Uzbraja silniki i czeka na potwierdzenie.
        print("[DRONE] Uzbrajanie silników...")
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
            0, 1, 0, 0, 0, 0, 0, 0
        )
        self.vehicle.motors_armed_wait()
        print("[DRONE] Silniki uzbrojone!")

    def takeoff(self, target_altitude=10.0):
        #Wznosi drona na wskazaną wysokość.
        print(f"[DRONE] Start na wysokość {target_altitude} m...")
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0, 0, target_altitude
        )
        # Oczekiwanie na osiągnięcie pułapu
        while True:
            msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=5)
            if msg:
                current_alt = msg.relative_alt / 1000.0
                if current_alt >= target_altitude * 0.95:
                    print(f"[DRONE] Osiągnięto pułap: {current_alt:.2f} m")
                    break
            time.sleep(0.5)

    def goto_location(self, lat, lon, alt):
       #Wysyła drona do współrzędnych GPS w trybie GUIDED.
        print(f"[DRONE] Lot do punktu: Lat={lat}, Lon={lon}, Alt={alt}m...")
        self.vehicle.mav.mission_item_int_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT,
            mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
            2, 0, 0, 0, 0, 0,
            int(lat * 1e7),
            int(lon * 1e7),
            alt
        )

    def get_position(self):
       #Zwraca słownik z bieżącymi współrzędnymi i wysokością.
        msg = self.vehicle.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=3)
        if msg:
            return {
                "lat": msg.lat / 1e7,
                "lon": msg.lon / 1e7,
                "alt": msg.relative_alt / 1000.0
            }
        return None

    def trigger_sprayer(self, duration_sec=2.0):
       #Symulacja oprysku: aktywacja zaworu przez MAVLink.
        print(f"[ACTION] >>> OPRYSK ROZPOCZĘTY (otwarcie zaworu na {duration_sec}s) <<<")
        # Przykładowa komenda wysterowania wyjścia PWM serwa.
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0, 5, 1900, 0, 0, 0, 0, 0
        )
        time.sleep(duration_sec)
        # Zamknięcie zaworu
        self.vehicle.mav.command_long_send(
            self.vehicle.target_system,
            self.vehicle.target_component,
            mavutil.mavlink.MAV_CMD_DO_SET_SERVO,
            0, 5, 1100, 0, 0, 0, 0, 0
        )
        print("[ACTION] >>> OPRYSK ZAKOŃCZONY (zamknięcie zaworu) <<<")

    def return_to_launch(self):
        #Włącza procedurę powrotu i lądowania.
        print("[DRONE] Zmiana trybu na RTL (Powrót do bazy)")
        self.set_mode("RTL")
