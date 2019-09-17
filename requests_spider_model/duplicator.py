
import time
from requests_spider_model.http import Request


class Duplicator:
    """
    请求指纹去重器
    """

    def __init__(self, redis_client, spider_name, ttl=86400 * 7, interval=600, duplicator_name='duplicator',
                 debug=False):
        """
        去重器构造方法

        Args:
            redis_client:redis连接
            spider_name: 爬虫名称
            ttl: 默认的请求指纹生命周期，单位s
            interval: 清理过期指纹的时间间隔
            duplicator_name: 去重器名称
            debug: 是否开启debug模式，开启将打印调试信息
        """
        self.client = redis_client
        self.duplicator_key = '{}:{}'.format(spider_name, duplicator_name)
        self.ttl = ttl
        self.interval = interval
        self.last_clean_time = 0
        self.debug = debug

    def request_seen(self, task: Request):
        """
        判断一个请求(task)是否在去重其中。
        若不存在，则将它的指纹加入到去重器中。

        Args:
            task:请求对象

        Returns:
            bool:是否重复

        """
        self.clean_expired_tasks()
        ttl = int(task.meta.get('ttl', self.ttl))
        fp = task.get_fingerprints()
        not_exsit_in_zset = self.client.zrank(self.duplicator_key, fp) is None
        fp_expire_time = self.client.zincrby(self.duplicator_key, 0, fp)
        if not_exsit_in_zset or (int(fp_expire_time) == 0) or (int(fp_expire_time) < int(time.time())):
            self.client.zadd(self.duplicator_key, {fp: int(time.time()) + ttl})
            if self.debug:
                if not_exsit_in_zset:
                    print("A new fingerprint is added to the collection.")
                else:
                    print("The expiration time of a fingerprint has been updated.")
            return False
        else:
            if self.debug:
                print("The fingerprint has not expired, skip this request.")
            return True

    def clean_expired_tasks(self):
        """
        清理去重器中的所有过期指纹

        Returns:
            None
        """
        current_time = int(time.time())
        if current_time - self.last_clean_time >= self.interval:
            x = self.client.zremrangebyscore(self.duplicator_key, 0, current_time)
            self.last_clean_time = current_time
            print('清理掉{}个过期指纹'.format(x))
