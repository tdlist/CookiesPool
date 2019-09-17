# -*- coding: utf-8 -*-
# @File  : http.py
# @Author: AaronJny
# @Date  : 2019/04/19
# @Desc  :

import json
import hashlib


class Request:
    """
    封装一次请求需要的所有信息的类
    """

    def __init__(self, url, requests_args=None, meta=None, callback='', property=0, dont_filter=False, timeout=20):
        """

        Args:
            url(str):需要请求的链接
            requests_args(dict):请求附加参数，用于使用requests库进行定制请求，默认{}
            meta(dict): 两次请求之间传递的参数，要求可以直接被json序列化，默认{}
            callback(method or str): 请求的回调方法的名称或者方法对象
            property(int): 优先级，数值越大越优先，默认0
            dont_filter(bool): 是否不进行去重，默认去重
            timeout(int): 请求超时时间，默认20s
        """
        if requests_args:
            self.requests_args = requests_args
        else:
            self.requests_args = {}
        self.requests_args['url'] = url
        self.requests_args['timeout'] = timeout
        if meta:
            self.meta = meta
        else:
            self.meta = {}
        self.url = url
        self.timeout = timeout
        if callback:
            if isinstance(callback, str):
                self.callback = callback
            else:
                self.callback = callback.__name__
        else:
            raise AttributeError("Request对象必须指定回调方法callback!")
        self.property = property
        self.dont_filter = dont_filter

    def get_fingerprints(self):
        """
        根据Request对象的相关信息，计算并返回它的指纹

        Returns:
            str:Request对象的指纹
        """
        url = self.url
        if isinstance(url, str):
            url = url.encode('utf8')
        fingerprints = hashlib.md5(url).hexdigest()
        return fingerprints

    def to_json(self):
        """
        将请求数据转化成json

        Returns:
            str:包含了请求对象全部信息的json字符串
        """
        text = json.dumps({
            'requests_args': self.requests_args,
            'meta': self.meta,
            'url': self.url,
            'callback': self.callback,
            'property': self.property,
            'dont_filter': self.dont_filter,
            'timeout': self.timeout
        })
        return text

    @classmethod
    def from_json(cls, text):
        """
        使用json数据创建Request对象

        Args:
            text:json形式的字符串，表示一个Request对象的全部信息

        Returns:
            Request:使用text恢复出来的Request对象
        """
        data = json.loads(text)
        return Request(**data)


class Response:
    """
    封装一次响应需要的所有信息的类，暂时未使用到
    """

    def __init__(self, request, content, status_code, url):
        self.request = request
        self.content = content
        self.status_code = status_code
        self.url = url

    def json(self):
        return json.loads(self.content)

    def to_json(self):
        data = {
            'request': self.request.to_json(),
            'content': self.content,
            'status_code': self.status_code,
            'url': self.url,
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, text):
        data = json.loads(text)
        data['request'] = Request.from_json(data['request'])
        return Response(**data)
