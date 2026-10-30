import sys, random
from PyQt6.QtWidgets import (QApplication, QWidget, QGridLayout, QPushButton, QLabel, QComboBox,
                             QDoubleSpinBox, QLabel, QComboBox, QDoubleSpinBox, QFormLayout, )
from PyQt6.QtCore import  Qt
from PyQt6.QtGui import QPixmap, QIcon


planets = ["Mercury", "Venus", "Terra", "Mars",
           "Jupiter", "Saturn", "Uranus", "Neptune"]
gravities = [3.7, 8.87, 9.807, 3,721, 24.79, 10.44, 8.87, 11.15]
planet_pics = [
               'images/merkur.png', 'images/venus.png', 'images/jorden.png', 'images/mars.png',
               'images/jupiter.png', 'images/saturn.png', 'images/uranus.png', 'images/neptun.png'
               ]
# 'images/sun.jpg',
solarsystem_dict = {"Sol":{
        "gravity": 274,
        "image": 'images/sun.png'
    }}



def make_system_dict():
    for planet, g, image in zip(planets, gravities, planet_pics):
        solarsystem_dict[planet] = {"gravity": g, "image": image}

make_system_dict()

print(solarsystem_dict["Sol"]["image"])

class MWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weight on different planets")
        self.setGeometry(100,100,500,400)

        windowicon = QIcon(solarsystem_dict["Sol"]["image"])
        self.setWindowIcon(windowicon)


        self.layout = QGridLayout()
        self.setLayout(self.layout)

        self.topplabel = QLabel()
        self.topplabel.setText("What is your weight on different planets?")
        self.layout.addWidget(self.topplabel,0,0,1,2,alignment=Qt.AlignmentFlag.AlignHCenter)

        self.form = QFormLayout()
        self.menu_combobox = QComboBox()
        self.menu_combobox.setPlaceholderText("Choose your planetary body..")
        self.menu_combobox.addItem("Random planet")
        for planet in planets:
            self.menu_combobox.addItem(planet)

        self.form.addRow(self.menu_combobox)
        self.layout.addLayout(self.form, 1, 0)

        self.weight_input = QDoubleSpinBox()
        self.weight_input.setPrefix("Your weight in kilograms:    ")
        self.weight_input.setDecimals(1)
        self.form.addRow(self.weight_input)

        self.calculate_button = QPushButton("Calculate")
        self.form.addRow(self.calculate_button)

        self.layout.addLayout(self.form, 1, 0)

        self.image_label = QLabel()
        self.pixmap = QPixmap("images/sun.png")
        self.pixmap = self.pixmap.scaled(512,512)
        self.image_label.setPixmap(self.pixmap)

        self.layout.addWidget(self.image_label, 1, 1)

        self.bottomlabel = QLabel("Choose a planet and enter your weight")
        self.layout.addWidget(self.bottomlabel,2,0,1,2, alignment=Qt.AlignmentFlag.AlignHCenter)






        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MWindow()
    sys.exit(app.exec())