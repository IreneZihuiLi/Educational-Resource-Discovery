from threading import Lock, Thread

from pipeline.downloader.download_manager import download_online_resource

class DownloadQueue():
    def __init__(self, queue: list) -> None:
        self.queue = queue
        self.lock = Lock()

    def pop(self) -> str:
        with self.lock:
            if len(self.queue) > 0:
                return self.queue.pop()
            else:
                return None

class Downloader(Thread):
    def __init__(self, queue: DownloadQueue, destination_dir: str) -> None:
        super().__init__()
        self.job_queue = queue
        self.destination_dir = destination_dir

    def run(self):
        while True:
            url = self.job_queue.pop()
            if url is None:
                break
            try:
                download_online_resource(url, True, self.destination_dir)
            except:
                pass

def download_batch_multithreaded(urls: list, destination_dir: str, jobs: int) -> None:
    queue = DownloadQueue(urls)
    downloaders = [Downloader(queue, destination_dir) for _ in range(jobs)]

    for downloader in downloaders:
        downloader.start()
    
    for downloader in downloaders:
        downloader.join()