import os
import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QStackedWidget, QStyleOption, QStyle,
    QListWidget, QListWidgetItem, QMessageBox, QInputDialog, QLineEdit,
    QFrame, QSpinBox, QCheckBox, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont, QPainter, QPixmap, QFontDatabase, QColor
from gui_classes import BlackJack, GamePhase

GREEN_FELT_STYLE = """
    background: qradialgradient(
        cx:0.5, cy:0.5, radius:0.8,
        fx:0.5, fy:0.5,
        stop:0 #175232,
        stop:1 #082113
    );
"""


def trigger_save_game_dialog(parent_widget, game_instance):
    save_name, ok = QInputDialog.getText(
        parent_widget,
        "Save Game",
        "Enter a name for your save file:",
        QLineEdit.EchoMode.Normal
    )

    if not ok or not save_name.strip():
        return False

    clean_name = save_name.strip()
    saves = BlackJack.get_all_saves()

    exists = any(s.get("save_name") == clean_name for s in saves)
    if exists:
        reply = QMessageBox.question(
            parent_widget,
            "Overwrite Save?",
            f"A save named '{clean_name}' already exists. Overwrite it?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return False

    success, message = game_instance.save_game(clean_name)
    if success:
        QMessageBox.information(parent_widget, "Game Saved", f"Game successfully saved as '{clean_name}'!")
        return True
    else:
        QMessageBox.warning(parent_widget, "Error", f"Failed to save game: {message}")
        return False


class MainMenuWidget(QWidget):
    def __init__(self, stacked_widget, on_load_requested=None, on_settings_requested=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.on_load_requested = on_load_requested
        self.on_settings_requested = on_settings_requested

        script_dir = os.path.dirname(os.path.abspath(__file__))
        cards_path = os.path.join(script_dir, "BloodJack_cards.png")
        self.cards_pixmap = QPixmap(cards_path)

        font_path = os.path.join(script_dir, "Rye.ttf")
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            family = QFontDatabase.applicationFontFamilies(font_id)[0]
            self.title_font = QFont(family, 52, QFont.Weight.Bold)
        else:
            self.title_font = QFont("Arial", 52, QFont.Weight.Bold)

        self.init_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

        if not self.cards_pixmap.isNull():
            scaled_cards = self.cards_pixmap.scaledToWidth(900, Qt.TransformationMode.SmoothTransformation)
            x = (self.width() - scaled_cards.width()) // 2 + 20
            y = (self.height() - scaled_cards.height()) // 2 + 20
            p.drawPixmap(x, y, scaled_cards)

        center_x = self.width() / 2.0
        center_y = (self.height() / 2.0) + 50
        radius = 420
        self._draw_curved_text(p, "BLOODJACK", center_x, center_y, radius, start_angle_deg=-90)

    def _draw_curved_text(self, painter, text, center_x, center_y, radius, start_angle_deg):
        painter.setFont(self.title_font)
        painter.setPen(QColor("#d63031"))

        angle_step = 6.5
        total_angle = (len(text) - 1) * angle_step
        current_angle = start_angle_deg - (total_angle / 2.0)

        for char in text:
            rad = math.radians(current_angle)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad)

            painter.save()
            painter.translate(x, y)
            painter.rotate(current_angle + 90)
            painter.drawText(-20, -20, 40, 40, Qt.AlignmentFlag.AlignCenter, char)
            painter.restore()

            current_angle += angle_step

    def init_ui(self):
        self.setStyleSheet(GREEN_FELT_STYLE)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

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
            btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
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
        self.stacked_widget.setCurrentIndex(1)

    def on_load_game(self):
        if self.on_load_requested:
            self.on_load_requested()
        else:
            self.stacked_widget.setCurrentIndex(2)

    def on_settings(self):
        if self.on_settings_requested:
            self.on_settings_requested()
        else:
            self.stacked_widget.setCurrentIndex(3)

    def on_quit(self):
        QApplication.quit()


class CardWidget(QFrame):
    def __init__(self, card_dict):
        super().__init__()
        self.setFixedSize(70, 100)

        is_face_down = card_dict.get("face_down", False)

        if is_face_down:
            self.setStyleSheet("""
                QFrame {
                    background-color: #2c3e50;
                    border: 2px solid #ecf0f1;
                    border-radius: 6px;
                }
            """)
            label = QLabel("🂠", self)
            label.setFont(QFont("Arial", 28))
            label.setStyleSheet("color: #e74c3c; background: transparent;")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            layout = QVBoxLayout(self)
            layout.addWidget(label)
        else:
            suit = card_dict.get("suit", "")
            rank = card_dict.get("rank", "")
            is_red = suit in ("Hearts", "Diamonds")
            text_color = "#e74c3c" if is_red else "#2c3e50"

            suit_symbol = {"Hearts": "♥", "Diamonds": "♦", "Spades": "♠", "Clubs": "♣"}.get(suit, suit)

            self.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 2px solid #bdc3c7;
                    border-radius: 6px;
                }
            """)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(4, 4, 4, 4)

            top_lbl = QLabel(f"{rank}{suit_symbol}")
            top_lbl.setFont(QFont("Arial", 11, QFont.Weight.Bold))
            top_lbl.setStyleSheet(f"color: {text_color}; background: transparent;")

            center_lbl = QLabel(suit_symbol)
            center_lbl.setFont(QFont("Arial", 20))
            center_lbl.setStyleSheet(f"color: {text_color}; background: transparent;")
            center_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            layout.addWidget(top_lbl)
            layout.addWidget(center_lbl)


class GameBoardWidget(QWidget):
    def __init__(self, stacked_widget, game_instance):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.game = game_instance
        self.init_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def init_ui(self):
        self.setStyleSheet(GREEN_FELT_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(15)

        # --- TOPPBAR ---
        top_bar = QHBoxLayout()

        self.status_label = QLabel("Place your wager to start!")
        self.status_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.status_label.setStyleSheet("color: #f1c40f; background: transparent;")

        save_btn = QPushButton("💾 Save Game")
        save_btn.setStyleSheet(self._btn_style("#2980b9", "#3498db"))
        save_btn.clicked.connect(lambda: trigger_save_game_dialog(self, self.game))

        menu_btn = QPushButton("MainMenu")
        menu_btn.setStyleSheet(self._btn_style("#7f8c8d", "#95a5a6"))
        menu_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        top_bar.addWidget(self.status_label)
        top_bar.addStretch()
        top_bar.addWidget(save_btn)
        top_bar.addWidget(menu_btn)
        main_layout.addLayout(top_bar)

        # --- DEALER SEKSJON ---
        dealer_box = QVBoxLayout()
        self.dealer_info_lbl = QLabel("DEALER (Score: 0)")
        self.dealer_info_lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.dealer_info_lbl.setStyleSheet("color: white; background: transparent;")

        self.dealer_cards_layout = QHBoxLayout()
        self.dealer_cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        dealer_box.addWidget(self.dealer_info_lbl)
        dealer_box.addLayout(self.dealer_cards_layout)
        main_layout.addLayout(dealer_box)

        main_layout.addStretch()

        # --- SPILLER SEKSJON ---
        player_box = QVBoxLayout()
        self.player_info_lbl = QLabel("PLAYER 1 | Funds: 10,000 D$")
        self.player_info_lbl.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.player_info_lbl.setStyleSheet("color: white; background: transparent;")

        self.player_cards_layout = QHBoxLayout()
        self.player_cards_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.player_cards_layout.setSpacing(25)

        player_box.addWidget(self.player_info_lbl)
        player_box.addLayout(self.player_cards_layout)
        main_layout.addLayout(player_box)

        main_layout.addStretch()

        # --- KONTROLLPANEL (2-Raders Oppsett) ---
        controls_vbox = QVBoxLayout()
        controls_vbox.setSpacing(8)

        self.bet_spinbox = QSpinBox()
        self.bet_spinbox.setRange(10, 1000000)
        self.bet_spinbox.setSingleStep(50)
        self.bet_spinbox.setValue(100)
        self.bet_spinbox.setFixedWidth(130)
        self.bet_spinbox.setFixedHeight(40)
        self.bet_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #2c3e50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 6px;
                padding-left: 5px;
            }
        """)

        self.btn_deal = QPushButton("DEAL")
        self.btn_deal.setFixedHeight(40)
        self.btn_deal.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_deal.setStyleSheet(self._btn_style("#27ae60", "#2ecc71"))
        self.btn_deal.clicked.connect(self.on_deal_clicked)

        self.btn_next_round = QPushButton("NEXT ROUND")
        self.btn_next_round.setFixedHeight(40)
        self.btn_next_round.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_next_round.setStyleSheet(self._btn_style("#2980b9", "#3498db"))
        self.btn_next_round.clicked.connect(self.on_next_round_clicked)

        self.btn_hit = QPushButton("HIT")
        self.btn_hit.setFixedHeight(40)
        self.btn_hit.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_hit.setStyleSheet(self._btn_style("#e67e22", "#f39c12"))
        self.btn_hit.clicked.connect(self.on_hit_clicked)

        self.btn_stand = QPushButton("STAND")
        self.btn_stand.setFixedHeight(40)
        self.btn_stand.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_stand.setStyleSheet(self._btn_style("#c0392b", "#e74c3c"))
        self.btn_stand.clicked.connect(self.on_stand_clicked)

        self.btn_double = QPushButton("DOUBLE")
        self.btn_double.setFixedHeight(40)
        self.btn_double.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_double.setStyleSheet(self._btn_style("#8e44ad", "#9b59b6"))
        self.btn_double.clicked.connect(self.on_double_clicked)

        self.btn_split = QPushButton("SPLIT")
        self.btn_split.setFixedHeight(40)
        self.btn_split.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        self.btn_split.setStyleSheet(self._btn_style("#16a085", "#1abc9c"))
        self.btn_split.clicked.connect(self.on_split_clicked)

        # Rad 1: Innsats, Deal og Next Round
        row1 = QHBoxLayout()
        row1.setSpacing(10)
        lbl_bet = QLabel("Bet:")
        lbl_bet.setStyleSheet("color: white; font-weight: bold;")
        row1.addWidget(lbl_bet)
        row1.addWidget(self.bet_spinbox)
        row1.addWidget(self.btn_deal)
        row1.addWidget(self.btn_next_round)

        # Rad 2: Spillhandlinger
        row2 = QHBoxLayout()
        row2.setSpacing(10)
        row2.addWidget(self.btn_hit)
        row2.addWidget(self.btn_stand)
        row2.addWidget(self.btn_double)
        row2.addWidget(self.btn_split)

        controls_vbox.addLayout(row1)
        controls_vbox.addLayout(row2)
        main_layout.addLayout(controls_vbox)

        self.setLayout(main_layout)
        self.update_ui()

    def update_ui(self):
        player = self.game.players[0] if self.game.players else None
        dealer = self.game.dealer
        phase = self.game.game_phase
        is_player_turn = (phase == GamePhase.PLAYER_TURN)

        # 1. Oppdater Spiller & Dealer Etiketter
        if player:
            self.player_info_lbl.setText(f"{player.name.upper()} | Funds: {player.funds:,} D$")
            max_bet = max(10, player.funds)
            self.bet_spinbox.setRange(10, max_bet)
            if self.bet_spinbox.value() > max_bet:
                self.bet_spinbox.setValue(max_bet)

        bank_text = "∞ D$" if self.game.infinite_bank else f"{dealer.bank:,} D$"
        d_score = dealer.hand.get_score()
        self.dealer_info_lbl.setText(f"DEALER | Bank: {bank_text} | Score: {d_score}")

        # 2. Tegn Dealerens kort
        self._clear_layout(self.dealer_cards_layout)
        for card in dealer.hand.cards:
            self.dealer_cards_layout.addWidget(CardWidget(card))

        # 3. Tegn Spillerens hender
        self._clear_layout(self.player_cards_layout)
        if player:
            for idx, hand in enumerate(player.hands):
                is_active = (is_player_turn and idx == self.game.current_hand_index)

                hand_frame = QFrame()
                border_color = "#f1c40f" if is_active else "#34495e"
                bg_color = "rgba(241, 196, 15, 0.12)" if is_active else "rgba(0, 0, 0, 0.25)"

                hand_frame.setStyleSheet(f"""
                    QFrame {{
                        background-color: {bg_color};
                        border: 2px solid {border_color};
                        border-radius: 8px;
                        padding: 6px;
                    }}
                """)

                hand_layout = QVBoxLayout(hand_frame)
                hand_layout.setSpacing(6)

                status_tag = "  ◄ ACTIVE" if is_active else ("  (Done)" if hand.is_done else "")
                hand_title = f"Hand {idx + 1}: {hand.get_score()} pts | Bet: {hand.bet:,} D${status_tag}"

                lbl_hand = QLabel(hand_title)
                lbl_hand.setFont(QFont("Arial", 11, QFont.Weight.Bold))
                lbl_hand.setStyleSheet(
                    f"color: {'#f1c40f' if is_active else '#ecf0f1'}; border: none; background: transparent;"
                )
                hand_layout.addWidget(lbl_hand)

                cards_box = QHBoxLayout()
                cards_box.setAlignment(Qt.AlignmentFlag.AlignLeft)
                cards_box.setSpacing(6)
                for card in hand.cards:
                    cards_box.addWidget(CardWidget(card))

                hand_layout.addLayout(cards_box)
                self.player_cards_layout.addWidget(hand_frame)

        # 4. Knappe-tilstander
        is_betting = (phase == GamePhase.BETTING)
        is_round_over = (phase in (GamePhase.ROUND_OVER, GamePhase.EVALUATION))

        self.bet_spinbox.setEnabled(is_betting)
        self.btn_deal.setEnabled(is_betting)

        self.btn_hit.setEnabled(is_player_turn)
        self.btn_stand.setEnabled(is_player_turn)

        can_double = False
        can_split = False
        if is_player_turn and player and self.game.current_hand:
            hand = self.game.current_hand
            can_double = (player.funds >= hand.bet and len(hand.cards) == 2)
            can_split = hand.is_splittable() and (player.funds >= hand.bet)

        self.btn_double.setEnabled(can_double)
        self.btn_split.setEnabled(can_split)
        self.btn_next_round.setEnabled(is_round_over)

        # Statusmelding
        if is_betting:
            self.status_label.setText("Place your wager and click DEAL!")
        elif is_player_turn:
            hand_num = self.game.current_hand_index + 1
            self.status_label.setText(f"{player.name}'s Turn - Playing Hand {hand_num}")
        elif phase == GamePhase.DEALER_TURN:
            self.status_label.setText("Dealer is drawing cards...")
        elif is_round_over:
            summary = getattr(self.game, "round_summary", "Round Over!")
            self.status_label.setText(summary)

    def on_deal_clicked(self):
        bet_amount = self.bet_spinbox.value()
        if self.game.place_bet(bet_amount):
            self.game.start_round()
            self.update_ui()
        else:
            QMessageBox.warning(self, "Insufficient Funds", "You cannot afford this wager!")

    def on_hit_clicked(self):
        self.game.hit()
        self.update_ui()

    def on_stand_clicked(self):
        self.game.stand()
        self.update_ui()

    def on_double_clicked(self):
        self.game.double_down()
        self.update_ui()

    def on_split_clicked(self):
        self.game.split()
        self.update_ui()

    def on_next_round_clicked(self):
        player = self.game.players[0] if self.game.players else None

        # Hvis spilleren har tapt alt etter at runden er ferdig -> vis Game Over!
        if player and player.funds <= 0:
            self.stacked_widget.setCurrentIndex(4)  # Bytter til GameOverWidget (indeks 4)
            return

        self.game.cleanup_round()
        self.update_ui()

    def _clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _btn_style(self, bg, hover):
        return f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border-radius: 6px;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:disabled {{
                background-color: rgba(127, 140, 141, 0.4);
                color: rgba(236, 240, 241, 0.4);
            }}
        """


class LoadGameWidget(QWidget):
    def __init__(self, stacked_widget, game_instance, on_game_loaded_callback=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.game = game_instance
        self.on_game_loaded_callback = on_game_loaded_callback
        self.init_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def init_ui(self):
        self.setStyleSheet(GREEN_FELT_STYLE)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.setSpacing(20)

        title = QLabel("LOAD GAME")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #ecf0f1; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title)

        self.save_list = QListWidget()
        self.save_list.setFixedWidth(600)
        self.save_list.setFixedHeight(350)
        self.save_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(27, 29, 30, 0.90);
                color: #ecf0f1;
                border: 2px solid #2c3e50;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid #34495e;
            }
            QListWidget::item:selected {
                background-color: #27ae60;
                color: white;
                border-radius: 4px;
            }
            QListWidget::item:hover {
                background-color: rgba(46, 204, 113, 0.3);
            }
        """)
        main_layout.addWidget(self.save_list)

        btn_box = QHBoxLayout()
        btn_box.setSpacing(15)

        load_btn = QPushButton("Load Selected")
        load_btn.setFixedWidth(160)
        load_btn.setFixedHeight(45)
        load_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        load_btn.setStyleSheet(self._btn_style("#27ae60", "#2ecc71"))
        load_btn.clicked.connect(self.load_selected_save)

        delete_btn = QPushButton("Delete Save")
        delete_btn.setFixedWidth(140)
        delete_btn.setFixedHeight(45)
        delete_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        delete_btn.setStyleSheet(self._btn_style("#c0392b", "#e74c3c"))
        delete_btn.clicked.connect(self.delete_selected_save)

        back_btn = QPushButton("Back to Menu")
        back_btn.setFixedWidth(140)
        back_btn.setFixedHeight(45)
        back_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        back_btn.setStyleSheet(self._btn_style("#7f8c8d", "#95a5a6"))
        back_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        btn_box.addWidget(load_btn)
        btn_box.addWidget(delete_btn)
        btn_box.addWidget(back_btn)

        main_layout.addLayout(btn_box)
        self.setLayout(main_layout)
        self.refresh_save_list()

    def refresh_save_list(self):
        self.save_list.clear()
        saves = BlackJack.get_all_saves()

        if not saves:
            item = QListWidgetItem("No saved games found.")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.save_list.addItem(item)
            return

        for metadata in saves:
            name = metadata.get("save_name", "Unsaved")
            player = metadata.get("player_name", "Unknown")
            funds = metadata.get("funds", 0)
            time = metadata.get("timestamp", "")

            display_text = f"💾 {name:<18} | Player: {player:<10} | {funds:,} D$ | {time}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, metadata.get("filepath"))
            self.save_list.addItem(item)

    def load_selected_save(self):
        current_item = self.save_list.currentItem()
        if not current_item:
            return

        filepath = current_item.data(Qt.ItemDataRole.UserRole)
        if not filepath:
            return

        if self.game.load_game(filepath):
            if self.on_game_loaded_callback:
                self.on_game_loaded_callback()
            self.stacked_widget.setCurrentIndex(1)
        else:
            QMessageBox.warning(self, "Error", "Failed to load save file!")

    def delete_selected_save(self):
        current_item = self.save_list.currentItem()
        if not current_item:
            return

        filepath = current_item.data(Qt.ItemDataRole.UserRole)
        if not filepath:
            return

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to permanently delete this save file?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(filepath)
                self.refresh_save_list()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not delete file: {e}")

    def _btn_style(self, bg, hover):
        return f"""
            QPushButton {{
                background-color: {bg};
                color: white;
                border-radius: 6px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
        """


