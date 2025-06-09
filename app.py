from flask import Flask, request, jsonify, render_template
from db_conn import open_db, close_db
from datetime import datetime

app = Flask(__name__)

@app.route('/movies_page')
def movies_page():
    return render_template('movies.html')

#영화명컴색(일부)
@app.route('/movies/title_search_result',
           methods=['GET'])
def search_movies_by_title():
    title=request.args.get('title','')

    conn, cur=open_db()

    query ="""
    select * from Movie_info where title_kr like %s
    """
    cur.execute(query,(f'%{title}%',))
    result =cur.fetchall()
    close_db(conn,cur)
    return jsonify(result)



# 감독명
@app.route('/movies/director/<director>',
           methods=['GET'])
def get_movies_by_director():
    director = request.args.get('director')
    conn, cur = open_db()
    query = """
            select *
            from Movie_info
            where (slecet mid from movie_director
                    where (select did from director where director like %s)"""
    cur.execute(query, (f'%{director}%',))
    result = cur.fetchall()
    close_db(conn, cur)
    return jsonify(result)


# 제작연도
@app.route('/movies/year/<year>',
           methods=['GET'])
def get_movies_by_year():
    y1 = request.args.get('year1')
    y2 = request.args.get('year2')
    if y2 is None:
        y2 = datetime.today().year
    conn, cur = open_db()
    query = """
        select *
        from Movie_info
        where year >= %s and year <= %s"""
    cur.execute(query, (f'%{y1}%', f'%{y2}%',))
    result = cur.fetchall()
    close_db(conn, cur)
    return jsonify(result)


# 제작상태
@app.route('/movies/status/<status>',
           methods=['GET'])
def get_movies_by_status(status):
    conn, cur = open_db()
    status_list = [t.strip() for t in status.split(',') if t.strip()]
    # 동적 IN 절
    placeholders = ','.join(['%s'] * len(status_list))
    query = f"""
    SELECT *
    FROM Movie_info
    WHERE status IN ({placeholders})
    """
    cur.execute(query, status_list)
    result = cur.fetchall()
    
    close_db(conn, cur)
    return jsonify(result)


# 제작상태
@app.route('/movies/type/<type>',
           methods=['GET'])
def get_movies_by_type(type_):
    conn, cur = open_db()
    query = """
    select *
    from Movie_info
    where type = %s
    """
    type_list = [t.strip() for t in type_.split(',') if t.strip()]
    # 동적 IN 절
    placeholders = ','.join(['%s'] * len(type_list))
    query = f"""
    SELECT *
    FROM Movie_info
    WHERE type IN ({placeholders})
    """
    cur.execute(query, type_list)
    result = cur.fetchall()
    
    close_db(conn, cur)
    return jsonify(result)


#장르별
@app.route('/movies/genre/<genres>',
           methods=['GET'])
def get_movies_by_genre(genres):
    genre_list=[g.strip()for g in genres.split(',')if g.strip()]

    conn,cur=open_db()

    placeholders=','.join(['%s'] * len(genre_list))

    query=f"""
    select distinct m.* 
    from Movie_info m 
    join Movie_Genre mg on m.movie_id=mg.movie_id
    join Genre g on g.genre_id=mg.genre_id
    where g.genre in ({placeholders})
    """
    cur.execute(query,genre_list)
    result=cur.fetchall()
    close_db(conn,cur)
    return jsonify(result)


#국적별
@app.route('/movies/country/<countries>',
           methods=['GET'])
def get_movies_by_country(countries):
    country_list=[c.strip()for c in countries.split(',')if c.strip()]

    conn,cur=open_db()

    placeholders=','.join(['%s'] * len(country_list))

    query=f"""
    select distinct m.* 
    from Movie_info m
    join Movie_country mc on m.movie_id=mc.movie_id
    join Country c on c.country_id= mc.country_id
    where c.country in ({placeholders})
    """
    cur.execute(query,country_list)
    result=cur.fetchall()
    close_db(conn,cur)
    return jsonify(result)

#등급별 - 성인 장르일 경우 19세 이상
@app.route('/movies/rating/<ratings>',
           methods=['GET'])
