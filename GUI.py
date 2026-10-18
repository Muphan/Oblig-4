import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "BloodJack.png")

        self.setWindowTitle("Bloodjack")
        self.setGeometry(150, 300, 1920, 1080) # (x_pos, y_pos, x, y)
        self.setWindowIcon(QIcon(icon_path))


def main ():
    app = QApplication(sys.argv)

    app.setDesktopFileName("bloodjack-app")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()