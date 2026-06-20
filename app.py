from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
import csv
import requests

app = Flask(__name__)
app.secret_key = "hulk_secret_key"


# 🟢 ADMIN CHECK
def admin_required():
    return session.get("role") == "admin"


# 🟢 MSF API TOKEN (SEPARADO)
def get_msf_token():

    url = "https://api.marvelstrikeforce.com/oauth/token"

    data = {
        "grant_type": "client_credentials",
        "client_id": "b6f8eb1f-40fa-4683-843d-f5588aa0e248",
        "client_secret": "QRZOnnt1plwLYjE522va.G3~65"
    }

    headers = {
        "x-api-key": "17wMKJLRxy3pYDCKG5ciP7VSU45OVumB2biCzzgw",
        "Content-Type": "application/json"
    }

    response = requests.post(url, data=data, headers=headers)

    print(response.status_code)
    print(response.text)

    return response.json()
    

    print(response.status_code)
    print(response.text)

    return response.json()


# 🟢 COUNTERS (CSV + SQLITE)
def get_counters():
    results = []

    # 1️⃣ LEER CSV
    try:
        with open("counters.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                results.append({
                    "team": row.get("Team") or row.get("team"),
                    "counter": row.get("Counter") or row.get("counter"),
                    "note": row.get("Note") or row.get("note")
                })

    except FileNotFoundError:
        print("No CSV found")

    # 2️⃣ LEER SQLITE
    conn = sqlite3.connect("hulkamb.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM counters")
    rows = cursor.fetchall()

    for r in rows:
        results.append({
            "team": r["team"],
            "counter": r["counter"],
            "note": r["note"]
        })

    conn.close()

    return results

ADMIN_USER = "Knull"


# ---------------------------
# BASE DE DATOS: GUERRAS
# ---------------------------

def get_wars():
    conn = sqlite3.connect("hulkamb.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM wars ORDER BY id DESC")
    wars = cursor.fetchall()

    conn.close()
    return wars


# ---------------------------
# BASE DE DATOS: INFOGRAFÍAS
# ---------------------------

def get_infografias():
    conn = sqlite3.connect("hulkamb.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM infografias ORDER BY id DESC")
    data = cursor.fetchall()

    conn.close()
    return data


# ---------------------------
# LOGIN
# ---------------------------

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form["user"]
        password = request.form["password"]

        # ADMIN
        if user == "knull" and password == "1234":
            session["user"] = user
            session["role"] = "admin"
            return redirect("/counters")

        # USUARIO NORMAL
        if user == "hulk" and password == "amb123":
            session["user"] = user
            session["role"] = "user"
            return redirect("/counters")

        return render_template("login.html", error="Credenciales incorrectas")

    return render_template("login.html")


# ---------------------------
# DASHBOARD
# ---------------------------

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")
    return render_template("dashboard.html")


# ---------------------------
# GUERRAS
# ---------------------------

@app.route("/war")
def war():
    if "user" not in session:
        return redirect("/")

    wars = get_wars()
    return render_template("war.html", wars=wars)


@app.route("/delete_war", methods=["POST"])
def delete_war():
    if "user" not in session:
        return redirect("/")

    if session.get("user") != ADMIN_USER:
        return "No autorizado 💀"

    war_id = request.form["id"]

    conn = sqlite3.connect("hulkamb.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM wars WHERE id = ?", (war_id,))

    conn.commit()
    conn.close()

    return redirect("/war")


# ---------------------------
# INFOGRAFÍAS
# ---------------------------

@app.route("/infografias")
def infografias():
    if "user" not in session:
        return redirect("/")

    data = get_infografias()

    query = request.args.get("q", "").lower()

    if query:
        data = [
            i for i in data
            if query in i["nombre"].lower()
        ]

    return render_template(
        "infografias.html",
        infografias=data,
        query=query
    )


