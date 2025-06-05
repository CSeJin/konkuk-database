import pymysql
import csv
from db_conn import *

###################################################################################
# 2025-06-05
# 실행 전 db_conn.py에서 유저, DB명을 확인해주세요.
# create 파일을 문자열 길이 등의 이유로 수정한 부분이 있으니 테이블을 다시 생성해주세요.
###################################################################################


# 영화명(한글)   영화명(영문)     연도  국가  유형  장르  상태  감독  제작사
#   0             1            2    3    4    5    6     7    8


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
            title_kr = str(row[0])
            title_en = str(row[1]) if row[1].strip() != "" else None
            year = int(row[2]) if row[2].strip() != "" else None
            mType = row[4] if row[4].strip() != "" else None
            status = row[6] if row[6].strip() != "" else None
            r = (title_kr, title_en, year, mType, status)
            rows.append(r)
        except Exception as e:
            print(f"Skipped row due to error: {e}")
            print("Row was:", row)
            return
        i += 1
        # print("%d rows" % i)  # 테스트용
        
        if i % 10000 == 0:
            try:
                cur.executemany(insert_sql, rows)  # rows는 tuple 리스트임
            except Exception as e:
                print(f"Error at row {i}: {e}")
                print("Row data:", row)
                print("Parsed:", (title_kr, title_en, year, mType, status))
            con.commit()
            print("%d rows" % i)
            rows = []
    
    if rows:  # 남은 데이터 삽입
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
            if c not in rows:  # 중복 제거
                if c != "":
                    rows.append(c)
    
    cur.executemany(insert_sql, [(c,) for c in rows])  # rows는 문자열리스트임
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
                if p != "":  # null값은 입력 x
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


# ---------------------------------------------------------------------------------------
# movie_country에 데이터 입력
def create_movie_country(data):
    con, cur = open_db()
    rows = []
    i = 0
    insert_sql = """
            insert into movie_country(country_id, movie_id) values (%s, %s)
        """
    # movie title → movie_id 매핑
    cur.execute("SELECT title_kr, movie_id FROM movie_info")
    movie_map = {row["title_kr"]: row["movie_id"] for row in cur.fetchall()}
    
    # country name → country_id 매핑
    cur.execute("SELECT country, country_id FROM country")
    country_map = {row["country"]: row["country_id"] for row in cur.fetchall()}
    
    for row in data:
        try:
            countries = data_cleansing(row[3])
            title_kr = row[0]
            
            if title_kr not in movie_map:
                continue
            movie_id = movie_map[title_kr]
            
            for c in countries:
                c = c.strip()
                if c not in country_map:
                    continue
                country_id = country_map[c]
                rows.append((int(country_id), int(movie_id)))
            
            i += 1
            # print("%d rows" % i)  # 테스트용
            
            if i % 10000 == 0:
                cur.executemany(insert_sql, rows)  # rows는 tuple 리스트임
                con.commit()
                print("%d rows" % i)
                rows = []
        except Exception as e:
            print(f"Skipped row due to error: {e}")
            print("Row was:", row)
            return
    if rows:  # 남은 데이터 삽입
        cur.executemany(insert_sql, rows)
        con.commit()
    
    print("insertion into table \'movie_country\' succeeded.")
    close_db(con, cur)


# movie_country에 데이터 입력
def create_movie_genre(data):
    con, cur = open_db()
    rows = []
    i = 0
    
    insert_sql = """
            insert into movie_genre(genre_id, movie_id) values (%s, %s)
        """
    # movie title → movie_id 매핑
    cur.execute("SELECT title_kr, movie_id FROM movie_info")
    movie_map = {row["title_kr"]: row["movie_id"] for row in cur.fetchall()}
    
    # genre name → genre_id 매핑
    cur.execute("SELECT genre, genre_id FROM genre")
    genre_map = {row["genre"]: row["genre_id"] for row in cur.fetchall()}
    
    for row in data:
        try:
            genres = data_cleansing(row[5])
            title_kr = row[0]
            
            if title_kr not in movie_map:
                continue
            movie_id = movie_map[title_kr]
            
            for g in genres:
                g = g.strip()
                if g not in genre_map:
                    continue
                genre_id = genre_map[g]
                rows.append((int(genre_id), int(movie_id)))
            
            i += 1
            # print("%d rows" % i)  # 테스트용
            
            if i % 10000 == 0:
                cur.executemany(insert_sql, rows)  # rows는 tuple 리스트임
                con.commit()
                print("%d rows" % i)
                rows = []
        except Exception as e:
            print(f"Skipped row due to error: {e}")
            print("Row was:", row)
            return
    if rows:  # 남은 데이터 삽입
        cur.executemany(insert_sql, rows)
        con.commit()
    
    print("insertion into table \'movie_genre\' succeeded.")
    close_db(con, cur)


