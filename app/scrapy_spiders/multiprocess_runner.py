import datetime
import os
import subprocess
from multiprocessing.pool import ThreadPool
from threading import Lock, Thread
from typing import Callable


class SafeCounter:
    def __init__(self) -> None:
        self.__counter = 0
        self.__lock = Lock()
        self.__callbacks = []

    def add_callback(self, func: Callable) -> None:
        self.__callbacks.append(func)

    def remove_callback(self, func: Callable) -> None:
        self.__callbacks.remove(func)

    def inc(self) -> None:
        with self.__lock:
            self.__counter += 1
            for func in self.__callbacks:
                func(self.__counter)

    def get(self) -> int:
        with self.__lock:
            return self.__counter

    def set(self, value: int) -> None:
        with self.__lock:
            self.__counter = value
            for func in self.__callbacks:
                func(self.__counter)


def work(
    sample: str,
    log_folder: str,
    index_depth: int,
    log_level: str,
    ignore_http_errors_in_log: bool,
    ignore_bots_content: bool,
    done_work_counter: SafeCounter,
) -> None:
    command = f'scrapy crawl random_indexer -a max_date_depth={index_depth} -a words="{sample}" -L {log_level} --logfile "{log_folder+"/"+sample.strip()}.log"'
    if ignore_http_errors_in_log:
        command += " -a ignore_errors=True"
    if ignore_bots_content:
        command += " -a ignore_bots=True"
    my_tool_subprocess = subprocess.Popen(command, shell=True, cwd="/app/scrapy_spiders")  # noqa: S602
    my_tool_subprocess.wait()
    done_work_counter.inc()


class SpiderRunner(Thread):
    def __init__(
        self,
        wordlist_file: str,
        cores_to_use: int,
        index_depth: int,
        log_level: str,
        ignore_http_errors_in_log: bool,
        ignore_bots_content: bool,
    ) -> None:
        super().__init__()
        self.wordlist_file = wordlist_file
        self.cores_to_use = cores_to_use
        self.index_depth = index_depth
        self.log_level = log_level
        self.ignore_http_errors_in_log = ignore_http_errors_in_log
        self.ignore_bots_content = ignore_bots_content
        self.total_work = SafeCounter()
        self.current_work = SafeCounter()

    def run(self) -> None:
        words = []
        with open(self.wordlist_file, encoding="utf-8") as file:
            words = file.readlines()
        self.total_work.set(len(words))
        if not os.path.exists("/work/run_logs"):
            os.mkdir("/work/run_logs")

        log_folder = (
            "/work/run_logs/"
            + self.wordlist_file[self.wordlist_file.rfind("/") + 1 :]
            + "_"
            + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        )
        os.mkdir(log_folder)
        tp = ThreadPool(self.cores_to_use)
        for word in words:
            tp.apply_async(
                work,
                (
                    word,
                    log_folder,
                    self.index_depth,
                    self.log_level,
                    self.ignore_http_errors_in_log,
                    self.ignore_bots_content,
                    self.current_work,
                ),
            )

        tp.close()
        tp.join()
