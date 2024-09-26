from pydub import AudioSegment as AS
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6.QtCore import pyqtSlot
import sys
from send2trash import send2trash
from pathlib import Path

AUDIO_IN_EXTS = ('m4a', 'webm', 'mov', 'mp4')
AUDIO_OUT_EXT = 'mp3'
AUDIO_OUT_BITRATE = '320k'

class Processor:

    @staticmethod
    def process_all(path_dir: Path, exts: tuple[str], process_one: callable) -> None:

        paths = []
        for ext in exts:
            paths.extend(path_dir.glob(f'*.{ext}'))

        print(f'Processing {len(paths)} files')

        for path in paths:
            process_one(path)


class AudioProcessor:

    @staticmethod
    def process_one(path: Path) -> None:
        path_out = path.with_suffix('').with_suffix(f'.{AUDIO_OUT_EXT}')
        audio = AS.from_file(path, format=path.suffix[1:]) # strip .

        try:
            audio.export(path_out, format=AUDIO_OUT_EXT, bitrate=AUDIO_OUT_BITRATE)
            print(f'Exported {path} to {path_out}')
            send2trash(path)

        except:
            print(f'Could not export {path}')

class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        self.run()

    def run(self):
        path_dir = self.ask_folder()
        Processor.process_all(path_dir, AUDIO_IN_EXTS, AudioProcessor.process_one)
        sys.exit()

    @pyqtSlot()
    def ask_folder(self):
        self.folder = QFileDialog.getExistingDirectory(
            self, "Open folder of files to convert", ".",
            options=QFileDialog.Option.DontUseNativeDialog
        )

        return Path(self.folder)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = Main()
    main_gui.show()
    sys.exit(app.exec())
