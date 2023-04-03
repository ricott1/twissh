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
                "id CHAR(24) PRIMARY KEY",
                "name VARCHAR(20)",
                "age SMALLINT",
                "gender BOOLEAN",
                "description VARCHAR(128)",
                "red SMALLINT",
                "green SMALLINT",
                "blue SMALLINT",
                "owner VARCHAR(20)",
                "rarity SMALLINT",
                "colors CHAR(24)",
                "parts CHAR(12)",
            ],
        )


def get_all_cats() -> list[tuple]:
    return select_all("hacknslassh", "cats", ["*"])

def get_owner_cats(owner: str) -> list[tuple]:
    ...


class SQLConnectorServer(resource.Resource):
    isLeaf = True
    def render_OPTIONS(self, request: Request) -> bytes:
        # if request.postpath[0] != b'gatti':
        #     return b""
            #may be useful to authenticate users later
            # auth = request.getHeader('Authorization')
            # if auth and auth.split(' ')[0] == 'Basic':
            #     decodeddata = base64.decodestring(auth.split(' ')[1])
            #     if decodeddata.split(':') == ['username', 'password']:
            #         return "Authorized!"

            # request.setResponseCode(401)
            # request.setHeader('WWW-Authenticate', 'Basic realm="realmname"')
            # return "Authorization required.".encode()
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'OPTIONS, GET')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', '2520') # 42 hours
        request.setResponseCode(204)
        return b""
    
    def render_GET(self, request: Request) -> bytes:
        print("render_GET", type(request), type(request.uri))
        request.setHeader('Access-Control-Allow-Origin', '*')
        request.setHeader('Access-Control-Allow-Methods', 'OPTIONS, GET')
        request.setHeader('Access-Control-Allow-Headers', 'x-prototype-version,x-requested-with')
        request.setHeader('Access-Control-Max-Age', '2520') # 42 hours
        
        
        if request.postpath[0] != b'gatti':
            request.setResponseCode(400)
            return b"Bad request"
        
        request.setResponseCode(200)
        # normal JSON header
        request.setHeader('Content-type', 'application/json')
        all_cats = get_all_cats()
        # json.dumps(all_cats).encode()
        request.write(json.dumps(all_cats).encode()) # gotta use double-quotes in JSON apparently 
        request.finish()
        return server.NOT_DONE_YET
    



# class Server(BaseHTTPRequestHandler):
#     def _set_response(self):
#         self.send_response(200, "ok")
#         self.end_headers()
    
#     def end_headers (self):
#         self.send_header('Access-Control-Allow-Origin', '*')
#         self.send_header('Access-Control-Allow-Headers', 'Content-type')
#         self.send_header('Referrer-Policy', 'no-referrer-when-downgrade')
#         super().end_headers()

#     def do_GET(self):
#         logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
#         self._set_response()
#         all_cats = get_all_cats()
#         if all_cats:
#             self.wfile.write(json.dumps(all_cats).encode())
    
#     def do_OPTIONS(self):
#         self._set_response()

#     def do_POST(self):
#         content_length = int(self.headers["Content-Length"])  # <--- Gets the size of data
#         post_data = self.rfile.read(content_length)  # <--- Gets the data itself
#         logging.info(
#             "POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
#             str(self.path),
#             str(self.headers),
#             post_data.decode("utf-8"),
#         )

#         self._set_response()
#         self.wfile.write("POST request for {}".format(self.path).encode("utf-8"))


# def run(port: int = 8080) -> None:
#     logging.basicConfig(level=logging.INFO)
#     server_address = ("localhost", port)
#     httpd = ThreadingHTTPServer(server_address, Server)
#     logging.info("Starting httpd...\n")
#     try:
#         httpd.serve_forever()
#     except KeyboardInterrupt:
#         pass
#     httpd.server_close()
#     logging.info("Stopping httpd...\n")

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