import pymysql


from pymysql.constants.CLIENT import MULTI_STATEMENTS

def open_db(dbname='movie'):
    conn = pymysql.connect(host='localhost',
                           user='root',
                           passwd='Mchltpwls1029!',
                           db=dbname,
                           client_flag=MULTI_STATEMENTS)
    cur = conn.cursor(pymysql.cursors.DictCursor)

    return conn, cur

def close_db(conn, cur):
    cur.close()
    conn.close()