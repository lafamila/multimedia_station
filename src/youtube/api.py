import pymysql
import os
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT', "3306")
DB_SCHEME = os.getenv('DB_SCHEME')

def get_status(display_id: str) -> dict:
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_SCHEME, port=int(DB_PORT))
    curs = conn.cursor(pymysql.cursors.DictCursor)
    raw = curs.execute("SELECT status_code FROM youtube WHERE display_id=%s", display_id)
    if not raw:
        raise Exception("Invalid key")
    result = curs.fetchone()
    curs.close()
    conn.close()
    return result

def get_output_path(display_id: str) -> dict:
    conn = pymysql.connect(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db=DB_SCHEME, port=int(DB_PORT))
    curs = conn.cursor(pymysql.cursors.DictCursor)
    raw = curs.execute("SELECT status_code, output_path, title FROM youtube WHERE display_id=%s", display_id)
    if not raw:
        raise Exception("Invalid key")
    result = curs.fetchone()
    curs.close()
    conn.close()
    if result['status_code'] != 'DONE':
        raise Exception("Not done yet")
    return result
