import mysql.connector


def connect(db: str) -> mysql.connector.MySQLConnection:
    mydb = mysql.connector.connect(host="localhost", user="costantino", password="MoxOpal{0}", database=db)
    return mydb


def select(db: str, table: str, columns: list[str], where: str) -> list[tuple]:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"SELECT {', '.join(columns)} FROM {table} WHERE {where}")
    return cursor.fetchall()


def select_all(db: str, table: str) -> list[tuple]:
    mydb = connect(db)
    cursor = mydb.cursor()
    cursor.execute(f"SELECT * FROM {table}")
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


def store(table: str, values: str) -> None:
    mydb = connect("hacknslassh")
    cursor = mydb.cursor()
    cursor.execute(f"INSERT INTO {table} VALUES {values}")
    mydb.commit()


def delete_all_cats() -> None:
    mydb = connect("hacknslassh")
    cursor = mydb.cursor()
    cursor.execute(f"DELETE FROM cats")
    mydb.commit()


def get_all_cats() -> list[tuple]:
    return select_all("hacknslassh", "cats")


def get_player(player_id: str) -> tuple:
    return select("hacknslassh", "players", ["*"], f"id = '{player_id}'")


def get_all_players() -> list[tuple]:
    return select_all("hacknslassh", "players")
