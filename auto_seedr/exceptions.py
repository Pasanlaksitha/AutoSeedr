class AutoSeedrError(Exception):
    """Base class for AutoSeedrClient exceptions."""


class ConfigFileNotFoundError(AutoSeedrError):
    """Raised when the specified configuration file is not found."""

    def __init__(self, config_file):
        super().__init__(f"Configuration file not found: {config_file}")


class SeedrAuthenticationError(AutoSeedrError):
    """Raised when there is an issue with Seedr authentication."""

    def __init__(self, message="Seedr authentication error"):
        super().__init__(message)


class FolderNotFoundError(AutoSeedrError):
    """Raised when the specified Seedr folder is not found."""

    def __init__(self, folder_name):
        super().__init__(f"Seedr folder not found: {folder_name}")


class FolderNotReadyError(AutoSeedrError):
    """Raised when the specified Seedr folder is not ready within the timeout period."""

    def __init__(self, folder_name):
        super().__init__(f"Seedr folder not ready: {folder_name}")


class TorrentUploadError(AutoSeedrError):
    """Raised when there is an issue with uploading a torrent file."""

    def __init__(self, filename):
        super().__init__(f"Error uploading torrent file: {filename}")


class DownloadError(AutoSeedrError):
    """Raised when there is an issue with downloading files from Seedr."""

    def __init__(self, folder_id):
        super().__init__(f"Error downloading files from Seedr folder: {folder_id}")


class FolderDeletionError(AutoSeedrError):
    """Raised when there is an issue with deleting a Seedr folder."""

    def __init__(self, folder_id):
        super().__init__(f"Error deleting Seedr folder: {folder_id}")


class DirectoryDownloadError(AutoSeedrError):
    """Raised when there is an issue with the directory download process."""

    def __init__(self, directory):
        super().__init__(f"Error during directory download: {directory}")


class ChunkedDownloadError(AutoSeedrError):
    """Raised when there is an issue with chunked download."""

    def __init__(self, message):
        super().__init__(f"Chunked download error: {message}")


class ChunkReassemblyError(AutoSeedrError):
    """Raised when there is an issue reassembling file chunks."""

    def __init__(self, message):
        super().__init__(f"Chunk reassembly error: {message}")


class FileDeletionError(AutoSeedrError):
    """Raised when there is an issue deleting a file from Seedr."""

    def __init__(self, file_id):
        super().__init__(f"Error deleting file from Seedr: {file_id}")
