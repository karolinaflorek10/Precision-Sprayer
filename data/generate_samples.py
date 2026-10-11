import cv2
import numpy as np
import os

def generate_data():
    os.makedirs("data", exist_ok=True)

    #Pole-zielone tło
    clean_field = np.full((300, 300, 3), (34, 139, 34), dtype=np.uint8)
    cv2.imwrite("data/clean_field.png", clean_field)

    #Pole z czerwoną rośliną: zielone tło + czerwona plama w środku
    weed_field = clean_field.copy()
    cv2.circle(weed_field, (150, 150), 30, (0, 0, 255), -1) 
    cv2.imwrite("data/weed_field.png", weed_field)

    print("Zapisano próbki: data/clean_field.png oraz data/weed_field.png")

if __name__ == "__main__":
    generate_data()
