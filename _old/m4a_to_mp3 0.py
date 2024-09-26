from pydub import AudioSegment as AS
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from pyQt6.QtCore import pyqtSlot
import sys

class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.fname_old = ''
        self.fname_new = ''
        self.base = ''
        self.ext_old = ''
        self.ext_new = ''
        
        self.ask_filename()

    @pyqtSlot()
    def ask_filename(self):
        
        

# fname_old = input('Enter old filename: ').strip()
fname_old = QFileDialog.getOpenFileName(None, "Open Audio File", ".", "All Files (*);;")

parts = fname_old.split('.')

ext_old = parts[-1]
base = '.'.join(parts[:-1])

# export_format = input('Enter new format: ').strip().lower()
ext_new = 'mp3'

fname_new = f'{base}.{ext_new}'

audio = AS.from_file(fname_old, format=ext_old)
audio.export(fname_new, format=ext_new, bitrate='320k')

print(f'Exported to {fname_new}')

input('Enter to exit')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_gui = Main()
    main_gui.show()
    sys.exit(app.exec())
