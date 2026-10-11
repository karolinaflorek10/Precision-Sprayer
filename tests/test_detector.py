import os
import pytest
from mission.detector import RedTargetDetector

@pytest.fixture
def detector():
    return RedTargetDetector(min_pixel_count=100)

def test_detects_red_weed(detector):
    detected, count = detector.detect("data/weed_field.png")
    assert detected is True
    assert count > 100

def test_ignores_clean_field(detector):
    detected, count = detector.detect("data/clean_field.png")
    assert detected is False
    assert count == 0
