import pymysql

def get_status(display_id: str) -> dict:
    conn = pymysql.connect(host='localhost', user='root', password='P@ssw0rd', db='multimedia')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    raw = curs.execute("SELECT status_code FROM youtube WHERE display_id=%s", display_id)
    if not raw:
        raise Exception("Invalid key")
    result = curs.fetchone()
    curs.close()
    conn.close()
    return result

def get_output_path(display_id: str) -> dict:
    conn = pymysql.connect(host='localhost', user='root', password='P@ssw0rd', db='multimedia')
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
