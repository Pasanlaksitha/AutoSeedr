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
