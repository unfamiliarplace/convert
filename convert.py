from __future__ import annotations

import sys
from pathlib import Path
from enum import Enum

from PyQt6.QtCore import pyqtSlot, QSize, QByteArray
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QPushButton, QGridLayout
from PyQt6.QtGui import QPalette, QColor, QPixmap, QIcon

from pydub import AudioSegment
from PIL import Image
import pillow_heif
from send2trash import send2trash

AUDIO_IN_EXTS = ('m4a', 'webm', 'mov', 'mp4')
AUDIO_OUT_EXT = 'mp3'
AUDIO_OUT_BITRATE = '320k'

IMAGE_IN_EXTS = ('jpg', 'jpeg', 'png', 'gif', 'heic', 'webp')
IMAGE_OUT_EXT = 'jpg'
IMAGE_OUT_FORMAT = 'JPEG'
IMAGE_OUT_QUALITY = 99
IMAGE_OUT_ICC = 'sRGB'

B64_IMAGE_SINGLE = b"iVBORw0KGgoAAAANSUhEUgAAADcAAABACAMAAACJIh8NAAAANlBMVEUAAAD///8AAAC/v79AQECfn58QEBDv7+/Pz8/f399gYGAwMDAgICCAgICvr6+Pj49wcHBQUFBiB6aDAAAAAXRSTlMAQObYZgAAANZJREFUSMft1sGOwyAMRdH0GdtASNr5/5+d0SRtF3UCuJuq4m5gc1ggYTGNRt4imaUKu+IgPmWKfDGiGiTQkQM7HdjpwE4Hdjqw04G7XMIT9rhLeTjRHhfDA1LN2Q33ttOAsjpcBiAOF/CXwzGAucex7mvI2uEIN899qgDrvu1xAYCk/+dXYrtbgPt9zJi11RG2lu2E3Oi0YI/24dnmfnBPZFtSi7vipbnBRRjdqk4LrNaayzCTdO5iOGj57DkxXN1F200S6LQgajoWnCZc+djZxWn0Nf0CfDkL02z2ivMAAAAASUVORK5CYII="
B64_IMAGE_PLURAL = b"iVBORw0KGgoAAAANSUhEUgAAADcAAABACAMAAACJIh8NAAAANlBMVEUAAAD///8AAABAQECAgIC/v79gYGAQEBDv7+/f398wMDDPz88gICCPj49QUFCfn5+vr69wcHD4/O7CAAAAAXRSTlMAQObYZgAAASRJREFUSMft1UtuwzAMRdHokaI+/sX732xVx6iRlKZkDYoiyB0KPBpwwtundyl6tVRhQ4Dearuck1MCIKYDuxMH6XSQTgfpdJBOB+l0kGtuNKDlBAY0XCQD7s6OCux0kE4H6XSQ646YqcDLrgwwDmg5DuPy6sBVt6A0vLpQcfuYf3JEGVXnAYT05Mqj4YZ9+E6zd+0uhuyO2h0B3OGmYx20tLsB34W4LTSkVhdHbNFjn7nVzdibHj+sbW7CT4Ste4tTzktIdRczfkd1J9Dimlug520XZ9KbTWf0cf/GBd3R6KOh0gSvumGE3epUV6SX7E9LTnF7TO48w02Itpuz6lIIZJUxaa5ApoxzJ3enu5KHM7Jcsh3rLoaRrQRyUxuEzDje/r4vb+4RcgZWfigAAAAASUVORK5CYII="
B64_AUDIO_SINGLE = b"iVBORw0KGgoAAAANSUhEUgAAADcAAABACAMAAACJIh8NAAAANlBMVEUAAAD///8AAAC/v7+AgIBAQEBgYGDf398QEBDv7+8wMDCvr69wcHBQUFDPz88gICCfn5+Pj49xJSIhAAAAAXRSTlMAQObYZgAAAM9JREFUSMft1U0LwyAMgOFqovG73f//s4MG7A7Wmg1GN3xPuTzgQeMym309D83KBStOt7N9lwOpRuYKalRtx1DuGModQ7ljKHcVyh1DuWMocqhrUeK8rQ4l7sj8m/PwSMbpMuqq4GDYZQZiZz53QeyMRSAFMmeJJ6lDNd19HCUT3nDFSe5nxLzyzGzM8RvaZ9AcjTjU1RGPRo249XDK7g/JD7nwejZAjIN7advZJt9nYE2i39q7Y85dubXtsovQC0/+TQq6X1pOIujll9nNegIZEwxkvjK4YwAAAABJRU5ErkJggg=="
B64_AUDIO_PLURAL = b"iVBORw0KGgoAAAANSUhEUgAAADcAAABACAMAAACJIh8NAAAANlBMVEUAAAD///8AAACAgIBAQEC/v79gYGDf398wMDDv7+/Pz88QEBAgICCfn59wcHBQUFCvr6+Pj49MpIyGAAAAAXRSTlMAQObYZgAAAR1JREFUSMft1stuAjEMhWF87DhXZuD9X7ZSLVoEiZvJomoR/yqLfFJWsU/vXqUcusUfWKnot/kupUidAKjrwDRw0EUHXXTQRQdddNBFBz3mmgM9p3Cg47J40JyfGFxx0EUHXXTQCRfOLA3l5oRZAHVcNmGFm2MihsG+SwYGDjxy8F2dcO3RiSS4Lu18KRQeHVFwnBayDjqmt/s7Lm6SFpxNqFkXmM3ligNuB2AuwIozbsOXK3YUmnH129mXm/KUa/dvOzOfiaYcf7K725OOLrtskQ4761+72nfSQnZUvCJ0XWnw2+jZmQyawrBIPWex0DjHXZF9t6eui7WKV8LV3BNkSRg7vZC5TgHk5LnoO+67XBt76WjhKipunE+/3wcubRGiizSsLgAAAABJRU5ErkJggg=="

SIZE_BUTTON = QSize(27, 32)
STYLE = """
QPushButton {
    border: none;
    background: #333;
    color: white;
    width: 185px;
    height: 120px;
    border-radius: 6px;
    margin: 10px;
    padding: 10px;
    font-size: 14px;
}

QPushButton:hover {
    background-color: #555;
}

QPushButton:pressed {
    background-color: #666;
}
"""

# https://stackoverflow.com/a/52298774
def iconFromB64(b64: bytes):
    pixmap = QPixmap()
    pixmap.loadFromData(QByteArray.fromBase64(b64))
    return QIcon(pixmap)

class Mode(Enum):
    IMAGE_SINGLE = 0
    IMAGE_PLURAL = 1
    AUDIO_SINGLE = 2
    AUDIO_PLURAL = 3

class Processor:

    @staticmethod
    def process_all(path_dir: Path, subp: SubProcessor) -> None:

        if not path_dir:
            return

        paths = []
        for ext in subp.exts():
            paths.extend(path_dir.glob(f'*.{ext}'))

        print(f'Processing {len(paths)} files')

        subp.set_up_all()

        for path in paths:
            Processor.process_one(path, subp)

        return True

    @staticmethod
    def process_one(path: Path, subp: SubProcessor) -> None:

        if not path:
            return

        # Read
        subp.set_up_one()
        data = subp.read(path)

        # Write
        try:
            path_out = path.with_suffix('').with_suffix(f'.{subp.out_ext()}')
            subp.write(data, path_out)
            print(f'Exported {path} to {path_out}')
            send2trash(path)
            return True

        except Exception as e:
            print(repr(e))
            print(f'Could not export {path}')
            return False

class SubProcessor:

    @staticmethod
    def set_up_all() -> None:
        return

    @staticmethod
    def set_up_one() -> None:
        return

    @staticmethod
    def in_exts() -> tuple[str]:
        raise NotImplementedError
    
    @staticmethod
    def out_ext() -> str:
        raise NotImplementedError

    @staticmethod
    def read(path: Path) -> object:
        raise NotImplementedError
    
    @staticmethod
    def write(data: object, path: Path) -> None:
        raise NotImplementedError

class AudioProcessor(SubProcessor):

    @staticmethod
    def in_exts() -> tuple[str]:
        return AUDIO_IN_EXTS
    
    @staticmethod
    def out_ext() -> str:
        return AUDIO_OUT_EXT

    @staticmethod
    def read(path: Path) -> AudioSegment:
        return AudioSegment.from_file(path, format=path.suffix[1:]) # strip .
    
    @staticmethod
    def write(data: AudioSegment, path: Path) -> None:
        data.export(path, format=AUDIO_OUT_EXT, bitrate=AUDIO_OUT_BITRATE)

class ImageProcessor(SubProcessor):

    @staticmethod
    def set_up_all() -> None:
        pillow_heif.register_heif_opener()

    @staticmethod
    def in_exts() -> tuple[str]:
        return IMAGE_IN_EXTS
    
    @staticmethod
    def out_ext() -> str:
        return IMAGE_OUT_EXT

    @staticmethod
    def read(path: Path) -> Image:
        return Image.open(path)
    
    @staticmethod
    def write(image: Image, path: Path) -> None:
        image.save(path,
                format = IMAGE_OUT_FORMAT,
                quality = IMAGE_OUT_QUALITY,
                icc_profile = IMAGE_OUT_ICC,
                exif=image.getexif()
            )

class Main(QMainWindow):

    def __init__(self: Main) -> None:
        super().__init__()
        self.do_layout()

    def do_layout(self: Main) -> None:
        self.setWindowTitle("Quick Converter")
        self.setFixedSize(QSize(400, 300))

        b_i_s = QPushButton(iconFromB64(B64_IMAGE_SINGLE), "Single image")
        b_i_p = QPushButton(iconFromB64(B64_IMAGE_PLURAL), "Multiple images")
        b_a_s = QPushButton(iconFromB64(B64_AUDIO_SINGLE), "Single audio")
        b_a_p = QPushButton(iconFromB64(B64_AUDIO_PLURAL), "Multiple audios")

        b_i_s.setIconSize(SIZE_BUTTON)
        b_i_p.setIconSize(SIZE_BUTTON)
        b_a_s.setIconSize(SIZE_BUTTON)
        b_a_p.setIconSize(SIZE_BUTTON)

        b_i_s.clicked.connect(lambda _: self.do_mode(Mode.IMAGE_SINGLE))
        b_i_p.clicked.connect(lambda _: self.do_mode(Mode.IMAGE_PLURAL))
        b_a_s.clicked.connect(lambda _: self.do_mode(Mode.AUDIO_SINGLE))
        b_a_p.clicked.connect(lambda _: self.do_mode(Mode.AUDIO_PLURAL))

        layout = QGridLayout()
        layout.addWidget(b_i_s, 0, 0)
        layout.addWidget(b_i_p, 0, 1)
        layout.addWidget(b_a_s, 1, 0)
        layout.addWidget(b_a_p, 1, 1)

        widget = QWidget()
        widget.setLayout(layout)

        widget.setAutoFillBackground(True)
        palette = widget.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor('#111'))
        widget.setPalette(palette)

        self.setCentralWidget(widget)

    def do_mode(self: Main, mode: Mode) -> None:

        match mode:

            case Mode.IMAGE_SINGLE:
                path = self.ask_filename('image')
                if path is not None:
                    success = Processor.process_one(path, ImageProcessor)

            case Mode.IMAGE_PLURAL:
                path = self.ask_folder('images')
                if path is not None:
                    success = Processor.process_all(path, ImageProcessor)

            case Mode.AUDIO_SINGLE:
                path = self.ask_filename('audio file')
                if path is not None:
                    success = Processor.process_one(path, AudioProcessor)

            case Mode.AUDIO_PLURAL:
                path = self.ask_folder('audio files')
                if path is not None:
                    success = Processor.process_all(path, AudioProcessor)

        if path and success:
            sys.exit()

    @pyqtSlot()
    def ask_filename(self: QMainWindow, keyword: str) -> Path:
        path, _ = QFileDialog.getOpenFileName(
            self, f"Choose {keyword} to convert", ".", "All files (*);;"
        )

        return Path(path) if path else None

    @pyqtSlot()
    def ask_folder(self: QMainWindow, keyword: str) -> Path:
        path = QFileDialog.getExistingDirectory(
            self, f"Choose folder of {keyword} to convert", ".",
            options=QFileDialog.Option.DontUseNativeDialog
        )

        return Path(path) if path else None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLE)
    main_gui = Main()
    main_gui.show()
    sys.exit(app.exec())
