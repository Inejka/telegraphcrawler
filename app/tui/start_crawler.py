import glob
import os
from typing import ClassVar

from scrapy_spiders.multiprocess_runner import SpiderRunner
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Select, Static
from utils import DICT_FOLDER_IS_NOT_FOUND, PATH_DICT, WORDLISTS_IS_NOT_FOUND


class ErrorScreen(Screen):
    CSS_PATH = "message.tcss"
    BINDINGS: ClassVar[list] = [("escape", "app.pop_screen", "Pop screen")]

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        text: str | None = None,
    ) -> None:
        super().__init__(name, id, classes)
        self.text = text

    def compose(self) -> ComposeResult:
        yield Static(self.text, id="message")
        yield Static("Press ESC key to continue", id="any-key")


class CrawlerStarter(Screen):
    CSS_PATH = "crawler_starter.tcss"
    BINDINGS: ClassVar[list] = [("escape", "app.pop_screen", "Pop screen")]
    BUTTON_START_ID = "start"
    BUTTON_CANCEL_ID = "cancel"

    def compose(self) -> ComposeResult:
        self.variants = Select([("", "")])
        yield self.variants
        with Horizontal(classes="buttons_container"):
            yield Button("Start", id=CrawlerStarter.BUTTON_START_ID, classes="crawl_button")
            yield Button("Cancel", id=CrawlerStarter.BUTTON_CANCEL_ID, classes="crawl_button")

    def on_mount(self) -> None:
        if not self.is_dict_folder_alive():
            self.app.pop_screen()
            self.app.push_screen(ErrorScreen(text=DICT_FOLDER_IS_NOT_FOUND))
        wordlists = self.get_wordlists()
        if len(wordlists) == 0:
            self.app.pop_screen()
            self.app.push_screen(ErrorScreen(text=WORDLISTS_IS_NOT_FOUND))
        self.variants.clear()
        self.variants.set_options((wordlists[i], wordlists[i]) for i in range(len(wordlists)))

    def is_dict_folder_alive(self) -> bool:
        return os.path.exists(PATH_DICT)

    def get_wordlists(self) -> list[str]:
        return glob.glob(PATH_DICT + "/*.txt")

    @on(Button.Pressed)
    def handle_button_pressed(self, pressed: Button.Pressed) -> None:
        if pressed.button.id == CrawlerStarter.BUTTON_CANCEL_ID:
            self.app.pop_screen()
        if pressed.button.id == CrawlerStarter.BUTTON_START_ID:
            if self.variants.is_blank():
                pass
            else:
                self.app.pop_screen()
                SpiderRunner(self.variants.value).start()
