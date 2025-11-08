# --- Contenido de video_item_frame.py (con Botón Borrar) ---

import customtkinter as ctk
import threading
import requests
import io
from PIL import Image


class VideoItemFrame(ctk.CTkFrame):
    def __init__(self, master, video_info, app_instance):
        super().__init__(master, fg_color=("#E5E5E5", "#2B2B2B"), corner_radius=6)

        self.video_info = video_info
        self.app_instance = app_instance
        self.format_buttons = []

        # --- 1. NUEVO: Grid de 2 Columnas ---
        self.grid_columnconfigure(0, weight=0)  # Col 0: Miniatura (fijo)
        self.grid_columnconfigure(1, weight=1)  # Col 1: Info (SE EXPANDE)

        # --- Col 0: Frame para Miniatura y Botón X ---
        # Usamos un frame para superponer el botón sobre la imagen
        self.thumbnail_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.thumbnail_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.label_thumbnail = ctk.CTkLabel(self.thumbnail_frame, text="Cargando...", width=160, height=90,
                                            fg_color=("#CCCCCC", "#3B3B3B"), corner_radius=6)
        self.label_thumbnail.grid(row=0, column=0)  # Imagen en la base
        threading.Thread(target=self.load_thumbnail_thread, daemon=True).start()

        # --- NUEVO: Botón de Borrar (Superpuesto) ---
        self.delete_button = ctk.CTkButton(self.thumbnail_frame, text="X",
                                           font=("Arial", 12, "bold"),
                                           width=24, height=24,
                                           fg_color="#DB4437", hover_color="#C13B2E",  # Rojo
                                           command=self.on_delete_click)
        # Colocar en la misma celda, esquina superior izquierda (nw)
        self.delete_button.grid(row=0, column=0, padx=4, pady=4, sticky="nw")

        # --- Col 1: Stack de Información ---
        self.info_stack_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.info_stack_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.info_stack_frame.grid_columnconfigure(0, weight=1)

        # --- Contenido del Stack (como lo tenías) ---
        title = self.video_info.get('title', 'Video sin título')
        duration = self.video_info.get('duration_string', '--:--')

        self.label_title = ctk.CTkLabel(self.info_stack_frame, text=title, font=("Arial", 14, "bold"), anchor="w")
        self.label_title.grid(row=0, column=0, sticky="ew")

        self.label_duration = ctk.CTkLabel(self.info_stack_frame, text=f"Duración: {duration}", font=("Arial", 12),
                                           anchor="w")
        self.label_duration.grid(row=1, column=0, sticky="ew", pady=(0, 2))

        self.format_frame = ctk.CTkScrollableFrame(self.info_stack_frame,
                                                   fg_color="transparent",
                                                   orientation="horizontal",
                                                   height=35)
        self.format_frame.grid(row=2, column=0, sticky="ew", pady=(0, 2))

        self.progress_frame = ctk.CTkFrame(self.info_stack_frame, fg_color="transparent")
        self.progress_frame.grid(row=2, column=0, sticky="ew", pady=(0, 2))
        self.progress_frame.grid_columnconfigure(1, weight=1)

        self.status_label = ctk.CTkLabel(self.progress_frame, text="", font=("Arial", 11))
        self.status_label.grid(row=0, column=0, padx=(0, 5))

        self.progress_bar = ctk.CTkProgressBar(self.progress_frame, mode='determinate', height=10)
        self.progress_bar.grid(row=0, column=1, sticky="ew")

        self.progress_frame.grid_remove()
        self.populate_format_buttons()

    # --- NUEVO: Función para borrar ---
    def on_delete_click(self):
        """Se destruye a sí mismo."""
        self.destroy()

    def load_thumbnail_thread(self):
        try:
            thumbnail_url = self.video_info.get('thumbnail')
            if not thumbnail_url:
                raise ValueError("No thumbnail URL")
            response = requests.get(thumbnail_url)
            response.raise_for_status()
            image_data = io.BytesIO(response.content)
            pil_image = Image.open(image_data)
            ctk_image = ctk.CTkImage(pil_image, size=(160, 90))
            self.after(0, self.update_thumbnail_on_gui, ctk_image)
        except Exception as e:
            print(f"Error cargando miniatura: {e}")
            self.after(0, lambda: self.label_thumbnail.configure(text="Error al\ncargar"))

    def update_thumbnail_on_gui(self, ctk_image):
        self.label_thumbnail.configure(image=ctk_image, text="")

    def populate_format_buttons(self):
        formats = self.video_info.get('formats', [])
        available_heights = set()
        has_audio_only = False
        btn_height = 22
        btn_font = ("Arial", 11)

        for f in formats:
            if f.get('vcodec') != 'none' and f.get('height'):
                available_heights.add(f.get('height'))
            if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                has_audio_only = True

        if has_audio_only:
            btn_audio = ctk.CTkButton(self.format_frame, text="MP3",
                                      height=btn_height,
                                      font=btn_font,
                                      command=lambda: self.start_download(format_type='audio', friendly_name="MP3"))
            btn_audio.pack(side="left", padx=3, pady=2)
            self.format_buttons.append(btn_audio)

        sorted_heights = sorted(list(available_heights), reverse=True)
        for height in sorted_heights:
            if height in [4320, 2160, 1440, 1080, 720, 480, 360]:
                resolution_text = f"{height}p"
                friendly_name = resolution_text
                tag_text = ""
                if height == 4320:
                    tag_text = " (8K)"
                    friendly_name = "8K"
                elif height == 2160:
                    tag_text = " (4K)"
                    friendly_name = "4K"
                elif height == 1440:
                    tag_text = " (2K)"
                    friendly_name = "2K"
                elif height == 1080:
                    tag_text = " (FHD)"
                    friendly_name = "FHD 1080p"
                elif height == 720:
                    tag_text = " (HD)"
                    friendly_name = "HD 720p"

                button_text = f"{resolution_text}{tag_text}"
                btn_video = ctk.CTkButton(self.format_frame,
                                          text=button_text,
                                          height=btn_height,
                                          font=btn_font,
                                          command=lambda h=height, fn=friendly_name: self.start_download(
                                              format_type='video', quality=h, friendly_name=fn))
                btn_video.pack(side="left", padx=3, pady=2)
                self.format_buttons.append(btn_video)

    def start_download(self, format_type, friendly_name, quality=None):
        for btn in self.format_buttons:
            btn.configure(state="disabled")

        self.format_frame.grid_remove()
        self.progress_frame.grid()
        self.progress_bar.set(0)

        self.app_instance.start_download_thread(self, format_type, quality, friendly_name)

    def update_gui_progress(self, d):
        if d['status'] == 'downloading':
            percent_str = d.get('_percent_str', '0.0%').strip().replace('%', '')
            speed_str = d.get('_speed_str', '...').strip()

            try:
                percent = float(percent_str) / 100.0
                self.progress_bar.set(percent)
                self.status_label.configure(text=f"{percent_str}% a {speed_str}",
                                            text_color=ctk.ThemeManager.theme["CTkLabel"]["text_color"])
            except ValueError:
                pass

        elif d['status'] == 'finished' and 'info_dict' in d:
            self.status_label.configure(text="Fusionando...")

    def on_download_finished(self, status_text, text_color):
        self.status_label.configure(text=status_text, text_color=text_color)
        if text_color != "#E06C75":
            self.progress_bar.set(1)

        self.progress_frame.grid_remove()
        self.format_frame.grid()

        for btn in self.format_buttons:
            btn.configure(state="normal")