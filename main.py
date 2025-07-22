import tkinter as tk
from tkinter import filedialog
from PIL import ImageTk
from modules.image_utils import preprocess_image
from modules import sprite_detection

# Crear la ventana principal
root = tk.Tk()
root.title("Sprite Tool")
root.geometry("1000x600")  # Ancho suficiente para ambas imágenes

# Marco principal dividido en dos columnas
frame_imagenes = tk.Frame(root)
frame_imagenes.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# Frame para la imagen original (izquierda)
frame_izquierda = tk.Frame(frame_imagenes)
frame_izquierda.pack(side=tk.LEFT, padx=10)

label_original = tk.Label(frame_izquierda, text="Original (fondo limpio)")
label_original.pack()

image_label_original = tk.Label(frame_izquierda)
image_label_original.pack()

# Frame para la imagen convertida (derecha)
frame_derecha = tk.Frame(frame_imagenes)
frame_derecha.pack(side=tk.LEFT, padx=10)

label_convertida = tk.Label(frame_derecha, text="Detección de sprites")
label_convertida.pack()

image_label_convertida = tk.Label(frame_derecha)
image_label_convertida.pack()

# Función al pulsar el botón
def cargar_imagen():
    ruta = filedialog.askopenfilename(
        title="Elegí una imagen",
        filetypes=[("Imágenes PNG", "*.png"), ("Todos los archivos", "*.*")]
    )

    if ruta:
        # Paso 1: Cargar imagen y limpiar fondo
        imagen_procesada = preprocess_image(ruta)
        imagen_tk = ImageTk.PhotoImage(imagen_procesada)
        image_label_original.config(image=imagen_tk)
        image_label_original.image = imagen_tk

        # Paso 2: Detección de sprites
        cajas = sprite_detection.detectar_sprites(imagen_procesada)
        imagen_con_rectangulos = sprite_detection.dibujar_rectangulos(imagen_procesada, cajas)

        # Paso 3: Mostrar imagen con rectángulos a la derecha
        imagen_tk_convertida = ImageTk.PhotoImage(imagen_con_rectangulos)
        image_label_convertida.config(image=imagen_tk_convertida)
        image_label_convertida.image = imagen_tk_convertida

# Botón para cargar imagen
boton_cargar = tk.Button(root, text="Cargar imagen", command=cargar_imagen)
boton_cargar.pack(pady=10)

# Ejecutar la app
root.mainloop()
