from __future__ import annotations

import sys
from pathlib import Path
from enum import Enum

from PyQt6.QtCore import pyqtSlot, QSize
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QWidget, QPushButton, QGridLayout
from PyQt6.QtGui import QPalette, QColor

from pydub import AudioSegment
from PIL import Image
import pillow_heif
from send2trash import send2trash

AUDIO_IN_EXTS = ('m4a', 'webm', 'mov', 'mp4')
AUDIO_OUT_EXT = 'mp3'
AUDIO_OUT_BITRATE = '320k'

IMAGE_IN_EXTS = ()
IMAGE_OUT_EXT = 'jpg'
IMAGE_OUT_FORMAT = 'JPEG'
IMAGE_OUT_QUALITY = 99
IMAGE_OUT_ICC = 'sRGB'

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

    @staticmethod
    def process_one(path: Path, subp: SubProcessor) -> None:

        if not path:
            return

        # Read
        subp.set_up_one()
        data = subp.read(path)

        # Write
        try:
            path_out = path.with_suffix('').with_suffix(f'.{AUDIO_OUT_EXT}')
            subp.write(data, path_out)
            print(f'Exported {path} to {path_out}')
            send2trash(path)

        except:
            print(f'Could not export {path}')

class SubProcessor:

    @staticmethod
    def set_up_all() -> None:
        return

    @staticmethod
    def set_up_one() -> None:
        return

    @staticmethod
    def exts() -> tuple[str]:
        raise NotImplementedError

    @staticmethod
    def read(path: Path) -> object:
        raise NotImplementedError
    
    @staticmethod
    def write(data: object, path: Path) -> None:
        raise NotImplementedError

class AudioProcessor(SubProcessor):

    @staticmethod
    def exts() -> tuple[str]:
        return AUDIO_IN_EXTS

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
    def exts() -> tuple[str]:
        return IMAGE_IN_EXTS

    @staticmethod
    def read(path: Path) -> Image:
        return Image.open(path)
    
    @staticmethod
    def write(data: Image, path: Path) -> None:
        data.save(path,
                format = IMAGE_OUT_FORMAT,
                quality = IMAGE_OUT_QUALITY,
                icc_profile = IMAGE_OUT_ICC,
                exif=data.info['exif']
            )

class Main(QMainWindow):

    def __init__(self: Main) -> None:
        super().__init__()
        self.do_layout()

    def do_layout(self: Main) -> None:
        self.setWindowTitle("Quick Converter")
        self.setFixedSize(QSize(400, 300))

        b_i_s = QPushButton("Single image")
        b_i_p = QPushButton("Multiple images")
        b_a_s = QPushButton("Single audio")
        b_a_p = QPushButton("Multiple audios")

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
        palette.setColor(QPalette.ColorRole.Window, QColor('#224455'))
        self.setPalette(palette)

        self.setCentralWidget(widget)

    def do_mode(self: Main, mode: Mode) -> None:

        match mode:

            case Mode.IMAGE_SINGLE:
                path = self.ask_filename('image')
                if path is not None:
                    Processor.process_one(path, ImageProcessor)

            case Mode.IMAGE_PLURAL:
                path = self.ask_folder('images')
                if path is not None:
                    Processor.process_all(path, ImageProcessor)

            case Mode.AUDIO_SINGLE:
                path = self.ask_filename('audio file')
                if path is not None:
                    Processor.process_one(path, AudioProcessor)

            case Mode.AUDIO_PLURAL:
                path = self.ask_folder('audio files')
                if path is not None:
                    Processor.process_all(path, AudioProcessor)

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
    main_gui = Main()
    main_gui.show()
    sys.exit(app.exec())
