import os
import sys
import math
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QStyleOption, QStyle
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QPainter, QPixmap, QFontDatabase, QColor


# Common casinogreen-QSS background (Radial gradient centered for "light" effect)
GREEN_FELT_STYLE = """
    background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.8,
        fx:0.5, fy:0.5,
        stop:0 #175232,  /* Soft green in the center under the light */
        stop:1 #082113   /* Dark moss green at the edges */
    );
"""


class MainMenuWidget(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        script_dir = os.path.dirname(os.path.abspath(__file__))
        cards_path = os.path.join(script_dir, "BloodJack_cards.png")
        self.cards_pixmap = QPixmap(cards_path)

        # (Optional) Add a font
        font_path = os.path.join(script_dir, "Rye.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.title_font = QFont(family, 52, QFont.Bold)
        else:
            self.title_font = QFont("Arial", 52, QFont.Bold)

        self.init_ui()

    def paintEvent(self, event):
        # Need this so QWidget can show custom QSS-backgrounds correctly
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        # 1. Draw Green background
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

        # 2. Draw Card background
        if not self.cards_pixmap.isNull():
            # Scale picture
            scaled_cards = self.cards_pixmap.scaledToWidth(900, Qt.SmoothTransformation)

            # Calculate center position
            x = (self.width() - scaled_cards.width()) // 2 +20
            y = (self.height() - scaled_cards.height()) // 2 + 20 # Tiny bit of offset

            p.drawPixmap(x, y, scaled_cards)

        center_x = self.width() / 2.0
        center_y = (self.height() / 2.0) + 50  # Sentrum for buen (dratt ned for at toppen av buen skal være øverst)
        radius = 420
        self._draw_curved_text(p, "BLOODJACK", center_x, center_y, radius, start_angle_deg=-90)



    def _draw_curved_text(self, painter, text, center_x, center_y, radius, start_angle_deg):
        """Hjelpemetode for å tegne tekst i en bue."""
        painter.setFont(self.title_font)
        painter.setPen(QColor("#d63031"))  # Rødfargen på teksten

        # Beregn vinkel per bokstav basert på antall tegn
        angle_step = 6.5  # Antall grader spredning mellom hver bokstav
        total_angle = (len(text) - 1) * angle_step
        current_angle = start_angle_deg - (total_angle / 2.0)

        for char in text:
            rad = math.radians(current_angle)

            # Beregn posisjon på buen
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)

            painter.save()
            painter.translate(x, y)
            # Roter bokstaven slik at den står vinkelrett på buen
            painter.rotate(current_angle + 90)

            # Tegn bokstaven sentrert
            painter.drawText(-20, -20, 40, 40, Qt.AlignCenter, char)
            painter.restore()

            current_angle += angle_step

    def init_ui(self):
        self.setStyleSheet(GREEN_FELT_STYLE)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)

        # Titel
        #title = QLabel("BLOODJACK")
        #title.setFont(QFont("Arial", 42, QFont.Bold))
        #title.setAlignment(Qt.AlignCenter)
        #title.setStyleSheet("color: #d63031; margin-bottom: 30px; background: transparent;")
        #layout.addWidget(title)

        # Menu buttons
        buttons = [
            ("New Game", self.on_new_game),
            ("Load Game", self.on_load_game),
            ("Settings", self.on_settings),
            ("Quit", self.on_quit)
        ]

        for text, callback in buttons:
            btn = QPushButton(text)
            btn.setFixedWidth(240)
            btn.setFixedHeight(50)
            btn.setFont(QFont("Arial", 12, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: rgba(27, 29, 30, 0.90);
                    color: #ecf0f1;
                    border: 2px solid #2c3e50;
                    border-radius: 8px;
                }
                QPushButton:hover {
                    background-color: rgba(39, 174, 96, 0.95);
                    border-color: #2ecc71;
                    color: white;
                }
                QPushButton:pressed {
                    background-color: rgba(30, 132, 73, 1.0);
                }
            """)
            btn.clicked.connect(callback)
            layout.addWidget(btn)

        self.setLayout(layout)

    def on_new_game(self):
        # Switch to GameBoardWidget (index 1)
        self.stacked_widget.setCurrentIndex(1)

    def on_load_game(self):
        print("Load game menu...")

    def on_settings(self):
        print("Settings menu...")

    def on_quit(self):
        QApplication.quit()


class GameBoardWidget(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.init_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PE_Widget, opt, p, self)

    def init_ui(self):
        self.setStyleSheet(GREEN_FELT_STYLE)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel("--- GAME TABLE (CASINO FELT) ---")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        label.setStyleSheet("color: white; background: transparent;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        # Temporary button to return to main menu
        back_btn = QPushButton("Back to Main Menu")
        back_btn.setFixedWidth(180)
        back_btn.setFixedHeight(40)
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #c0392b;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e74c3c;
            }
        """)
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)

        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "../BloodJack.png")

        self.setWindowTitle("Bloodjack")
        self.setGeometry(0, 0, 1920, 1080)
        self.setWindowIcon(QIcon(icon_path))

        # Create StackedWidget that holds the screens
        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # Screen 0: Main menu
        self.main_menu = MainMenuWidget(self.stacked_widget)
        self.stacked_widget.addWidget(self.main_menu)

        # Screen 1: Game table
        self.game_board = GameBoardWidget(self.stacked_widget)
        self.stacked_widget.addWidget(self.game_board)


def main():
    app = QApplication(sys.argv)
    app.setDesktopFileName("bloodjack-app")

    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()