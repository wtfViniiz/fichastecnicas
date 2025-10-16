from PyQt6 import QtWidgets, QtGui, QtCore
from datetime import date
import os

from ..core.models import OrderInfo, SizeTable, Gender, Size, Sleeve
from ..core.utils import add_business_days_including_saturday
from ..pdf.generator import TechSheetPDF, PDFOptions


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Fichas Técnicas - Manauara Design")
		self.resize(1100, 780)
		self._init_ui()

	def _init_ui(self):
		container = QtWidgets.QWidget()
		layout = QtWidgets.QVBoxLayout(container)

		form = QtWidgets.QGridLayout()
		row = 0

		# Cliente
		form.addWidget(QtWidgets.QLabel("Cliente"), row, 0)
		self.client_input = QtWidgets.QLineEdit()
		self.client_input.setPlaceholderText("Nome")
		form.addWidget(self.client_input, row, 1, 1, 3)

		# Datas
		row += 1
		form.addWidget(QtWidgets.QLabel("Data Encomenda"), row, 0)
		self.order_date = QtWidgets.QDateEdit(QtCore.QDate.currentDate())
		self.order_date.setCalendarPopup(True)
		form.addWidget(self.order_date, row, 1)

		form.addWidget(QtWidgets.QLabel("Data Entrega (+7 úteis incl. sáb.)"), row, 2)
		self.delivery_date = QtWidgets.QDateEdit()
		self.delivery_date.setCalendarPopup(True)
		self._update_delivery()
		form.addWidget(self.delivery_date, row, 3)
		self.order_date.dateChanged.connect(lambda *_: self._update_delivery())

		# Opções
		row += 1
		form.addWidget(QtWidgets.QLabel("Tecido"), row, 0)
		self.fabric = QtWidgets.QComboBox()
		self.fabric.addItems(["helanca", "dryfit", "dryfit_colmeia"])
		form.addWidget(self.fabric, row, 1)

		form.addWidget(QtWidgets.QLabel("Gola"), row, 2)
		self.neck = QtWidgets.QComboBox()
		self.neck.addItems(["careca", "gola_v", "gola_transpassada"])
		form.addWidget(self.neck, row, 3)

		row += 1
		self.is_set = QtWidgets.QCheckBox("Conjunto")
		form.addWidget(self.is_set, row, 0)

		# Imagens
		row += 1
		img_group = QtWidgets.QGroupBox("Imagens")
		img_layout = QtWidgets.QHBoxLayout(img_group)
		
		# Frente
		front_group = QtWidgets.QVBoxLayout()
		front_group.addWidget(QtWidgets.QLabel("Frente"))
		self.front_path = QtWidgets.QLineEdit()
		self.front_path.setPlaceholderText("Caminho da imagem...")
		btn_front = QtWidgets.QPushButton("Selecionar...")
		btn_front.clicked.connect(lambda: self._pick_image(self.front_path, self.front_preview))
		front_group.addWidget(self.front_path)
		front_group.addWidget(btn_front)
		self.front_preview = QtWidgets.QLabel()
		self.front_preview.setFixedSize(120, 100)
		self.front_preview.setStyleSheet("border: 1px solid gray; background-color: white;")
		self.front_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.front_preview.setText("Sem imagem")
		front_group.addWidget(self.front_preview)
		
		# Costa
		back_group = QtWidgets.QVBoxLayout()
		back_group.addWidget(QtWidgets.QLabel("Costa"))
		self.back_path = QtWidgets.QLineEdit()
		self.back_path.setPlaceholderText("Caminho da imagem...")
		btn_back = QtWidgets.QPushButton("Selecionar...")
		btn_back.clicked.connect(lambda: self._pick_image(self.back_path, self.back_preview))
		back_group.addWidget(self.back_path)
		back_group.addWidget(btn_back)
		self.back_preview = QtWidgets.QLabel()
		self.back_preview.setFixedSize(120, 100)
		self.back_preview.setStyleSheet("border: 1px solid gray; background-color: white;")
		self.back_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.back_preview.setText("Sem imagem")
		back_group.addWidget(self.back_preview)
		
		img_layout.addLayout(front_group)
		img_layout.addLayout(back_group)
		form.addWidget(img_group, row, 0, 1, 4)

		# Descrição
		row += 1
		form.addWidget(QtWidgets.QLabel("Descrição"), row, 0, QtCore.Qt.AlignmentFlag.AlignTop)
		self.description = QtWidgets.QPlainTextEdit()
		self.description.setPlaceholderText("--//--")
		self.description.setFixedHeight(90)
		form.addWidget(self.description, row, 1, 1, 3)

		# Tabela de tamanhos
		row += 1
		self.table_inputs: dict[tuple[str, str, str], QtWidgets.QSpinBox] = {}
		table_group = QtWidgets.QGroupBox("Tabela de Tamanhos")
		grid = QtWidgets.QGridLayout(table_group)
		genders = ["feminino", "masculino", "infantil"]
		sizes = ["PP", "P", "M", "G", "GG", "XG"]
		sleeves = ["curta", "longa"]
		row_g = 0
		for gi, gender in enumerate(genders):
			grid.addWidget(QtWidgets.QLabel(gender.upper()), row_g, gi * 3, 1, 3)
			grid.addWidget(QtWidgets.QLabel(""), row_g + 1, gi * 3)  # coluna tamanhos vazia
			grid.addWidget(QtWidgets.QLabel("CURTA"), row_g + 1, gi * 3 + 1)
			grid.addWidget(QtWidgets.QLabel("LONGA"), row_g + 1, gi * 3 + 2)
			for si, size in enumerate(sizes):
				grid.addWidget(QtWidgets.QLabel(size), row_g + 2 + si, gi * 3)
				for sj, sleeve in enumerate(sleeves):
					spin = QtWidgets.QSpinBox()
					spin.setRange(0, 999)
					grid.addWidget(spin, row_g + 2 + si, gi * 3 + 1 + sj)
					self.table_inputs[(gender, size, sleeve)] = spin
		layout.addLayout(form)
		layout.addWidget(table_group)

		# Ações
		actions = QtWidgets.QHBoxLayout()
		self.btn_new = QtWidgets.QPushButton("Nova ficha")
		self.btn_new.clicked.connect(self._on_reset)
		self.btn_generate = QtWidgets.QPushButton("Gerar PDF")
		self.btn_generate.clicked.connect(self._on_generate)
		actions.addStretch(1)
		actions.addWidget(self.btn_new)
		actions.addWidget(self.btn_generate)
		layout.addLayout(actions)

		self.setCentralWidget(container)

	def _pick_image(self, target: QtWidgets.QLineEdit, preview: QtWidgets.QLabel):
		file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecionar imagem", os.getcwd(), "Imagens (*.png *.jpg *.jpeg)")
		if file:
			target.setText(file)
			self._update_preview(file, preview)

	def _update_preview(self, image_path: str, preview: QtWidgets.QLabel):
		try:
			pixmap = QtGui.QPixmap(image_path)
			if not pixmap.isNull():
				# Redimensionar mantendo proporção
				scaled_pixmap = pixmap.scaled(120, 100, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
				preview.setPixmap(scaled_pixmap)
			else:
				preview.setText("Imagem inválida")
		except Exception:
			preview.setText("Erro ao carregar")

	def _update_delivery(self):
		od = self.order_date.date().toPyDate()
		deliv = add_business_days_including_saturday(od, 7)
		self.delivery_date.setDate(QtCore.QDate(deliv.year, deliv.month, deliv.day))

	def _collect_size_table(self) -> SizeTable:
		st = SizeTable()
		for (gender, size, sleeve), widget in self.table_inputs.items():
			val = widget.value()
			if val:
				st.set_quantity(gender, size, sleeve, val)  # type: ignore
		return st

	def _on_reset(self):
		self.client_input.clear()
		self.order_date.setDate(QtCore.QDate.currentDate())
		self._update_delivery()
		self.fabric.setCurrentIndex(0)
		self.neck.setCurrentIndex(0)
		self.is_set.setChecked(False)
		self.front_path.clear()
		self.back_path.clear()
		self.front_preview.clear()
		self.front_preview.setText("Sem imagem")
		self.back_preview.clear()
		self.back_preview.setText("Sem imagem")
		self.description.clear()
		for widget in self.table_inputs.values():
			widget.setValue(0)

	def _on_generate(self):
		client = self.client_input.text().strip()
		if not client:
			QtWidgets.QMessageBox.warning(self, "Campo obrigatório", "Informe o nome do cliente.")
			self.client_input.setFocus()
			return

		info = OrderInfo(
			client_name=client,
			order_date=self.order_date.date().toPyDate(),
			delivery_date=self.delivery_date.date().toPyDate(),
			description=self.description.toPlainText().strip(),
			fabric=self.fabric.currentText(),  # type: ignore
			neck=self.neck.currentText(),  # type: ignore
			is_set=self.is_set.isChecked(),
			front_image_path=self.front_path.text().strip() or None,
			back_image_path=self.back_path.text().strip() or None,
		)
		st = self._collect_size_table()

		default_name = f"Ficha_{info.client_name}_{date.today().isoformat()}.pdf"
		path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Salvar PDF", default_name, "PDF (*.pdf)")
		if not path:
			return

		try:
			pdf = TechSheetPDF(logos_dir="public")
			pdf.build(info, st, PDFOptions(output_path=path))
			QtWidgets.QMessageBox.information(self, "Sucesso", "PDF gerado com sucesso.")
		except Exception as e:
			QtWidgets.QMessageBox.critical(self, "Erro ao gerar PDF", str(e))
