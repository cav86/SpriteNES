from collections import Counter

import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk, Image, ImageDraw
from modules.image_utils import preprocess_image
from modules import sprite_detection
from modules.selection_module import SpriteBox, punto_en_caja, cajas_en_area
from modules.color_picker import ColorPicker

root = tk.Tk()
root.title("Sprite Tool")
root.geometry("1200x800")

imagen_original = None
imagen_procesada = None
sprite_boxes = []
zoom_factor = 1.0
seleccion_inicial = None
rectangulo_temp = None
color_picker_widget = None

# Marco principal
frame_imagenes = tk.Frame(root)
frame_imagenes.pack(fill=tk.BOTH, expand=True)

# Canvas con scrollbars
canvas_frame = tk.Frame(frame_imagenes)
canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

canvas = tk.Canvas(canvas_frame, bg="gray")
h_scroll = tk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=canvas.xview)
v_scroll = tk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Panel derecho (espacio reservado)
frame_derecha = tk.Frame(frame_imagenes)
frame_derecha.pack(side=tk.LEFT, padx=10)

label_convertida = tk.Label(frame_derecha, text="(espacio reservado)")
label_convertida.pack()

image_label_convertida = tk.Label(frame_derecha)
image_label_convertida.pack()

# Panel inferior para el color picker
frame_inferior = tk.Frame(root)
frame_inferior.pack(fill=tk.X, padx=10, pady=5)

def redibujar_canvas():
    if not imagen_procesada:
        return

    img = imagen_procesada.copy()
    draw = ImageDraw.Draw(img)

    for box in sprite_boxes:
        color = (0, 0, 255, 255) if box.selected else (255, 0, 0, 255)
        draw.rectangle([box.x, box.y, box.x + box.w, box.y + box.h], outline=color, width=2)

    w, h = img.size
    resized = img.resize((int(w * zoom_factor), int(h * zoom_factor)), Image.NEAREST)
    img_tk = ImageTk.PhotoImage(resized)
    canvas.img = img_tk
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=img_tk)
    canvas.config(scrollregion=canvas.bbox("all"))

def cargar_imagen():
    global imagen_original, imagen_procesada, sprite_boxes, zoom_factor
    ruta = filedialog.askopenfilename(
        title="Elegí una imagen",
        filetypes=[("Imágenes PNG", "*.png"), ("Todos los archivos", "*.*")]
    )
    if ruta:
        imagen_procesada = preprocess_image(ruta)
        imagen_original = imagen_procesada.copy()
        sprite_boxes = []
        zoom_factor = 0.5
        redibujar_canvas()
        limpiar_color_picker()

def detectar_sprites():
    global sprite_boxes
    if imagen_procesada:
        cajas = sprite_detection.detectar_sprites(imagen_procesada)
        sprite_boxes = [SpriteBox(*caja) for caja in cajas]
        for box in sprite_boxes:
            box.selected = False
        for box in sprite_boxes:
            box.selected = True
        for box in sprite_boxes:
            box.selected = True
        redibujar_canvas()

def abrir_color_picker_con_sprites_seleccionados():
    global color_picker_widget
    from modules.color_analysis import contar_colores_en_sprites, obtener_top_colores

    limpiar_color_picker()

    seleccionados = [box for box in sprite_boxes if not box.selected]  # Solo los que quedaron con recuadro rojo
    if not seleccionados:
        print("No hay sprites seleccionados.")
        return

    colores_total = Counter()
    for box in seleccionados:
        sprite_crop = imagen_procesada.crop((
            int(box.x), int(box.y),
            int(box.x + box.w), int(box.y + box.h)
        ))
        colores = contar_colores_en_sprites(sprite_crop, [(0, 0, sprite_crop.width, sprite_crop.height)])
        for color, cantidad in colores.items():
            colores_total[color] = colores_total.get(color, 0) + cantidad

    top_colores = obtener_top_colores(colores_total, top_n=10)

    # Crear una imagen simulada para el picker
    sprite_virtual = Image.new("RGBA", (10, 10))
    pixels = sprite_virtual.load()
    for i in range(10):
        for j in range(10):
            color_index = (i * 10 + j) % len(top_colores)
            pixels[i, j] = (*top_colores[color_index][0], 255)

    def cuando_confirma(colores):
        print("Colores elegidos:", colores)

    color_picker_widget = ColorPicker(frame_inferior, sprite_virtual, cuando_confirma)
    color_picker_widget.pack(side=tk.LEFT)

