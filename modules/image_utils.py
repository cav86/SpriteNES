# Carga de imagen, borrado de fondo, exportación
from PIL import Image
import numpy as np
from collections import Counter

def load_image(path):
    """Carga una imagen y la convierte a RGBA."""
    image = Image.open(path).convert("RGBA")
    return image

def detect_background_color(image, border_width=1):
    """
    Detecta el color más común en los bordes de la imagen.
    Se usa como color de fondo para eliminarlo.
    """
    pixels = np.array(image)
    h, w = pixels.shape[:2]
    
    border_pixels = []
    border_pixels.extend(pixels[0:border_width, :, :].reshape(-1, 4))         # borde superior
    border_pixels.extend(pixels[-border_width:, :, :].reshape(-1, 4))        # borde inferior
    border_pixels.extend(pixels[:, 0:border_width, :].reshape(-1, 4))        # borde izquierdo
    border_pixels.extend(pixels[:, -border_width:, :].reshape(-1, 4))        # borde derecho

    # Convertir los píxeles a tuplas para contar ocurrencias
    colors = [tuple(px) for px in border_pixels]
    most_common_color = Counter(colors).most_common(1)[0][0]
    return most_common_color

def remove_background(image, bg_color, tolerance=10):
    """
    Elimina el color de fondo de la imagen (lo vuelve transparente).
    bg_color: (R,G,B,A)
    tolerance: cuán diferente puede ser un píxel del color de fondo
    """
    pixels = np.array(image)
    new_pixels = []

    for row in pixels:
        new_row = []
        for px in row:
            # Compara solo R, G y B con tolerancia
            if all(abs(int(px[i]) - int(bg_color[i])) <= tolerance for i in range(3)):
                new_row.append((0, 0, 0, 0))  # transparente
            else:
                new_row.append(tuple(px))
        new_pixels.append(new_row)

    new_img = Image.fromarray(np.array(new_pixels, dtype=np.uint8), mode="RGBA")
    return new_img

def preprocess_image(path):
    """
    Carga una imagen, detecta el fondo y lo elimina.
    Devuelve la imagen lista para detección.
    """
    img = load_image(path)
    bg_color = detect_background_color(img)
    clean_img = remove_background(img, bg_color)
    return clean_img