def create_movie_director(data):
    con, cur = open_db()
    rows = []
    i = 0
    
    insert_sql = """
        insert into movie_director(director_id, movie_id) values (%s, %s)
    """
    # movie title → movie_id 매핑
    cur.execute("SELECT title_kr, movie_id FROM movie_info")
    movie_map = {row["title_kr"]: row["movie_id"] for row in cur.fetchall()}
    
    # director name → director_id 매핑
    cur.execute("SELECT director, director_id FROM director")
    director_map = {row["director"]: row["director_id"] for row in cur.fetchall()}
    
    for row in data:
        try:
            directors = data_cleansing(row[7])
            title_kr = row[0]
            
            if title_kr not in movie_map:
                continue
            movie_id = movie_map[title_kr]
            
            for d in directors:
                d = d.strip()
                if d not in director_map:
                    continue
                director_id = director_map[d]
                rows.append((int(director_id), int(movie_id)))
            
            i += 1
            # print("%d rows" % i)  # 테스트용
            
            if i % 10000 == 0:
                cur.executemany(insert_sql, rows)  # rows는 tuple 리스트임
                con.commit()
                print("%d rows" % i)
                rows = []
        except Exception as e:
            print(f"Skipped row due to error: {e}")
            print("Row was:", row)
            return
    if rows:  # 남은 데이터 삽입
        cur.executemany(insert_sql, rows)
        con.commit()
    
    print("insertion into table \'movie_director\' succeeded.")
    close_db(con, cur)


def create_movie_production(data):
    con, cur = open_db()
    rows = []
    i = 0
    
    insert_sql = """
        insert into movie_production(production_id, movie_id) values (%s, %s)
    """
    # movie title → movie_id 매핑
    cur.execute("SELECT title_kr, movie_id FROM movie_info")
    movie_map = {row["title_kr"]: row["movie_id"] for row in cur.fetchall()}
    
    # production name → production_id 매핑
    cur.execute("SELECT production, production_id FROM production")
    production_map = {row["production"]: row["production_id"] for row in cur.fetchall()}
    
    for row in data:
        try:
            productions = data_cleansing(row[8])
            title_kr = row[0]
            
            if title_kr not in movie_map:
                continue
            movie_id = movie_map[title_kr]
            
            for p in productions:
                p = p.strip()
                if p not in production_map:
                    continue
                production_id = production_map[p]
                rows.append((int(production_id), int(movie_id)))
            
            i += 1
            # print("%d rows" % i)  # 테스트용
            
            if i % 10000 == 0:
                cur.executemany(insert_sql, rows)  # rows는 tuple 리스트임
                con.commit()
                print("%d rows" % i)
                rows = []
        except Exception as e:
            print(f"Skipped row due to error: {e}")
            print("Row was:", row)
            return
    if rows:  # 남은 데이터 삽입
        cur.executemany(insert_sql, rows)
        con.commit()
    
    print("insertion into table \'movie_production\' succeeded.")
    close_db(con, cur)


if __name__ == '__main__':
    # f = open("test.csv", encoding="utf-8")  # 테스트용
    f1 = open("list1.csv", encoding="utf-8")
    
    # data = list(csv.reader(f))  # 테스트용
    
    # list1.csv
    data = list(csv.reader(f1))
    create_movie_info(data[:])
    create_country(data[:])
    create_production(data[:])
    create_director(data[:])
    create_genre(data[:])
    create_movie_country(data[:])
    create_movie_genre(data[:])
    create_movie_director(data[:])
    create_movie_production(data[:])
    
    f1.close()
    print("\nlist1.csv done\n")
    
    f2 = open("list2.csv", encoding="utf-8")
    # list2.csv
    data = list(csv.reader(f2))
    create_movie_info(data[:])
    create_country(data[:])
    create_production(data[:])
    create_director(data[:])
    create_genre(data[:])
    create_movie_country(data[:])
    create_movie_genre(data[:])
    create_movie_director(data[:])
    create_movie_production(data[:])
    
    f2.close()
    print("\nlist2.csv done\n")
    
    # f.close()
