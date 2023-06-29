from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import mysql.connector
from twisted.web import resource, server
from twisted.web.server import Request


def create_db(db: str) -> mysql.connector.MySQLConnection:
    mydb = mysql.connector.connect(host="localhost", user="costantino", password="MoxOpal{0}")
    cursor = mydb.cursor()
    cursor.execute(f"CREATE DATABASE {db}")
    return mydb


def connect(db: str) -> mysql.connector.MySQLConnection:
    mydb = mysql.connector.connect(host="localhost", user="costantino", password="MoxOpal{0}", database=db)
    return mydb


def db_exists(db: str) -> bool:
    try:
        _ = connect(db)
        return True
    except mysql.connector.errors.ProgrammingError:
        return False


def create_table(db: str, table: str, columns: list[str]) -> None:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"CREATE TABLE {table} ({', '.join(columns)})")


def table_exists(db: str, table: str) -> bool:
    mydb = connect(db)
    cursor = mydb.cursor()
    try:
        cursor.execute(f"SHOW TABLES LIKE '{table}'")
        return bool(cursor.fetchall())
    except mysql.connector.errors.ProgrammingError:
        return False


def insert(db: str, table: str, columns: list[str], values: list[str]) -> None:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)})")
    mydb.commit()


def select(db: str, table: str, columns: list[str], where: str) -> list[tuple]:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"SELECT {', '.join(columns)} FROM {table} WHERE {where}")
    return cursor.fetchall()


def select_all(db: str, table: str, columns: list[str]) -> list[tuple]:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"SELECT {', '.join(columns)} FROM {table}")
    return cursor.fetchall()


def update(db: str, table: str, columns: list[str], values: list[str], where: str) -> None:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"UPDATE {table} SET {', '.join([f'{c} = {v}' for c, v in zip(columns, values)])} WHERE {where}")
    mydb.commit()


def delete(db: str, table: str, where: str) -> None:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"DELETE FROM {table} WHERE {where}")
    mydb.commit()


def delete_all(db: str, table: str) -> None:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"DELETE FROM {table}")
    mydb.commit()


def drop_table(db: str, table: str) -> None:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"DROP TABLE {table}")
    mydb.commit()


def drop_db(db: str) -> None:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"DROP DATABASE {db}")
    mydb.commit()


def reset() -> None:
    if db_exists("hacknslassh"):
        drop_db("hacknslassh")
    create_cats_table()
    create_players_table()


def create_cats_table() -> None:
    if not db_exists("hacknslassh"):
        print("Creating hacknslassh database...")
        create_db("hacknslassh")
    if not table_exists("hacknslassh", "cats"):
        print("Creating cats table...")
        create_table(
            "hacknslassh",
            "cats",
            [
                "id CHAR(32) PRIMARY KEY",
                "name VARCHAR(20)",
                "age SMALLINT",
                "gender BOOLEAN",
                "description VARCHAR(128)",
                "red SMALLINT",
                "green SMALLINT",
                "blue SMALLINT",
                "owner VARCHAR(32)",
                "rarity SMALLINT",
            ],
        )


def create_players_table() -> None:
    if not db_exists("hacknslassh"):
        print("Creating hacknslassh database...")
        create_db("hacknslassh")
    if not table_exists("hacknslassh", "players"):
        print("Creating players table...")
        create_table(
            "hacknslassh",
            "players",
            [
                "id CHAR(32) PRIMARY KEY",
                "name VARCHAR(20)",
                "age SMALLINT",
                "gender BOOLEAN",
                "gameclass VARCHAR(20)",
                "red SMALLINT",
                "green SMALLINT",
                "blue SMALLINT",
            ],
        )


def get_all_cats() -> list[tuple]:
    return select_all("hacknslassh", "cats", ["*"])


def get_all_players() -> list[tuple]:
    return select_all("hacknslassh", "players", ["*"])


def get_owner_cats(owner: str) -> list[tuple]:
    ...


class SQLConnectorServer(resource.Resource):
    isLeaf = True

    def render_OPTIONS(self, request: Request) -> bytes:
        # if request.postpath[0] != b'gatti':
        #     return b""
        # may be useful to authenticate users later
        # auth = request.getHeader('Authorization')
        # if auth and auth.split(' ')[0] == 'Basic':
        #     decodeddata = base64.decodestring(auth.split(' ')[1])
        #     if decodeddata.split(':') == ['username', 'password']:
        #         return "Authorized!"

        # request.setResponseCode(401)
        # request.setHeader('WWW-Authenticate', 'Basic realm="realmname"')
        # return "Authorization required.".encode()
        request.setHeader("Access-Control-Allow-Origin", "*")
        request.setHeader("Access-Control-Allow-Methods", "OPTIONS, GET")
        request.setHeader("Access-Control-Allow-Headers", "x-prototype-version,x-requested-with")
        request.setHeader("Access-Control-Max-Age", "2520")  # 42 hours
        request.setResponseCode(204)
        return b""

    def render_GET(self, request: Request) -> bytes:
        print("render_GET", type(request), type(request.uri))
        request.setHeader("Access-Control-Allow-Origin", "*")
        request.setHeader("Access-Control-Allow-Methods", "OPTIONS, GET")
        request.setHeader("Access-Control-Allow-Headers", "x-prototype-version,x-requested-with")
        request.setHeader("Access-Control-Max-Age", "2520")  # 42 hours

        if request.postpath[0] == b"":
            request.setResponseCode(200)
            request.setHeader("Content-type", "text/html")
            return b"<html>Hello, world!</html>"

        if request.postpath[0] == b"gatti":
            request.setResponseCode(200)
            request.setHeader("Content-type", "application/json")
            data = get_all_cats()
            request.write(json.dumps(data).encode())
            request.finish()
            return server.NOT_DONE_YET

        if request.postpath[0] == b"players":
            request.setResponseCode(200)
            request.setHeader("Content-type", "application/json")
            data = get_all_players()
            request.write(json.dumps(data).encode())
            request.finish()
            return server.NOT_DONE_YET

        request.setResponseCode(400)
        return b"Bad request"


def test():
    create_db("catbase")
    create_table("catbase", "cats", ["name VARCHAR(255)", "age INT"])
    print(db_exists("catbase"))
    print(db_exists("catbase2"))
    print(table_exists("catbase", "cats"))
    print(table_exists("catbase", "cats2"))
    insert("catbase", "cats", ["name", "age"], ["'Costantino'", "30"])
    insert("catbase", "cats", ["name", "age"], ["'Mia'", "2"])
    insert("catbase", "cats", ["name", "age"], ["'Mia'", "2"])

    print(select("catbase", "cats", ["name", "age"], "name = 'Costantino'"))
    print(select_all("catbase", "cats", ["name", "age"]))
    update("catbase", "cats", ["name", "age"], ["'Costantino'", "31"], "name = 'Costantino'")
    print(select_all("catbase", "cats", ["name", "age"]))
    delete("catbase", "cats", "name = 'Costantino'")
    print(select_all("catbase", "cats", ["name", "age"]))
    delete_all("catbase", "cats")
    print(select_all("catbase", "cats", ["name", "age"]))
    drop_table("catbase", "cats")
    drop_db("catbase")


if __name__ == "__main__":
    reset()
    # run()
