import argparse
import logging
import os
import sys
from configparser import ConfigParser
from logging.handlers import RotatingFileHandler

from auto_seedr import AutoSeedrClient, setup_config

DEFAULT_CONFIG_FILE = 'config.ini'
DEFAULT_LOG_LEVEL = 'ERROR'
DEFAULT_LOG_FILE = 'auto_seedr_cli.log'


def configure_logging(log_level: str, log_file: str) -> None:
    """
    Configure logging for the application.

    :param log_level: The desired logging level.
    :param log_file: The file path for the log file.
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


def get_user_input(prompt, default=None):
    """
    Get user input with an optional default value.

    :param prompt: The prompt to display to the user.
    :param default: The default value if the user input is empty.
    :return: User input or the default value.
    """
    user_input = input(prompt)
    return user_input.strip() if user_input.strip() != '' else default


def parse_args():
    """
    Parse command-line arguments using argparse.

    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(description='AutoSeedr CLI')

    parser.add_argument('-C', '--create-config', action='store_true', help='Create a new config file')
    parser.add_argument('-L', '--load-config', action='store_true', help='Load an existing config file')

    config_group = parser.add_argument_group('Configuration Options')
    config_group.add_argument('-f', '--config-file', default=DEFAULT_CONFIG_FILE,
                              help='INI file path for configuration (default: config.ini)')
    config_group.add_argument('-e', '--email', help='Seedr account email')
    config_group.add_argument('-p', '--password', help='Seedr account password')
    config_group.add_argument('-td', '--torrent-directory', default='torrents',
                              help='Directory containing torrent files (default: torrents)')
    config_group.add_argument('-dd', '--download-directory', default='downloads',
                              help='Directory to store downloaded files (default: downloads)')
    config_group.add_argument('-cs', '--chunk-size', default=1024, type=int,
                              help='Chunk size for downloading files in kilobytes (default: 1024)')

    log_group = parser.add_argument_group('Logging Options')
    log_group.add_argument('-ll', '--log-level', default=DEFAULT_LOG_LEVEL,
                           choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                           help='Logging level (default: ERROR)')
    log_group.add_argument('-lf', '--log-file', default=DEFAULT_LOG_FILE,
                           help='Log file path (default: auto_seedr_cli.log)')

    args = parser.parse_args()

    if not args.create_config and not args.load_config and not (args.email and args.password):
        parser.print_help()
        print(
            "\nInvalid combination of arguments. Please provide either --create-config, --load-config, or valid email "
            "and password.")
        sys.exit(1)

    return args


def prompt_for_missing_details():
    """
    Prompt the user for missing details (email and password).

    :return: Tuple containing email and password.
    """
    email = get_user_input('Seedr account email: ')
    password = get_user_input('Seedr account password: ')
    return email, password


def main():
    """The main function that orchestrates the AutoSeedr CLI functionality."""
    args = parse_args()
    torrent_directory, download_directory, chunk_size = (
        args.torrent_directory,
        args.download_directory,
        args.chunk_size
    )

    if args.create_config:
        if not args.email or not args.password:
            logging.warning('Email and password are required to create a new config.')
            email, password = prompt_for_missing_details()
        else:
            email, password = args.email, args.password

        setup_config(
            email=email,
            password=password,
            config_file=args.config_file,
            torrent_directory=args.torrent_directory,
            download_directory=args.download_directory,
            chunk_size=args.chunk_size
        )
        logging.info(f'Config file "{args.config_file}" created successfully.')
    elif args.load_config:
        if not os.path.exists(args.config_file):
            logging.error(f'Config file "{args.config_file}" not found.')
            return
        config = ConfigParser()
        config.read(args.config_file)
        email = config.get('SEEDR', 'user')
        password = config.get('SEEDR', 'password')
        torrent_directory = config.get('APP', 'torrent_folder')
        download_directory = config.get('APP', 'download_folder')
        chunk_size = config.get('APP', 'chunk_size')
    else:
        email, password, torrent_directory, download_directory, chunk_size = (
            args.email,
            args.password,
            args.torrent_directory,
            args.download_directory,
            args.chunk_size
        )

    configure_logging(args.log_level, args.log_file)

    seedr_client = AutoSeedrClient(
        email=email,
        password=password,
        torrent_directory=torrent_directory,
        download_directory=download_directory,
        chunk_size=chunk_size,
    )

    try:
        seedr_client.directory_download()
        logging.info(f'Directory download completed successfully. Files downloaded to: {download_directory}')
    except Exception as e:
        logging.error(f'Error: {e}', exc_info=True)


if __name__ == '__main__':
    main()
