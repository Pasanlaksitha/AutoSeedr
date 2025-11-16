from os import makedirs, listdir, remove
from os.path import join, exists, getsize
from time import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed
import math

import requests
from seedr_client import SeedrHandler
from tqdm import tqdm

from auto_seedr.exceptions import (FolderNotReadyError, FolderNotFoundError,
                                    ChunkedDownloadError, ChunkReassemblyError,
                                    FileDeletionError)


class AutoSeedrClient:
    def __init__(self, email, password, torrent_directory: str = 'torrents', download_directory: str = 'downloads',
                 chunk_size: str = '1024', time_out: int = 100, enable_chunked_download: bool = True,
                 chunk_download_size: int = 2147483648, max_workers: int = 4, delete_after_download: bool = False):
        self.torrent_folder = torrent_directory
        self.download_folder = download_directory
        self.chunk_size = chunk_size
        self.time_out = time_out
        self.enable_chunked_download = enable_chunked_download
        self.chunk_download_size = chunk_download_size  # Default 2GB in bytes
        self.max_workers = max_workers
        self.delete_after_download = delete_after_download
        self.email = email
        self.password = password

        self.__seedr = SeedrHandler(email=email, password=password)

        self._create_directories()

    def _create_directories(self) -> None:
        """
        Create the required directories for the torrent and download operations.

        :return: None
        """
        for directory in [self.torrent_folder, self.download_folder]:
            if not exists(directory):
                makedirs(directory)

    def is_folder_ok(self, folder_name, folder_id=None):
        """
        Checks if the specified Seedr folder is ready for use.

        :param folder_name: Name of the Seedr folder.
        :param folder_id: ID of the Seedr folder.
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
        while count <= self.time_out:
            try:
                if self.__seedr.get_folder(folder_id):
                    return folder_id
            except LookupError:
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

        count = 0
        while count <= self.time_out:
            if self.__seedr.get_drive()['torrents']:
                return file_name, self.is_folder_ok(file_name)
            count += 1
            sleep(1)
        raise FolderNotFoundError(file_name)

    def download_torrent(self, folder_id, fast_download: bool = False):
        """
        Downloads files from the specified Seedr folder with optional chunked download support.

        :param folder_id: ID of the Seedr folder.
        :param fast_download: If True, uses fast download without progress bars.
        :return: None
        """

        def download_file(url, path, file_name, file_size, file_id=None):
            print(f"\033[92m Downloading {file_name} to {path} \033[0m")
            if not exists(path):
                makedirs(path)

            # Use chunked download if enabled and file is large enough
            if self.enable_chunked_download and not fast_download and file_size > self.chunk_download_size:
                try:
                    self._download_file_chunked(url, path, file_name, file_size)
                except Exception as e:
                    print(f"\033[93m Chunked download failed: {str(e)}, falling back to standard download \033[0m")
                    self._download_file_standard(url, path, file_name)
            elif fast_download:
                # Fast download without progress bar
                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(join(path, file_name), 'wb') as f:
                        for chunk in r.iter_content(chunk_size=1024):
                            f.write(chunk)
            else:
                # Standard download with progress bar
                self._download_file_standard(url, path, file_name)

            # Delete file from Seedr after download if enabled
            if self.delete_after_download and file_id:
                try:
                    self.delete_file(file_id)
                except Exception as e:
                    print(f"\033[93m Warning: Could not delete file {file_id} from Seedr: {str(e)} \033[0m")

        file_to_download = []
        folders_to_look = [folder_id]
        for _folder in folders_to_look:
            _data = self.__seedr.get_folder(_folder)
            file_to_download += _data["files"]
            folders_to_look += [fol["folder_id"] for fol in _data["folders"]]

        for _file in file_to_download:
            file_info = self.__seedr.get_file(_file.get('folder_file_id'))
            download_url = file_info['download_url']
            file_name = _file.get('file_name')
            file_size = _file.get('size', 0)  # Get file size from metadata
            file_id = _file.get('folder_file_id')

            download_file(download_url, join(self.download_folder, _file.get('folder_path')),
                         file_name, file_size, file_id)

    def delete_folder(self, folder_id):
        """
        Deletes the specified Seedr folder.

        :param folder_id: ID of the parent folder containing the folder to be deleted.
        :return: None
        """
        self.__seedr.delete_folder(folder_id)

    def delete_file(self, file_id):
        """
        Deletes an individual file from Seedr using direct API call.

        :param file_id: ID of the file to delete.
        :return: None
        :raises: FileDeletionError if deletion fails.
        """
        try:
            # Make direct API call to Seedr to delete the file
            session = requests.Session()
            session.auth = (self.email, self.password)
            response = session.delete(f'https://www.seedr.cc/rest/file/{file_id}')
            response.raise_for_status()
            print(f"\033[93m Deleted file {file_id} from Seedr to free up space \033[0m")
        except Exception as e:
            raise FileDeletionError(file_id) from e

    def _supports_range_requests(self, url):
        """
        Check if the server supports HTTP Range requests.

        :param url: URL to check.
        :return: True if Range requests are supported, False otherwise.
        """
        try:
            response = requests.head(url, timeout=10)
            return response.headers.get('Accept-Ranges') == 'bytes'
        except Exception:
            return False

    def _download_chunk(self, url, start, end, chunk_path, progress_bar=None):
        """
        Download a specific byte range of a file.

        :param url: Download URL.
        :param start: Start byte position.
        :param end: End byte position.
        :param chunk_path: Path to save the chunk.
        :param progress_bar: Optional tqdm progress bar for updating progress.
        :return: Tuple of (chunk_path, success_status).
        """
        headers = {'Range': f'bytes={start}-{end}'}
        try:
            response = requests.get(url, headers=headers, stream=True, timeout=300)
            response.raise_for_status()

            with open(chunk_path, 'wb') as f:
                for data in response.iter_content(chunk_size=int(self.chunk_size)):
                    f.write(data)
                    if progress_bar:
                        progress_bar.update(len(data))

            return chunk_path, True
        except Exception as e:
            print(f"\033[91m Error downloading chunk {chunk_path}: {str(e)} \033[0m")
            return chunk_path, False

    def _reassemble_chunks(self, chunk_files, output_path):
        """
        Reassemble downloaded chunks into a single file.

        :param chunk_files: List of chunk file paths in order.
        :param output_path: Path for the final assembled file.
        :return: None
        :raises: ChunkReassemblyError if reassembly fails.
        """
        try:
            print(f"\033[94m Reassembling {len(chunk_files)} chunks into {output_path} \033[0m")
            with open(output_path, 'wb') as outfile:
                for chunk_file in chunk_files:
                    if not exists(chunk_file):
                        raise ChunkReassemblyError(f"Chunk file not found: {chunk_file}")

                    with open(chunk_file, 'rb') as infile:
                        outfile.write(infile.read())

                    # Delete chunk file after writing
                    remove(chunk_file)

            print(f"\033[92m Successfully reassembled file: {output_path} \033[0m")
        except Exception as e:
            raise ChunkReassemblyError(str(e)) from e

    def _download_file_chunked(self, url, path, file_name, file_size):
        """
        Download a file in chunks using HTTP Range requests and reassemble.

        :param url: Download URL.
        :param path: Directory to save the file.
        :param file_name: Name of the file.
        :param file_size: Total size of the file in bytes.
        :return: None
        """
        output_path = join(path, file_name)

        # Check if Range requests are supported
        if not self._supports_range_requests(url):
            print(f"\033[93m Server doesn't support Range requests, falling back to standard download \033[0m")
            return self._download_file_standard(url, path, file_name)

        # Calculate number of chunks
        num_chunks = math.ceil(file_size / self.chunk_download_size)

        if num_chunks == 1:
            print(f"\033[93m File is smaller than chunk size, using standard download \033[0m")
            return self._download_file_standard(url, path, file_name)

        print(f"\033[94m Downloading {file_name} in {num_chunks} chunks of ~{self.chunk_download_size / (1024**3):.2f}GB each \033[0m")

        # Prepare chunk files
        chunk_files = []
        download_tasks = []

        for i in range(num_chunks):
            start = i * self.chunk_download_size
            end = min(start + self.chunk_download_size - 1, file_size - 1)
            chunk_path = join(path, f"{file_name}.part{i}")
            chunk_files.append(chunk_path)
            download_tasks.append((url, start, end, chunk_path))

        # Download chunks with progress bar
        with tqdm(total=file_size, unit='B', unit_scale=True, desc=f"Downloading {file_name}") as pbar:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = {executor.submit(self._download_chunk, *task, pbar): task for task in download_tasks}

                for future in as_completed(futures):
                    chunk_path, success = future.result()
                    if not success:
                        raise ChunkedDownloadError(f"Failed to download chunk: {chunk_path}")

        # Reassemble chunks
        self._reassemble_chunks(chunk_files, output_path)

    def _download_file_standard(self, url, path, file_name):
        """
        Standard download method (non-chunked).

        :param url: Download URL.
        :param path: Directory to save the file.
        :param file_name: Name of the file.
        :return: None
        """
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('Content-Length', 0))
            with open(join(path, file_name), 'wb') as file_stream, tqdm(total=total_size, unit='B',
                                                                        unit_scale=True, desc=f"Downloading {file_name}") as pbar:
                for chunk in r.iter_content(chunk_size=int(self.chunk_size)):
                    file_stream.write(chunk)
                    pbar.update(len(chunk))

    def directory_download(self):
        """
        Uploads, downloads, and deletes torrents from the specified directory.

        :return: None
        """
        file_list = listdir(self.torrent_folder)
        for i in file_list:
            _, folder_id = self.upload_torrent(i)
            self.download_torrent(folder_id)
            self.delete_folder(folder_id)
