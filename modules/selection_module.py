from dataclasses import dataclass

@dataclass
class SpriteBox:
    x: int
    y: int
    w: int
    h: int
    selected: bool = False

def punto_en_caja(px, py, box: SpriteBox):
    """
    Retorna True si el punto (px, py) está dentro del rectángulo box.
    """
    return box.x <= px <= box.x + box.w and box.y <= py <= box.y + box.h

def cajas_en_area(x0, y0, x1, y1, boxes):
    """
    Devuelve una lista de cajas que están completamente dentro del rectángulo (x0, y0)-(x1, y1)
    """
    x_min, x_max = sorted([x0, x1])
    y_min, y_max = sorted([y0, y1])

    seleccionadas = []
    for box in boxes:
        if (box.x >= x_min and box.x + box.w <= x_max and
            box.y >= y_min and box.y + box.h <= y_max):
            seleccionadas.append(box)

    return seleccionadas
