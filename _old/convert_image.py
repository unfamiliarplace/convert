from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog
from PyQt6.QtCore import pyqtSlot
from send2trash import send2trash
import sys
import io
import traceback

from PIL import Image, ImageCms
import pillow_heif

FORCE_EXT = 'jpg'
FORCE_FORMAT = 'JPEG'

# TODO Colour space of HEIC is not preserved.

class Main(QMainWindow):
    def __init__(self):
        super().__init__()

        pillow_heif.register_heif_opener()

        self.fname_old = ''
        self.fname_new = ''
        self.base = ''
        self.ext_old = ''
        self.ext_new = ''
        self.image = None
        self.image_orig = None
        self.icc_orig = ''
        self.icc = ''
        self.icc_name = 'sRGB'
        self.quality = 99
        
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

        self.ext_old = parts[-1].lower()
        self.base = '.'.join(parts[:-1])

    def ask_extension(self):
        # TODO Just set it...
        self.ext_new = FORCE_EXT
        
    def ask_save_location(self):
        # TODO Just set it...
        self.fname_new = f'{self.base}.{self.ext_new}'

    def convert_icc(self):

        # https://stackoverflow.com/a/50623824        
        self.icc_orig = self.image.info.get('icc_profile', '')
        if self.icc_orig:
            self.image_orig = self.image
            
            io_handle = io.BytesIO(self.icc_orig)
            p_src = ImageCms.ImageCmsProfile(io_handle)
            p_dst = ImageCms.createProfile(self.icc_name)
            
            self.image = ImageCms.profileToProfile(self.image, p_src, p_dst, renderingIntent=0, outputMode='RGB')
            self.icc = self.image.info.get('icc_profile', '')

    def read(self):
        self.image = Image.open(self.fname_old)
        # self.convert_icc()

    def write(self):
        try:
            self.image.save(self.fname_new,
                format = FORCE_FORMAT,
                quality = self.quality,
                icc_profile = self.icc,
                exif=self.image.info.get('exif', b"")
            )
            print(f'Exported to {self.fname_new}')
            return True
        except Exception as e:
            print('Could not export')
            print(traceback.format_exc())
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
