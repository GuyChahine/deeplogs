from typing import Any
from pickle import dump, load
from os import PathLike, makedirs
from threading import Timer
from dataclasses import dataclass, field
import pandas as pd
import numpy as np
from PIL import Image
from math import ceil
from functools import wraps

@dataclass
class Log():
    
    """
    Data class to store and manage logs for a model.

    Args:
        name (str): Name of the model or log entry.
        description (str, optional): Description of the log. Default is an empty string.
        hyperparams (dict, optional): Dictionary containing hyperparameters for the model. Default is an empty dictionary.
        timestep (list of int or float, optional): List to store the timesteps of logged data. Default is an empty list.
        logs (dict of str to list, optional): Dictionary to store the logged data with keys as log names and values as lists
            of corresponding log values. Default is an empty dictionary.
    """
    
    name: str
    description: str = ""
    hyperparams: dict = field(default_factory=lambda: {})
    timestep: list[int|float] = field(default_factory=lambda: [])
    logs: dict[str: list] = field(default_factory=lambda: {})
    
    def save(self, path: PathLike|str) -> None:
        
        """
        Save the Log object to a file using pickle.

        Args:
            path (PathLike or str): The file path where the Log object will be saved.
        """
        
        with open(path, "wb") as f: dump(self.__dict__, f)
    
    @classmethod
    def load(cls, path: PathLike|str):
        
        """
        Load a Log object from a file using pickle.

        Args:
            path (PathLike or str): The file path from which the Log object will be loaded.

        Returns:
            Log: The loaded Log object.
        """
        
        with open(path, "rb") as f: return cls(**load(f))
        
    def scalar_to_dataframe(self) -> pd.DataFrame:
        
        """
        Convert the scalar log data to a pandas DataFrame for easy analysis and visualization.

        Returns:
            pd.DataFrame: A pandas DataFrame with log data and timesteps organized in columns and rows, respectively.
        """
        
        return pd.DataFrame(
            self.logs,
            index=pd.MultiIndex.from_product([[self.name], self.timestep])
        )

class Logger():
    
    """
    A logging utility to store and manage logs generated during the training or execution of a model.

    Args:
        name (str): Name of the session.
        description (str, optional): Description of the session. Default is an empty string.
        hyperparams (dict, optional): Dictionary containing hyperparameters of the session. Default is an empty dictionary.
        folder_path (PathLike or str, optional): Path to the folder where logs will be saved. Default is './dplogs/'.
        save_interval (float, optional): Time interval (in seconds) between automatic saves. Default is 5.0 seconds.
    """
    
    def __init__(
        self,
        name: str,
        description: str = "",
        hyperparams: dict = {},
        folder_path: PathLike[str]|str = "./dplogs/",
        save_interval: float = 5.,
    ):
        self.L: Log = Log(name, description, hyperparams)
        
        self.log_folder_path: str = f"{folder_path}{name}/"
        self.image_folder_path: str = f"{self.log_folder_path}images/"
        self.save_interval = save_interval
        self.__need_save: bool = True
        
        makedirs(self.image_folder_path, exist_ok=True)
    
    def __save_timer(func):
        
        """
        Decorator to schedule automatic log saving.

        Args:
            func (Callable): A function or method that triggers log changes.

        Returns:
            Callable: A wrapped function or method that schedules log saving after a specified interval.
        """
        
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.__need_save:
                self.__need_save = False
                Timer(self.save_interval, self.__save_logs).start()
            results = func(self, *args, **kwargs)
            return results
        return wrapper

    def __save_logs(self) -> None:
        
        """
        Save the logs to the log file.
        """
        
        self.__need_save = True
        self.L.save(self.log_folder_path + ".log")
    
    @__save_timer
    def scalar(self, timestep: int|float, **logs: dict[str: Any]) -> None:
        
        """
        Log scalar data at a specific timestep.

        Args:
            timestep (int or float): The timestep associated with the logged data.
            **logs (dict[str: Any]): Keyword arguments representing the logged data with log names as keys and
                corresponding scalar values as values.
        """
        
        for log_name in logs:
            if log_name not in self.L.logs.keys():
                self.L.logs[log_name] = [None for _ in range(len(self.L.timestep))]
        for log_name in self.L.logs.keys():
            self.L.logs[log_name].append(logs.get(log_name))
        self.L.timestep.append(timestep)
    
    @staticmethod
    def __create_image_grid(img: np.ndarray) -> np.ndarray:
        
        """
        Create a single image with a grid layout from a batch of images.

        Args:
            img (np.ndarray): A numpy array representing a batch of images.

        Returns:
            np.ndarray: A numpy array representing the grid layout of the images.
        """
        
        n, h, w, c = img.shape
        nrows = int(n**(1/2))
        ncols = ceil(n / nrows)
        if mod:= nrows * ncols % n:
            img = np.concatenate([img, np.zeros((mod, w, h, c))], 0)
        grid = img.reshape(nrows, ncols, h, w, c).swapaxes(1,2).reshape(h*nrows, w*ncols, c)
        return grid
    
    VALID_FORMAT: str = "NHWC"
    
    def image(
        self,
        timestep: int|float,
        img: np.ndarray,
        tag: str,
        image_format: str = "NCHW",
    ) -> None:
        
        """
        Log image data at a specific timestep with the provided tag.

        Args:
            timestep (int or float): The timestep associated with the logged image.
            img (np.ndarray): The image data to be logged as a NumPy array.
            tag (str): A descriptive tag for the logged image.
            image_format (str, optional): Format of the image data. Default is "NCHW".
        """
        
        if "C" not in image_format: img = np.expand_dims(img, -1); image_format += "C"
        if "N" not in image_format: img = np.expand_dims(img, -1); image_format += "N"
        transpose_vector = [image_format.find(rf) for rf in self.VALID_FORMAT]
        img = img.transpose(transpose_vector)
        if img.shape[0] > 1: img = self.__create_image_grid(img)
        img = (img.squeeze() * 255).astype(np.uint8)
        Image.fromarray(img).save(self.image_folder_path + f"{tag}_{timestep}.png")
        
    def flush(self) -> None:
        
        """
        Save the logs immediately.
        """
        
        self.L.save(self.log_folder_path + ".log")
