from datetime import date, datetime

from flask import Flask, redirect, render_template, request, session, url_for
import base64
import hashlib
import secrets

import psycopg2
import psycopg2.extras

HASH_ALGORITHM = "pbkdf2_sha256"
app = Flask(__name__)
app.secret_key = b"opensesame"


def hash_password(password, salt=None, iterations=310000):
    if salt is None:
        salt = secrets.token_hex(16)
    assert salt and isinstance(salt, str) and "$" not in salt
    assert isinstance(password, str)
    pw_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), iterations
    )
    b64_hash = base64.b64encode(pw_hash).decode("ascii").strip()
    return "{}${}${}${}".format(HASH_ALGORITHM, iterations, salt, b64_hash)


def verify_password(password, password_hash):
    if (password_hash or "").count("$") != 3:
        return False
    algorithm, iterations, salt, _ = password_hash.split("$", 3)
    iterations = int(iterations)
    assert algorithm == HASH_ALGORITHM
    compare_hash = hash_password(password, salt, iterations)
    return secrets.compare_digest(password_hash, compare_hash)

#ここまでパスワードをどうするかの云々

def get_db():
    conn = psycopg2.connect(
        host="ep-morning-sea-a1daf9b1-pooler.ap-southeast-1.aws.neon.tech",
        database="neondb",
        user="neondb_owner",
        password="npg_tCTxuWfA3km1",
        port=5432,
        sslmode="require"
    )
    return conn




def format_datetime(dt):
    if dt:
        # datetime.strptime()を使ってもOK
        return datetime.fromisoformat(dt).strftime("%Y年%m月%d日 %H:%M")
    else:
        return dt


def format_date(d):
    if d:
        return date.fromisoformat(d).strftime("%Y年%m月%d日")
    else:
        return d


@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("index"))


@app.route("/login", methods=["GET"])
def login_form():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():

    username = request.form.get("username")
    print(username)
    if not username:
        print('名前が違う')
        return render_template("login.html", error_user=True, form=request.form)

    password = request.form.get("password")
    if not password:
        return render_template("login.html", error_password=True, form=request.form)
        print('パスワードが違う')

    db = get_db()

    try:
        with db:
            cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

            cursor.execute(
                "SELECT * FROM users where name = %(name)s", {"name":username}
            )
            row = cursor.fetchone()
            #ここのエラー治った
            verified = row is not None and verify_password(
                password, row["password_hash"]
            )
            
            if verified:
                session["user_id"] = row["user_id"]
                return redirect(url_for("index"))
            else:
                print('verifiedできてない')
                return render_template("login.html", error_login=True)
    finally:
        db.close()


@app.route("/register", methods=["GET"])
def register_form():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username")
    password = request.form.get("password")
    
	
    ###ここでdbからユーザー認証してる
    db = get_db()
    try:
        with db:
            #ここでミスってる_
            #↑なおした！！
            cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)

            res = cursor.execute(
                "SELECT * FROM users WHERE name = %(name)s", {"name": username}
            )
            res = cursor.fetchall()
            if len(res) != 0:
                return render_template(
                    "register.html", error_unique=True, form=request.form
                )

            #ここのカラム名みすってた
            password_hash = hash_password(password,)
            cursor.execute(
                "INSERT INTO users (name, password_hash) VALUES (%s, %s)",
                (username, password_hash),
            )

        return redirect(url_for("login_form"))

    finally:
        db.close()


####ここで日記の内容！！！！！！！！
@app.route("/", methods=["GET"])
def index():
    if "user_id" not in session:
        return redirect("/login")

    # query_select = """
    #     SELECT dia_id, text, date, user_id,title
    #     FROM diary
    # """
    query = """
        SELECT * FROM diary
        WHERE user_id = %s
        ORDER BY date DESC
    """
    #query_where = "WHERE user_id = %s"
    #query = f"{query_select} {query_where}"

    # データベースに接続
    db = get_db()
    try:
        with db:
            # クエリを実行            
            cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(query, (session["user_id"],))

            tasks = []
            for row in cursor:
                task = dict(row)
                tasks.append(task)
    finally:
        # 接続をクローズ
        db.close()
        #print(tasks)

    return render_template("index.html", tasks=tasks)


@app.route("/new", methods=["GET"])
def new():
    if "user_id" not in session:
        return redirect("/login")

    return render_template("new.html")


@app.route("/create", methods=["POST"])
def create():
    if "user_id" not in session:
        return redirect("/login")

    title = request.form.get("title")
    text = request.form.get("text")
    date = request.form.get("date")

    query = """
        INSERT INTO diary (user_id, title, text, date)
        VALUES (%s, %s, %s, %s)
    """

    db = get_db()
    try:
        with db:
            cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(
                query, (session["user_id"], title, text, date)
            )  # palceholderにタプルで与える
    finally:
        db.close()

    return redirect(url_for("index"))


#ここで削除！！
@app.route("/delete", methods=["POST"])
def complete():
    if "user_id" not in session:
        return redirect("/login")

    dia_id = request.form.get("id")
    query = """
        DELETE  FROM diary
        WHERE dia_id = %s AND user_id = %s
    """
    print(dia_id)
    print("dia_id")

    db = get_db()
    try:
        with db:
            cursor = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(
                query, (dia_id, session['user_id'])            
            )
    finally:
        db.close()

    return redirect(url_for("index"))