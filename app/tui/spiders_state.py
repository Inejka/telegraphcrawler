from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widget import Widget
from textual.widgets import Label, ProgressBar


class SpiderState(Widget):
    DEFAULT_CSS = """
    SpiderState{
        width: 1fr;
        border: solid green;
        height: 40%;
        margin-top: 5;
    }
    SpiderState>Label{
        text-align: center;
        width: 100%;
    }
    """

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def compose(self) -> ComposeResult:
        yield Label("Alive spiders")
        with VerticalScroll(id="spider_state_vertical_scroll"):
            pass


class SpiderItem(Widget):
    DEFAULT_CSS = """
    SpiderItem{
        layout: horizontal;
        width: 1fr;
        border: solid green;
        max-height: 3;
    }
    #file{
        margin-left: 2;
        width: 80;
    }
    #total_work{
        margin-left: 2;
        width: 5;
    }
    #done_work{
        margin-left: 2;
        width: 5;
    }
    SpiderItem>ProgressBar{
        margin-left: 2;
    }
    """

    def __init__(
        self,
        working_dict: str,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)
        self.working_dict = working_dict
        self.progress_bar = ProgressBar()
        self.done_work = Label("0", id="done_work")
        self.total_work = Label("", id="total_work")

    def compose(self) -> ComposeResult:
        yield Label(self.working_dict, id="file")
        yield Label("Done: ")
        yield self.done_work
        yield Label("Total: ")
        yield self.total_work
        yield self.progress_bar

    def set_total_work(self, value: int) -> None:
        self.progress_bar.update(total=value)
        self.total_work.update(str(value))

    def set_done_work(self, value: int) -> None:
        self.progress_bar.update(progress=value)
        self.done_work.update(str(value))
