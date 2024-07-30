from database.db import get_engine
from tui.main_app import MainApp

if __name__ == "__main__":
    get_engine()
    MainApp().run()
