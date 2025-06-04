import pymysql
import csv
from db_conn import *

# 테스트용
def printFIle(rdr):
    i = 0
    for row in rdr:
        print(row)
        i+=1
        if i==10 :
            break
 

# movie_info에 데이터 입력
def create_movie_info(data):
    con, cur = open_db()
    insert_sql = """
        insert into movie_info(title_kr, title_en, year, type, status)
         values (%s, %s, %s, %s, %s)
    """
    
    rows = []
    i = 0
    for row in data:
        try:
            title_kr = row[0]
            title_en = row[1]
            year = int(row[2])
            mType = row[4]
            status = row[6]
            r = (title_kr, title_en, year, mType, status)
            rows.append(r)
        except Exception as e:
            print(f"Skipped row due to error: {e}")
            print("Row was:", row)
        i += 1
        print("%d rows" %i)
        
        if i % 10000 == 0:
            cur.executemany(insert_sql, rows)   # rows는 tuple 리스트임
            con.commit()
            print("%d rows" %i)
            rows = []
        
        if rows:        # 남은 데이터 삽입
            cur.executemany(insert_sql, rows)
            con.commit()
        
    print("insertion into table \'movie_info\' succeeded.")
    close_db(con, cur)

# ","가 포함된 2개 이상의 값을 가진 데이터를 리스트로 정제
def data_cleansing(data):
    data = data.replace("\"", "")
    return data.split(',')

# country에 데이터 입력
def create_country(rdr):
    con, cur = open_db()
    insert_sql = """
        insert into country(country) values (%s)
    """
    
    rows = []
    for row in rdr:
        country = row[3]
        country = data_cleansing(country)
        
        for c in country:
            if c not in rows:   # 중복 제거
                if c != "":
                    rows.append(c)
    
    cur.executemany(insert_sql, [(c,) for c in rows])   # rows는 문자열리스트임
    con.commit()
    print("insertion into table \'country\' succeeded.")
    close_db(con, cur)


# director에 데이터 입력
def create_director(rdr):
    con, cur = open_db()
    insert_sql = """
        insert into director(director) values (%s)
    """
    
    rows = []
    for row in rdr:
        director = row[7]
        director = data_cleansing(director)
        
        for d in director:
            if d not in rows:  # 중복 제거
                if d != "":
                    rows.append(d)
    
    cur.executemany(insert_sql, [(d,) for d in rows])
    con.commit()
    print("insertion into table \'director\' succeeded.")
    close_db(con, cur)


# production에 데이터 입력
def create_production(data):
    con, cur = open_db()
    insert_sql = """
        insert into production(production) values (%s)
    """
    
    rows = []
    for row in data:
        production = row[8]
        production = data_cleansing(production)
        
        for p in production:
            if p not in rows:  # 중복 제거
                if p != "": #null값은 입력 x
                    rows.append(p)
    
    cur.executemany(insert_sql, [(p,) for p in rows])
    con.commit()
    print("insertion into table \'production\' succeeded.")
    close_db(con, cur)


# genre에 데이터 입력
def create_genre(data):
    con, cur = open_db()
    insert_sql = """
        insert into genre(genre) values (%s)
    """
    
    rows = []
    for row in data:
        genre = row[5]
        genre = data_cleansing(genre)
        
        for g in genre:
            if g not in rows:  # 중복 제거
                if g != "":
                    rows.append(g)
    
    cur.executemany(insert_sql, [(g,) for g in rows])
    con.commit()
    print("insertion into table \'genre\' succeeded.")
    close_db(con, cur)

if __name__ == '__main__':
    f = open("test.csv", encoding="utf-8")
    # f1 = open("list1.csv")
    # f2 = open("list2.csv")
    
    data = list(csv.reader(f))
    
    create_movie_info(data[:])
    create_country(data[:])
    create_production(data[:])
    create_director(data[:])
    create_genre(data[:])
    
    f.close()