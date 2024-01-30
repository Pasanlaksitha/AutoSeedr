import logging
from os import makedirs, listdir
from os.path import join, exists
from time import sleep

import requests
from seedr_client import SeedrHandler
from tqdm import tqdm

from auto_seedr.exceptions import FolderNotReadyError


class AutoSeedrClient:
    def __init__(self, email, password, error_log_file='errors.log', log_level=logging.ERROR,
                 torrent_directory: str = 'torrents', download_directory: str = 'downloads', chunk_size: str = '1024'):
        self.error_log_file = error_log_file

        self.torrent_folder = torrent_directory
        self.download_folder = download_directory
        self.chunk_size = chunk_size

        self.__seedr = SeedrHandler(email=email, password=password)

        self._create_directories()

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        file_handler = logging.FileHandler(error_log_file)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def _create_directories(self) -> None:
        """
        Create the required directories for the torrent and download operations.

        :return: None
        """
        for directory in [self.torrent_folder, self.download_folder]:
            if not exists(directory):
                makedirs(directory)

    def is_folder_ok(self, folder_name, folder_id=None, time_out=100):
        """
        Checks if the specified Seedr folder is ready for use.

        :param folder_name: Name of the Seedr folder.
        :param folder_id: ID of the Seedr folder.
        :param time_out: Maximum time (in seconds) to wait for the folder to be ready.
        :return: Folder ID if the folder is ready, otherwise raises an exception.
        """

        def get_folder_id(_folder_name):
            data = self.__seedr.get_drive()
            for _folder in data['folders']:
                if _folder['folder_name'] == _folder_name:
                    return _folder['folder_id']
            return None

        if not folder_id:
            folder_id = get_folder_id(folder_name)

        count = 0
        while count <= time_out:
            try:
                if self.__seedr.get_folder(folder_id):
                    return folder_id
            except:
                # TODO: add specific Exception
                folder_id = get_folder_id(folder_name)
                sleep(1)
                count += 1

        raise FolderNotReadyError(folder_name)

    def upload_torrent(self, filename):
        """
        Uploads a torrent file to Seedr.

        :param filename: Name of the torrent file.
        :return: Tuple containing the uploaded file's name and the folder ID.
        """
        progression_data = self.__seedr.add_torrent(torrent=join(self.torrent_folder, filename))
        file_name = progression_data.get('file_name')

        while self.__seedr.get_drive()['torrents']:
            sleep(1)

        return file_name, self.is_folder_ok(file_name)

    def download_torrent(self, folder_id, fast_download: bool = False):
        """
        Downloads files from the specified Seedr folder.

        :param folder_id: ID of the Seedr folder.
        :param root_dir: Root directory where downloaded files will be stored.
        :param fast_download: If True, uses fast download; otherwise, uses tqdm for progress.
        :return: None
        """

        def download_file(url, path, file):
            print(f"\033[92m Downloading {file} to {path} \033[0m")
            if not exists(path):
                makedirs(path)

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                if fast_download:
                    with open(join(path, file), 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)
                else:
                    total_size = int(r.headers.get('Content-Length', 0))
                    with open(join(path, file), 'wb') as file_stream, tqdm(total=total_size, unit='B',
                                                                           unit_scale=True) as pbar:
                        for chunk in r.iter_content(chunk_size=int(self.chunk_size)):
                            file_stream.write(chunk)
                            pbar.update(len(chunk))

        file_to_download = []
        folders_to_look = [folder_id]
        for _folder in folders_to_look:
            _data = self.__seedr.get_folder(_folder)
            file_to_download += _data["files"]
            folders_to_look += [fol["folder_id"] for fol in _data["folders"]]

        for _file in file_to_download:
            download_file(self.__seedr.get_file(_file.get('folder_file_id'))['download_url'],
                          join(self.download_folder, _file.get('folder_path')), _file.get('file_name'))

    def delete_folder(self, folder_id):
        """
        Deletes the specified Seedr folder.

        :param folder_id: ID of the parent folder containing the folder to be deleted.
        :return: None
        """
        self.__seedr.delete_folder(folder_id)

    def directory_download(self):
        """
        Uploads, downloads, and deletes torrents from the specified directory.

        :return: None
        """
        file_list = listdir(self.torrent_folder)
        for i in file_list:
            try:
                _, folder_id = self.upload_torrent(i)
                self.download_torrent(folder_id)
                self.delete_folder(folder_id)
            except Exception as e:
                self.logger.error(f'Error processing {i}: {e}', exc_info=True)
