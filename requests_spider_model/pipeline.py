
from requests_spider_model.item import Item
import traceback
from requests_spider_model import utils


class MysqlPipeline:
    """
    mysql数据管道，将接收到的item批量写入到相应数据表中
    """

    def __init__(self, batch_size=100):
        """

        Args:
            batch_size: 批量写入的batch大小，默认100
        """
        self.batch_size = batch_size
        self.item_dict = {}
        self.conn = utils.get_local_conn('xxx')

    def write_to_db(self, table_name, items):
        """
        将数据批量写入到数据表中

        Args:
            table_name:数据表名称
            items: 待写入数据列表

        Returns:
            None
        """
        if len(items):
            record = items[0]
            keys = record.keys()
            tmps = ['{key}=values({key})'.format(key=key) for key in keys]
            sql = """
            insert into {}({}) values({}) on duplicate key update {}
            """.format(table_name,
                       ','.join(keys),
                       ','.join('%s' for _ in range(len(record))),
                       ','.join(tmps))
            records = [[item[key] for key in keys] for item in items]
            self.conn.ping()
            utils.executemany_sql(sql, params=records, conn=self.conn)
        else:
            print('数据列表为空，不需要写入！')

    def flush_to_db(self):
        """
        检查内存中缓存的待写入数据数量，当某个表对应的数据数量达到
        batch_size时，就将数据批量写入到数据表中，并清空掉这些数据
        Returns:
            None
        """
        for table_name, items in self.item_dict.items():
            if len(items) >= self.batch_size:
                try:
                    self.write_to_db(table_name, items)
                except Exception as e:
                    print('数据库写入失败！{}'.format(e.args))
                    traceback.print_exc()
                self.item_dict[table_name].clear()

    def close(self):
        """
        关闭数据管道

        先将剩余的待写入数据全部写入到数据库中，再关闭数据库连接

        Returns:

        """
        self.batch_size = 1
        self.flush_to_db()
        self.conn.close()

    def encode_item(self, item):
        """
        处理数据中的编码问题，将gbk不能编解码的数据剔除

        Args:
            item:数据项

        Returns:

        """
        for key, value in item.items():
            if isinstance(value, str):
                tmp_value = value.replace('）', ')').replace('（', '(').replace('【', '[').replace('】', ']')
                item[key] = tmp_value.encode('gbk', errors='ignore').decode('gbk', errors='ignore')
        return item

    def process_item(self, item: Item):
        """
        处理数据的入口，这里是将数据加入到待写入列表中

        Args:
            item:

        Returns:

        """
        item = self.encode_item(item)
        if item.check():
            self.item_dict.setdefault(item.table_name, []).append(item)
        else:
            print('数据异常，放弃！{}'.format(item))


class MongoPipeline:
    """
    mongo数据管道，将接收到的item批量写入到相应数据集合中
    """

    def __init__(self, site, batch_size=100):
        """
        Args:
            batch_size: 批量写入的batch大小，默认100
        """
        self.site = site
        self.batch_size = batch_size
        self.item_dict = {}
        self.client = utils.get_online_mongo_client()
        # self.client = utils.get_local_mongo_client()
        self.db_name = 'crawl_datastore_{}'.format(self.site)
        self.db = self.client[self.db_name]

    def write_to_db(self, collection, items):
        """
        将数据批量写入到数据表中
        Args:
            collection: 集合名称
            items: 待写入数据列表
        Returns:
            None
        """
        if len(items):
            self.db[collection].insert_many(items, ordered=False)
        else:
            print('数据列表为空，不需要写入！')

    def update_to_db(self, collection, items, index_list):
        """
        批量更新数据集合中的数据
        Args:
            collection: 集合名称
            items: 待写入数据列表
        Returns:
            None
        """
        if len(items):
            # 创建唯一索引
            self.db[collection].create_index([(index, 1) for index in index_list])  # 升序, pymongo.DSCENDING: 降序
            for item in items:
                data = item.data  # 注: item 是自定义类, 不是字典类型, item的data属性 才是item类携带的字典数据
                filter_dict = {}
                for index in index_list:
                    filter_dict[index] = data[index]
                try:
                    # 数据库中有则更新, 没有则插入
                    self.db[collection].update_one(filter_dict, {'$set': data}, True)
                except Exception as e:
                    traceback.print_exc()
        else:
            print('数据列表为空，不需要写入！')

    def process_item(self, item: Item):
        """
        处理数据的入口，这里是将数据加入到待写入列表中
        Args:
            item:
        Returns:
        """
        item = self.encode_item(item)
        if item.check():
            self.item_dict.setdefault(item.collection_name, []).append(item)
        else:
            print('数据异常，放弃！\n{}'.format(item.data))

    def flush_to_db(self):
        """
        检查内存中缓存的待写入数据数量，当某个表对应的数据数量达到
        batch_size时，就将数据批量写入到数据表中，并清空掉这些数据
        Returns:
            None
        """
        for collection, items in self.item_dict.items():
            if len(items) >= self.batch_size:
                try:
                    # md5去重
                    self.update_to_db(collection, items, ['hash_text', ])
                except Exception as e:
                    print('数据库写入失败！{}'.format(e.args))
                    traceback.print_exc()
                self.item_dict[collection].clear()

    def encode_item(self, item):
        """
        处理数据中的编码问题，将gbk不能编解码的数据剔除
        Args:
            item:数据项
        Returns:
        """
        for key, value in item.items():
            if isinstance(value, str):
                tmp_value = value.replace('）', ')').replace('（', '(').replace('【', '[').replace('】', ']')
                item[key] = tmp_value.encode('gbk', errors='ignore').decode('gbk', errors='ignore')
        return item

    def close(self):
        """
        关闭数据管道
        先将剩余的待写入数据全部写入到数据库中，再关闭数据库连接
        Returns:
        """
        self.batch_size = 1
        self.flush_to_db()
        self.client.close()
