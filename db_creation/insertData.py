import pymysql
import csv
from db_conn import *


 

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
        print("%d rows" %i)     #테스트용
        
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
    
#-----------------------------------------------------------
# movie_country에 데이터 입력
def create_movie_country(data):
    con, cur = open_db()
    rows = []
    i = 0

    insert_sql = """
        insert into movie_country(country_id, movie_id) values (%s, %s)
    """
    get_cid_sql = """
        select country_id from country where country=%s
    """
    get_mid_sql = """
        select movie_id from movie_info where title_kr=%s
    """
    for row in data:
        try:
            countries = data_cleansing(row[3])
            title_kr = row[1]
            # mid 가져오기
            cur.execute(get_mid_sql, (title_kr,))
            mid = cur.fetchone()
            if not mid:
                continue
            movie_id = mid["movie_id"] if isinstance(mid, dict) else mid[0]
            
            # 국가마다 cid 조회 후 관계 추가
            for country in countries:
                cur.execute(get_cid_sql, (country.strip(),))
                cid = cur.fetchone()
                if not cid:
                    continue
                country_id = cid["country_id"] if isinstance(cid, dict) else cid[0]
                
                rows.append((country_id, movie_id))
            
            i += 1
            print("%d rows" % i)  # 테스트용
            
            if i % 10000 == 0:
                cur.executemany(insert_sql, rows)  # rows는 tuple 리스트임
                con.commit()
                print("%d rows" % i)
                rows = []
        except Exception as e:
            print(f"Skipped row due to error: {e}")
            print("Row was:", row)
    if rows:  # 남은 데이터 삽입
        cur.executemany(insert_sql, rows)
        con.commit()
    
    print("insertion into table \'movie_country\' succeeded.")
    close_db(con, cur)

if __name__ == '__main__':
    f = open("test.csv", encoding="utf-8")  # 테스트용
    # f1 = open("list1.csv")
    # f2 = open("list2.csv")
    
    data = list(csv.reader(f))  # 테스트용
    # data = list(csv.reader(f1))
    create_movie_info(data[:])
    create_country(data[:])
    create_production(data[:])
    create_director(data[:])
    create_genre(data[:])
    

    # data = list(csv.reader(f2))
    create_movie_info(data[:])
    create_country(data[:])
    create_production(data[:])
    create_director(data[:])
    create_genre(data[:])
    
    f.close()