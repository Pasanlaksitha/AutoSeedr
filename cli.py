import argparse
import logging
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler

from auto_seedr import AutoSeedrClient, setup_config


def configure_logging(log_level: str, log_file: str) -> None:
    """
    Configure logging based on the specified log level.

    :param log_level: The log level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
    :param log_file: The log file path
    :return: None
    """
    logging.basicConfig(level=log_level.upper())

    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=3)
    file_formatter = logging.Formatter('%(asctime)s [%(levelname)s] - %(message)s')
    file_handler.setFormatter(file_formatter)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('[%(levelname)s] - %(message)s')
    console_handler.setFormatter(console_formatter)

    logging.getLogger().addHandler(file_handler)
    logging.getLogger().addHandler(console_handler)


def parse_args():
    parser = argparse.ArgumentParser(description='AutoSeedr CLI')
    parser.add_argument('-c', '--create-config', action='store_true', help='Create a new config file')
    parser.add_argument('-f', '--config-file', default='config.ini', help='INI file path for configuration')
    parser.add_argument('-e', '--email', help='Seedr account email')
    parser.add_argument('-p', '--password', help='Seedr account password')
    parser.add_argument('-td', '--torrent-directory', default='torrents', help='Directory containing torrent files')
    parser.add_argument('-dd', '--download-directory', default='downloads', help='Directory to store downloaded files')
    parser.add_argument('-cs', '--chunk-size', default='1024', help='Chunk size for downloading files')
    parser.add_argument('-l', '--log-level', default='ERROR',
                        help='Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('-lf', '--log-file', default='auto_seedr_cli.log', help='Log file path')

    return parser.parse_args()


def main():
    args = parse_args()

    configure_logging(args.log_level, args.log_file)

    if args.create_config:
        setup_config(
            email=args.email,
            password=args.password,
            config_file=args.config_file,
            torrent_directory=args.torrent_directory,
            download_directory=args.download_directory,
            chunk_size=args.chunk_size
        )
        logging.info(f'Config file "{args.config_file}" created successfully.')
        return

    if args.config_file:
        config = ConfigParser()
        config.read(args.config_file)
        email = config.get('SEEDR', 'user')
        password = config.get('SEEDR', 'password')
        torrent_directory = config.get('APP', 'folder')
        download_directory = config.get('APP', 'download_folder')
        chunk_size = config.get('APP', 'chunk_size')
    else:
        email = args.email
        password = args.password
        torrent_directory = args.torrent_directory
        download_directory = args.download_directory
        chunk_size = args.chunk_size

    seedr_client = AutoSeedrClient(
        __email=email,
        __password=password,
        torrent_directory=torrent_directory,
        download_directory=download_directory,
        chunk_size=chunk_size,
        log_level=args.log_level.upper()
    )

    try:
        seedr_client.directory_download()
        logging.info(f'Directory download completed successfully. Files downloaded to: {download_directory}')
    except Exception as e:
        logging.error(f'Error: {e}')


if __name__ == '__main__':
    main()
