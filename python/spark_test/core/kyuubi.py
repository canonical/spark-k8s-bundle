# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.

from contextlib import contextmanager
from typing import Type

from pyhive.hive import Connection

TYPES = {int: "int", str: "string"}

ITYPES = {v: k for k, v in TYPES.items()}

SchemaType = Type[int | str]


class TableExists(Exception):
    pass


class TableNotFound(Exception):
    pass


class KyuubiClient:

    def __init__(self, username: str, password: str, host: str, port: int = 10009):
        self.username = username
        self.password = password
        self.host = host
        self.port = port

    @property
    @contextmanager
    def connection(self) -> Connection:
        conn = Connection(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            auth="CUSTOM",
        )
        yield conn
        conn.close()

    @property
    def databases(self):
        with self.connection as conn, conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES;")
            results = cursor.fetchall()
            return [result[0] for result in results]

    def get_database(self, name: str):
        with self.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {name};")

            return Database(name, self)


class Database:

    def __init__(self, name: str, client: KyuubiClient):
        self.client = client
        self.name = name

    @property
    def tables(self):
        with self.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"USE {self.name};")
            cursor.execute("SHOW TABLES;")
            results = cursor.fetchall()
            return [result[1] for result in results]

    def get_table(self, name: str):
        if name not in self.tables:
            raise TableNotFound()

        with self.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"DESCRIBE {self.name}.{name}")
            schema = [(str(value[0]), ITYPES[value[1]]) for value in cursor.fetchall()]
            return Table(name, self, schema)

    def drop(self):
        with self.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"DROP DATABASE {self.name};")

    def create_table(self, name: str, schema: list[tuple[str, SchemaType]]):
        if name in self.tables:
            raise TableExists(name)

        with self.client.connection as conn, conn.cursor() as cursor:
            schema_str = ", ".join(
                f"{col_name} {TYPES[_type]}" for col_name, _type in schema
            )
            cursor.execute(f"CREATE TABLE {self.name}.{name} ({schema_str});")

            return Table(name, self, schema)


class Table:

    def __init__(
        self, name: str, database: Database, schema: list[tuple[str, SchemaType]]
    ):
        self.name = name
        self.database = database
        self.schema = schema

    def validate(self, values: list[SchemaType]):
        output = {}

        for value, (col_name, _type) in zip(values, self.schema):
            if not isinstance(value, _type):
                raise TypeError(
                    f"Column {col_name}: Expected {_type}, " f"found {type(value)}"
                )
            output[col_name] = value

        return output

    def drop(self):
        with self.database.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"DROP TABLE {self.database.name}.{self.name};")

    def rows(self):
        with self.database.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.database.name}.{self.name}")

            for row in cursor.fetchall():
                yield self.validate(row)

    def parse_value(self, value: SchemaType):
        match value:
            case int():
                return str(value)
            case str():
                return f'"{value}"'
            case _:
                raise TypeError(type(value))

    def _parse_row(self, row: list[SchemaType]):

        _ = self.validate(row)

        return "(" + ",".join(self.parse_value(value) for value in row) + ")"

    def _parse_rows(self, rows: list[list[SchemaType]]):
        return ", ".join(self._parse_row(row) for row in rows)

    def insert(self, *rows: list[SchemaType]):
        with self.database.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {self.database.name}.{self.name} "
                f"VALUES {self._parse_rows(list(rows))};"
            )
