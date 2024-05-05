import datetime
import os
import subprocess
from multiprocessing.pool import ThreadPool
from threading import Thread


def work(sample:str, log_folder: str, index_depth:int, log_level:str, ignore_http_errors_in_log:bool) -> None:
    command = f'scrapy crawl random_indexer -a max_date_depth={index_depth} -a words="{sample}" -L {log_level} --logfile "{log_folder+"/"+sample.strip()}.log"'
    if ignore_http_errors_in_log:
        command += " -a ignore_errors=True"
        # command += " -s SPIDER_MIDDLEWARES='telegraph.middlewares.MyHttpErrorMiddleware:50'"
    my_tool_subprocess = subprocess.Popen(command, shell=True, cwd="/app/scrapy_spiders")  # noqa: S602
    my_tool_subprocess.wait()




class SpiderRunner(Thread):
    def __init__(self, wordlist_file: str, cores_to_use: int, index_depth: int, log_level: str, ignore_http_errors_in_log:bool) -> None:
        super().__init__()
        self.wordlist_file = wordlist_file
        self.cores_to_use = cores_to_use
        self.index_depth = index_depth
        self.log_level = log_level
        self.ignore_http_errors_in_log = ignore_http_errors_in_log

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
        tp = ThreadPool(self.cores_to_use)
        for word in words:
            tp.apply_async(work, (word,log_folder, self.index_depth, self.log_level, self.ignore_http_errors_in_log))

        tp.close()
        tp.join()

