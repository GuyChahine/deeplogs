from tempfile import TemporaryDirectory
from time import sleep
from random import random
import pandas as pd
from plotly import io
import matplotlib.pyplot as plt
import matplotlib

from deeplogs import Logger
from deeplogs import Reader


class TestReader():
    
    NB_VERSION: int = 4
    TEST_SIZE: int = 100
    SAVE_INTERVAL: float = 0.1
    
    def setup_class(self):
        self.temp_folder = TemporaryDirectory(dir="./")
        
        self.NAME: str = "test"
        self.DESCRIPTION: str = "This is a description"
        self.HYPERPARAM: dict = {
            "param1": 1,
            "param2": (1,2,3)
        }
        
        for n in range(self.NB_VERSION):
            L = Logger(
                f"{self.NAME}{n+1}",
                self.DESCRIPTION,
                self.HYPERPARAM,
                self.temp_folder.name + "/",
                self.SAVE_INTERVAL,
            )
            for i in range(self.TEST_SIZE):
                L.scalar(i, **{"log1": random(), "log2": random()})
        sleep(self.SAVE_INTERVAL + 0.1)
            
        self.R = Reader([], self.temp_folder.name + "/")
    
    def teardown_class(self):
        del self.R
        self.temp_folder.cleanup()
    
    def test_describe(self):
        percentiles = [0.1, 0.2, 0.3, 0.4, 0.5]
        df = self.R.describe(percentiles=percentiles)
        assert type(df) == pd.DataFrame
        assert (df.shape[0] / self.NB_VERSION) == (5 + len(percentiles))
        assert df.shape[1] == 2
        
    def test_infos(self):
        infos = self.R.infos()
        assert type(infos) == pd.DataFrame
        assert infos.shape == (self.NB_VERSION, 1 + len(self.HYPERPARAM))
        
    def test_scalar(self):
        io.renderers.default = None
        self.R.scalar(using="plotly")
        plt.ion()
        self.R.scalar(using="matplotlib")