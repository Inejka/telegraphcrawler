import datetime
import os
import subprocess
from multiprocessing.pool import ThreadPool
from threading import Thread


def work(sample:str, log_folder: str) -> None:
    command = f'scrapy crawl random_indexer -a max_date_depth=10 -a words="{sample}" -L INFO --logfile "{log_folder+"/"+sample.strip()}.log"'
    my_tool_subprocess = subprocess.Popen(command, shell=True, cwd="/app/scrapy_spiders")  # noqa: S602
    my_tool_subprocess.wait()




class SpiderRunner(Thread):
    def __init__(self, wordlist_file: str) -> None:
        super().__init__()
        self.wordlist_file = wordlist_file

    def run(self) -> None:
        words = []
        with open(self.wordlist_file, encoding="utf-8") as file:
            words = file.readlines()

        if not os.path.exists("/work/run_logs"):
            os.mkdir("/work/run_logs")

        log_folder = (
            "/work/run_logs/"
            + self.wordlist_file[self.wordlist_file.rfind("/") + 1 :]
            + "_"
            + datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        )
        os.mkdir(log_folder)

        num = 10
        tp = ThreadPool(num)
        for word in words:
            tp.apply_async(work, (word,log_folder))

        tp.close()
        tp.join()

