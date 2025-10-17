from PyQt6 import QtWidgets, QtGui
import sys

from .ui.main_window import MainWindow


def main():
	app = QtWidgets.QApplication(sys.argv)

	# Splash com logo (não bloqueante)
	try:
		from .ui.start_window import load_app_icon
		app.setWindowIcon(load_app_icon())
		pix = app.windowIcon().pixmap(256, 256)
		splash = QtWidgets.QSplashScreen(pix)
		splash.show()
		QtWidgets.QApplication.processEvents()
	except Exception:
		splash = None

	# Tela inicial (seleção de fluxo)
	from .ui.start_window import StartDialog
	dlg = StartDialog()
	result = dlg.exec()
	if result != QtWidgets.QDialog.DialogCode.Accepted:
		# usuário cancelou
		if splash is not None:
			splash.finish(None)
		return

	if dlg.start_ficha:
		# Abrir gerador de fichas técnicas
		from .ui.main_window import MainWindow
		window = MainWindow()
		window.show()
		if splash is not None:
			splash.finish(window)
	elif dlg.start_orcamento:
		# Abrir simulador de orçamentos
		from .ui.simulator_window import SimulatorWindow
		window = SimulatorWindow()
		window.show()
		if splash is not None:
			splash.finish(window)
	elif dlg.start_admin:
		# Abrir painel de administração
		from .ui.admin_window import AdminWindow
		window = AdminWindow()
		window.show()
		if splash is not None:
			splash.finish(window)
	else:
		# Nenhuma opção selecionada
		if splash is not None:
			splash.finish(None)
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
