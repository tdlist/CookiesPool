
from collections import UserDict


class LimitDict(UserDict):
    """
    限制了可选择key的字典

    当使用`LimitDict.from_limit_keys(cls, default_data)`创建字典对象时，
    将会使用default_data初始化字典对象，且字典对象只能修改现有key的值，不能添加新的key
    """

    limit_keys = set()

    @classmethod
    def from_limit_keys(cls, default_data):
        """
        使用default_data创建并初始化字典对象

        Args:
            default_data:默认映射对象，用以创建并初始化当前对象

        Returns:
            LimitDict:一个限制了key的LimitDict对象
        """
        ld = cls()
        ld.limit_keys = set(default_data.keys())
        ld.update(default_data)
        return ld

    def __setitem__(self, key, value):
        """
        重写设置key->value的方法，当key在初始key集合中时，允许本次修改，
        否则，抛出AttributeError
        Args:
            key: 键
            value: 值

        Returns:

        """
        if key in self.limit_keys:
            self.data[key] = value
        else:
            raise AttributeError('{}没有属性{}！'.format(getattr(getattr(self, '__class__'), '__name__'), key))


class Item:
    """
    参照scrapy中item的思路实现的Item类，用于封装数据对象。

    子Item类只需要集成Item类即可实现对item属性的控制，只能存取声明过的属性，
    且外部操作方法与scrapy中的Item类类似。
    """

    table_name = ''  # Mysql 数据表名，item对象将被写入到该表中

    collection_name = ''  # Mongo 数据集合名, Item 对象将被写入到该集合中

    insert_method = ''  # 写入数据表方法，目前暂未实现，默认使用insert into ... on duplicate key ... update ...

    data = None  # LimitDict对象，存放数据的地方
    # 默认字典，需要在子类中覆盖
    default_data = {}  # LimitDict对象，存放数据的地方

    def __init__(self):
        self.data = LimitDict.from_limit_keys(self.default_data)

    def __setitem__(self, key, value):
        """
        将键值存写操作委托给self.data对象

        当键不存在默认字典的keys里时则抛出AttributeError

        Args:
            key:键
            value:值

        Returns:

        """
        try:
            self.data[key] = value
        except AttributeError:
            raise AttributeError('{}没有属性{}！'.format(getattr(getattr(self, '__class__'), '__name__'), key))

    def __getitem__(self, item):
        """
        将键值读取操作委托给self.data对象

        Args:
            item:键

        Returns:
            self.data[item]
        """

        return self.data[item]

    def __len__(self):
        """
        委托len方法给self.data

        Returns:

        """
        return len(self.data)

    def __contains__(self, item):
        """
        委托`in`操作给self.data

        Args:
            item: 键

        Returns:
            bool:键是否存在于self.data中
        """
        return item in self.data

    def update(self, *args, **kwargs):
        """
        委托update方法给self.data

        Args:
            *args:
            **kwargs:

        Returns:

        """
        self.data.update(*args, **kwargs)

    def items(self):
        """
        委托items方法给self.data

        Returns:

        """
        return self.data.items()

    def keys(self):
        """
        委托keys方法给self.data

        Returns:

        """
        return self.data.keys()

    def clean_data(self):
        """
        清洗数据，通过实现名为`_check_attr`的方法，
        来自动化地清洗所有需要清洗的数据项

        Returns:
            None
        """
        for key in self.keys():
            method = '_clean_{}'.format(key)
            if hasattr(self, method):
                getattr(self, method)()

    def check_data(self):
        """
        判断数据是否合法

        默认恒为True，子类根据实际情况决定是否重写

        Returns:
            bool:是否合法

        """
        return True

    def check(self):
        """
        先清洗数据，再检查数据是否合法

        Returns:
            bool:是否合法
        """
        self.clean_data()
        return self.check_data()

    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, repr(self.data))
    

if __name__ == '__main__':
    x = Item()
    print(x.keys())
