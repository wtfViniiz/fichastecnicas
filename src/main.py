from PyQt6 import QtWidgets
import sys

from .ui.main_window import MainWindow


def main():
	app = QtWidgets.QApplication(sys.argv)
	window = MainWindow()
	window.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
