from flask import Flask, request, jsonify, render_template
from db_conn import open_db, close_db
from datetime import datetime

app = Flask(__name__)


@app.route('/movies_page')
def movies_page():
    return render_template('movies.html')


def _build_conditions():
    """URL 파라미터에 따라 WHERE 절 조각들과 바인딩 값을 모아서 반환"""
    args = request.args
    conds = []
    params = []

    # 1) 영화명 (부분일치)
    title = args.get('sMovName', '').strip()
    if title:
        conds.append("(mi.title_kr LIKE %s OR mi.title_en LIKE %s)")
        like = f"%{title}%"
        params += [like, like]

    # 2) 감독명 (부분일치)
    director = args.get('sDirector', '').strip()
    if director:
        conds.append("d.director LIKE %s")
        params.append(f"%{director}%")

    # 3) 제작연도 BETWEEN
    y1 = args.get('sPrdtYearS', '').strip()
    y2 = args.get('sPrdtYearE', '').strip()
    if y1 or y2:
        if not y1:
            y1 = '0'
        if not y2:
            y2 = str(datetime.today().year)
        conds.append("mi.year BETWEEN %s AND %s")
        params += [y1, y2]


    # 5) 제작상태, 유형, 장르, 국적, 대표국적
    for field, col in [
        ('sPrdtStatStr', 'mi.status'),
        ('sMovTypeStr', 'mi.type'),
        ('sGenreStr', 'g.genre'),
        ('sNationStr', 'c.country')
    ]:
        vals = [v.strip() for v in args.get(field, '').split(',') if v.strip()]
        if vals:
            ph = ','.join(['%s'] * len(vals))
            conds.append(f"{col} IN ({ph})")
            params += vals

    # 6) 인덱싱
    idx = args.get('chosung', '').strip()
    if idx:
        chosung_map = {
            'ㄱ': ('가', '나'), 'ㄴ': ('나', '다'), 'ㄷ': ('다', '라'),
            'ㄹ': ('라', '마'), 'ㅁ': ('마', '바'), 'ㅂ': ('바', '사'),
            'ㅅ': ('사', '아'), 'ㅇ': ('아', '자'), 'ㅈ': ('자', '차'),
            'ㅊ': ('차', '카'), 'ㅋ': ('카', '타'), 'ㅌ': ('타', '파'),
            'ㅍ': ('파', '하'), 'ㅎ': ('하', '힣'),
        }
        if idx in chosung_map:
            start, end = chosung_map[idx]
            conds.append("mi.title_kr >= %s AND mi.title_kr < %s")
            params += [start, end]
        elif idx.isalpha():
            conds.append("mi.title_en LIKE %s")
            params.append(f"{idx.upper()}%")

    return conds, params


@app.route('/movies/searchMovieList', methods=['GET'])
def search_movie_list():
    # 1) 기본 SELECT + JOIN
    sql = """
    SELECT mi.movie_id, mi.title_kr, mi.title_en, mi.year, mi.type, mi.status,
           GROUP_CONCAT(DISTINCT c.country ORDER BY c.country SEPARATOR ', ') AS nation_name,
           GROUP_CONCAT(DISTINCT g.genre ORDER BY g.genre SEPARATOR ', ') AS genres,
           GROUP_CONCAT(DISTINCT d.director ORDER BY d.director SEPARATOR ', ') AS director,
           GROUP_CONCAT(DISTINCT p.company_name ORDER BY p.company_name SEPARATOR ', ') AS company_name
    FROM movie_info mi
    LEFT JOIN movie_country mc ON mi.movie_id = mc.movie_id
    LEFT JOIN country c ON mc.country_id = c.country_id
    LEFT JOIN movie_genre mg ON mi.movie_id = mg.movie_id
    LEFT JOIN genre g ON mg.genre_id = g.genre_id
    LEFT JOIN movie_director md ON mi.movie_id = md.movie_id
    LEFT JOIN director d ON md.director_id = d.director_id
    LEFT JOIN movie_production mp ON mi.movie_id = mp.movie_id
    LEFT JOIN production p ON mp.company_id = p.company_id
    """

    # 2) 조건절 처리
    conds, params = _build_conditions()
    if conds:
        sql += " WHERE " + " AND ".join(conds)

    sql += " GROUP BY mi.movie_id"

    # 3) DB 실행
    conn, cur = open_db()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    close_db(conn, cur)

    result = [dict(zip(cols, r)) for r in rows]
    return jsonify(result)


@app.route('/movies', methods=['GET'])
def get_all_movies():
    conn, cur = open_db()
    cur.execute("SELECT * FROM Movie_info")
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    close_db(conn, cur)
    return jsonify([dict(zip(cols, r)) for r in rows])


if __name__ == '__main__':
    app.run(debug=True)
