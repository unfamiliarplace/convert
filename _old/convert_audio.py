from pydub import AudioSegment as AS
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6.QtCore import pyqtSlot
import sys
from send2trash import send2trash

class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.fname_old = ''
        self.fname_new = ''
        self.base = ''
        self.ext_old = ''
        self.ext_new = ''
        self.output_bitrate = ''
        self.audio = None
        
        self.run()

    def run(self):
        self.ask_filename()
        self.ask_extension()
        self.ask_save_location()
        self.read()
        wrote = self.write()
        if wrote and self.ask_delete_original():
            self.delete_original()

        # input('Enter to exit')
        sys.exit()

    @pyqtSlot()
    def ask_filename(self):
        self.fname_old, selected_type = QFileDialog.getOpenFileName(
            self, "Open Audio File", ".", "All Files (*);;"
        )

        parts = self.fname_old.split('.')

        self.ext_old = parts[-1]
        self.base = '.'.join(parts[:-1])

    def ask_extension(self):
        # TODO Just set it...
        self.ext_new = 'mp3'
        self.output_bitrate = '320k'

    def ask_save_location(self):
        # TODO Just set it...
        self.fname_new = f'{self.base}.{self.ext_new}'

    def read(self):
        self.audio = AS.from_file(self.fname_old, format=self.ext_old)

    def write(self):
        try:
            self.audio.export(self.fname_new, format=self.ext_new, bitrate=self.output_bitrate)
            print(f'Exported to {self.fname_new}')
            return True
        except:
            print('Could not export')
            return False

    def ask_delete_original(self) -> bool:
        # TODO
        return True

    def delete_original(self):
        # send2trash stupidly requires this
        path_to_trash = self.fname_old.replace('/', '\\')
        send2trash(path_to_trash)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = Main()
    main_gui.show()
    sys.exit(app.exec())
