from __future__ import annotations

import sys
from pathlib import Path
from enum import Enum

from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6.QtCore import pyqtSlot

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

        paths = []
        for ext in subp.exts():
            paths.extend(path_dir.glob(f'*.{ext}'))

        print(f'Processing {len(paths)} files')

        subp.set_up_all()

        for path in paths:
            Processor.process_one(path, subp)

    @staticmethod
    def process_one(path: Path, subp: SubProcessor) -> None:

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

class ImageProcessor:

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
    mode: str

    def __init__(self):
        super().__init__()
        self.run()

    def run(self):

        # TODO choose mode
        mode = Mode.AUDIO_PLURAL

        match mode:

            case Mode.AUDIO_SINGLE:
                path = self.ask_filename()
                Processor.process_one(path, AudioProcessor)

            case Mode.AUDIO_PLURAL:
                path = self.ask_folder()
                Processor.process_all(path, AudioProcessor)

            case Mode.IMAGE_SINGLE:
                path = self.ask_filename()
                Processor.process_one(path, ImageProcessor)

            case Mode.IMAGE_PLURAL:
                path = self.ask_folder()
                Processor.process_all(path, ImageProcessor)

        sys.exit()

    @pyqtSlot()
    def ask_filename(self) -> Path:
        path, _ = QFileDialog.getOpenFileName(
            self, "Choose file to convert", ".", "All files (*);;"
        )

        return Path(path)

    @pyqtSlot()
    def ask_folder(self) -> Path:
        path = QFileDialog.getExistingDirectory(
            self, "Choose folder of files to convert", ".",
            options=QFileDialog.Option.DontUseNativeDialog
        )

        return Path(path)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = Main()
    main_gui.show()
    sys.exit(app.exec())
