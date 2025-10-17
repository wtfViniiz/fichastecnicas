from PyQt6 import QtWidgets, QtGui, QtCore
import os


def load_app_icon() -> QtGui.QIcon:
	# Prioriza logo_manauara_app.png, fallback para qualquer .png em public
	try:
		public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "public")
		public_dir = os.path.abspath(public_dir)
		candidates = [
			os.path.join(public_dir, "logo_manauara_app.png"),
		]
		if not os.path.exists(candidates[0]):
			# busca qualquer png
			for name in os.listdir(public_dir):
				if name.lower().endswith(".png"):
					candidates.append(os.path.join(public_dir, name))
		for path in candidates:
			if os.path.exists(path):
				icon = QtGui.QIcon(path)
				if not icon.isNull():
					return icon
	except Exception:
		pass
	return QtGui.QIcon()


class StartDialog(QtWidgets.QDialog):
	def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Manauara Design - Início")
		self.resize(420, 260)
		self.start_ficha = False
		self.start_orcamento = False
		self.start_admin = False
		self._init_ui()

	def _init_ui(self) -> None:
		layout = QtWidgets.QVBoxLayout(self)
		logo = QtWidgets.QLabel()
		logo.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		# tenta carregar da pasta public
		icon = load_app_icon()
		pix = icon.pixmap(160, 160)
		if not pix.isNull():
			logo.setPixmap(pix.scaled(160, 160, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
		layout.addWidget(logo)

		btns = QtWidgets.QHBoxLayout()
		btn_orc = QtWidgets.QPushButton("Simular Orçamento")
		btn_ficha = QtWidgets.QPushButton("Gerar Ficha Técnica")
		btn_admin = QtWidgets.QPushButton("⚙️ Administração")
		btn_orc.clicked.connect(self._on_orc)
		btn_ficha.clicked.connect(self._on_ficha)
		btn_admin.clicked.connect(self._on_admin)
		btns.addWidget(btn_orc)
		btns.addWidget(btn_ficha)
		btns.addWidget(btn_admin)
		layout.addLayout(btns)

		close_box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.StandardButton.Close)
		close_box.rejected.connect(self.reject)
		layout.addWidget(close_box)

	def _on_orc(self) -> None:
		# abrir simulador de orçamentos
		self.start_ficha = False
		self.start_orcamento = True
		self.start_admin = False
		self.accept()

	def _on_ficha(self) -> None:
		self.start_ficha = True
		self.start_orcamento = False
		self.start_admin = False
		self.accept()

	def _on_admin(self) -> None:
		self.start_ficha = False
		self.start_orcamento = False
		self.start_admin = True
		self.accept()


