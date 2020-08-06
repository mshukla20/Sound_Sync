import MySQLdb


class Database:

    def sql_insert(self, query):
        self.cursor.execute(query)
        self.conn.commit()

    def sql_query(self, query):
        self.cursor.execute(query)
        fetch_all =[]
        for row in self.cursor.fetchall():
            fetch_all.append(row[0])
        return fetch_all
    def __init__(self):
        try:
            self.conn = MySQLdb.connect(host='localhost',
                                db='musicsync',
                                user='root',
                                passwd='0306')
            if self.conn:
                print('Connected to MySQL database')
                self.cursor = self.conn.cursor()

        except Exception as e:
            print(str(e))