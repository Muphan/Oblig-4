from PyQt6.QtWidgets import (QLabel, QPushButton, QLineEdit, QRadioButton,
                             QCheckBox, QComboBox, QTextEdit, QMessageBox,
                             QSlider, QProgressBar, QMainWindow, QApplication,
                             QVBoxLayout, QWidget)
import sys
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QMovie
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Heisann sveisann!")
        #self.setGeometry(0, 0, 600, 400)
        self.resize(1000, 600)
        self.move(300, 0)

        layout = QVBoxLayout()
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)


        label1 = QLabel()
        label1.setText("Let's groove!")

        label_movie = QLabel()
        movie = QMovie("gandy.gif")
        movie.setFormat(b"gif")
        label_movie.setMovie(movie)
        movie.setScaledSize(QSize(1000, 500))


        self.setLayout(layout)

        layout.addWidget(label1)
        layout.addWidget(label_movie)

        label_movie.setMovie(movie)
        movie.start()





def main():
    app = QApplication(sys.argv)
    #app.setDesktopFileName("Heisann-app")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()