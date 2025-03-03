# Copyright 2024 Canonical Ltd.
# See LICENSE file for licensing details.
"""Kyuubi module."""

from contextlib import contextmanager
from typing import Iterable, Type, TypeAlias

from pyhive.hive import Connection

TYPES = {int: "int", str: "string"}

ITYPES = {v: k for k, v in TYPES.items()}

DataType: TypeAlias = int | str
SchemaType: TypeAlias = Type[DataType]


class TableExists(Exception):
    """Exception from table already exists."""

    pass


class TableNotFound(Exception):
    """Exception for table not found."""

    pass


class KyuubiClient:
    """Kyuubi client."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 10009,
        username: str | None = None,
        password: str | None = None,
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    @property
    @contextmanager
    def connection(self) -> Iterable[Connection]:
        """Instantiate connection."""
        params = {"host": self.host, "port": self.port}
        if self.username:
            params.update({"username": self.username})
        if self.password:
            params.update({"password": self.password, "auth": "CUSTOM"})
        conn = Connection(**params)
        yield conn
        conn.close()

    @property
    def databases(self):
        """List databases."""
        with self.connection as conn, conn.cursor() as cursor:
            cursor.execute("SHOW DATABASES;")
            results = cursor.fetchall()
            return [result[0] for result in results]

    def get_database(self, name: str):
        """Get database from name."""
        with self.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {name};")

            return Database(name, self)


class Database:
    """Kyuubi database."""

    def __init__(self, name: str, client: KyuubiClient):
        self.client = client
        self.name = name

    @property
    def tables(self):
        """List tables in database."""
        with self.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"USE {self.name};")
            cursor.execute("SHOW TABLES;")
            results = cursor.fetchall()
            return [result[1] for result in results]

    def get_table(self, name: str):
        """Get table from name."""
        if name not in self.tables:
            raise TableNotFound()

        with self.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"DESCRIBE {self.name}.{name}")
            schema = [(str(value[0]), ITYPES[value[1]]) for value in cursor.fetchall()]
            return Table(name, self, schema)

    def drop(self):
        """Drop database."""
        with self.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"DROP DATABASE {self.name};")

    def create_table(self, name: str, schema: list[tuple[str, SchemaType]]):
        """Create table from name and schema."""
        if name in self.tables:
            raise TableExists(name)

        with self.client.connection as conn, conn.cursor() as cursor:
            schema_str = ", ".join(
                f"{col_name} {TYPES[_type]}" for col_name, _type in schema
            )
            cursor.execute(f"CREATE TABLE {self.name}.{name} ({schema_str});")

            return Table(name, self, schema)


class Table:
    """Kyuubi table."""

    def __init__(
        self, name: str, database: Database, schema: list[tuple[str, SchemaType]]
    ):
        self.name = name
        self.database = database
        self.schema = schema

    def validate(self, values: list[DataType]):
        """Validate values."""
        output = {}

        for value, (col_name, _type) in zip(values, self.schema, strict=False):
            if not isinstance(value, _type):
                raise TypeError(
                    f"Column {col_name}: Expected {_type}, found {type(value)}"
                )
            output[col_name] = value

        return output

    def drop(self):
        """Drop table."""
        with self.database.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"DROP TABLE {self.database.name}.{self.name};")

    def rows(self):
        """Iterate over rows."""
        with self.database.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(f"SELECT * FROM {self.database.name}.{self.name}")

            for row in cursor.fetchall():
                yield self.validate(row)

    def parse_value(self, value: DataType):
        """Convert value to str."""
        match value:
            case int():
                return str(value)
            case str():
                return f'"{value}"'
            case _:
                raise TypeError(type(value))

    def _parse_row(self, row: list[DataType]):
        _ = self.validate(row)

        return "(" + ",".join(self.parse_value(value) for value in row) + ")"

    def _parse_rows(self, rows: list[list[DataType]]):
        return ", ".join(self._parse_row(row) for row in rows)

    def insert(self, *rows: list[DataType]):
        """Insert rows."""
        with self.database.client.connection as conn, conn.cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {self.database.name}.{self.name} "
                f"VALUES {self._parse_rows(list(rows))};"
            )