@app.route("/add_infografia", methods=["GET", "POST"])
def add_infografia():

    if not admin_required():
        return "No autorizado", 403

    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        nombre = request.form["nombre"]
        imagen = request.files["imagen"]

        filename = imagen.filename
        path = os.path.join("static/images", filename)
        imagen.save(path)

        conn = sqlite3.connect("hulkamb.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO infografias (nombre, imagen)
            VALUES (?, ?)
        """, (nombre, filename))

        conn.commit()
        conn.close()

        return redirect("/infografias")

    return render_template("add_infografia.html")

    return render_template("add_infografia.html")

@app.route("/infografia/<int:id>")
def ver_infografia(id):
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("hulkamb.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM infografias WHERE id = ?",
        (id,)
    )

    infografia = cursor.fetchone()

    conn.close()

    return render_template(
        "ver_infografia.html",
        infografia=infografia
    )


# ---------------------------
# OTRAS SECCIONES
# ---------------------------

@app.route("/stats")
def stats():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("hulkamb.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM wars")
    wars = cursor.fetchall()

    conn.close()

    total = len(wars)

    victorias = sum(
        1 for w in wars
        if w["resultado"].lower() == "victoria"
    )

    derrotas = total - victorias

    porcentaje = 0
    if total > 0:
        porcentaje = round((victorias / total) * 100)

    return render_template(
        "stats.html",
        total=total,
        victorias=victorias,
        derrotas=derrotas,
        porcentaje=porcentaje
    )


@app.route("/counters", methods=["GET"])
def counters():
    if "user" not in session:
        return redirect("/")

    data = get_counters()

    query = request.args.get("q", "").lower()

    if query:
        data = [
            c for c in data
            if query in c["team"].lower()
            or query in c["counter"].lower()
            or query in c["note"].lower()
        ]

    return render_template("counters.html", counters=data, query=query)


@app.route("/members")
def members():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("hulkamb.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM members")
    data = cursor.fetchall()

    conn.close()

    return render_template("members.html", members=data)


@app.route("/api_test")
def api_test():
    try:
        token = get_msf_token()
        return {
            "status": "ok",
            "token_received": "access_token" in token,
            "raw": token
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }


@app.route("/add_member", methods=["GET", "POST"])
def add_member():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        role = request.form["role"]
        pc = request.form["pc"]

        conn = sqlite3.connect("hulkamb.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO members (name, role, tcp)
            VALUES (?, ?, ?)
        """, (name, role, pc))

        conn.commit()
        conn.close()

        return redirect("/members")

    return render_template("add_member.html")


@app.route("/admin")
def admin():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("hulkamb.db")
    cursor = conn.cursor()

    # Guerras
    cursor.execute("SELECT COUNT(*) FROM wars")
    wars = cursor.fetchone()[0]

    # Counters
    cursor.execute("SELECT COUNT(*) FROM counters")
    counters = cursor.fetchone()[0]

    # Infografías
    cursor.execute("SELECT COUNT(*) FROM infografias")
    infografias = cursor.fetchone()[0]

    # Miembros
    cursor.execute("SELECT COUNT(*) FROM members")
    members = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        wars=wars,
        counters=counters,
        infografias=infografias,
        members=members
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/add_war", methods=["GET", "POST"])
def add_war():
    if "user" not in session:
        return redirect("/")
    
    if not admin_required():
        return "No autorizado", 403

    if request.method == "POST":
        rival = request.form["rival"]
        liga = request.form["liga"]
        fecha = request.form["fecha"]
        resultado = request.form["resultado"]
        fallos = request.form["fallos"]
        defensas = request.form["defensas"]

        conn = sqlite3.connect("hulkamb.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO wars (rival, liga, fecha, resultado, fallos, defensas)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (rival, liga, fecha, resultado, fallos, defensas))

        conn.commit()
        conn.close()

        return redirect("/war")

    return render_template("add_war.html")


@app.route("/add_counter", methods=["GET", "POST"])
def add_counter():
    if "user" not in session:
        return redirect("/")
    
    if not admin_required():
        return "No autorizado", 403

    if request.method == "POST":
        team = request.form["team"]
        counter = request.form["counter"]
        note = request.form["note"]

        conn = sqlite3.connect("hulkamb.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO counters (team, counter, note)
            VALUES (?, ?, ?)
        """, (team, counter, note))

        conn.commit()
        conn.close()

        return redirect("/counters")

    return render_template("add_counter.html")


@app.route("/delete_counter/<int:id>")
def delete_counter(id):
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("hulkamb.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM counters WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/counters")





# ---------------------------
# RUN APP
# ---------------------------

if __name__ == "__main__":
    app.run(debug=True)