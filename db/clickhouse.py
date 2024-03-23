import clickhouse_connect
from clickhouse_connect.driver import httputil

class ClickClientPool:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(ClickClientPool, cls).__new__(cls)
            cls._instance._initialize(*args, **kwargs)
        return cls._instance

    def _initialize(self, maxsize, num_pools):
        self.big_pool_mgr = httputil.get_pool_manager(maxsize=maxsize, num_pools=num_pools)

    def get_client(self, host='localhost', username='default', password='password', **kwargs):
        return clickhouse_connect.get_client(host=host, username=username, password=password, pool_mgr=self.big_pool_mgr, **kwargs)
    
    @classmethod
    def set_pool(cls, maxsize=16, num_pools=2):
        if cls._instance is None:
            cls._instance = super(ClickClientPool, cls).__new__(cls)
            cls._instance._initialize(maxsize, num_pools)
        else:
            raise("Pool already exists")


## Usage
## ClickClientPool.set_pool(16, 2)
## ClickClientPool().get_client(agagag, agawg)
## ClickClientPool.set_pool(16, 2) -> "ERROR"
## database='github',
