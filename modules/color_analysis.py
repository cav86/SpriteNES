from collections import Counter

def contar_colores_en_sprites(imagen, cajas):
    """
    Recorre los pixeles de los rectángulos dados y cuenta la cantidad de veces que aparece cada color.
    Retorna un Counter con los colores y su frecuencia.
    """
    diccionario_colores = Counter()
    for (x, y, w, h) in cajas:
        for i in range(x, x + w):
            for j in range(y, y + h):
                if i < imagen.width and j < imagen.height:
                    pixel = imagen.getpixel((i, j))
                    if pixel[3] > 0:  # ignorar transparencia
                        diccionario_colores[pixel[:3]] += 1
    return diccionario_colores

def obtener_top_colores(diccionario_colores, top_n=10):
    """
    Retorna los top_n colores más comunes en el diccionario.
    """
    return diccionario_colores.most_common(top_n)
