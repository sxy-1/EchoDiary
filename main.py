import sys

from PySide6.QtWidgets import QApplication
from qfluentwidgets import setTheme, Theme

from view.splash_screen import SplashScreen
import resource_rc  # noqa: F401

if __name__ == "__main__":
    setTheme(Theme.DARK)
    app = QApplication(sys.argv)

    splash = SplashScreen()
    splash.show()
    # w.show()
    app.exec()
