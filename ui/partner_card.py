"""
Виджет «карточка партнёра» для главного окна
Отображает:
    тип партнёра и его наименование
    ФИО директора
    телефон
    суммарный объём продаж
    рассчитанную скидку
    рейтинг партнёра
"""

from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QFont, QMouseEvent
from PyQt6.QtCore import Qt

from services.partner_utils import format_phone, calc_discount

class PartnerCard(QFrame):
    # Карточка партнёра одна компания

    def __init__(self, partner, on_click=None, parent=None):
        super().__init__(parent)
        self.partner = partner
        self.on_click = on_click
        self.init_ui()

    def init_ui(self) -> None:
        """
        Создаёт визуальное оформление карточки:
            фон, скруглённые углы, отсутствие рамки
            заголовок тип + имя партнёра
            зелёный акцент со скидкой
            информация о директоре, телефоне, объёме продаж, рейтинге.
        """
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setStyleSheet(
            """
            QFrame {
                background-color: #F4E8D3;
                border-radius: 12px;
                border: none;
            }
            QLabel[role="accent"] {
                color: #67BA80;
                font-weight: 700;
                font-size: 14pt;
            }
            QLabel[role="title"] {
                font-size: 16pt;
                font-weight: 800;
            }
            QLabel {
                font-size: 14pt;
            }
            """
        )

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(10)

        # Верхняя строка: тип + название партнёра и скидка
        header_layout = QHBoxLayout()

        # Тип партнёра берём из связанной сущности типы партнеров
        partner_type = self.partner.partner_type.name if self.partner.partner_type else "Тип не указан"

        # Заголовок: «Тип партнёра «Наименование»»
        lbl_title = QLabel(f"{partner_type} «{self.partner.name}»")
        lbl_title.setProperty("role", "title")

        # Суммарный объём продаж и скидка
        total_qty = int(self.partner.summary.total_quantity or 0) if self.partner.summary else 0
        discount = calc_discount(total_qty)
        lbl_discount = QLabel(f"{discount}%")
        lbl_discount.setProperty("role", "accent")

        header_layout.addWidget(lbl_title, stretch=1)
        header_layout.addStretch()
        header_layout.addWidget(lbl_discount)

        # Информация о директоре
        lbl_director = QLabel(f"Директор: {self.partner.director_full_name}")

        # Телефон
        phone = "—"
        if self.partner.contacts:
            # Берём первый контакт и форматируем номер в чтебарельный вид.
            phone = format_phone(self.partner.contacts[0].phone)
        lbl_phone = QLabel(f"Телефон: {phone}")

        # Объём продаж и рейтинг 
        lbl_summary = QLabel(f"Объём продаж: {total_qty} м²")
        lbl_summary.setProperty("role", "accent")

        lbl_rating = QLabel(f"Рейтинг партнёра: {self.partner.rating}")
        rating_font = QFont()
        rating_font.setBold(True)
        rating_font.setPointSize(14)
        lbl_rating.setFont(rating_font)

        main_layout.addLayout(header_layout)
        main_layout.addWidget(lbl_director)
        main_layout.addWidget(lbl_phone)
        main_layout.addWidget(lbl_summary)
        main_layout.addWidget(lbl_rating)

    # Обработчика клика мышью по карточке
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton and self.on_click:
            try:
                self.on_click(self.partner)
            except Exception as e:
                print(f"Ошибка при обработке клика по карточке партнёра: {e}")
        super().mousePressEvent(event)
