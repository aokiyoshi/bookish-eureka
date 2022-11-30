from collections import OrderedDict
from itertools import chain
import os
import sqlite3
import unittest
from contextlib import ContextDecorator

from attr import dataclass

from common.settings import DATABASE_NAME


class DatabaseConnection(ContextDecorator):
    def __init__(self, database_name):
        self.database_name = database_name

    def __enter__(self):
        self.sqlite_connection = sqlite3.connect(self.database_name)
        return self.sqlite_connection.cursor()

    def __exit__(self, *exc):
        if self.sqlite_connection:
            self.sqlite_connection.close()


class TableManager:
    conn = DatabaseConnection

    def __init__(self, table_name, db, **kwargs):
        # Параметры
        self.db = db
        self.table_name = table_name
        self.types = OrderedDict(**kwargs)
        self.foreign_keys = []
        # Генерируем типы для SQL
        for key, val in self.types.items():
            if isinstance(val, str):
                self.types[key] = val.upper()
            elif hasattr(val, 'table_name'):
                self.types[key] = 'INTEGER'
                self.foreign_keys.append(
                    f'FOREIGN KEY({key}) REFERENCES {val.table_name}(id)')
            else:
                raise TypeError
        # Создаем и закрываем подключение, чтобы создалась база
        with self.conn(self.db) as db:
            pass

    def create_table(self):
        """
        Создать таблицу
        """
        vals = ', '.join([f'{key} {val}' for key, val in self.types.items()])
        foreigns = ', ' + \
            ', '.join(self.foreign_keys) if self.foreign_keys else ''
        command = f'CREATE TABLE IF NOT EXISTS {self.table_name} ( id INTEGER PRIMARY KEY, {vals}{foreigns})'
        with self.conn(self.db) as db:
            db.executescript(command)

        return self

    def serialize(self, data):
        return [{key: value for key, value in zip(chain(('id',), self.types.keys()), data_tuple)} for data_tuple in data]

    def insert(self, **kwargs):
        colums = ', '.join([f'"{key}"' for key in kwargs.keys()])
        values = ', '.join([f'"{val}"' for val in kwargs.values()])
        command = f'INSERT INTO {self.table_name} ({colums}) values({values});'
        with self.conn(self.db) as db:
            db.executescript(command)

        return self

    def select(self, *args, **kwargs):
        conds = ' AND '.join([f'{cond}' for cond in args])
        args = ' AND '.join(['{} = {!r}'.format(k, v)
                             for k, v in kwargs.items()])
        command = f'SELECT * FROM {self.table_name} WHERE {args}{conds};'
        print(f'{command=}')
        with self.conn(self.db) as db:
            db.execute(command)
            return self.serialize(db.fetchall())

    def select_all(self):
        with self.conn(self.db) as db:
            db.execute(f'SELECT * FROM {self.table_name};')
            return self.serialize(db.fetchall())

    def select_when_id_greater(self, id):
        """
        Специфичная для некоторых нужд функция
        Выбор всех строк, если id больше
        """
        with self.conn(self.db) as db:
            db.execute(f'SELECT * FROM {self.table_name} WHERE id>{id};')
            return self.serialize(db.fetchall())

    def update(self, new_data: dict, **kwargs):
        values = ', '.join(['{} = "{}"'.format(k, v)
                            for k, v in new_data.items()])
        cond = ' AND '.join(['{}.{} = "{}"'.format(self.table_name, k, v)
                             for k, v in kwargs.items()])
        command = f'UPDATE {self.table_name} SET {values} WHERE {cond};'
        print(f"{command=}")
        with self.conn(self.db) as db:
            db.executescript(command)


class User(TableManager):
    table_name = 'users'

    def __init__(self, db):
        super().__init__(table_name=self.table_name, db=db,
                         username='TEXT', info='TEXT', msg_read_date='TEXT')

    def get_msgs_read_date(self, username):
        return self.select(username=username)[0].get("msg_read_date", None)

    def update_msg_read_datex(self, date, user):
        self.update({'msg_read_date': date}, username=user)

    def get_user_id_by_name(self, name):
        return self.select(username=name)[-1].get('id', None)

    def get_by_id(self, uid):
        return self.select(id=uid)[0]


class ClientHistory(TableManager):
    table_name = 'client_history'

    def __init__(self, db):
        super().__init__(table_name=self.table_name,
                         db=db, login_date='INTEGER', ip_addr='TEXT')

    def insert(self, login_date, ip_addr):
        return super().insert(login_date=login_date, ip_addr=ip_addr)


