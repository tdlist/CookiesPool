
from gevent import monkey

monkey.patch_all()
import time
from gevent.pool import Pool
from requests_spider_model.queue import PropertyTaskQueue
from datetime import datetime
from requests_spider_model.pipeline import MongoPipeline
from redis import StrictRedis, ConnectionPool
from requests_spider_model.duplicator import Duplicator


class Counter:

    def __init__(self, data):
        self.maps = dict(data)
        self.cnt = {}

    def add(self, key, value=1):
        """
        对需要打印的项目数等内容, [0, 0] 第一个0表示总数, 第二个0表示每分钟数
        :param key:
        :param value:
        :return:
        """
        x = self.cnt.setdefault(key, [0, 0])
        x[0] += value
        x[1] += value

    def clean_per_min(self):
        for key in self.cnt.keys():
            self.cnt[key][1] = 0

    def __repr__(self):
        """
        重构打印方法, __repr__ 面向程序员, 控制台使用 print 调用 __repr__ 方法
        :return:
        """
        tmps = []
        for key, name in self.maps.items():
            total, per = self.cnt.get(key, [0, 0])
            tmps.append('{}{}({} new)'.format(name, total, per))
        return '统计：{}'.format(','.join(tmps))

    def __str__(self):
        """
        __str__ 面向用户, print 时默认调用 __str__ 方法
        :return:
        """
        return repr(self)


class BaseSpider:
    # 去重器默认过期时间
    ttl = 86400 * 7
    # 定期清理过期指纹的时间间隔
    interval = 600
    # 爬虫名称
    spider_name = 'base_spider'
    # 站点
    site = ''
    # mongo管道写入批大小
    mongo_batch_size = 100
    # 最大的出错次数
    max_error_limit = 40
    # 最大运行时间
    max_time_limit = 40 * 60
    # 使用的队列类型
    task_queue_class = PropertyTaskQueue
    # 使用数据管道的类型
    pipeline_class = MongoPipeline
    # redis_url
    redis_url = 'redis://:YINhang2018@47.95.214.108:7312/1'
    # 每次从队列中读取任务的数量
    read_tasks_size = 5
    # 并发池大小
    pool_size = 5
    # 是否显示错误信息
    log_error = True

    def __init__(self):
        self.client = StrictRedis(connection_pool=ConnectionPool.from_url(self.redis_url))
        self.task_queue = self.task_queue_class(self.client, self.spider_name)
        self.pipeline = self.pipeline_class(self.site, self.mongo_batch_size)
        self.duplicator = Duplicator(self.client, spider_name=self.spider_name, ttl=self.ttl, interval=self.interval)
        self.counter = Counter({'req': '请求数', 'item': '项目数', 'ingore': '忽略请求数'})
        self.error_cnt = 0

    @classmethod
    def log(cls, text):
        current_time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        print(current_time, text)

    def add_task(self, task):
        """
        将一个请求加入到任务队列中
        :param task:
        :return:
        """
        if task.dont_filter or not self.duplicator.request_seen(task):
            self.task_queue.add_task(task)

    def get_task(self, size=5):
        tasks = self.task_queue.get_task(size)
        return tasks

    def add_item(self, item):
        self.counter.add('item')
        self.pipeline.process_item(item)

    def close(self):
        self.pipeline.close()

    def log_counter(self):
        self.log(self.counter)
        self.counter.clean_per_min()

    def start_requests(self):
        pass

    def the_one_loop(self):
        task_size = self.task_queue.llen()
        last_time = datetime.today().timestamp()
        if task_size:
            self.log('当前队列大小{}...'.format(task_size))
            do_loop = True
        else:
            self.log('队列为空，开始推送初始url...')
            res = self.start_requests()
            if res is None:
                do_loop = True
            elif res:
                do_loop = True
            else:
                do_loop = False
        while do_loop:
            tasks = self.get_task(size=self.read_tasks_size)
            if not tasks:
                break
            error_done = False
            time_done = False
            pool = Pool(self.pool_size)
            for task in tasks:
                callback = getattr(self, task.callback)
                pool.spawn(callback, task)
                self.counter.add('req')
            pool.join(timeout=100)
            self.pipeline.flush_to_db()
            # 出错次数过多导致的退出
            if self.error_cnt > self.max_error_limit:
                error_done = True
            # 运行时间超出导致的退出
            tmp_time = datetime.today().timestamp()
            if tmp_time - self.start_time.timestamp() >= self.max_time_limit:
                time_done = True
            if tmp_time - last_time >= 60 or error_done or time_done:
                last_time = tmp_time
                self.log_counter()
            if error_done:
                self.log('被ban次数过多，准备关闭爬虫...')
                break
            if time_done:
                self.log('超出最大运行时间，准备关闭爬虫...')
                break

    def run(self):
        self.start_time = datetime.today()
        start_time_fmt = self.start_time.strftime('%Y-%m-%d %H:%M:%S')
        self.log('开启爬虫 {}'.format(self.spider_name))
        try:
            self.the_one_loop()
        except KeyboardInterrupt:
            self.log('手动终止了爬虫，正在关闭...')
        self.log_counter()
        self.close()
        self.log('关闭爬虫 {}'.format(self.spider_name))
        end_time = datetime.today()
        end_time_fmt = end_time.strftime('%Y-%m-%d %H:%M:%S')
        self.log('开启时间 {}'.format(start_time_fmt))
        self.log('关闭时间 {}'.format(end_time_fmt))
        self.log('总运行时间 {}'.format(end_time - self.start_time))
