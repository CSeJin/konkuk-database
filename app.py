rom flask import Flask, request, jsonify,render_template
from db import open_db, close_db

app= Flask(__name__)

#영화명컴색(일부)
@app.route('/movies/search',
           methods=['GET'])
def search_movies():
    title=request.args.get('title')
    conn, cur=open_db()
    query ="select * from Movie_info where title_kr like %s"
    cur.execute(query,(f'%{title}%',))
    result =cur.fetchall()
    close_db(conn,cur)
    return jsonify(result)

#장르별
@app.route('/movies/genre/<genre>',
           methods=['GET'])
def get_movies_by_genre(genre):
    conn,cur=open_db()
    query="""
    select m.* 
    from Movie_info m 
    join Movie_Genre mg on m.movie_id=mg.movie_id
    join Genre g on g.genre_id=mg.genre_id
    where g.genre=%s
"""
    cur.execute(query,(genre,))
    result=cur.fetchall()
    close_db(conn,cur)
    return jsonify(result)

#국적별
@app.route('/movies/country/<country>',
           methods=['GET'])
def get_movies_by_country(country):
    conn,cur=open_db()
    query="""
    select m.* 
    from Movie_info m
    join Movie_country mc on m.movie_id=mc.movie_id
    join Country c on c.country_id= mc.country_id
    where c.country=%s
    """
    cur.execute(query,(country,))
    result=cur.fetchall()
    close_db(conn,cur)
    return jsonify(result)

#등급별 - 성인 장르일 경우 19세 이상
@app.route('/movies/rating/<rating>',
           methods=['GET'])
def get_movie_by_rating(rating):
    conn,cur=open_db()
    if rating=="19세 이상":
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
        query="select * from Movie_info where status=%s"
        cur.execute(query,(rating,))

    result=cur.fetchall()
    close_db(conn,cur)
    return jsonify(result)

#대표국적별(대표국적=처음으로 등록된 국적)
@app.route('/movies/primary_country/<country>',
           methods=['GET'])
def get_movies_by_primary_country(country):
    conn, cur=open_db()
    query="""
    select m.*
    from Movie_info m
    join(
    select movie_id, min(country_id) as primary_country_id
    from Movie_country
    group by movie_id
    )
    mc on m.movie_id=mc.movie_id
    join Country c on mc.primary_country_id=c.country_id
    where c.country=%s
    """
    cur.execute(query,(country,))
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

#Flask 
if __name__=='__main__':
    app.run(debug=True)
