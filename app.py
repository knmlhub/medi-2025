import sqlite3
from datetime import date, datetime

from flask import Flask, redirect, render_template, request, session, url_for
import base64
import hashlib
import secrets

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
    db = sqlite3.connect("todo.db")
    # 結果にカラム名でアクセスできるようにする
    db.row_factory = sqlite3.Row
    return db


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
        return render_template("login.html", error_user=True, form=request.form)

    password = request.form.get("password")
    if not password:
        return render_template("login.html", error_password=True, form=request.form)

    db = get_db()

    try:
        with db:
            row = db.execute(
                "SELECT * FROM users where name = ?", (username,)
            ).fetchone()
            #ここのエラー治った
            verified = row is not None and verify_password(
                password, row["password_hash"]
            )
            
            if verified:
                session["user_id"] = row["user_id"]
                return redirect(url_for("index"))
            else:
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
    
    # if not username or len(username) < 3:
    #     return render_template("register.html", error_user=True, form=request.form)

    # if not password:
    #     return render_template("register.html", error_password=True, form=request.form)

    # password_confirmation = request.form.get("password_confirmation")
    # if password != password_confirmation:
    #     return render_template("register.html", error_confirm=True, form=request.form)
	
    ###ここでdbからユーザー認証してる
    db = get_db()
    try:
        with db:
            res = db.execute(
                "SELECT * FROM users WHERE name = ?", (username,)
            ).fetchall()
            if len(res) != 0:
                return render_template(
                    "register.html", error_unique=True, form=request.form
                )

            #ここのカラム名みすってた
            password_hash = hash_password(password,)
            db.execute(
                "INSERT INTO users (name, password_hash) VALUES (?, ?)",
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

    query_select = """
        SELECT dia_id, text, date, user_id,title
        FROM diary
    """
    query_where = "WHERE user_id = ?"

    # すべてのタスクを表示するか？ (bool)
    # show_all = request.args.get("all") == "1"
    # if show_all:
    #     # すべてのタスクを完了時刻が新しい順に選択する（NULLはSQLiteでは最も小さい値とみなされる）
    #     # 完了時刻が同じ場合（NULLの場合）、作成時刻が新しい順にする
    #     query_order = "ORDER BY completed_at DESC, created_at DESC"
    #     # query_order = query + " ORDER BY completed_at DESC, created_at DESC"
    #     # query_order = f"{query} ORDER BY completed_at DESC, created_at DESC"
    # else:
    #     # 未完了のタスクを作成時刻が新しい順に選択する
    #     query_where += "AND completed_at IS NULL"
    #     query_order = "ORDER BY created_at DESC"
        
    query = f"{query_select} {query_where}"

    # データベースに接続
    db = get_db()
    try:
        with db:
            # クエリを実行
            cursor = db.execute(query, (session["user_id"],))

            tasks = []
            for row in cursor:
                task = dict(row)
                # 日付時刻をフォーマット
                # task["created_at"] = format_datetime(task["created_at"])
                # task["completed_at"] = format_datetime(task["completed_at"])
                # task["due_date"] = format_date(task["due_date"])
                tasks.append(task)
    finally:
        # 接続をクローズ
        db.close()
        print(tasks)

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
        VALUES (?, ?, ?, ?)
    """

    db = get_db()
    try:
        with db:
            db.execute(
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
        UPDATE diary SET text = ''
        WHERE dia_id = ? AND user_id = ?
    """

    db = get_db()
    try:
        with db:
            db.execute(query, (dia_id, session["user_id"]))
    finally:
        db.close()

    return redirect(url_for("index"))