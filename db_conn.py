import pymysql


from pymysql.constants.CLIENT import MULTI_STATEMENTS

def open_db(dbname='movie'):
    conn = pymysql.connect(host='127.0.0.1',
                           port=3306,
                           user='db2025',
                           passwd='db2025',
                           db=dbname,
                           charset='utf8',
                           client_flag=MULTI_STATEMENTS)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    return conn, cur

def close_db(conn, cur):
    cur.close()
    conn.close()