def get_movie_by_rating(ratings):
    rating_list=[r.strip()for r in ratings.split(',')if r.strip()]

    conn,cur=open_db()

    if "19세 이상" in rating_list:
 #'성인' 장르인 영화만 필터링
        query="""
        select m.* 
        from Movie_info m
        join Movie_Genre mg on m.movie_id=mg.movie_id
        join Genre g on mg.genre_id=g.genre_id
        where g.genre like '%성인%' 
        """
        cur.execute(query)
    else:
        placeholders=','.join(['%s'] * len(rating_list))

        query=f"select * from Movie_info where rating in({placeholders})"
        cur.execute(query,rating_list)

    result=cur.fetchall()
    close_db(conn,cur)
    return jsonify(result)


#대표국적별(대표국적=처음으로 등록된 국적)
@app.route('/movies/primary_country/<countries>',
           methods=['GET'])
def get_movies_by_primary_country(countries):
    country_list=[c.strip()for c in countries.split(',')if c.strip()]

    conn, cur=open_db()

    placeholders=','.join(['%s'] * len(country_list))

    query=f"""
    select m.*
    from Movie_info m
    join(
    select movie_id, min(country_id) as primary_country_id
    from Movie_country
    group by movie_id
    )
    mc on m.movie_id=mc.movie_id
    join Country c on mc.primary_country_id=c.country_id
    where c.country in ({placeholders})
    """
    cur.execute(query,country_list)
    result=cur.fetchall()
    close_db(conn,cur)
    return jsonify(result)


#인덱싱
@app.route('/movies/title_index/<index>',
            methods=['GET'])
def get_movies_by_title_index(index):

    conn, cur = open_db()
    
# 초성에 따른 한글 시작/끝 범위
    chosung_range = {
        'ㄱ': ('가', '나'),
        'ㄴ': ('나', '다'),
        'ㄷ': ('다', '라'),
        'ㄹ': ('라', '마'),
        'ㅁ': ('마', '바'),
        'ㅂ': ('바', '사'),
        'ㅅ': ('사', '아'),
        'ㅇ': ('아', '자'),
        'ㅈ': ('자', '차'),
        'ㅊ': ('차', '카'),
        'ㅋ': ('카', '타'),
        'ㅌ': ('타', '파'),
        'ㅍ': ('파', '하'),
        'ㅎ': ('하', '힣')  
    }

    if index in chosung_range:
        start, end = chosung_range[index]
        query = """
            select * 
            from Movie_info
            where title_kr >= %s and title_kr < %s
        """
        cur.execute(query, (start, end))
    elif index.isalpha():  # A〜Z
        query = "select * from Movie_info where title_en like %s"
        cur.execute(query, (index.upper() + '%',))
    else:
        return jsonify([])

    result = cur.fetchall()
    close_db(conn, cur)
    return jsonify(result)


# # 제작연도순 정렬
# def order_by_year():
#     return " order by year desc"
#
#
# # 영화명순 정렬
# def order_by_title():
#     return """
#         order by
#         CASE
#             WHEN title_kr IS NULL OR title_kr = '' THEN 1 ELSE 0
#         END,
#         title_kr,
#         title_en
#     """


# 조회
@app.route('/movies/searchMovieList',
           methods=['GET'])
def search():
    # pass
    # 각 조회기능별 함수는 get한 값을 "where ~" 형식으로 조건만 담아 return
    # 각 변수에 return된 값을 담아 값이 있으면 search_sql에 join
    query = "select * from movie_info"
    condition = [search_movies(),
                 get_movies_by_director(),
                 get_movies_by_year(),
                 get_movies_by_status(),
                 get_movies_by_type(),
                 get_movies_by_genre(),
                 get_movies_by_country(),
                 get_movie_by_rating(),
                 get_movies_by_primary_country(),
                 get_movies_by_title_index(),
                ]
    
    for i in condition:
        query += " " + condition[i]

    conn, cur = open_db()
    cur.execute(query)
    result = cur.fetchall()
    
    close_db(conn, cur)
    return jsonify(result)

# 초기화, 정렬은 js로만 가능
@app.route('/movies',
           methods=['GET'])
def get_all_movies():
    conn,cur=open_db()
    query="select * from Movie_info"
    cur.execute(query)
    result=cur.fetchall()
    close_db(conn,cur)
    return jsonify(result)

# Flask
if __name__ == '__main__':
    app.run(debug=True)
