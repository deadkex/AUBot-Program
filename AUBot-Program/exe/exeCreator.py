import PyInstaller.__main__
import os

dirname, filename = os.path.split(os.path.abspath(__file__))
dirname = dirname.rsplit("\\", 1)[0]

PyInstaller.__main__.run(
    [
        "--noconfirm",
        "--noconsole",
        "--icon=" + os.path.join(dirname, 'exe\\shhPicture.ico'),
        "--onefile",
        os.path.join(dirname, 'main_window.py'),
    ]
)
