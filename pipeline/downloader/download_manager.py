import os
import logging
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_online_resource(uri: str, force_download: bool, destination_dir: str) -> str:
    if force_download or not os.path.exists(uri):
        fname = uri[uri.rfind('/') + 1:]
        query_param_idx = fname.rfind('?')
        if query_param_idx != -1:
            fname = fname[:query_param_idx]

        http = urllib3.PoolManager()
        try:
            r = http.request('GET', uri, preload_content=False)
        except Exception as e:
            #logging.error('Skipping faulty URL: ' + uri)
            #logging.error(str(e))
            return None
        fname_end = fname.rfind('.')
        extension = '.html'

        if fname_end != -1:
            fname, extension = fname[:fname_end], fname[fname_end:]

        id = -1
        local_path = ''
        while True:
            if id >= 0:
                local_path = os.path.join(destination_dir, fname + str(id) + extension)
            else:
                local_path = os.path.join(destination_dir, fname + extension)

            if not os.path.exists(local_path):
                break
            id += 1

        try:
            with open(local_path, 'wb') as out:
                out.write(r.read())
        except Exception as e:
            logging.error(f'Error when saving online resource to {local_path}: ' + str(e))
            return None

        r.release_conn()
        logging.info(f'Downloading resource {uri} -> {local_path}')

    return local_path


class DownloadManager():
    TMP_DIR = 'pipeline/tmp_downloads'

    def __init__(self, cleanup: bool = True) -> None:
        self.downloaded_files = list()
        self.cleanup = cleanup

    def __enter__(self):
        return self

    def __exit__(self ,type, value, traceback):
        if self.cleanup:
            self.clean_downloaded_files()

    def download_online_resource(self, uri: str, force_download: bool) -> str:
        local_path = download_online_resource(uri, force_download, self.TMP_DIR)
        if local_path is not None:
            self.downloaded_files.append(local_path)
        return local_path

    def download_batch(self, urls: list, force_download: bool = False) -> list:
        local_dirs = list()
        for url in urls:
            local_dirs.append(self.download_online_resource(url, force_download))

        return local_dirs

    def clean_downloaded_files(self) -> None:
        for downloaded_file in set(self.downloaded_files):
            logging.info('Deleting downloaded resource: ' + str(downloaded_file))
            os.remove(downloaded_file)
