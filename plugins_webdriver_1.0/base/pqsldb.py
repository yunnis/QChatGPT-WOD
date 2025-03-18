import psycopg
import traceback

from pkg.plugin.context import BasePlugin, APIHost, EventContext

# 数据库连接参数
dbname = 'wodreport'
user = 'postgres'
password = ' '
host = 'localhost'  # 或者你指定的数据库主机
port = '5432'       # PostgreSQL 默认端口

class Pdb(object):
    __cursor = None # 数据库游标
    __connection = None # 连接
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super(Pdb, cls).__new__(cls)
        return cls.__instance

    @classmethod
    def get_instance(self):
        return self.__instance

    def __init__(self):
        if self.__connection == None:
            print("\ninit postgreSQL connect\n")
            try:
            # 建立数据库连接
                self.__connection = psycopg.connect(
                    dbname=dbname,
                    user=user,
                    password=password,
                    host=host,
                    port=port
                )
                self.__cursor = self.__connection.cursor()

            except Exception as e:
                print(f"\nconnect psql failed, str:{e} ! \n")

    def __del__(self):
        if self.__cursor:
            self.__cursor.close()
            print("cursor closed.")
        if self.__connection:
            self.__connection.close()
            print("Connection closed.")
        super().__del__()

    def exec_one(self, code, params: psycopg.cursor.Params | None = None):
        try:
            self.__cursor.execute(code, params)
            return self.__cursor.fetchone()
        except Exception as e:
            print(f'\n exec_no_fetch failed & rollback, e: {e}')
            self.__connection.rollback()
            return None
    
    def exec_all(self, code, params: psycopg.cursor.Params | None = None):
        try:
            self.__cursor.execute(code, params)
            return self.__cursor.fetchall()
        except Exception as e:
            print(f'\n exec_no_fetch failed & rollback, e: {e}')
            self.__connection.rollback()
            return None

    def exec_many(self, code, count, params: psycopg.cursor.Params | None = None):
        try:
            self.__cursor.execute(code, params)
            return self.__cursor.fetchmany(count)
        except Exception as e:
            print(f'\n exec_no_fetch failed & rollback, e: {e}')
            self.__connection.rollback()
            return None

    def exec_no_fetch(self, code, params: psycopg.cursor.Params | None = None):
        try:
            self.__cursor.execute(code, params)
            print("插入成功，受影响的行数:", self.__cursor.rowcount)  # 输出受影响的行数
            return True
        except Exception as e:
            print(f'\n exec_no_fetch failed & rollback, e: {e}')
            self.__connection.rollback()
            return None

    def commit(self):
        self.__connection.commit()  # 提交事务

    def insert(self):
        pass


# try:
#     # 建立数据库连接
#     connection = psycopg2.connect(
#         dbname=dbname,
#         user=user,
#         password=password,
#         host=host,
#         port=port
#     )

#     cursor = connection.cursor()

#     # 执行查询
#     cursor.execute("SELECT version();")
#     db_version = cursor.fetchone()
#     print(f"PostgreSQL Database Version: {db_version}")
#     #等效\d 因为psycopg2 不能执行psql命令
#     cursor.execute("""
#         SELECT table_name 
#         FROM information_schema.tables 
#         WHERE table_schema = 'public';
#     """)
#     db_version = cursor.fetchone()
#     print(f"PostgreSQL Database Version: {db_version}")
    
    # table_name = 'abilities'
    # # 查询特定表的列信息
    # cursor.execute("""
    #     SELECT column_name, data_type, is_nullable
    #     FROM information_schema.columns
    #     WHERE table_name = %s;
    # """, (table_name,))
    
    # columns = cursor.fetchall()
    
    # # 输出表的列信息
    # print(f"Columns {len(columns)} in table '{table_name}':")
    # for column in columns:
    #     print(f"Column Name: {column[0]}, Data Type: {column[1]}, Is Nullable: {column[2]}, len of this col: {len(column)}")
    
# except Exception as e:
#     print(f"Error occurred: {e}")

# finally:
#     # 关闭数据库连接
#     if cursor:
#         cursor.close()
#     if connection:
#         connection.close()
#     print("Connection closed.")
