# -*- coding: utf-8 -*-
# @File  : queue.py
# @Author: AaronJny
# @Date  : 2019/04/19
# @Desc  :

from requests_spider_model.http import Request


class TaskQueue:
    """
    任务队列
    """

    def add_task(self, task: Request):
        """
        添加一个任务到任务队列中

        Args:
            task: 要加入的任务

        Returns:
            None
        """
        raise NotImplementedError

    def get_task(self, size):
        """
        从任务队列中，获取指定数量(size)的任务，并从队列中删除它们

        Args:
            size: 任务数量

        Returns:
            list[Request]: Request对象组成的列表
        """
        raise NotImplementedError

    def clean_queue(self):
        """
        清空任务队列

        Returns:
            None
        """
        raise NotImplementedError

    def llen(self):
        """
        获取任务队列的长度

        Returns:
            int: 表示任务队列的长度
        """
        raise NotImplementedError


class FIFOTaskQueue(TaskQueue):
    """
    先进先出的任务队列
    """

    def __init__(self, redis_client, spider_name, queue_name='requests'):
        self.redis_client = redis_client
        self.task_queue_key = '{}:{}'.format(spider_name, queue_name)

    def add_task(self, task: Request):
        self.redis_client.lpush(self.task_queue_key, task.to_json())

    def _get_task(self):
        task_json = self.redis_client.lpop(self.task_queue_key)
        if task_json:
            task = Request.from_json(task_json)
        else:
            task = None
        return task

    def get_task(self, size):
        tasks = []
        for i in range(size):
            task = self._get_task()
            if task:
                tasks.append(task)
            else:
                break
        return tasks

    def clean_queue(self):
        self.redis_client.delete(self.task_queue_key)

    def llen(self):
        return self.redis_client.llen(self.task_queue_key)


class PropertyTaskQueue(TaskQueue):
    """
    具有优先级的任务队列
    """

    def __init__(self, redis_client, spider_name, queue_name='requests'):
        self.redis_client = redis_client
        self.task_queue_key = '{}:{}'.format(spider_name, queue_name)

    def add_task(self, task: Request):
        self.redis_client.zadd(self.task_queue_key, {task.to_json(): - task.property})

    def _get_task(self):
        pipe = self.redis_client.pipeline()
        pipe.multi()
        pipe.zrange(self.task_queue_key, 0, 0).zremrangebyrank(self.task_queue_key, 0, 0)
        results, count = pipe.execute()
        if results:
            task_json = results[0]
            if task_json:
                task = Request.from_json(task_json)
            else:
                task = None
            return task

    def get_task(self, size):
        tasks = []
        for i in range(size):
            task = self._get_task()
            if task:
                tasks.append(task)
            else:
                break
        return tasks

    def clean_queue(self):
        self.redis_client.delete(self.task_queue_key)

    def llen(self):
        """
        获取任务队列的长度
        :return:
        """
        return self.redis_client.zcard(self.task_queue_key)