def limpiar_color_picker():
    global color_picker_widget
    if color_picker_widget:
        color_picker_widget.destroy()
        color_picker_widget = None

def on_click(event):
    global seleccion_inicial
    if not imagen_procesada:
        return

    seleccion_inicial = (canvas.canvasx(event.x), canvas.canvasy(event.y))

    for box in sprite_boxes:
        px, py = seleccion_inicial
        if punto_en_caja(px / zoom_factor, py / zoom_factor, box):
            if event.state & 0x0004:
                box.selected = not box.selected
            else:
                for b in sprite_boxes:
                    b.selected = False
                box.selected = True
            redibujar_canvas()
            return

    if not (event.state & 0x0004):
        for b in sprite_boxes:
            b.selected = False
        redibujar_canvas()

def on_drag(event):
    global rectangulo_temp
    canvas.delete("seleccion")

    if seleccion_inicial:
        x0, y0 = seleccion_inicial
        x1, y1 = canvas.canvasx(event.x), canvas.canvasy(event.y)
        rectangulo_temp = (x0, y0, x1, y1)
        canvas.create_rectangle(x0, y0, x1, y1, outline="blue", width=1, dash=(4, 2), tag="seleccion")

def on_release(event):
    global seleccion_inicial, rectangulo_temp
    canvas.delete("seleccion")

    if not seleccion_inicial:
        return

    x0, y0 = seleccion_inicial
    x1, y1 = canvas.canvasx(event.x), canvas.canvasy(event.y)
    seleccionadas = cajas_en_area(x0 / zoom_factor, y0 / zoom_factor, x1 / zoom_factor, y1 / zoom_factor, sprite_boxes)

    for box in sprite_boxes:
        if box in seleccionadas:
            box.selected = True

    redibujar_canvas()
    seleccion_inicial = None
    rectangulo_temp = None

def eliminar_seleccionados():
    global sprite_boxes
    sprite_boxes = [box for box in sprite_boxes if not box.selected]
    redibujar_canvas()
    limpiar_color_picker()

def set_zoom(nivel):
    global zoom_factor
    zoom_factor = nivel
    redibujar_canvas()

# Eventos
canvas.bind("<Button-1>", on_click)
canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)

# Botones
frame_botones = tk.Frame(root)
frame_botones.pack()

tk.Button(frame_botones, text="Cargar imagen", command=cargar_imagen).pack(side=tk.LEFT, padx=5)
tk.Button(frame_botones, text="Detectar sprites", command=detectar_sprites).pack(side=tk.LEFT, padx=5)
tk.Button(frame_botones, text="Eliminar seleccionados", command=eliminar_seleccionados).pack(side=tk.LEFT, padx=5)
tk.Button(frame_botones, text="Elegir colores", command=abrir_color_picker_con_sprites_seleccionados).pack(side=tk.LEFT, padx=5)

tk.Label(frame_botones, text="Zoom:").pack(side=tk.LEFT, padx=10)
tk.Button(frame_botones, text="x0", command=lambda: set_zoom(0.5)).pack(side=tk.LEFT)
tk.Button(frame_botones, text="x1", command=lambda: set_zoom(1)).pack(side=tk.LEFT)
tk.Button(frame_botones, text="x2", command=lambda: set_zoom(2)).pack(side=tk.LEFT)
tk.Button(frame_botones, text="x3", command=lambda: set_zoom(3)).pack(side=tk.LEFT)

root.mainloop()
