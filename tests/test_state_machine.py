import pytest
from unittest.mock import MagicMock
from mission.state_machine import CropSprayerMission, MissionState

@pytest.fixture
def mock_controller():
    controller = MagicMock()
    controller.get_position.return_value = {"lat": 50.0614, "lon": 19.9365, "alt": 10.0}
    return controller

def test_full_mission_flow(mock_controller):
    waypoints = [(50.061, 19.936, 10), (50.062, 19.937, 10)]
    images = ["data/clean_field.png", "data/weed_field.png"]

    mission = CropSprayerMission(mock_controller, waypoints, images)
    sprayed = mission.run()

    # Weryfikacja:
    # 1. Sprawdzamy czy stan końcowy to FINISHED
    assert mission.state == MissionState.FINISHED
    # 2. Sprawdzamy czy oprysk wykonał się dokładnie 1 raz 
    assert len(sprayed) == 1
    assert mock_controller.trigger_sprayer.call_count == 1
    # 3. Sprawdzamy czy wywołano RTL
    mock_controller.return_to_launch.assert_called_once()
