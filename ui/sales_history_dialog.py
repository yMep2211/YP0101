# Окно истории реализации продукции партнёров

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QWidget, QSizePolicy, QHeaderView, QFileDialog
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from sqlalchemy.orm import Session

from db.models import Partner
from services.partner_service import get_all_partners
from services.sales_history_service import get_partner_sales
from services.report_service import generate_partner_sales_report


class SalesHistoryDialog(QDialog):
    # Окно истории реализации продукции партнёров
    def __init__(self, session: Session, parent: QWidget | None = None):
        super().__init__(parent)
        self.session = session
        # Список партнёров для списка
        self.partners: list[Partner] = []

        # Виджеты интерфейса
        self.combo_partners: QComboBox | None = None
        self.table: QTableWidget | None = None

        self.init_ui()
        self.load_partners()
        # Если партнёры есть, сразу подгружаем продажи первого
        if self.partners:
            self.load_sales_for_current_partner()

    def init_ui(self) -> None:
        """
        Создаёт и настраивает элементы интерфейса диалога:
            шапку с логотипом
            комбобокс для выбора партнёра
            таблицу с продажами
            кнопки «Сформировать отчёт» и «Закрыть»
        """
        self.setWindowTitle("История реализации продукции")
        self.resize(900, 500)

        base_font = QFont("Segoe UI", 11)
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

        # Логотип
        logo_label = QLabel(header)
        pixmap = QPixmap("resources/logo.png")
        if not pixmap.isNull():
            pixmap = pixmap.scaled(
                36, 36,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            logo_label.setPixmap(pixmap)

        # Заголовок
        title_label = QLabel("История реализации продукции", header)
        title_font = QFont("Segoe UI", 16)
        title_font.setBold(True)
        title_label.setFont(title_font)

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
        row_top = QHBoxLayout()

        lbl_partner = QLabel("Партнёр:", self)
        lbl_partner.setMinimumWidth(120)
        lbl_font = QFont("Segoe UI", 12)
        lbl_font.setBold(True)
        lbl_partner.setFont(lbl_font)

        self.combo_partners = QComboBox(self)
        self.combo_partners.setFont(QFont("Segoe UI", 11))
        
        # При смене выбранного партнёра подгружаем его продажи
        self.combo_partners.currentIndexChanged.connect(self.on_partner_changed)

        row_top.addWidget(lbl_partner)
        row_top.addWidget(self.combo_partners)
        layout.addLayout(row_top)

        # Таблица продаж
        self.table = QTableWidget(self)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Дата продажи", "Продукция", "Количество (м²)"])

        # Растягивание по экрану
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        header_view = self.table.horizontalHeader()
        
        # Ширина столбцов по содержимому
        header_view.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header_view.setStretchLastSection(True)

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

        layout.addWidget(self.table)

        # Кнопки
        buttons_row = QHBoxLayout()
        buttons_row.addStretch()

        btn_report = QPushButton("Сформировать отчёт", self)
        btn_close = QPushButton("Закрыть", self)

        font_btn = QFont("Segoe UI", 11)
        font_btn.setBold(True)
        btn_report.setFont(font_btn)
        btn_close.setFont(font_btn)

        btn_report.setStyleSheet(
            """
            QPushButton {
                background-color: #67BA80;
                color: white;
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

        btn_report.clicked.connect(self.on_generate_report_clicked)
        btn_close.clicked.connect(self.reject)

        buttons_row.addWidget(btn_report)
        buttons_row.addWidget(btn_close)
        layout.addLayout(buttons_row)

    # Загрузка данных

    def load_partners(self) -> None:
        # Загружает список партнёров из БД и заполняет комбобокс в случае ошибки показывает окно с сообщением и оставляет список пустым
        try:
            self.partners = get_all_partners(self.session)
        except Exception as e:
            QMessageBox.critical( self, "Ошибка", f"Не удалось загрузить список партнёров:\n{e}", QMessageBox.StandardButton.Ok,)
            self.partners = []
            return

        self.combo_partners.blockSignals(True)
        self.combo_partners.clear()
        for p in self.partners:
            self.combo_partners.addItem(p.name, p.id)
        self.combo_partners.blockSignals(False)

    # Обработчики
    
    def on_partner_changed(self, index: int) -> None:
        # Обработчик смены выбранного партнёра в комбобоксе
        if index < 0:
            return
        self.load_sales_for_current_partner()

    def load_sales_for_current_partner(self) -> None:
        # Подгружает продажи выбранного партнёра в таблицу
        idx = self.combo_partners.currentIndex()
        if idx < 0 or not self.partners:
            self.table.setRowCount(0)
            return

        partner = self.partners[idx]

        try:
            sales = get_partner_sales(self.session, partner.id)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить продажи:\n{e}", QMessageBox.StandardButton.Ok,)
            return

        self.table.setRowCount(len(sales))
        for row, (sale_date, product_name, quantity) in enumerate(sales):
            # Дата в формате ДД.ММ.ГГГГ.
            date_str = sale_date.strftime("%d.%m.%Y") if hasattr(sale_date, "strftime") else str(sale_date)
            self.table.setItem(row, 0, QTableWidgetItem(date_str))
            self.table.setItem(row, 1, QTableWidgetItem(product_name or ""))
            self.table.setItem(row, 2, QTableWidgetItem(str(quantity)))

        # Ширину столбцов подстаивается под содержимое
        self.table.resizeColumnsToContents()

    def on_generate_report_clicked(self) -> None:
        # Формирование ПДФ отчета
        if not self.partners:
            QMessageBox.information(self, "Отчёт", "Нет партнёров для формирования отчёта.", QMessageBox.StandardButton.Ok,)
            return

        idx = self.combo_partners.currentIndex()
        if idx < 0:
            QMessageBox.information(self, "Отчёт", "Партнёр не выбран.", QMessageBox.StandardButton.Ok,)
            return

        partner = self.partners[idx]

        safe_name = (
            partner.name
            .replace('"', "")
            .replace("'", "")
            .replace("/", "_")
            .replace("\\", "_")
        )
        default_name = f"История продаж {safe_name}.pdf"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт",
            default_name,
            "PDF файлы (*.pdf)"
        )
        if not filename:
            return

        try:
            generate_partner_sales_report(self.session, partner.id, filename)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать PDF-отчёт:\n{e}", QMessageBox.StandardButton.Ok,)
            return

        QMessageBox.information(self, "Готово", "PDF-отчёт успешно сформирован.", QMessageBox.StandardButton.Ok,)
