import json
from configparser import ConfigParser
from os import makedirs, listdir
from os.path import join, exists
from time import sleep

import requests
from seedr_client import SeedrHandler
from tqdm import tqdm

from auto_seedr.utils import logging


def setup(config_file='config.ini'):
    __config = ConfigParser()
    __username = input("Enter your seedr email: ")
    __password_ = input("Enter your seedr password: ")
    _torrent_directory = input("Enter your Torrent folder default(torrents): ")
    _download_directory = input("Enter your download folder default(downloads): ")
    _chunkiness = input("Enter your chunk size (1024, 8192) default(1024): ")

    if not _chunkiness:
        _chunkiness = '1024'

    if not _torrent_directory:
        _torrent_directory = 'torrents'

    if not _download_directory:
        _download_directory = 'downloads'

    __config['SEEDR'] = {'user': __username, 'password': __password_}

    __config['APP'] = {'torrent_folder': _torrent_directory, 'chunk_size': _chunkiness,
                       'download_folder': _download_directory}

    with open(config_file, 'w') as configfile:
        __config.write(configfile)

    print("Setup complete")


def get_progression_data(url):
    response = requests.get(url)
    json_data = response.text.replace('?(', '').rstrip(')')
    data = json.loads(json_data)

    title = data['title']
    size = data['size']
    download_rate = data['download_rate']
    folder_created = data['stats']['folder_created']

    return title, size, download_rate, folder_created


def is_folder_ok(folder_name, folder_id=None):
    def get_folder_id(_folder_name):
        data = seedr.get_drive()
        for _folder in data['folders']:
            if _folder['folder_name'] == _folder_name:
                return _folder['folder_id']
        print('Error not found folder id')
        return None

    folder_ok = False
    if not folder_id:
        folder_id = get_folder_id(folder_name)
    while not folder_ok:
        try:
            if seedr.get_folder(folder_id):
                folder_ok = True
        except:
            folder_id = get_folder_id(folder_name)
            sleep(1)
    return folder_id


def upload_torrent(filename):
    progression_data = seedr.add_torrent(torrent=join(torrent_folder, filename), folder_id=-1, check_size=True)

    file_name = progression_data.get('file_name')

    while seedr.get_drive()['torrents']:
        sleep(1)

    return file_name, is_folder_ok(file_name)


# Remove all the progress bar to make it faster and more efficient
def fast_download(url, path, file):
    print(f"\033[92m Downloading {file} to {path} \033[0m")
    if not exists(path):
        makedirs(path)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(join(path, file), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)


def download_torrent(folder_id):
    def download_file(url, path, file):
        print(f"\033[92m Downloading {file} to {path} \033[0m")
        if not exists(path):
            makedirs(path)

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('Content-Length', 0))
            with open(join(path, file), 'wb') as file_stream, tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in r.iter_content(chunk_size=int(chunk_size)):
                    file_stream.write(chunk)
                    pbar.update(len(chunk))

    file_to_download = []
    folders_to_look = [folder_id]
    for _folder in folders_to_look:
        _data = seedr.get_folder(_folder)
        file_to_download += _data["files"]
        folders_to_look += [fol["folder_id"] for fol in _data["folders"]]

    for _file in file_to_download:
        download_file(seedr.get_file(_file.get('folder_file_id'))['download_url'],
                      join(download_folder, _file.get('folder_path')), _file.get('file_name'))


def delete_folder(parent_folder_id):
    seedr.delete_folder(parent_folder_id)


def directory_download():
    if not exists(torrent_folder):
        makedirs(torrent_folder)
    file_list = [f for f in listdir(torrent_folder) if f.endswith(".torrent")]
    if file_list:
        for i in file_list:
            try:
                _, folder_id = upload_torrent(i)
                download_torrent(folder_id)
                delete_folder(folder_id)
            except Exception as e:
                logging(f'{i} - {e}')
    else:
        print(f"No torrent files found in {torrent_folder}")


if __name__ == '__main__':
    if not exists('config.ini'):
        setup()

    config = ConfigParser()
    config.read('config.ini')

    user = config['SEEDR']['user']
    password = config['SEEDR']['password']
    torrent_folder = config['APP']['torrent_folder']
    download_folder = config['APP']['download_folder']
    chunk_size = config['APP']['chunk_size']

    seedr = SeedrHandler(email=user, password=password)

    directory_download()

# TODO: add a function to check if the file is already downloaded
# TODO: add argument parser using argparse (fastdownload, progressbar download,)
# TODO: Multiple torrent download from multiple seedr accounts to use maximum bandwidth from isp and avoid limits of seedr server bandwidth
# FIXME: fix the progress bar
