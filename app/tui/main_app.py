from typing import ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Label, OptionList
from textual.widgets.option_list import Option
from tui.spiders_state import SpiderState
from tui.start_crawler import CrawlerStarter


class MainApp(App[None]):
    CSS_PATH = "main_app.tcss"
    TITLE = "Crawlers controller and stats app"
    SCREENS: ClassVar[dict] = {"CrawlerStarter": CrawlerStarter}
    BINDINGS: ClassVar[list] = [("q", "quit", "Exit app")]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Label("Options")
        self.options_list = OptionList(
            Option("Start crawler", id = "CrawlerStarter"), id = "main_option_list"
        )
        yield self.options_list
        yield SpiderState(id="SpiderState")
        yield Footer()

    @on(OptionList.OptionSelected)
    def on_options_list_select(self)->None:
        if self.options_list.get_option_at_index(self.options_list.highlighted).id in MainApp.SCREENS:
            self.push_screen(MainApp.SCREENS[self.options_list.get_option_at_index(self.options_list.highlighted).id]())
