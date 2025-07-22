# Funciones para detectar y manipular sprites

from PIL import Image, ImageDraw
import numpy as np
import cv2

def detectar_sprites(imagen, min_size=16):
    """
    Detecta los sprites (regiones con píxeles no transparentes) y devuelve sus cajas [(x, y, w, h)].
    Usa OpenCV sobre una máscara binaria.
    """
    rgba = np.array(imagen)
    alpha = rgba[:, :, 3]  # canal alfa
    _, binary = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)

    # Buscar contornos
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cajas = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if w >= min_size and h >= min_size:
            cajas.append((x, y, w, h))

    return cajas

def dibujar_rectangulos(imagen, cajas, color=(255, 0, 0, 255)):
    """
    Dibuja rectángulos sobre la imagen para cada caja detectada.
    """
    nueva = imagen.copy()
    draw = ImageDraw.Draw(nueva)

    for (x, y, w, h) in cajas:
        draw.rectangle([(x, y), (x + w, y + h)], outline=color, width=2)

    return nueva
