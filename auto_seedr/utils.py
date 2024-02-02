from configparser import ConfigParser
from datetime import datetime
from functools import wraps
from time import perf_counter


def datetime_to_timestamp(include_milliseconds: bool = False) -> str:
    """
    Timestamp
    With milliseconds ex: 2022-12-27 10:09:20.430322
    Without milliseconds ex: 2022-12-27 10:09:20

    :param include_milliseconds: boolean to include milliseconds
    :return: timestamp
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f" if include_milliseconds else "%Y-%m-%d %H:%M:%S")


def logging(content: str, log_file: str = 'log.txt') -> None:
    """
    Logging function
    :param content: content to log
    :param log_file: name of the log file
    :return: None
    """
    with open(log_file, 'a') as f:
        f.write(f"{datetime_to_timestamp(include_milliseconds=False)}: {content} \n")


# This function for logging the total running time of function
def timeit(func, time_log_file: str = 'time_log.txt'):
    """
    Decorator to logging the total running time of function
    :param func: function to calculate the total running time
    :param time_log_file: name of the log file
    :return: time taken to run the function
    """

    @wraps(func)
    def timeit_wrapper(*args, **kwargs):
        start_time = perf_counter()
        result = func(*args, **kwargs)
        end_time = perf_counter()
        total_time = end_time - start_time

        stamp = datetime_to_timestamp(include_milliseconds=True)

        with open(time_log_file, 'a') as f:
            f.write(
                f"Program started {stamp}\tProgram runtime: {total_time}\n")

        return result

    return timeit_wrapper


def setup_config(email: str, password: str, config_file: str = 'config.ini', torrent_directory: str = 'torrents',
                 download_directory: str = 'downloads', chunk_size: str = '1024') -> None:
    """
    Set up the configuration

    :param email: The email address associated with the user account.
    :param password: The password for the user account.
    :param config_file: The configuration file path. Default is 'config.ini'.
    :param torrent_directory: The directory where torrent files will be stored. Default is 'torrents'.
    :param download_directory:The directory where downloaded files will be stored. Default is 'downloads'
    :param chunk_size: The chunk size for downloading files. Default is '1024'.
    :return: None
    """
    __config = ConfigParser()
    __config['SEEDR'] = {'user': email, 'password': password}
    __config['APP'] = {'torrent_folder': torrent_directory, 'chunk_size': chunk_size,
                       'download_folder': download_directory}

    with open(config_file, 'w') as configfile:
        __config.write(configfile)
