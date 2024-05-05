import glob
import os
from typing import ClassVar

from rich.text import Text
from scrapy_spiders.multiprocess_runner import SpiderRunner
from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.screen import Screen
from textual.widgets import Button, Checkbox, Footer, Input, Label, Select, Static
from utils import (
    CORES_ARE_EMPTY,
    DICT_FOLDER_IS_NOT_FOUND,
    INDEX_DEPTH_IS_EMPTY,
    PATH_DICT,
    WORDLISTS_IS_EMPTY,
    WORDLISTS_IS_NOT_FOUND,
    get_init_config,
)


class CustomCheckbox(Checkbox):
    def render(self) -> Text:
        temp = super().render()
        temp_str = temp.plain
        temp.plain = temp_str.replace("X", "T") if self.value else temp_str.replace("X", "F")
        return temp


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
    BINDINGS: ClassVar[list] = [("escape", "app.pop_screen", "Pop screen"), ("S", "start_crawler", "Start crawler")]
    BUTTON_START_ID = "start"
    BUTTON_CANCEL_ID = "cancel"

    def compose(self) -> ComposeResult:
        configs = get_init_config()
        self.variants = Select([("", "")])
        yield self.variants
        yield Label("Cores to use")
        self.cores_to_use = Input(
            placeholder="Cores to use", type="integer", restrict=r"^[1-9]\d*$", value=str(configs["cores_to_use"])
        )
        yield self.cores_to_use
        yield Label("Indexing depth")
        self.indexing_depth = Input(
            placeholder="Indexing depth", type="integer", restrict=r"^[1-9]\d*$", value=str(configs["indexing_depth"])
        )
        yield self.indexing_depth
        yield Label("Log Level")
        with Horizontal():
            self.log_level_select = Select(
                [
                    ("Critical", "CRITICAL"),
                    ("Error", "ERROR"),
                    ("Warning", "WARNING"),
                    ("Info", "INFO"),
                    ("Debug", "DEBUG"),
                ],
                value=str(configs["log_level_select"]),
                allow_blank=False,
                id="with_border_1",
            )
            yield self.log_level_select
            self.ignore_http_errors_in_log = CustomCheckbox(
                "Do not spam non 200 http codes in log", configs["ignore_http_errors_in_log"], id="with_border_2"
            )
            yield self.ignore_http_errors_in_log
        with Horizontal(classes="buttons_container"):
            yield Button("Start", id=CrawlerStarter.BUTTON_START_ID, classes="crawl_button")
            yield Button("Cancel", id=CrawlerStarter.BUTTON_CANCEL_ID, classes="crawl_button")
        yield Footer()

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
        self.variants.value = wordlists[0]

    def is_dict_folder_alive(self) -> bool:
        return os.path.exists(PATH_DICT)

    def get_wordlists(self) -> list[str]:
        return glob.glob(PATH_DICT + "/*.txt")

    @on(Button.Pressed)
    def handle_button_pressed(self, pressed: Button.Pressed) -> None:
        if pressed.button.id == CrawlerStarter.BUTTON_CANCEL_ID:
            self.app.pop_screen()
        if pressed.button.id == CrawlerStarter.BUTTON_START_ID:
            self.action_start_crawler()

    def action_start_crawler(self) -> None:
        if self.variants.is_blank():
            self.app.push_screen(ErrorScreen(text=WORDLISTS_IS_EMPTY))
            return
        if not self.cores_to_use.is_valid:
            self.app.push_screen(ErrorScreen(text=CORES_ARE_EMPTY))
            return
        if not self.indexing_depth.is_valid:
            self.app.push_screen(ErrorScreen(text=INDEX_DEPTH_IS_EMPTY))
            return
        self.app.pop_screen()
        SpiderRunner(
            self.variants.value,
            int(self.cores_to_use.value),
            int(self.indexing_depth.value),
            self.log_level_select.value,
            self.ignore_http_errors_in_log.value,
        ).start()
