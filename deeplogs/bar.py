from typing import Iterable, Generator
from time import time
from datetime import timedelta

from deeplogs.logger import Logger

class Bar():
    
    """
    A progress bar that optionally displays the logs of a model.

    Args:
        logger (Logger, optional): An instance of the Logger class to log in the Bar. Default is None.
        description (str, optional): Description to be displayed before the progress bar. Default is an empty string.
        running_mean_size (int, optional): The number of most recent iterations on which the moving average is based. The default value is 1.
        bar_size (int, optional): Total size of the progress bar. Default is 10.
        empty_char (str, optional): Character to represent empty space in the progress bar. Default is a single space ' '.
        fill_char (str, optional): Character to represent filled space in the progress bar. Default is the Unicode block character u"\u2588".
        print_interval (float, optional): Time interval (in seconds) between progress bar updates. Default is 0.2 seconds.
    """
    
    def __init__(
        self,
        logger: Logger = None,
        description: str = "",
        running_mean_size: int = 1,
        bar_size: int = 10,
        empty_char: str = " ",
        fill_char: str = u"\u2588",
        print_interval: float = 0.2,
    ):

        self.logger = logger
        self.description = description
        self.rms = running_mean_size
        self.bar_size = bar_size
        self.empty_char = empty_char
        self.fill_char = fill_char
        self.print_interval = print_interval
    
    @staticmethod
    def __format_seconds(seconds: float) -> str:
        """
        Convert a number of seconds to a formatted string representing the duration.

        Args:
            seconds (float): Number of seconds.

        Returns:
            str: Formatted string representing the duration in a human-readable format (e.g., '2 days, 4:30:00').
        """
        return str(timedelta(seconds=int(seconds)))
    
    def __call__(self, iterator: Iterable | Generator, iterator_length: int = None) -> Generator[int, float, str]:

        """
        Create a generator for iterating over an iterable while displaying a progress bar while logging the progress of a model.

        Args:
            iterator (Iterable): The iterable to be iterated over.
            iterator_length (int): The number of elements in the iterable. Required if ``iterator`` does not have a defined length.

        Yields:
            Generator[int, float, str]: A generator that yields elements from the original iterator.
        """

        if self.description: 
            self.description += ": "
        try: iterator_length = len(iterator)
        except: assert iterator_length, "Need to specify the iterator_length"
        t0 = time()
        last_print = t0 - self.print_interval
        for i, args in enumerate(iterator):
            yield args
            if time() - last_print >= self.print_interval or (i+1) == iterator_length:
                logs_string = []
                if self.logger:
                    for log_name, log_list in self.logger.L.logs.items():
                        running_list = log_list[-self.rms:]
                        logs_string.append(
                            f"{log_name}: {round(sum(running_list)/len(running_list), 3):>5}"
                        )
                
                perc = (i+1) / iterator_length
                nb_fill = int(self.bar_size * perc)
                nb_empty = self.bar_size - nb_fill
                elapsed_time = time() - t0
                eta = (elapsed_time / perc) - elapsed_time
                iter_per_sec = (i+1) / elapsed_time
                
                string = "{}{:>4.0%}|{}{}| {}/{} [{}<{}, {:.2F}it/s] {}"
                print(string.format(
                    self.description,
                    perc,
                    self.fill_char*nb_fill, self.empty_char*nb_empty,
                    i+1, iterator_length,
                    self.__format_seconds(elapsed_time), self.__format_seconds(eta), iter_per_sec,
                    " | ".join(logs_string),
                ), end="\r")
                last_print = time()