
import tkinter as tk
from modules.color_analysis import contar_colores_en_sprites, obtener_top_colores

class ColorPicker(tk.Frame):
    def __init__(self, parent, sprite_img, on_confirm_callback):
        super().__init__(parent)
        self.selected_colors = []
        self.check_vars = []
        self.check_buttons = []
        self.on_confirm_callback = on_confirm_callback

        color_counts = contar_colores_en_sprites(sprite_img, [(0, 0, sprite_img.width, sprite_img.height)])
        top_colors = obtener_top_colores(color_counts, top_n=10)

        for i, (color, count) in enumerate(top_colors):
            var = tk.IntVar()
            cb = tk.Checkbutton(self, variable=var, command=self.update_selection_limit)
            cb.grid(row=i, column=1, sticky="w", pady=2)

            color_box = tk.Canvas(self, width=30, height=20, bg=self.rgb_to_hex(color), highlightthickness=1)
            color_box.grid(row=i, column=0, padx=5, pady=2)

            self.check_vars.append((var, color))
            self.check_buttons.append(cb)

        confirm_btn = tk.Button(self, text="Confirmar", command=self.confirm_selection)
        confirm_btn.grid(row=11, column=0, columnspan=2, pady=10)

    def update_selection_limit(self):
        selected = [var for var, color in self.check_vars if var.get() == 1]
        if len(selected) >= 3:
            for i, (var, _) in enumerate(self.check_vars):
                if var.get() == 0:
                    self.check_buttons[i].config(state="disabled")
        else:
            for i, _ in enumerate(self.check_vars):
                self.check_buttons[i].config(state="normal")

    def confirm_selection(self):
        seleccionados = [color for var, color in self.check_vars if var.get() == 1]
        if len(seleccionados) == 3:
            self.on_confirm_callback(seleccionados)

    @staticmethod
    def rgb_to_hex(rgb):
        return "#{:02x}{:02x}{:02x}".format(*rgb)
