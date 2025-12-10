# Диалог добавления и редактирования партнёра.

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QSpinBox, QPushButton, QMessageBox, QWidget, QSizePolicy
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from sqlalchemy.orm import Session

from db.models import Partner
from services.partner_service import get_partner_types, create_or_update_partner


class PartnerDialog(QDialog):
    # Диалог для добавления и редактирования партнёра.

    def __init__(self, session: Session, partner: Partner | None = None, parent: QWidget | None = None):
        super().__init__(parent)
        self.session = session
        self.partner = partner
        # Кэш типов партнёров из справочника
        self.partner_types = []

        # Элементы формы
        self.combo_type: QComboBox | None = None
        self.edit_name: QLineEdit | None = None
        self.edit_director: QLineEdit | None = None
        self.edit_address: QLineEdit | None = None
        self.edit_inn: QLineEdit | None = None
        self.edit_email: QLineEdit | None = None
        self.edit_phone: QLineEdit | None = None
        self.spin_rating: QSpinBox | None = None

        # Флаг чтобы не зациклить обработчик при обновлении текста
        self._phone_updating: bool = False

        self.init_ui()
        self.load_partner_types()
        self.fill_for_edit()

    def init_ui(self) -> None:
        """
        Создаёт и настраивает элементы интерфейса диалога:
            шапку с логотипом
            поля ввода данных партнёра
            кнопки «Добавить/Сохранить» и «Отмена»
        """
        is_edit = self.partner is not None
        self.setWindowTitle("Редактирование партнёра" if is_edit else "Добавление партнёра")
        self.resize(700, 430)

        font = QFont("Segoe UI", 11)
        self.setFont(font)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

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

        # Логотип
        logo_label = QLabel(header)
        pixmap = QPixmap("resources/logo.png")
        if not pixmap.isNull():
            # Масштабирование с сохранением пропорций.
            pixmap = pixmap.scaled(
                36, 36,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)

        # Заголовок шапки
        header_text = "Редактирование партнёра" if is_edit else "Добавление партнёра"
        title_label = QLabel(header_text, header)
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

        # Форма
        def add_row(label_text: str) -> QLineEdit:
            row = QHBoxLayout()
            lbl = QLabel(label_text, self)
            lbl.setMinimumWidth(200)
            edit = QLineEdit(self)
            row.addWidget(lbl)
            row.addWidget(edit)
            layout.addLayout(row)
            return edit

        # Тип партнёра список
        row_type = QHBoxLayout()
        lbl_type = QLabel("Тип партнёра:", self)
        lbl_type.setMinimumWidth(200)
        self.combo_type = QComboBox(self)
        row_type.addWidget(lbl_type)
        row_type.addWidget(self.combo_type)
        layout.addLayout(row_type)

        # Остальные поля формы
        self.edit_name = add_row("Наименование партнёра:")
        self.edit_director = add_row("ФИО директора:")
        self.edit_address = add_row("Юридический адрес:")
        self.edit_inn = add_row("ИНН:")
        self.edit_email = add_row("Электронная почта:")
        self.edit_phone = add_row("Телефон:")

        # Телефон: изначально "+7 " и дальше пользователь вводит 10 цифр
        self.edit_phone.setText("+7 ")
        self.edit_phone.setCursorPosition(len("+7 "))
        self.edit_phone.textChanged.connect(self._on_phone_changed)

        # Рейтинг
        row_rating = QHBoxLayout()
        lbl_rating = QLabel("Рейтинг (0–10):", self)
        lbl_rating.setMinimumWidth(200)
        self.spin_rating = QSpinBox(self)
        self.spin_rating.setRange(0, 10)
        self.spin_rating.setSingleStep(1)
        row_rating.addWidget(lbl_rating)
        row_rating.addWidget(self.spin_rating)
        layout.addLayout(row_rating)

        # Кнопки
        buttons_row = QHBoxLayout()
        buttons_row.addStretch()

        # Текст кнопки "Добавить" или "Сохранить"
        btn_ok_text = "Сохранить" if is_edit else "Добавить"
        btn_ok = QPushButton(btn_ok_text, self)
        btn_cancel = QPushButton("Отмена", self)

        font_btn = QFont("Segoe UI", 11)
        font_btn.setBold(True)
        btn_ok.setFont(font_btn)
        btn_cancel.setFont(font_btn)

        # Зелёная кнопка
        btn_ok.setStyleSheet(
            """
            QPushButton {
                background-color: #67BA80;
                color: black;
                border-radius: 6px;
                padding: 6px 16px;
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

        btn_ok.clicked.connect(self.on_save_clicked)
        btn_cancel.clicked.connect(self.reject)

        buttons_row.addWidget(btn_ok)
        buttons_row.addWidget(btn_cancel)
        layout.addLayout(buttons_row)

    def load_partner_types(self) -> None:
        # Загружает список типов партнёров из БД и заполняет комбобокс.
        try:
            self.partner_types = get_partner_types(self.session)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить типы партнёров:\n{e}", QMessageBox.StandardButton.Ok,)
            self.partner_types = []
            return

        self.combo_type.clear()
        for pt in self.partner_types:
            self.combo_type.addItem(pt.name, pt.id)

    def fill_for_edit(self) -> None:
        # Если диалог открыт для редактирования заполняет поля формы данными существующего партнёра
        if self.partner is None:
            return

        # Устанавливаем тип партнёра в списке
        if self.partner.partner_type_id and self.partner_types:
            for i, pt in enumerate(self.partner_types):
                if pt.id == self.partner.partner_type_id:
                    self.combo_type.setCurrentIndex(i)
                    break

        self.edit_name.setText(self.partner.name or "")
        self.edit_director.setText(self.partner.director_full_name or "")
        self.edit_address.setText(self.partner.legal_address or "")
        self.edit_inn.setText(self.partner.inn or "")
        self.spin_rating.setValue(self.partner.rating or 0)

        email = ""
        phone_digits = ""
        if self.partner.contacts:
            c = self.partner.contacts[0]
            email = c.email or ""
            phone_digits = c.phone or ""

        self.edit_email.setText(email)

        digits = "".join(ch for ch in (phone_digits or "") if ch.isdigit())
        if len(digits) > 10:
            digits = digits[-10:]

        self._phone_updating = True
        try:
            # Если есть цифры показываем "+7 " + цифры если нет просто "+7 ".
            if digits:
                self.edit_phone.setText("+7 " + digits)
            else:
                self.edit_phone.setText("+7 ")
            self.edit_phone.setCursorPosition(len(self.edit_phone.text()))
        finally:
            self._phone_updating = False

    def _on_phone_changed(self, text: str) -> None:
        # Обработчик изменения телефона
        if self._phone_updating:
            return

        self._phone_updating = True
        try:
            prefix = "+7 "

            # Вытаскиваем все цифры из текста
            digits = "".join(ch for ch in text if ch.isdigit())

            if digits.startswith("7"):
                digits = digits[1:]

            # Максимум 10 цифр после +7
            digits = digits[:10]

            new_text = prefix + digits
            if new_text != self.edit_phone.text():
                self.edit_phone.setText(new_text)

            self.edit_phone.setCursorPosition(len(self.edit_phone.text()))
        finally:
            self._phone_updating = False

    def on_save_clicked(self) -> None:
        # Обработчик нажатия кнопки сохранить или добавить
        try:
            data = self.collect_data()
            create_or_update_partner(self.session, self.partner, data)
        except ValueError as e:
            # Ошибки валидации (формат ИНН, email, телефон, рейтинг и остальные
            QMessageBox.warning( self, "Ошибка ввода", str(e), QMessageBox.StandardButton.Ok,)
            return
        except Exception as e:
            QMessageBox.critical( self, "Ошибка", f"Не удалось сохранить партнёра:\n{e}", QMessageBox.StandardButton.Ok,)
            return

        self.accept()

    def collect_data(self) -> dict:
        # Сборка данных формы в словарь
        partner_type_id = self.combo_type.currentData()
        return {
            "partner_type_id": int(partner_type_id) if partner_type_id is not None else None,
            "name": self.edit_name.text(),
            "director_full_name": self.edit_director.text(),
            "legal_address": self.edit_address.text(),
            "inn": self.edit_inn.text(),
            "email": self.edit_email.text(),
            "phone": self.edit_phone.text(),
            "rating": self.spin_rating.value(),
        }
