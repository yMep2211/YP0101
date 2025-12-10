# Диалог расчёта количества материала.

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QDoubleSpinBox, QSpinBox,
    QPushButton, QMessageBox, QWidget, QSizePolicy, QFileDialog
)
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
from sqlalchemy.orm import Session

from services.calculation_service import (
    get_product_types,
    get_material_types,
    calculate_required_material,
)
from services.report_service import generate_material_calc_report


class MaterialCalcDialog(QDialog):
    # Диалог расчёта количества материала

    def __init__(self, session: Session, parent: QWidget | None = None):
        super().__init__(parent)
        self.session = session

        # Кэш справочников типов продукции и материалов
        self.product_types = []
        self.material_types = []

        # Элементы интерфейса
        self.combo_product: QComboBox | None = None
        self.combo_material: QComboBox | None = None
        self.spin_quantity: QSpinBox | None = None
        self.spin_param1: QDoubleSpinBox | None = None
        self.spin_param2: QDoubleSpinBox | None = None
        self.label_result: QLabel | None = None

        self.init_ui()
        self.load_reference_data()

    def init_ui(self) -> None:
        """
        Создаёт и настраивает элементы интерфейса:
            шапка с логотипом и заголовком
            поля выбора типа продукции и материала
            числовые поля для количества и параметров
            подпись с результатом
            кнопки «Рассчитать», «Сформировать PDF», «Закрыть»
        """
        self.setWindowTitle("Расчёт количества материала")
        self.resize(700, 420)

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
        title_label = QLabel("Расчёт количества материала", header)
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

        # Строки формы

        def add_row(widget_label: str, widget) -> None:
            # Вспомогательная функция: добавляет в основной layout строку с подписью слева и виджетом справа
            
            row = QHBoxLayout()
            lbl = QLabel(widget_label, self)
            lbl.setMinimumWidth(220)
            lbl_font = QFont("Segoe UI", 11)
            lbl_font.setBold(True)
            lbl.setFont(lbl_font)
            row.addWidget(lbl)
            row.addWidget(widget)
            layout.addLayout(row)

        # Тип продукции
        self.combo_product = QComboBox(self)
        self.combo_product.setFont(QFont("Segoe UI", 11))
        add_row("Тип продукции:", self.combo_product)

        # Тип материала
        self.combo_material = QComboBox(self)
        self.combo_material.setFont(QFont("Segoe UI", 11))
        add_row("Тип материала:", self.combo_material)

        # Количество продукции
        self.spin_quantity = QSpinBox(self)
        self.spin_quantity.setRange(1, 1_000_000)
        self.spin_quantity.setValue(1)
        add_row("Количество продукции (шт.):", self.spin_quantity)

        # Параметр 1
        self.spin_param1 = QDoubleSpinBox(self)
        self.spin_param1.setDecimals(3)
        self.spin_param1.setRange(0.001, 1_000_000.0)
        self.spin_param1.setValue(1.0)
        add_row("Параметр 1:", self.spin_param1)

        # Параметр 2
        self.spin_param2 = QDoubleSpinBox(self)
        self.spin_param2.setDecimals(3)
        self.spin_param2.setRange(0.001, 1_000_000.0)
        self.spin_param2.setValue(1.0)
        add_row("Параметр 2:", self.spin_param2)

        # Результат
        self.label_result = QLabel("Результат: ещё не рассчитано", self)
        res_font = QFont("Segoe UI", 12)
        res_font.setBold(True)
        self.label_result.setFont(res_font)
        layout.addWidget(self.label_result)

        # Кнопки
        buttons_row = QHBoxLayout()
        buttons_row.addStretch()

        btn_calc = QPushButton("Рассчитать", self)
        btn_pdf = QPushButton("Сформировать PDF", self)
        btn_close = QPushButton("Закрыть", self)

        font_btn = QFont("Segoe UI", 11)
        font_btn.setBold(True)
        btn_calc.setFont(font_btn)
        btn_pdf.setFont(font_btn)
        btn_close.setFont(font_btn)

        # Общий стиль кнопок
        green_style = """
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
        btn_calc.setStyleSheet(green_style)
        btn_pdf.setStyleSheet(green_style)

        btn_calc.clicked.connect(self.on_calc_clicked)
        btn_pdf.clicked.connect(self.on_pdf_clicked)
        btn_close.clicked.connect(self.reject)

        buttons_row.addWidget(btn_calc)
        buttons_row.addWidget(btn_pdf)
        buttons_row.addWidget(btn_close)

        layout.addLayout(buttons_row)

    def load_reference_data(self) -> None:
        # Загрузка данных из БД
        try:
            self.product_types = get_product_types(self.session)
            self.material_types = get_material_types(self.session)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить типы продукции/материалов:\n{e}", QMessageBox.StandardButton.Ok,)
            self.product_types = []
            self.material_types = []
            return

        # Продукты
        self.combo_product.clear()
        for pt in self.product_types:
            self.combo_product.addItem(pt.name, pt.id)

        # Материалы
        self.combo_material.clear()
        for mt in self.material_types:
            self.combo_material.addItem(mt.name, mt.id)

    # Обработчики

    def _collect_params(self):
        # Считывает значения выбранные или введённые пользователем и возвращает их в виде кортежа\
            
        if not self.product_types or not self.material_types:
            raise ValueError("Справочники типов продукции и материалов не загружены.")

        p_index = self.combo_product.currentIndex()
        m_index = self.combo_material.currentIndex()

        if p_index < 0 or m_index < 0:
            raise ValueError("Тип продукции и тип материала должны быть выбраны.")

        product_type_id = self.combo_product.currentData()
        material_type_id = self.combo_material.currentData()

        quantity = self.spin_quantity.value()
        param1 = self.spin_param1.value()
        param2 = self.spin_param2.value()

        return product_type_id, material_type_id, quantity, param1, param2

    def on_calc_clicked(self) -> None:
        # Обработчик кнопки «Рассчитать»
        
        try:
            product_type_id, material_type_id, quantity, param1, param2 = self._collect_params()
            result = calculate_required_material(
                self.session,
                product_type_id,
                material_type_id,
                quantity,
                param1,
                param2,
            )
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e), QMessageBox.StandardButton.Ok,)
            return
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось выполнить расчёт:\n{e}", QMessageBox.StandardButton.Ok,)
            return

        # Интерпретируем отрицательное значение как расчёт невозможен
        if result < 0:
            self.label_result.setText(
                "Результат: невозможно выполнить расчёт (проверьте введённые данные)."
            )
        else:
            self.label_result.setText(f"Результат: необходимо {result} единиц материала.")

    def on_pdf_clicked(self) -> None:
        # Обработчик кнопки «Сформировать PDF»
        
        try:
            product_type_id, material_type_id, quantity, param1, param2 = self._collect_params()
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка ввода", str(e), QMessageBox.StandardButton.Ok,)
            return

        # Выбор файла для сохранения отчёта
        prod_index = self.combo_product.currentIndex()
        prod_name = self.combo_product.itemText(prod_index)
        
        # Делаем название безопасным для файловой системы
        safe_prod_name = (
            prod_name
            .replace('"', "")
            .replace("'", "")
            .replace("/", "_")
            .replace("\\", "_")
        )
        default_name = f"Расчёт материала для {safe_prod_name}.pdf"

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт",
            default_name,
            "PDF файлы (*.pdf)",
        )

        # Если пользователь отменил диалог сохранения просто выходим
        if not filename:
            return

        try:
            generate_material_calc_report(
                self.session,
                product_type_id,
                material_type_id,
                quantity,
                param1,
                param2,
                filename,
            )
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сформировать PDF-отчёт:\n{e}", QMessageBox.StandardButton.Ok,)
            return

        QMessageBox.information(self, "Готово", "PDF-отчёт по расчёту материала успешно сформирован.", QMessageBox.StandardButton.Ok,)
