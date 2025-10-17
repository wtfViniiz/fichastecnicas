from PyQt6 import QtWidgets, QtGui, QtCore
from datetime import date
import os

from ..core.models import OrderInfo, SizeTable, Gender, Size, Sleeve
from ..core.utils import add_business_days_including_saturday
from ..pdf.generator import TechSheetPDF, PDFOptions
from .theme import ThemeManager


class MainWindow(QtWidgets.QMainWindow):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Fichas Técnicas - Manauara Design")
		self.resize(1100, 780)
		self._init_ui()
		self._init_menu()

	def _init_ui(self):
		container = QtWidgets.QWidget()
		layout = QtWidgets.QVBoxLayout(container)

		# Toolbar com botão Home
		tb = QtWidgets.QToolBar("Principal", self)
		tb.setMovable(False)
		a_home = QtGui.QAction("🏠 Home", self)
		a_home.triggered.connect(self._go_back_to_start)
		tb.addAction(a_home)
		self.addToolBar(QtCore.Qt.ToolBarArea.TopToolBarArea, tb)

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
		btn_front_paste = QtWidgets.QPushButton("Colar da área de transferência")
		btn_front_paste.clicked.connect(lambda: self._paste_image(self.front_path, self.front_preview, prefix="front"))
		btn_front_clear = QtWidgets.QPushButton("Excluir imagem")
		btn_front_clear.clicked.connect(lambda: self._clear_image(self.front_path, self.front_preview))
		front_group.addWidget(self.front_path)
		front_group.addWidget(btn_front)
		front_group.addWidget(btn_front_paste)
		front_group.addWidget(btn_front_clear)
		self.front_preview = QtWidgets.QLabel()
		self.front_preview.setFixedSize(120, 100)
		self.front_preview.setStyleSheet("border: 1px solid gray; background-color: white;")
		self.front_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.front_preview.setText("Sem imagem")
		self.front_preview.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
		action_paste_front = QtGui.QAction("Colar imagem", self)
		action_paste_front.triggered.connect(lambda: self._paste_image(self.front_path, self.front_preview, prefix="front"))
		action_clear_front = QtGui.QAction("Excluir imagem", self)
		action_clear_front.triggered.connect(lambda: self._clear_image(self.front_path, self.front_preview))
		self.front_preview.addAction(action_paste_front)
		self.front_preview.addAction(action_clear_front)
		front_group.addWidget(self.front_preview)
		
		# Costa
		back_group = QtWidgets.QVBoxLayout()
		back_group.addWidget(QtWidgets.QLabel("Costa"))
		self.back_path = QtWidgets.QLineEdit()
		self.back_path.setPlaceholderText("Caminho da imagem...")
		btn_back = QtWidgets.QPushButton("Selecionar...")
		btn_back.clicked.connect(lambda: self._pick_image(self.back_path, self.back_preview))
		btn_back_paste = QtWidgets.QPushButton("Colar da área de transferência")
		btn_back_paste.clicked.connect(lambda: self._paste_image(self.back_path, self.back_preview, prefix="back"))
		btn_back_clear = QtWidgets.QPushButton("Excluir imagem")
		btn_back_clear.clicked.connect(lambda: self._clear_image(self.back_path, self.back_preview))
		back_group.addWidget(self.back_path)
		back_group.addWidget(btn_back)
		back_group.addWidget(btn_back_paste)
		back_group.addWidget(btn_back_clear)
		self.back_preview = QtWidgets.QLabel()
		self.back_preview.setFixedSize(120, 100)
		self.back_preview.setStyleSheet("border: 1px solid gray; background-color: white;")
		self.back_preview.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.back_preview.setText("Sem imagem")
		self.back_preview.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.ActionsContextMenu)
		action_paste_back = QtGui.QAction("Colar imagem", self)
		action_paste_back.triggered.connect(lambda: self._paste_image(self.back_path, self.back_preview, prefix="back"))
		action_clear_back = QtGui.QAction("Excluir imagem", self)
		action_clear_back.triggered.connect(lambda: self._clear_image(self.back_path, self.back_preview))
		self.back_preview.addAction(action_paste_back)
		self.back_preview.addAction(action_clear_back)
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
		self.infantil_sizes: list[str] = [str(n) for n in range(2, 18, 2)]  # padrão 2..16
		table_group = QtWidgets.QGroupBox("Tabela de Tamanhos")
		grid = QtWidgets.QGridLayout(table_group)
		genders = ["feminino", "masculino", "infantil"]
		sizes_by_gender: dict[str, list[str]] = {
			"feminino": ["PP", "P", "M", "G", "GG", "XG", "XGG", "XG3"],
			"masculino": ["PP", "P", "M", "G", "GG", "XG", "XGG", "XG3"],
			"infantil": self.infantil_sizes,
		}
		sleeves = ["curta", "longa"]
		row_g = 0
		self._infantil_size_labels: list[QtWidgets.QLabel] = []
		self._infantil_row_spins: list[dict[str, QtWidgets.QSpinBox]] = []
		for gi, gender in enumerate(genders):
			grid.addWidget(QtWidgets.QLabel(gender.upper()), row_g, gi * 3, 1, 3)
			grid.addWidget(QtWidgets.QLabel(""), row_g + 1, gi * 3)  # coluna tamanhos vazia
			grid.addWidget(QtWidgets.QLabel("CURTA"), row_g + 1, gi * 3 + 1)
			grid.addWidget(QtWidgets.QLabel("LONGA"), row_g + 1, gi * 3 + 2)
			for si, size in enumerate(sizes_by_gender[gender]):
				lbl = QtWidgets.QLabel(size)
				grid.addWidget(lbl, row_g + 2 + si, gi * 3)
				if gender == "infantil":
					self._infantil_size_labels.append(lbl)
				row_spins: dict[str, QtWidgets.QSpinBox] = {}
				for sj, sleeve in enumerate(sleeves):
					spin = QtWidgets.QSpinBox()
					spin.setRange(0, 999)
					grid.addWidget(spin, row_g + 2 + si, gi * 3 + 1 + sj)
					self.table_inputs[(gender, size, sleeve)] = spin
					if gender == "infantil":
						row_spins[sleeve] = spin
				if gender == "infantil":
					self._infantil_row_spins.append(row_spins)
		layout.addLayout(form)
		layout.addWidget(table_group)

		# Controles auxiliares para infantil
		aux = QtWidgets.QHBoxLayout()
		self.btn_select_infantil = QtWidgets.QPushButton("Selecionar idades infantis…")
		self.btn_select_infantil.clicked.connect(self._select_infantil_ages)
		aux.addStretch(1)
		aux.addWidget(self.btn_select_infantil)
		layout.addLayout(aux)

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

		# Ícone da aplicação (logo)
		try:
			from .start_window import load_app_icon
			app_icon = load_app_icon()
			if not app_icon.isNull():
				self.setWindowIcon(app_icon)
		except Exception:
			pass

	def _init_menu(self):
		bar = self.menuBar()
		app_menu = bar.addMenu("Aplicativo")

		action_toggle_theme = QtGui.QAction("Alternar tema (Claro/Escuro)", self)
		action_toggle_theme.triggered.connect(self._toggle_theme)
		app_menu.addAction(action_toggle_theme)

		action_back = QtGui.QAction("Voltar ao Início", self)
		action_back.triggered.connect(self._go_back_to_start)
		app_menu.addAction(action_back)

	def _toggle_theme(self):
		app = QtWidgets.QApplication.instance()
		if app is not None:
			ThemeManager.toggle_theme(app)

	def _go_back_to_start(self):
		from .start_window import StartDialog
		dlg = StartDialog(None)
		self.hide()
		result = dlg.exec()
		if result == QtWidgets.QDialog.DialogCode.Accepted:
			if dlg.start_ficha:
				from .main_window import MainWindow
				win = MainWindow()
				win.show()
				self._next_window = win
			elif dlg.start_orcamento:
				from .simulator_window import SimulatorWindow
				win = SimulatorWindow()
				win.show()
				self._next_window = win
			elif dlg.start_admin:
				from .admin_window import AdminWindow
				win = AdminWindow()
				win.show()
				self._next_window = win
			self.close()
		else:
			# Usuário cancelou: manter janela atual
			self.show()

	def _pick_image(self, target: QtWidgets.QLineEdit, preview: QtWidgets.QLabel):
		settings = QtCore.QSettings("ManauaraDesign", "BudgetApp")
		start_dir = settings.value("lastDir", os.getcwd())
		file, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Selecionar imagem", start_dir, "Imagens (*.png *.jpg *.jpeg)")
		if file:
			target.setText(file)
			self._update_preview(file, preview)
			settings.setValue("lastDir", os.path.dirname(file))

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

	def _paste_image(self, target: QtWidgets.QLineEdit, preview: QtWidgets.QLabel, prefix: str = "img"):
		cb = QtWidgets.QApplication.clipboard()
		img = cb.image()
		if img.isNull():
			# tenta ler de QPixmap (copiado do explorador)
			pix = cb.pixmap()
			if pix.isNull():
				QtWidgets.QMessageBox.information(self, "Área de transferência", "Nenhuma imagem encontrada para colar.")
				return
			else:
				img = pix.toImage()
		cache_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.CacheLocation)
		if not cache_dir:
			cache_dir = os.path.join(os.getcwd(), ".cache")
		os.makedirs(cache_dir, exist_ok=True)
		filename = f"{prefix}_{QtCore.QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss_zzz')}.png"
		path = os.path.join(cache_dir, filename)
		img.save(path, "PNG")
		target.setText(path)
		self._update_preview(path, preview)

	def _clear_image(self, target: QtWidgets.QLineEdit, preview: QtWidgets.QLabel):
		target.clear()
		preview.clear()
		preview.setText("Sem imagem")

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
		# Atualiza ordem/labels infantis no info
		info.infantil_selected_sizes = self.infantil_sizes.copy()

		default_name = f"Ficha_{info.client_name}_{date.today().isoformat()}.pdf"
		settings = QtCore.QSettings("ManauaraDesign", "BudgetApp")
		start_dir = settings.value("lastDir", os.getcwd())
		initial_path = os.path.join(start_dir, default_name)
		path, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Salvar PDF", initial_path, "PDF (*.pdf)")
		if not path:
			return
		settings.setValue("lastDir", os.path.dirname(path))

		try:
			pdf = TechSheetPDF(logos_dir="public")
			pdf.build(info, st, PDFOptions(output_path=path))
			QtWidgets.QMessageBox.information(self, "Sucesso", "PDF gerado com sucesso.")
		except Exception as e:
			QtWidgets.QMessageBox.critical(self, "Erro ao gerar PDF", str(e))

	def _select_infantil_ages(self):
		# Diálogo simples com checkboxes para 2..16, selecionar até 8
		dlg = QtWidgets.QDialog(self)
		dlg.setWindowTitle("Selecionar idades infantis")
		layout = QtWidgets.QVBoxLayout(dlg)
		info_lbl = QtWidgets.QLabel("Selecione até 8 idades (2 a 16, de 2 em 2)")
		layout.addWidget(info_lbl)
		scroll = QtWidgets.QScrollArea()
		scroll.setWidgetResizable(True)
		inner = QtWidgets.QWidget()
		inner_layout = QtWidgets.QVBoxLayout(inner)
		checks: list[QtWidgets.QCheckBox] = []
		for n in range(2, 18, 2):
			cb = QtWidgets.QCheckBox(str(n))
			cb.setChecked(str(n) in set(self.infantil_sizes))
			checks.append(cb)
			inner_layout.addWidget(cb)
		inner_layout.addStretch(1)
		scroll.setWidget(inner)
		layout.addWidget(scroll)
		btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
		layout.addWidget(btns)
		btns.accepted.connect(dlg.accept)
		btns.rejected.connect(dlg.reject)
		if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
			selected = [cb.text() for cb in checks if cb.isChecked()]
			# limita a 8 itens; se mais, pega os 8 primeiros em ordem numérica
			selected_sorted = sorted(selected, key=lambda s: int(s))[:8]
			# se menos de 8, completa com vazio? Manteremos menos linhas usadas; labels vazias
			self.infantil_sizes = selected_sorted + []
			# Atualiza labels no grid
			for idx, lbl in enumerate(self._infantil_size_labels):
				text = self.infantil_sizes[idx] if idx < len(self.infantil_sizes) else ""
				lbl.setText(text)
			# Recria o mapeamento de entradas infantis para refletir novos rótulos por linha
			# Mantém as entradas de feminino/masculino
			new_map: dict[tuple[str, str, str], QtWidgets.QSpinBox] = {k: v for k, v in self.table_inputs.items() if k[0] != "infantil"}
			for idx, lbl in enumerate(self._infantil_size_labels):
				label_text = lbl.text()
				if not label_text:
					continue
				row_spins = self._infantil_row_spins[idx] if idx < len(self._infantil_row_spins) else {}
				for sleeve, spin in row_spins.items():
					new_map[("infantil", label_text, sleeve)] = spin
			self.table_inputs = new_map
