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
        #self.resize(1000, 600)
        self.move(300, 0)

        self.layout = QVBoxLayout()
        self.container = QWidget()
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.setLayout(self.layout)

        self.button1 = QPushButton("Let's groove")
        self.button1.clicked.connect(self.groovegandalf)

        self.layout.addWidget(self.button1)

    def  groovegandalf(self):
        self.resize(1000, 600)
        self.move(300, 0)

        self.label_movie = QLabel()
        self.layout.addWidget(self.label_movie)


        self.movie = QMovie("gandy.gif")
        self.movie.setFormat(b"gif")
        self.label_movie.setMovie(self.movie)
        self.movie.setScaledSize(QSize(1000, 500))

        self.layout.addWidget(self.label_movie)

        self.label_movie.setMovie(self.movie)
        self.movie.start()







def main():
    app = QApplication(sys.argv)
    #app.setDesktopFileName("Heisann-app")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()