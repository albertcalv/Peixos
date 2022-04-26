from config import Config
from PyQt5.QtWidgets import QApplication
import sys
import automatic_tracking as au


if __name__ == "__main__":
    config = Config()
    print(config.get_workspace())
    app = QApplication(sys.argv)
    window = au.Application(app, Config().config)
    window.show()

    sys.exit(app.exec_())
