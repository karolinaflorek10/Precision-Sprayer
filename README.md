## Autonomiczna Misja Oprysku Precyzyjnego 

System realizuje autonomiczną misję bezzałogowego statku powietrznego (UAV) wykonującego zadanie rolnictwa precyzyjnego: 
patrolowanie uprawy, wykrywanie ognisk zachwaszczenia za pomocą analizy obrazu oraz wykonanie punktowego oprysku (symulacja zaworu serwomechanizmu przez MAVLink) zakończonego bezpiecznym powrotem do bazy (RTL).

---

## Spis Treści
1. [Koncepcja misji](#1-koncepcja-misji)
2. [Przebieg prawidłowego scenariusza](#2-przebieg-prawidłowego-scenariusza)
3. [Architektura rozwiązania i komponenty](#3-architektura-rozwiązania-i-komponenty)
4. [Wykorzystane źródła i biblioteki](#4-wykorzystane-źródła-i-biblioteki)
5. [Instrukcja instalacji i uruchomienia](#5-instrukcja-instalacji-i-uruchomienia)
6. [Sposób uruchomienia symulacji w SITL / Mission Plannerze](#6-sposób-uruchomienia-symulacji-w-sitl--mission-plannerze)
7. [Sposób uruchomienia testów automatycznych](#7-sposób-uruchomienia-testów-automatycznych)
8. [Scenariusze testowe i oczekiwane wyniki](#8-scenariusze-testowe-i-oczekiwane-wyniki)
9. [Przyjęte uproszczenia i ograniczenia symulacji](#9-przyjęte-uproszczenia-i-ograniczenia-symulacji)
10. [Pomysły na dalszy rozwój rozwiązania](#10-pomysły-na-dalszy-rozwój-rozwiązania)

---

## 1. Koncepcja misji

Projekt symuluje zadanie inspekcji i precyzyjnego zabiegu agrotechnicznego. 
Tradycyjny oprysk całego pola generuje wysokie koszty i obciąża środowisko. Celem systemu jest:
- Autonomiczny oblot rzędów uprawy w zadanym obszarze,
- Analiza obrazu z kamery pod dronem pod kątem wykrywania anomalii barwnych (czerwonych chwastów na zielonym tle uprawy),
- Reakcja wykonawcza: zatrzymanie w rejonie detekcji, uruchomienie układu dozującego (otwarcie zaworu oprysku przez komendę sterowania serwem MAVLink),
- Zapis koordynatów GPS potraktowanego obszaru i powrót na lądowisko.

---

## 2. Przebieg prawidłowego scenariusza

1. **Inicjalizacja (INIT):** Połączenie z autopilotem przez interfejs UDP, odbiór pierwszego sygnału heartbeat, weryfikacja trybu oraz uzbrojenie silników (`ARM`).
2. **Start (TAKEOFF):** Wzniesienie drona w trybie `GUIDED` na wysokość operacyjną 10 m AGL.
3. **Patrol (PATROL):** Przelot wzdłuż wyznaczonych punktów trasy (waypointów) nad uprawą.
4. **Inspekcja sensoryczna:** Po dotarciu do punktu następuje pobranie klatki z kamery podpokładowej i analiza algorytmem wizyjnym.
5. **Reakcja na detekcję (SPRAYING):** W razie wykrycia ogniska chwastów następuje wyzwolenie procedury oprysku (komenda `MAV_CMD_DO_SET_SERVO` otwierająca zawór na 2 sekundy) oraz odnotowanie pozycji w raporcie. W przypadku braku detekcji dron natychmiast kontynuuje lot do kolejnego punktu.
6. **Powrót i lądowanie (RTL):** Po zrealizowaniu planu trasy system aktywuje tryb `RTL` (Return to Launch), dron wraca na współrzędne startu i bezpiecznie ląduje.

---

## 3. Architektura rozwiązania i komponenty

System zaprojektowano zgodnie z zasadą modularności i separacji odpowiedzialności (Separation of Concerns):

```text
Precision-Sprayer/
├── mission/
│   ├── drone_controller.py   # Warstwa abstrakcji MAVLink / pymavlink (komendy lotu, telemetria)
│   ├── detector.py           # Moduł wizyjny (detekcja koloru w przestrzeni HSV przy użyciu OpenCV)
│   └── state_machine.py      # Deterministyczna maszyna stanów sterująca przepływem misji
├── data/
│   ├── generate_samples.py   # Generator syntetycznych danych testowych (obrazy pola)
│   ├── clean_field.png       # Próbka: czysta uprawa
│   └── weed_field.png        # Próbka: uprawa z wykrywalną anomalią chwastu
├── tests/
│   ├── test_detector.py      # Testy jednostkowe modułu analizy obrazu
│   └── test_state_machine.py # Testy jednostkowe logiki FSM z wykorzystaniem mocków
├── main.py                   # Główny punkt wejścia do aplikacji
├── requirements.txt          # Zależności biblioteczne
└── README.md                 # Dokumentacja projektu
```
Maszyna stanów (Finite State Machine):
Przepływ misji jest kontrolowany przez stany:
INIT -> TAKEOFF -> PATROL <-> SPRAYING -> RTL -> FINISHED (z obsługą przejścia do ERROR w sytuacjach awaryjnych).

---

## 4. Wykorzystane źródła i biblioteki

pymavlink – oficjalna implementacja protokołu MAVLink w Pythonie, użyta do komunikacji telemetrycznej i wysyłania komend do autopilota ArduPilot.

OpenCV (opencv-python) i NumPy – do implementacji algorytmu segmentacji barwnej w przestrzeni HSV.

pytest – środowisko do automatycznych testów jednostkowych i integracyjnych.

ArduPilot SITL / MAVProxy – środowisko symulacji dynamiki lotu i autopilota.

---

### 5. Instrukcja instalacji i uruchomienia
Wymagania wstępne:
System Linux (np. Ubuntu 20.04 / 22.04) lub WSL2
Python w wersji 3.8+

Krok 1: Klonowanie repozytorium i utworzenie środowiska
```text
git clone https://github.com/karolinaflorek10/Precision-Sprayer.git
cd Precision-Sprayer
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Krok 2: Przygotowanie danych testowych
Jeśli obrazy nie istnieją, można je wygenerować jednym poleceniem:
```text
python data/generate_samples.py
```
Krok 3: Uruchomienie misji
```text
source venv/bin/activate
python main.py
```
---

### 6. Sposób uruchomienia symulacji w SITL / Mission Plannerze
Opcja A: Bezpośrednio w terminalu
Symulator ArduCopter SITL uruchamiamy z przekierowaniem strumienia MAVLink na port 14551 dla skryptu:
```text
cd ~/ardupilot/ArduCopter
sim_vehicle.py -v ArduCopter --out=udp:127.0.0.1:14551
```
Opcja B: Poprzez Mission Planner Simulation (Windows / Mono)
1. W Mission Plannerze przejdź do zakładki Simulation.
2. Wybierz model Multirotor (ArduCopter) i uruchom symulację.
3. W konsoli MAVProxy lub w ustawieniach połączeń Mission Plannera upewnij się, że strumień UDP jest kierowany na port 14551 (output add 127.0.0.1:14551).
4. Uruchom skrypt python main.py.

---

### 7. Sposób uruchomienia testów automatycznych
Testy sprawdzają poprawność logiki FSM oraz modułu detektora bez potrzeby uruchamiania autopilota czy symulatora fizyki
```text
pytest -v
```
Oczekiwany wynik:
```text
tests/test_detector.py::test_detects_red_weed PASSED
tests/test_detector.py::test_ignores_clean_field PASSED
tests/test_state_machine.py::test_full_mission_flow PASSED
```
---

### 8. Scenariusze testowe i ich oczekiwane wyniki
Scenariusz pozytywny (chwast wykryty):
Obraz wejściowy: weed_field.png
Oczekiwane zachowanie: funkcja detect() zwraca True, FSM przełącza się w stan SPRAYING, aktywuje serwo zaworu na 2s, loguje współrzędne i wraca do PATROL.

Scenariusz negatywny (czysta uprawa):
Obraz wejściowy: clean_field.png
Oczekiwane zachowanie: brak detekcji, pominięcie procedury oprysku, natychmiastowy przelot do kolejnego punktu.

Scenariusz izolowany FSM (Mocking):
Weryfikacja sekwencji przejść stanów od INIT, przez przelot, po RTL w teście jednostkowym test_state_machine.py.

---

### 9. Przyjęte uproszczenia i ograniczenia symulacji
Kamera: Zamiast pełnej symulacji rendera 3D kamery w czasie rzeczywistym zastosowano wirtualny moduł kamery wczytujący syntetyczne próbki terenowe przypisane do rejonu waypointów.
Układ wykonawczy oprysku: Fizyczny zawór opryskiwacza i pompa zostały zasymulowane standardową komendą MAVLink MAV_CMD_DO_SET_SERVO.
Algorytm wizyjny: Użyto klasycznego algorytmu segmentacji barwnej HSV zamiast ciężkich sieci neuronowych.

---

### 10. Pomysły na dalszy rozwój rozwiązania

Pomysłem na dalszy rozwój rozwiązania jest wdrożenie zaawansowanej klasyfikacji upraw za pomocą wykorzystania uczenia maszynowego.
