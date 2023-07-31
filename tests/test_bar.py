from tempfile import TemporaryDirectory
from time import sleep

from deeplogs import Bar
from deeplogs import Logger


class TestBar():
    
    TEST_SIZE: int = 100
    SAVE_INTERVAL: float = 0.1
    BAR_SLEEP: float = 0.001
    
    def setup_class(self):
        self.temp_folder = TemporaryDirectory(dir="./")
    
    def teardown_class(self):
        sleep(self.SAVE_INTERVAL + 0.1)
        self.temp_folder.cleanup()
    
    def setup_method(self):
        self.B = Bar(None, "Epoch 1", 20, 15, "-", "|", 0.)
    
    def teardown_method(self):
        del self.B
        
    def test_call(self):
        iterator = list(range(self.TEST_SIZE))
        bar_iterator = [i for i in self.B(iterator)]
        assert bar_iterator == iterator
        for i in self.B(iterator):
            sleep(self.BAR_SLEEP)
        
    def test_call_with_logger(self):
        L = Logger(
            "test1",
            "This is a description",
            {"param1": 1},
            self.temp_folder.name + "/",
            self.SAVE_INTERVAL,
        )
        self.B.logger = L
        for i in range(self.TEST_SIZE):
            L.scalar(i, **{"log1": 1, "log2": 2})
            sleep(self.BAR_SLEEP)