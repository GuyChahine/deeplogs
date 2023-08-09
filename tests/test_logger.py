from random import random
from tempfile import TemporaryDirectory
import pandas as pd
from time import sleep
from os.path import exists
import numpy as np

from deeplogs import Log, Logger

class TestLog():
    
    TEST_SIZE: int = 100
    
    def setup_class(self):
        
        self.L = Log(
            name="test1",
            description="This is a description",
            hyperparams={
                "param1": 1,
                "param2": "p2",
                "param3": (1,3,3),
                "param4": {"a": 1, "b": 2}
            },
            timestep=list(range(self.TEST_SIZE)),
            logs={
                "log1": [random() for _ in range(self.TEST_SIZE)],
                "log2": [random() for _ in range(self.TEST_SIZE)],
            },
        )
        
        self.temp_folder = TemporaryDirectory(dir="./")
    
    def teardown_class(self):
        del self.L
        self.temp_folder.cleanup()
    
    def test_save(self):
        self.L.save(self.temp_folder.name + "/test_save.log")
    
    def test_load(self):
        self.L.save(self.temp_folder.name + "/test_load.log")
        loaded_L = Log.load(self.temp_folder.name + "/test_load.log")
        assert loaded_L.__dict__ == self.L.__dict__
    
    def test_scalar_to_dataframe(self):
        df = self.L.scalar_to_dataframe()
        assert type(df) == pd.DataFrame
        assert df.shape == (self.TEST_SIZE, len(self.L.logs))

class TestLogger():
    
    TEST_SIZE: int = 100
    SAVE_INTERVAL: float = 0.2
    
    def setup_class(self):
        self.logs = {
            "log1": [random() for _ in range(self.TEST_SIZE)],
            "log2": [random() for _ in range(self.TEST_SIZE)],
        }
        
    def teardown_class(self):
        del self.logs
    
    def setup_method(self):
        self.temp_folder = TemporaryDirectory(dir="./")
        self.L = Logger(
            name="name1",
            description="This is a description",
            hyperparams={
                "param1": 1,
                "param2": "p2",
                "param3": (1,3,3),
                "param4": {"a": 1, "b": 2}
            },
            folder_path=self.temp_folder.name + "/",
            save_interval=self.SAVE_INTERVAL,
        )
    
    def teardown_method(self):
        sleep(self.SAVE_INTERVAL + 0.1)
        del self.L
        self.temp_folder.cleanup()
    
    def test_scalar(self):
        for i in range(self.TEST_SIZE):
            logs = {key: value[i] for key, value in self.logs.items()}
            self.L.scalar(i, **logs)
        assert self.L.L.logs == self.logs
    
    def test_save_timer(self):
        self.L.scalar(0, **{"log1": 1})
        sleep(self.SAVE_INTERVAL)
        loaded_L = Log.load(f"{self.temp_folder.name}/{self.L.L.name}/.log")
        assert loaded_L.__dict__ == self.L.L.__dict__
        
    def test_flush(self):
        self.L.scalar(0, **{"log2": 2})
        self.L.flush()
        loaded_L = Log.load(f"{self.temp_folder.name}/{self.L.L.name}/.log")
        assert loaded_L.__dict__ == self.L.L.__dict__
        
    def test_image(self):
        img = np.random.random((self.TEST_SIZE, self.TEST_SIZE))
        self.L.image(0., img, "image1", "HW")
        assert exists(f"{self.temp_folder.name}/{self.L.L.name}/images/image1_0.0.png")
        self.L.image(0., img[None].repeat(3,0), "image2", "CHW")
        assert exists(f"{self.temp_folder.name}/{self.L.L.name}/images/image2_0.0.png")
        self.L.image(0., img[None].repeat(3,0)[None].repeat(4,0), "image3", "NCHW")
        assert exists(f"{self.temp_folder.name}/{self.L.L.name}/images/image3_0.0.png")
        
    def test_scalar_inconsistancy(self):
        # https://github.com/GuyChahine/deeplogs/issues/3#issue-1841820163
        temp_file_path = f"{self.temp_folder.name}/name1/.log"
        for i in range(10000):
            self.L.scalar(i, **{f"log{nlog}": nlog for nlog in range(10)})
            sleep(self.SAVE_INTERVAL / 2000)
            if i == 0: self.L.flush() 
            if i % 15 == 0:
                logs = Log.load(temp_file_path)
                logs_lengths = [len(value) for value in logs.logs.values()] + [len(logs.timestep)]
                assert len(set(logs_lengths)) == 1