class Message(TableManager):
    table_name = 'messages'

    def __init__(self, db):
        super().__init__(
            table_name=self.table_name,
            db=db,
            user='TEXT',
            message='TEXT',
            date='INTEGER'
        )

    def append(self, data):
        self.insert(**data)

    def __len__(self):
        return len(self.select_all())

    def get_after(self, date):
        command = f'SELECT * from {self.table_name} where {self.table_name}.date > "{date}"'
        print(f"{command=}")
        with self.conn(self.db) as db:
            db.execute(command)
            return self.serialize(db.fetchall())


class Contact(TableManager):
    table_name = 'contacts'

    def __init__(self, db):
        super().__init__(
            table_name=self.table_name, 
            db=db, 
            owner_id=User, 
            client_id=User
        )

    def insert(self, owner_id, client_id):
        return super().insert(owner_id=owner_id, client_id=client_id)


class Database:
    def __init__(self, db=DATABASE_NAME):
        self._db = db
        self.users = User(self._db).create_table()
        self.history = ClientHistory(self._db).create_table()
        self.contacts = Contact(self._db).create_table()
        self.messages = Message(self._db).create_table()

    def add_user(self, data):
        self.users.insert(**data)


# Тесты

class TestConnManager(unittest.TestCase):

    def setUp(self):
        self.db = 'testdb.db'
        with DatabaseConnection(self.db) as db:
            db.execute('create table test (id INTEGER, test INTEGER)')

    def test_create_db(self):
        self.assertTrue(os.path.isfile(self.db))

    def test_insert(self):
        with DatabaseConnection(self.db) as db:
            db.executescript('insert into test values (1, 1);')
            data = db.execute('select * from test').fetchone()
        self.assertEqual(data, (1, 1))

    def tearDown(self):
        os.remove(self.db)


class TestTableManager(unittest.TestCase):
    def setUp(self):
        self.db = 'test.db'
        self.tb = TableManager(
            table_name='test', db=self.db, name='TEXT', a='TEXT'
        ).create_table()

    def test_create_db_and_table(self):
        self.assertTrue(os.path.isfile(self.db))
        self.assertEqual(self.tb.select_all(), [])

    def test_insert(self):
        self.tb.insert(name='lorem', a='2')
        self.assertEqual(self.tb.select_all(), [
                         dict(id=1, name='lorem', a='2')])

    def test_select_positive(self):
        self.tb.insert(name='lorem', a='2')
        self.assertEqual(self.tb.select(id=1), [
                         dict(id=1, name='lorem', a='2')])
        self.assertEqual(self.tb.select(name='lorem'), [
                         dict(id=1, name='lorem', a='2')])

    def test_select_negative(self):
        self.tb.insert(name='lorem')
        self.assertEqual(self.tb.select(id=99), [])
        self.assertEqual(self.tb.select(name='not lorem'), [])

    def test_update(self):
        self.tb.insert(name='lorem', a='')
        self.tb.update({'name': 'new name', 'a': 'new a'}, id=1)
        self.assertEqual(self.tb.select_all(), [
                         dict(id=1, name='new name', a='new a')])

    def tearDown(self):
        os.remove(self.db)


class TestUsers(unittest.TestCase):
    def setUp(self):
        self.db = 'test.db'

    def test_insert(self):
        self.users = User(db='test.db').create_table()
        self.users.insert(username='test', info='lorem')
        self.assertEqual(self.users.select_all(), [dict(
            id=1, username='test', info='lorem', last_read_msg=0)])

    def tearDown(self):
        os.remove(self.db)


class TestContacts(unittest.TestCase):
    def setUp(self):
        self.db = 'test.db'

    def test_insert(self):
        self.contacts = Contact(db='test.db').create_table()
        self.contacts.insert(owner_id=1, client_id=1)
        self.assertEqual(self.contacts.select_all(), [
                         dict(id=1, owner_id=1, client_id=1)])

    def tearDown(self):
        os.remove(self.db)


class TestHistory(unittest.TestCase):
    def setUp(self):
        self.db = 'test.db'

    def test_insert(self):
        self.history = ClientHistory(db='test.db').create_table()
        self.history.insert(login_date=100000, ip_addr='127.0.0.1')
        self.assertEqual(self.history.select_all(), [dict(
            id=1, login_date=100000, ip_addr='127.0.0.1')])

    def tearDown(self):
        os.remove(self.db)


if __name__ == '__main__':
    unittest.main()


@dataclass
class Foo:
    pass
