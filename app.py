from flask import Flask, request, jsonify, render_template
from db_conn import open_db, close_db
from datetime import datetime

app = Flask(__name__)


@app.route('/movies_page')
def movies_page():
    return render_template('movies.html')


def _build_conditions():
    args = request.args
    conds = []
    params = []

    # 영화명
    title = args.get('sMovName', '').strip()
    if title:
        conds.append("(mi.title_kr LIKE %s OR mi.title_en LIKE %s)")
        like = f"%{title}%"
        params += [like, like]

    # 감독명
    director = args.get('sDirector', '').strip()
    if director:
        conds.append("d.director LIKE %s")
        params.append(f"%{director}%")

    # 제작연도
    y1 = args.get('sPrdtYearS', '').strip()
    y2 = args.get('sPrdtYearE', '').strip()
    if y1 or y2:
        if not y1:
            y1 = '0'
        if not y2:
            y2 = str(datetime.today().year)
        conds.append("mi.year BETWEEN %s AND %s")
        params += [y1, y2]

    # 제작상태, 유형, 장르, 국가
    for field, col in [
        ('sPrdtStatStr', 'mi.status'),
        ('sMovTypeStr', 'mi.type'),
        ('sGenreStr', 'g.genre'),
        ('sNationStr', 'c.country')
    ]:
        vals = [v.strip() for v in args.get(field, '').split(',') if v.strip()]
        if vals:
            placeholders = ','.join(['%s'] * len(vals))
            conds.append(f"{col} IN ({placeholders})")
            params += vals

    # 영화명 인덱싱 (초성/알파벳)
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
            conds.append("LEFT(mi.title_kr, 1) >= %s AND LEFT(mi.title_kr, 1) < %s")
            params += [start, end]
        elif idx.isalpha():
            conds.append("mi.title_en LIKE %s")
            params.append(f"{idx.upper()}%")

    print("chosung idx:", idx)
    print("conds:", conds)
    print("params:", params)

    return conds, params


@app.route('/movies/searchMovieList', methods=['GET'])
def search_movie_list():
    sql = """
    SELECT 
        mi.movie_id, mi.title_kr, mi.title_en, mi.year, mi.type, mi.status,
        GROUP_CONCAT(DISTINCT c.country ORDER BY c.country SEPARATOR ', ') AS nation_name,
        GROUP_CONCAT(DISTINCT g.genre ORDER BY g.genre SEPARATOR ', ') AS genres,
        GROUP_CONCAT(DISTINCT d.director ORDER BY d.director SEPARATOR ', ') AS director,
        GROUP_CONCAT(DISTINCT p.production ORDER BY p.production SEPARATOR ', ') AS production
    FROM movie_info mi
    LEFT JOIN movie_country mc ON mi.movie_id = mc.movie_id
    LEFT JOIN country c ON mc.country_id = c.country_id
    LEFT JOIN movie_genre mg ON mi.movie_id = mg.movie_id
    LEFT JOIN genre g ON mg.genre_id = g.genre_id
    LEFT JOIN movie_director md ON mi.movie_id = md.movie_id
    LEFT JOIN director d ON md.director_id = d.director_id
    LEFT JOIN movie_production mp ON mi.movie_id = mp.movie_id
    LEFT JOIN production p ON mp.production_id = p.production_id
    """

    # 조건 추가
    conds, params = _build_conditions()
    if conds:
        sql += " WHERE " + " AND ".join(conds)

    # 그룹핑
    sql += " GROUP BY mi.movie_id"

    # 실행
    conn, cur = open_db()
    cur.execute(sql, params)
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    close_db(conn, cur)

    # 결과 반환
    result = rows
    # result = [dict(zip(cols, r)) for r in rows]
    # print("[rows]", rows[:3])
    # print("[cols]", cols)
    # print(result)
    return jsonify(result)


@app.route('/movies', methods=['GET'])
def get_all_movies():
    conn, cur = open_db()
    cur.execute("SELECT * FROM movie_info")
    rows = cur.fetchall()
    cols = [d[0] for d in cur.description]
    close_db(conn, cur)
    return jsonify([dict(zip(cols, r)) for r in rows])


if __name__ == '__main__':
    app.run(debug=True)
