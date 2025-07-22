import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image, ImageDraw
from modules.image_utils import preprocess_image
from modules import sprite_detection
from modules.selection_module import SpriteBox, punto_en_caja, cajas_en_area

# Crear ventana
root = tk.Tk()
root.title("Sprite Tool")
root.geometry("1000x600")

# Variables globales
imagen_procesada = None
sprite_boxes = []
seleccion_inicial = None
rectangulo_temp = None

# Marco principal
frame_imagenes = tk.Frame(root)
frame_imagenes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Panel izquierdo
frame_izquierda = tk.Frame(frame_imagenes)
frame_izquierda.pack(side=tk.LEFT, padx=10)

label_original = tk.Label(frame_izquierda, text="Imagen con selección")
label_original.pack()

canvas = tk.Canvas(frame_izquierda, width=512, height=512, bg="gray")
canvas.pack()

# Panel derecho (vacío por ahora)
frame_derecha = tk.Frame(frame_imagenes)
frame_derecha.pack(side=tk.LEFT, padx=10)

label_convertida = tk.Label(frame_derecha, text="(espacio reservado)")
label_convertida.pack()

image_label_convertida = tk.Label(frame_derecha)
image_label_convertida.pack()

def cargar_imagen():
    global imagen_procesada, sprite_boxes
    ruta = filedialog.askopenfilename(
        title="Elegí una imagen",
        filetypes=[("Imágenes PNG", "*.png"), ("Todos los archivos", "*.*")]
    )
    if ruta:
        imagen_procesada = preprocess_image(ruta)
        sprite_boxes = []
        mostrar_imagen_con_rectangulos()

def detectar_sprites():
    global sprite_boxes
    if imagen_procesada:
        cajas = sprite_detection.detectar_sprites(imagen_procesada)
        sprite_boxes = [SpriteBox(*caja) for caja in cajas]
        mostrar_imagen_con_rectangulos()

def mostrar_imagen_con_rectangulos():
    if not imagen_procesada:
        return

    img = imagen_procesada.copy()
    draw = ImageDraw.Draw(img)

    for box in sprite_boxes:
        color = (0, 255, 0, 255) if box.selected else (255, 0, 0, 255)
        draw.rectangle([box.x, box.y, box.x + box.w, box.y + box.h], outline=color, width=2)

    img_tk = ImageTk.PhotoImage(img)
    canvas.img = img_tk
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=img_tk)

def on_click(event):
    global seleccion_inicial
    if not imagen_procesada:
        return

    seleccion_inicial = (event.x, event.y)

    for box in sprite_boxes:
        if punto_en_caja(event.x, event.y, box):
            if event.state & 0x0004:  # Ctrl presionado
                box.selected = not box.selected
            else:
                for b in sprite_boxes:
                    b.selected = False
                box.selected = True
            mostrar_imagen_con_rectangulos()
            return

    # Click vacío: deseleccionar si no hay Ctrl
    if not (event.state & 0x0004):
        for b in sprite_boxes:
            b.selected = False
        mostrar_imagen_con_rectangulos()

def on_drag(event):
    global rectangulo_temp
    canvas.delete("seleccion")

    if seleccion_inicial:
        x0, y0 = seleccion_inicial
        x1, y1 = event.x, event.y
        rectangulo_temp = (x0, y0, x1, y1)
        canvas.create_rectangle(x0, y0, x1, y1, outline="blue", width=1, dash=(4, 2), tag="seleccion")

def on_release(event):
    global seleccion_inicial, rectangulo_temp
    canvas.delete("seleccion")

    if not seleccion_inicial:
        return

    x0, y0 = seleccion_inicial
    x1, y1 = event.x, event.y
    seleccionadas = cajas_en_area(x0, y0, x1, y1, sprite_boxes)

    for box in sprite_boxes:
        if box in seleccionadas:
            box.selected = True

    mostrar_imagen_con_rectangulos()
    seleccion_inicial = None
    rectangulo_temp = None

def eliminar_seleccionados():
    global sprite_boxes
    sprite_boxes = [box for box in sprite_boxes if not box.selected]
    mostrar_imagen_con_rectangulos()

# Eventos del canvas
canvas.bind("<Button-1>", on_click)
canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)

# Botones
boton_cargar = tk.Button(root, text="Cargar imagen", command=cargar_imagen)
boton_cargar.pack(pady=5)

boton_detectar = tk.Button(root, text="Detectar sprites", command=detectar_sprites)
boton_detectar.pack(pady=5)

boton_borrar = tk.Button(root, text="Eliminar seleccionados", command=eliminar_seleccionados)
boton_borrar.pack(pady=5)

root.mainloop()
