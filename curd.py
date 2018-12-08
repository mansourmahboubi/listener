# !/usr/bin/python3
# encoding: utf-8
from pymysql import (connect, cursors, escape_sequence)


class curd:

    def __init__(self, dbhost, dbuser, dbpwd, dbname, dbcharset='utf8mb4',
                 unix_socket="/var/run/mysqld/mysqld.sock", dbport=3306):
        self.dbhost = dbhost
        self.dbport = int(dbport)
        self.dbsocket = unix_socket
        self.dbuser = dbuser
        self.dbpwd = dbpwd
        self.dbname = dbname
        self.dbcharset = dbcharset
        self.connection = self.session()
        self.version()

    def session(self):
        connection = connect(
            host=self.dbhost,
            port=self.dbport,
            user=self.dbuser,
            password=self.dbpwd,
            db=self.dbname,
            charset=self.dbcharset,
            unix_socket=self.dbsocket,
            cursorclass=cursors.DictCursor)
        return connection

    def insert(self, table, data):
        with self.connection.cursor() as cursor:

            params = self.join_field_value(data)

            sql = "INSERT IGNORE INTO {table} SET {params}".format(
                table=table, params=params)

            cursor.execute(sql, tuple(data.values()))
            last_id = self.connection.insert_id()

            self.connection.commit()
            return last_id

    def bulk_insert(self, table, data):

        assert isinstance(data, list) and data != [], "data format is error"

        with self.connection.cursor() as cursor:

            params = []
            for param in data:
                params.append(escape_sequence(param.values(), 'utf-8'))

            values = ', '.join(params)
            fields = ', '.join('`{}`'.format(x) for x in param.keys())

            sql = "INSERT IGNORE INTO {table} ({fields}) VALUES {values}".format(
                fields=fields, table=table, values=values)

            cursor.execute(sql)
            last_id = self.connection.insert_id()

            self.connection.commit()
            return last_id

    def delete(self, table, condition=None, limit=None):
        """
        mysql delete() function
        sql.PreparedStatement method
        """
        with self.connection.cursor() as cursor:

            prepared = []

            if not condition:
                where = '1'
            elif isinstance(condition, dict):
                where = self.join_field_value(condition, ' AND ')
                prepared.extend(condition.values())
            else:
                where = condition

            limits = "LIMIT {limit}".format(limit=limit) if limit else ""

            sql = "DELETE FROM {table} WHERE {where} {limits}".format(
                table=table, where=where, limits=limits)

            if not prepared:
                result = cursor.execute(sql)
            else:
                result = cursor.execute(sql, tuple(prepared))

            self.connection.commit()
            return result

    def update(self, table, data, condition=None):
        """
        mysql update() function
        Use sql.PreparedStatement method
        """
        with self.connection.cursor() as cursor:

            prepared = []
            params = self.join_field_value(data)
            prepared.extend(data.values())

            if not condition:
                where = '1'
            elif isinstance(condition, dict):
                where = self.join_field_value(condition, ' AND ')
                prepared.extend(condition.values())
            else:
                where = condition

            sql = "UPDATE IGNORE {table} SET {params} WHERE {where}".format(
                table=table, params=params, where=where)

            # check PreparedStatement
            if not prepared:
                result = cursor.execute(sql)
            else:
                result = cursor.execute(sql, tuple(prepared))

            self.connection.commit()
            return result

    def count(self, table, condition=None):
        """
        count database record
        Use sql.PreparedStatement method
        """
        with self.connection.cursor() as cursor:

            prepared = []

            if not condition:
                where = '1'
            elif isinstance(condition, dict):
                where = self.join_field_value(condition, ' AND ')
                prepared.extend(condition.values())
            else:
                where = condition

            sql = "SELECT COUNT(*) as cnt FROM {table} WHERE {where}".format(
                table=table, where=where)

            if not prepared:
                cursor.execute(sql)
            else:
                cursor.execute(sql, tuple(prepared))

            self.connection.commit()
            return cursor.fetchone().get('cnt')

    def fetch_rows(self, table, fields=None, condition=None, order=None, limit=None, fetchone=False):
        """
        mysql select() function
        Use sql.PreparedStatement method
        """
        with self.connection.cursor() as cursor:

            prepared = []

            if not fields:
                fields = '*'
            elif isinstance(fields, tuple) or isinstance(fields, list):
                fields = '`{0}`'.format('`, `'.join(fields))
            else:
                fields = fields

            if not condition:
                where = '1'
            elif isinstance(condition, dict):
                where = self.join_field_value(condition, ' AND ')
                prepared.extend(condition.values())
            else:
                where = condition

            if not order:
                orderby = ''
            else:
                orderby = 'ORDER BY {order}'.format(order=order)

            limits = "LIMIT {limit}".format(limit=limit) if limit else ""

            sql = "SELECT {fields} FROM {table} WHERE {where} {orderby} {limits}".format(
                fields=fields, table=table, where=where, orderby=orderby, limits=limits)

            if not prepared:
                cursor.execute(sql)
            else:
                cursor.execute(sql, tuple(prepared))

            self.connection.commit()
            return cursor.fetchone() if fetchone else cursor.fetchall()

    def query(self, sql, fetchone=False, execute=False):
        with self.connection.cursor() as cursor:

            cursor.execute(sql)
            self.connection.commit()

            if execute:
                return

            return cursor.fetchone() if fetchone else cursor.fetchall()

    def join_field_value(self, data, glue=', '):
        sql = comma = ''
        for key in data.keys():
            sql += "{}`{}` = %s".format(comma, key)
            comma = glue
        return sql

    def __del__(self):
        if getattr(self, 'connection', 0):
            return self.connection.close()

    def version(self):
        data = self.query("select version()")
        for line in data:
            print("Database version : %s " % line['version()'])


if __name__ == '__main__':
    print("curd class")
