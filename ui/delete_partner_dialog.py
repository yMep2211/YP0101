# Диалоговое окно для удаления партнёра

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QMessageBox, QWidget, QSizePolicy
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from sqlalchemy.orm import Session

from db.models import Partner
from services.partner_service import get_all_partners, delete_partner

class DeletePartnerDialog(QDialog):
    # Диалог удаления партнёра
    def __init__(self, session: Session, parent: QWidget | None = None):
        super().__init__(parent)
        self.session = session
        # Список партнёров, загружаемых из БД для заполнения комбобокса
        self.partners: list[Partner] = []
        self.combo_partners: QComboBox | None = None
        
        self.init_ui()
        self.load_partners()

    def init_ui(self):
        """
        Создаёт и настраивает элементы интерфейса диалога:
            шапка с логотипом и заголовком
            подпись «Выберите партнёра для удаления» и выпадающий список
            кнопки «Удалить» и «Отмена»
        """
        self.setWindowTitle("Удаление партнёра")
        self.resize(600, 260)

        base_font = QFont("Segoe UI", 12)
        self.setFont(base_font)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)

        # Шапка
        header = QWidget(self)
        header.setStyleSheet(
            """
            QWidget {
                background-color: #F4E8D3;
                border-radius: 8px;
            }
            """
        )
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(10, 4, 10, 4)
        header_layout.setSpacing(10)
        header.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # Логотип компании 
        logo_label = QLabel(header)
        pixmap = QPixmap("resources/logo.png")
        if not pixmap.isNull():
            # Масштабируем с сохранением пропорций
            pixmap = pixmap.scaled(
                36, 36,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)

        # Заголовок диалога
        title_label = QLabel("Удаление партнёра", header)
        title_label.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))

        header_layout.addWidget(
            logo_label,
            0,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        header_layout.addWidget(
            title_label,
            1,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        header_layout.addStretch()

        layout.addWidget(header)

        # Выбор партнера
        row = QHBoxLayout()

        # Подпись перед выпадающим списокм
        lbl = QLabel("Выберите партнёра для удаления:", self)
        lbl.setMinimumWidth(260)
        label_font = QFont("Segoe UI", 14)
        label_font.setBold(True)
        lbl.setFont(label_font)

        # Выпадающий список со списком партнёров
        self.combo_partners = QComboBox(self)
        combo_font = QFont("Segoe UI", 13)
        combo_font.setBold(True)
        self.combo_partners.setFont(combo_font)
        self.combo_partners.setStyleSheet(
            """
            QComboBox {
                padding: 6px;
                font-size: 14px;
            }
            """
        )

        row.addWidget(lbl)
        row.addWidget(self.combo_partners)
        layout.addLayout(row)

        # Кнопки
        btns_row = QHBoxLayout()
        btns_row.addStretch()

        btn_delete = QPushButton("Удалить", self)
        btn_cancel = QPushButton("Отмена", self)

        font_btn = QFont("Segoe UI", 12)
        font_btn.setBold(True)
        btn_delete.setFont(font_btn)
        btn_cancel.setFont(font_btn)

        # Зелёная кнопка удаления
        btn_delete.setStyleSheet(
            """
            QPushButton {
                background-color: #67BA80;
                color: black;
                border-radius: 6px;
                padding: 8px 20px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #5AA872;
            }
            QPushButton:pressed {
                background-color: #4C9462;
            }
            """
        )

        btn_delete.clicked.connect(self.on_delete_clicked)
        btn_cancel.clicked.connect(self.reject)

        btns_row.addWidget(btn_delete)
        btns_row.addWidget(btn_cancel)
        layout.addLayout(btns_row)

    def load_partners(self) -> None:
        """
        Загружает список партнёров из БД и заполняет список
        В списке отображается: «Имя партнёра рейтинг », а в качестве пользовательских данных в QComboBox хранится id партнёра.
        """
        try:
            self.partners = get_all_partners(self.session)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить список партнёров:\n{e}", QMessageBox.StandardButton.Ok,)
            self.partners = []
            return

        self.combo_partners.clear()
        for p in self.partners:
            display = f"{p.name} (рейтинг {p.rating})"
            self.combo_partners.addItem(display, p.id)

    def on_delete_clicked(self) -> None:
        # Обработчик нажатия кнопки «Удалить»

        if not self.partners:
            QMessageBox.information(self, "Удаление", "Нет партнёров для удаления.", QMessageBox.StandardButton.Ok,)
            return

        idx = self.combo_partners.currentIndex()
        if idx < 0:
            return

        partner = self.partners[idx]

        # Своё окно подтверждения с подписями Да / Нет
        msg = QMessageBox(self)
        msg.setWindowTitle("Подтверждение")
        msg.setText(f"Вы действительно хотите удалить партнёра:\n«{partner.name}»?")
        msg.setIcon(QMessageBox.Icon.Question)

        btn_yes = msg.addButton("Да", QMessageBox.ButtonRole.YesRole)
        btn_no = msg.addButton("Нет", QMessageBox.ButtonRole.NoRole)
        msg.setDefaultButton(btn_no)

        msg.exec()

        # Если пользователь не нажал «Да» выходим без удаления
        if msg.clickedButton() is not btn_yes:
            return

        # Пытаемся удалить партнёра через сервис
        try:
            delete_partner(self.session, partner)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось удалить партнёра:\n{e}", QMessageBox.StandardButton.Ok,)
            return
        # Успешное удаление закрываем диалог
        self.accept()
