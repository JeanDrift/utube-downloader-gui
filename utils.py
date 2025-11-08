# --- Contenido de utils.py (Optimizado) ---

import sys
import os

def get_bundled_path(relative_path):
    """
    Obtiene la ruta a un recurso bundlizado (interno).
    (Para cosas como ffmpeg.exe que incluyes en PyInstaller)
    """
    if getattr(sys, 'frozen', False):
        # Estamos en modo "portable" (PyInstaller)
        # sys._MEIPASS es la carpeta temporal donde se extraen los datos
        base_path = sys._MEIPASS
    else:
        # Estamos en modo "desarrollo" (PyCharm)
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_user_path(relative_path):
    """
    Obtiene la ruta a un archivo de usuario.
    (Para cosas como cookies.txt que debe estar AL LADO del .exe)
    """
    if getattr(sys, 'frozen', False):
        # La ruta al .exe
        base_path = os.path.dirname(sys.executable)
    else:
        # Estamos en modo "desarrollo"
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_ffmpeg_path():
    """ Encuentra la ruta a ffmpeg.exe (bundlizado) """
    # Asumimos que "bin/ffmpeg.exe" está siendo añadido
    # en tu .spec de PyInstaller como "datas"
    return get_bundled_path(os.path.join("bin", "ffmpeg.exe"))

def get_cookies_path():
    """ Encuentra la ruta a cookies.txt (externo/usuario) """
    # El usuario pondrá cookies.txt al lado del .exe
    return get_user_path("cookies.txt")