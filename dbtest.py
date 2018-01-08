import pymysql.cursors

connection = pymysql.connect(host = "localhost",
                             user = "leon",
                             password = "on*AdImA{4",
                             db = "torstats",
                             charset="utf8mb4",
                             cursorclass = pymysql.cursors.DictCursor,
                             autocommit = True,
                             port = 3306)

if __name__ == "__main__":
    with connection.cursor() as cursor:
        help(cursor)