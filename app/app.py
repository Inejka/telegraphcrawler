import time

from database.db import Base, get_engine
from tui.main_app import MainApp

if __name__ == "__main__":
    # init db
    db_init = False
    while not db_init:
        try:
            print("Waiting for db")
            engine = get_engine()
            Base.metadata.create_all(engine)
            db_init = True
        except Exception:
            time.sleep(0.1)

    MainApp().run()
