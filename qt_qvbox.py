from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
import sys

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QVBoxlayout")
        self.setGeometry(0, 0, 200, 300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        button1 = QPushButton("Button 1")
        layout.addWidget(button1)

        button2 = QPushButton()
        button2.setText("Button 2")
        layout.addWidget(button2)

        button3 = QPushButton("Button 3")
        layout.addWidget(button3)


        self.show()




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec())