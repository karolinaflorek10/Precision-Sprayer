import cv2
import numpy as np

class RedTargetDetector:
    """
    Prosty detektor chwastów bazujący na standardowym 
    algorytmie progowania barwnego OpenCV (HSV Color Segmentation).
    Wykrywa czerwone obiekty na zielonym tle uprawy.
    """
    def __init__(self, min_pixel_count=200):
        self.min_pixel_count = min_pixel_count

    def detect(self, image_path):
        """
        Wczytuje obraz i zwraca True, jeśli liczba czerwonych pikseli 
        przekracza ustalony próg błędu.
	"""
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"Nie znaleziono pliku: {image_path}")

        # Konwersja obrazu z BGR do HSV
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        # Maski progowe
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        red_mask = mask1 | mask2

        # Zliczanie wykrytych czerwonych pikseli
        red_pixels = cv2.countNonZero(red_mask)

        is_detected = red_pixels >= self.min_pixel_count
        return is_detected, red_pixels
