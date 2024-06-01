import pymysql

# MySQL数据库配置
MYSQL_HOST = '47.97.118.247'
MYSQL_USER = 'root'
MYSQL_PASSWORD = 'sober123456'
MYSQL_DATABASE = 'psl'


# 连接到 MySQL 数据库
connection = pymysql.connect(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database=MYSQL_DATABASE,
    cursorclass=pymysql.cursors.DictCursor
)

