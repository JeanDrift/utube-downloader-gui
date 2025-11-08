# Soluciona TI Downloader v1.0

Una interfaz gráfica para descargar videos y música de YouTube, construida con Python, CustomTkinter y yt-dlp.

## 🚀 Instalación y Uso

Para ejecutar este proyecto, necesitas:

1.  **Python 3.10** o superior.
2.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Descargar FFmpeg:**
    * Descarga el `ffmpeg.exe` y `ffprobe.exe` (desde [ffmpeg.org](https://ffmpeg.org/download.html) o [los builds de yt-dlp](https://github.com/yt-dlp/FFmpeg-Builds/releases)).
    * Crea una carpeta `bin` en la raíz del proyecto.
    * Coloca los archivos `.exe` dentro de la carpeta `bin/`.

4.  **(Opcional) Cookies:**
    * Si tienes problemas de "bot" con YouTube, genera un `cookies.txt` usando el método de incógnito (ver wiki de yt-dlp).
    * Coloca el `cookies.txt` en la misma carpeta que `main.py`.

5.  **Ejecutar:**
    ```bash
    python main.py
    ```

## ⚠️ Advertencia de Cookies
Las cookies de tu sesión de YouTube son sensibles. No compartas tu archivo `cookies.txt`.