# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymysql
from itemadapter import ItemAdapter
from scrapy import Item


class BBCnews_pipeline:
    def process_item(self, item, spider):
        self.insert_mysql(item)
        return item

    # 打开数据库
    def open_spider(self, spider):
        self.conn = pymysql.connect(host='127.0.0.1',
                                    port=3306,
                                    user='root',
                                    password='mfw990404',
                                    db='rec',
                                    charset='utf8mb4')
        # self.cursor = self.db.cursor(DictCursor)
        self.cursor = self.conn.cursor()
        self.ori_table = 'news_table'

    # 关闭数据库
    def close_spider(self, spider):
        print("关闭" + spider.name + "项目爬虫。。。")
        self.cursor.close()
        self.conn.close()
        # self.db_conn.connection_pool.disconnect()

    # 插入数据
    def insert_mysql(self, item):
        sql = '''insert into {0}  VALUES ('{1}','{2}','{3}','{4}') '''.format(self.ori_table,
                                                                              item.get(
                                                                                  'publish_time',
                                                                                  ''),
                                                                              pymysql.escape_string(item.get(
                                                                                  'title',
                                                                                  '')),
                                                                              pymysql.escape_string(
                                                                                  item.get(
                                                                                      'content',
                                                                                      '')),
                                                                              item.get('url',
                                                                                       ''))
        # print(sql)
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            print('写入成功')
        except BaseException as e:
            # print(e)
            print("异常sql:" + sql)
