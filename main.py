from os import makedirs, listdir
from os.path import join, exists
from pathlib import Path
from time import sleep, time
from tqdm import tqdm
import requests
import json
from configparser import ConfigParser
from seedr_client import SeedrHandler
from datetime import datetime


# import atexit


def setup():
    username = input("Enter your seedr email: ")
    password_ = input("Enter your seedr password: ")
    torrent_directory = input("Enter your Torrent folder: ")
    # download_directory = input("Enter your download folder: ")
    chunkiness = input("Enter your chunk size (1024, 8192) put 1024 to default:  ")

    config['seedr'] = {'user': username,
                       'password': password_,
                       'folder': torrent_directory,
                       'chunk_size': chunkiness}
    # 'download_folder': download_directory

    with open('cred.ini', 'w') as configfile:
        config.write(configfile)
    print("Setup complete")


def datetime_to_timestamp(mode):
    stamp = datetime.now()
    if mode == 1:
        return stamp  # use in the log.txt for logging eg:2022-12-27 10:09:20.430322
    elif mode == 2:
        return stamp.strftime("%Y-%m-%d %H:%M:%S")  # use as a file name and folder name eg:2022-12-27 10:09:20
    else:
        raise ValueError("mode must be 1 or 2")


def get_progression_data(url):
    response = requests.get(url)
    json_data = response.text.replace('?(', '').rstrip(')')
    data = json.loads(json_data)

    title = data['title']
    size = data['size']
    download_rate = data['download_rate']
    folder_created = data['stats']['folder_created']
    # torrent_hash = data['stats']['torrent_hash']

    return title, size, download_rate, folder_created


def is_folder_ok(folder_name, folder_id=None):
    def get_folder_id(_folder_name):
        data = seedr.get_drive()
        for _folder in data['folders']:
            if _folder['folder_name'] == _folder_name:
                return _folder['folder_id']
        else:
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
    progression_data = seedr.add_torrent(torrent=f'torrent/{filename}', folder_id=-1, check_size=True)

    # torrent_id = progression_data.get('torrent_id')
    file_name = progression_data.get('file_name')
    # progression_url = progression_data.get('progress_url')

    while seedr.get_drive()['torrents']:
        sleep(1)

    return file_name, is_folder_ok(file_name)


# remove all the progress bar to make it faster and more efficient
def fast_download(url, path, file):
    print(f"\033[92m Downloading {file} to {path} \033[0m")
    if not exists(path):
        makedirs(path)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        # total_size = int(r.headers.get('Content-Length', 0))
        with open(join(path, file), 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                f.write(chunk)


def download_torrent(folder_id, root_dir='download'):
    def download_file(url, path, file):
        print(f"\033[92m Downloading {file} to {path} \033[0m")
        if not exists(path):
            makedirs(path)

        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('Content-Length', 0))
            with open(join(path, file), 'wb') as file_stream, tqdm(total=total_size, unit='B', unit_scale=True) as pbar:
                for chunk in r.iter_content(chunk_size=int(chunk_size * 1024)):
                    file_stream.write(chunk)
                    pbar.update(len(chunk))

    file_to_download = []
    folders_to_look = [folder_id]
    for _folder in folders_to_look:
        _data = seedr.get_folder(_folder)
        file_to_download += _data["files"]
        folders_to_look += [fol["folder_id"] for fol in _data["folders"]]
    start_time = time()
    print(start_time)
    for _file in file_to_download:
        download_file(seedr.get_file(_file.get('folder_file_id'))['download_url'],
                      join(root_dir, _file.get('folder_path')), _file.get('file_name'))
    end_time = time()

    folder_name = seedr.get_folder(folder_id)["folder_name"]
    root_directory = Path(join(root_dir, folder_name))
    with open('speed.txt', 'a') as f:
        f.write(
            f"{end_time - start_time}, {folder_name}, {sum(f.stat().st_size for f in root_directory.glob('**/*') if f.is_file())} \n")


def delete_folder(parent_folder_id):
    seedr.delete_folder(parent_folder_id)


def logging(faulty_torrents_):
    with open('log.txt', 'a') as f:
        for i in faulty_torrents_:
            f.write(f"{datetime_to_timestamp(1)}: {i} \n")


# This function for logging the total running time of the program
def trigger_while_exit():
    end_time = time()
    with open('time_log.txt', 'a') as f:
        f.write(f"Program started {datetime_to_timestamp(1)}\tProgram runtime: {end_time - program_start_time}\n")


def directory_download():
    if not exists(torrent_folder):
        makedirs(torrent_folder)
    file_list = listdir(torrent_folder)
    for i in file_list:
        try:
            folder_name, folder_id = upload_torrent(i)
            download_torrent(folder_id)
            delete_folder(folder_id)
        except Exception as e:
            faulty_torrents.append(f'{i} - {e}')
            pass
    logging(faulty_torrents)


if not exists('cred.ini'):
    setup()
else:
    config = ConfigParser()
    config.read('cred.ini')
    user = config['seedr']['user']
    password = config['seedr']['password']
    torrent_folder = config['seedr']['torrent_folder']
    download_folder = config['seedr']['download_folder']
    chunk_size = config['seedr']['chunk_size']

    seedr = SeedrHandler(email=user, password=password)

    faulty_torrents = []
    program_start_time = time()

    directory_download()

# atexit.register(trigger_while_exit)
# TODO: add a function to check if the file is already downloaded
# TODO: add argument parser using argparse (fastdownload, progressbar download,)
# TODO: Multiple torrent download from multiple seedr accounts to use maximum bandwidth
#  from isp and avoid limits of seedr server bandwidth
# FIXME: fix the progress bar