class SettingsWidget(QWidget):
    """Instillingsskjerm for spillet."""

    def __init__(self, stacked_widget, game_instance):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.game = game_instance
        self.init_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def init_ui(self):
        self.setStyleSheet(GREEN_FELT_STYLE)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("SETTINGS")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("color: #ecf0f1; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Innstillingsramme
        box = QFrame()
        box.setFixedWidth(500)
        box.setStyleSheet("""
            QFrame {
                background-color: rgba(27, 29, 30, 0.90);
                border: 2px solid #2c3e50;
                border-radius: 8px;
                padding: 20px;
            }
            QLabel {
                color: #ecf0f1;
                font-size: 14px;
                font-weight: bold;
                border: none;
                background: transparent;
            }
        """)

        box_layout = QVBoxLayout(box)
        box_layout.setSpacing(15)

        # Infinite Bank Checkbox
        self.chk_infinite_bank = QCheckBox("Unlimited House Bank (Husets bank går aldri tom)")
        self.chk_infinite_bank.setChecked(self.game.infinite_bank)
        self.chk_infinite_bank.setStyleSheet("color: white; font-size: 14px;")

        # Shoe Size
        shoe_box = QHBoxLayout()
        lbl_shoe = QLabel("Decks in Shoe (Kortstokker):")
        self.spin_shoe = QSpinBox()
        self.spin_shoe.setRange(1, 8)
        self.spin_shoe.setValue(self.game.shoe_size)
        self.spin_shoe.setStyleSheet("color: white; background: #2c3e50; padding: 4px;")
        shoe_box.addWidget(lbl_shoe)
        shoe_box.addWidget(self.spin_shoe)

        # Hole Card
        self.chk_hole_card = QCheckBox("Dealer Hole Card (Dealer har ett skjult kort)")
        self.chk_hole_card.setChecked(self.game.hole_card)
        self.chk_hole_card.setStyleSheet("color: white; font-size: 14px;")

        box_layout.addWidget(self.chk_infinite_bank)
        box_layout.addLayout(shoe_box)
        box_layout.addWidget(self.chk_hole_card)

        layout.addWidget(box)

        # Lagre og tilbake knapp
        back_btn = QPushButton("Save & Return")
        back_btn.setFixedWidth(200)
        back_btn.setFixedHeight(45)
        back_btn.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        back_btn.clicked.connect(self.save_settings)
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def save_settings(self):
        self.game.infinite_bank = self.chk_infinite_bank.isChecked()
        self.game.shoe_size = self.spin_shoe.value()
        self.game.hole_card = self.chk_hole_card.isChecked()
        self.stacked_widget.setCurrentIndex(0)


class GameOverWidget(QWidget):
    def __init__(self, stacked_widget, game_instance, on_restart_callback=None):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.game = game_instance
        self.on_restart_callback = on_restart_callback
        self.init_ui()

    def paintEvent(self, event):
        opt = QStyleOption()
        opt.initFrom(self)
        p = QPainter(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, opt, p, self)

    def init_ui(self):
        self.setStyleSheet(GREEN_FELT_STYLE)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(25)

        title = QLabel("THE HOUSE ALWAYS WINS")
        title.setFont(QFont("Arial", 42, QFont.Weight.Bold))
        title.setStyleSheet("color: #e74c3c; background: transparent;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        sub_title = QLabel("You have run out of funds and were thrown out of the casino...")
        sub_title.setFont(QFont("Arial", 16))
        sub_title.setStyleSheet("color: #ecf0f1; background: transparent;")
        sub_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        restart_btn = QPushButton("Try Again (New Run)")
        restart_btn.setFixedWidth(240)
        restart_btn.setFixedHeight(50)
        restart_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        restart_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        restart_btn.clicked.connect(self.on_restart)

        menu_btn = QPushButton("Main Menu")
        menu_btn.setFixedWidth(240)
        menu_btn.setFixedHeight(50)
        menu_btn.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        menu_btn.setStyleSheet("""
            QPushButton {
                background-color: #7f8c8d;
                color: white;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #95a5a6;
            }
        """)
        menu_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))

        layout.addWidget(title)
        layout.addWidget(sub_title)
        layout.addWidget(restart_btn)
        layout.addWidget(menu_btn)
        self.setLayout(layout)

    def on_restart(self):
        p_name = self.game.players[0].name if self.game.players else "Player 1"
        self.game.reset_game(player_name=p_name, starting_funds=10000)
        if self.on_restart_callback:
            self.on_restart_callback()
        self.stacked_widget.setCurrentIndex(1)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game = BlackJack()

        self.setWindowTitle("Bloodjack")
        self.setGeometry(0, 0, 1920, 1080)

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        # 0: Main Menu
        self.main_menu = MainMenuWidget(
            self.stacked_widget,
            on_load_requested=self.open_load_menu,
            on_settings_requested=self.open_settings_menu
        )
        self.stacked_widget.addWidget(self.main_menu)

        # 1: Game Board
        self.game_board = GameBoardWidget(self.stacked_widget, self.game)
        self.stacked_widget.addWidget(self.game_board)

        # 2: Load Game Screen
        self.load_menu = LoadGameWidget(
            self.stacked_widget,
            self.game,
            on_game_loaded_callback=self.on_game_loaded
        )
        self.stacked_widget.addWidget(self.load_menu)

        # 3: Settings Screen
        self.settings_menu = SettingsWidget(self.stacked_widget, self.game)
        self.stacked_widget.addWidget(self.settings_menu)

        # 4: Game Over Screen
        self.game_over_screen = GameOverWidget(
            self.stacked_widget,
            self.game,
            on_restart_callback=self.game_board.update_ui
        )
        self.stacked_widget.addWidget(self.game_over_screen)

    def on_game_loaded(self):
        self.game_board.update_ui()

    def open_load_menu(self):
        self.load_menu.refresh_save_list()
        self.stacked_widget.setCurrentIndex(2)

    def open_settings_menu(self):
        self.stacked_widget.setCurrentIndex(3)


def main():
    app = QApplication(sys.argv)
    app.setDesktopFileName("bloodjack-app")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()