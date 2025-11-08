# --- Contenido de main.py (con "Pegar") ---

import customtkinter as ctk
import threading
import yt_dlp
import os
import sys
import tkinter  # <-- 1. NUEVO IMPORT

# --- IMPORTS NECESARIOS ---
import requests
import mutagen
import mutagen.id3
import traceback
# ---------------------

from utils import get_ffmpeg_path, get_cookies_path
from video_item_frame import VideoItemFrame


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Soluciona TI Downloader v1.0")
        self.geometry("1300x800")
        self.minsize(600, 400)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.ffmpeg_path = get_ffmpeg_path()
        self.download_path = os.path.join(os.path.expanduser("~"), "Downloads")
        os.makedirs(self.download_path, exist_ok=True)

        # --- LÓGICA HÍBRIDA DE COOKIES ---
        self.cookie_config = {}
        manual_cookies_path = get_cookies_path()

        if os.path.exists(manual_cookies_path):
            print("Usando 'cookies.txt' (Método Manual).")
            self.cookie_config = {'cookies': manual_cookies_path}
        else:
            print("No se encontró 'cookies.txt'. Usando 'cookies_from_browser' (Método Automático).")
            self.cookie_config = {
                'cookies_from_browser': ('brave', 'chrome', 'firefox', 'edge', 'opera', 'vivaldi')
            }
        # -----------------------------------

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- BARRA SUPERIOR ---
        self.frame_top = ctk.CTkFrame(self, height=50)
        self.frame_top.grid(row=0, column=0, padx=10, pady=10, sticky="new")

        self.frame_top.grid_columnconfigure(0, weight=1)
        self.frame_top.grid_columnconfigure(1, weight=0)

        self.entry_url = ctk.CTkEntry(self.frame_top, placeholder_text="Pega la URL del video aquí...")
        self.entry_url.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.right_cluster_frame = ctk.CTkFrame(self.frame_top, fg_color="transparent")
        self.right_cluster_frame.grid(row=0, column=1, padx=10, pady=10, sticky="e")

        self.format_switch = ctk.CTkSwitch(self.right_cluster_frame, text="Forzar MP4", onvalue=1, offvalue=0)
        self.format_switch.pack(side="left", padx=10)
        self.format_switch.select()

        self.button_add = ctk.CTkButton(self.right_cluster_frame, text="+ Añadir", command=self.on_add_button_click)
        self.button_add.pack(side="left")

        # --- LISTA DE VIDEOS ---
        self.scrollable_frame_videos = ctk.CTkScrollableFrame(self, label_text="Cola de Descarga")
        self.scrollable_frame_videos.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

        self.scrollable_frame_videos.grid_columnconfigure(0, weight=1)

        self.next_item_row = 0

        # --- 2. NUEVO: Lógica del Menú "Pegar" ---
        self.entry_menu = tkinter.Menu(self, tearoff=0)
        self.entry_menu.add_command(label="Pegar", command=self.paste_to_entry)

        # Asignar el clic derecho al entry_url
        self.entry_url.bind("<Button-3>", self.show_entry_menu)
        # ------------------------------------

    # --- 3. NUEVO: Funciones para el Menú ---
    def show_entry_menu(self, event):
        """Muestra el menú en la posición del clic."""
        self.entry_menu.post(event.x_root, event.y_root)

    def paste_to_entry(self):
        """Obtiene el portapapeles y lo inserta en el entry."""
        try:
            clipboard_text = self.clipboard_get()
            self.entry_url.insert(tkinter.INSERT, clipboard_text)
        except tkinter.TclError:
            # Esto pasa si el portapapeles está vacío o no es texto
            pass

    # --------------------------------------

    def on_add_button_click(self):
        url = self.entry_url.get()
        if not url:
            return

        self.entry_url.delete(0, "end")
        self.button_add.configure(state="disabled", text="Cargando...")

        thread = threading.Thread(target=self.fetch_video_info_thread, args=(url,), daemon=True)
        thread.start()

    def fetch_video_info_thread(self, url):
        ydl_opts = {
            'quiet': True,
            'format_sort': ['res', 'ext:mp4:m4a'],
        }
        ydl_opts.update(self.cookie_config)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
            self.after(0, self.add_video_item_to_gui, info)
        except Exception as e:
            print(f"Error al obtener info: {e}")
            self.after(0, self.reenable_add_button)

    def add_video_item_to_gui(self, video_info):
        video_item = VideoItemFrame(self.scrollable_frame_videos,
                                    video_info,
                                    self)
        video_item.grid(row=self.next_item_row, column=0, sticky="ew", padx=5, pady=5)
        self.next_item_row += 1

        self.reenable_add_button()

    def reenable_add_button(self):
        self.button_add.configure(state="normal", text="+ Añadir")

    def start_download_thread(self, video_frame, format_type, quality, friendly_name):
        thread = threading.Thread(target=self.download_thread,
                                  args=(video_frame, format_type, quality, friendly_name),
                                  daemon=True)
        thread.start()

    def download_thread(self, video_frame, format_type, quality, friendly_name):

        ruta_mp3 = ""
        status = ""
        status_color = ""

        try:
            if self.format_switch.get() == 1:
                output_format = 'mp4'
            else:
                output_format = 'webm'

            base_ydl_opts = {
                'quiet': True,
                'progress_hooks': [lambda d: self.on_download_progress(d, video_frame)],
                'ffmpeg_location': self.ffmpeg_path,
                'paths': {'home': self.download_path},
                'force_overwrites': True,
            }
            base_ydl_opts.update(self.cookie_config)

            ydl_opts = base_ydl_opts.copy()

            if format_type == 'audio':
                video_frame.after(0, lambda: video_frame.status_label.configure(text="Descargando audio..."))
                ydl_opts.update({
                    'outtmpl': '%(title)s.%(ext)s',
                    'format': 'ba/bestaudio',
                    'postprocessors': [
                        {
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }
                    ],
                })

            elif format_type == 'video':
                video_frame.after(0, lambda: video_frame.status_label.configure(text=f"Descargando {friendly_name}..."))
                ydl_opts.update({
                    'outtmpl': '%(title)s (%(height)sp).%(ext)s',
                    'format': f'bv*[height<={quality}]+ba/b[height<={quality}]/bv*+ba/b',
                    'merge_output_format': output_format,
                })

            # --- PASO 1: DESCARGA DE YT-DLP ---
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_frame.video_info.get('webpage_url')])

            # --- PASO 2: AÑADIR METADATOS MANUALMENTE (SOLO PARA MP3) ---
            if format_type == 'audio':
                print("Descarga de MP3 finalizada. Intentando escribir metadatos...")

                temp_info = video_frame.video_info.copy()
                temp_info['ext'] = 'mp3'
                temp_ydl_opts = {'paths': {'home': self.download_path}, 'outtmpl': '%(title)s.%(ext)s'}

                with yt_dlp.YoutubeDL(temp_ydl_opts) as ydl_path:
                    ruta_mp3 = ydl_path.prepare_filename(temp_info)

                if not os.path.exists(ruta_mp3):
                    print(f"Error: No se encontró el MP3 en {ruta_mp3}")
                    raise Exception("Fallo al crear el MP3")

                thumbnail_url = video_frame.video_info.get('thumbnail')
                image_data = None
                if thumbnail_url:
                    try:
                        response = requests.get(thumbnail_url)
                        if response.status_code == 200:
                            image_data = response.content
                            print("Carátula descargada exitosamente.")
                    except Exception as e:
                        print(f"No se pudo descargar la carátula: {e}")

                try:
                    print(f"Abriendo archivo: {ruta_mp3}")
                    audio = mutagen.File(ruta_mp3)

                    if not audio:
                        print("[ERROR] Mutagen no pudo abrir o reconocer el archivo.")
                    else:
                        print("Archivo MP3 abierto. Escribiendo etiquetas...")

                        if audio.tags is None:
                            audio.add_tags()

                        audio.tags.add(mutagen.id3.TIT2(encoding=3, text=video_frame.video_info.get('track',
                                                                                                    video_frame.video_info.get(
                                                                                                        'title',
                                                                                                        'Título Desconocido'))))
                        audio.tags.add(mutagen.id3.TPE1(encoding=3, text=video_frame.video_info.get('artist',
                                                                                                    video_frame.video_info.get(
                                                                                                        'uploader',
                                                                                                        'Artista Desconocido'))))
                        if video_frame.video_info.get('album'):
                            audio.tags.add(mutagen.id3.TALB(encoding=3, text=video_frame.video_info.get('album')))

                        if image_data:
                            print("Escribiendo carátula...")
                            audio.tags.add(
                                mutagen.id3.APIC(
                                    encoding=3,
                                    mime=self.get_image_mime(image_data),
                                    type=3,
                                    desc='Cover',
                                    data=image_data
                                )
                            )

                        audio.save()
                        print("Metadatos escritos manualmente con Mutagen (Modo ID3).")

                except Exception as e:
                    print(f"Error al escribir metadatos con Mutagen:")
                    traceback.print_exc()

            # --- PASO 3: NOTIFICAR A LA GUI ---
            status = f"Completado {friendly_name}"
            status_color = "#98C379"

        except Exception as e:
            if "requested format not available" in str(e).lower():
                status = "Error: Formato no disponible"
            else:
                status = "Error de descarga"
            print(f"Error en descarga: {e}")
            status_color = "#E06C75"

        finally:
            video_frame.after(0, video_frame.on_download_finished, status, status_color)

    def get_image_mime(self, image_data):
        if image_data.startswith(b'\xFF\xD8\xFF'):
            return 'image/jpeg'
        elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image/png'
        elif image_data.startswith(b'RIFF') and image_data[8:12] == b'WEBP':
            return 'image/webp'
        return 'image/jpeg'

    def on_download_progress(self, d, video_frame):
        video_frame.after(0, video_frame.update_gui_progress, d)


# --- PUNTO DE ENTRADA DE LA APLICACIÓN ---
if __name__ == "__main__":
    app = App()
    app.mainloop()