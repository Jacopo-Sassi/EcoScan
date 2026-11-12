import os

import bcrypt
import pymysql
from flask import Flask, request, jsonify

app = Flask(__name__)

# Campi dell'utente che si possono restituire al frontend (mai la password)
USER_PUBLIC_FIELDS = "id_user, name, surname, email, id_city"


def get_db_connection():
    # La configurazione arriva da variabili d'ambiente, non dal codice
    return pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ecoscan"),
        cursorclass=pymysql.cursors.DictCursor,
    )


def query_all(sql, params=None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        connection.close()


def query_one(sql, params=None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            return cursor.fetchone()
    finally:
        connection.close()


def execute(sql, params=None):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            last_id = cursor.lastrowid
        connection.commit()
        return last_id
    finally:
        connection.close()


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def check_password(password, password_hash):
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except ValueError:
        # Il valore salvato non è un hash valido (per esempio una vecchia password in chiaro)
        return False


@app.route("/get-user/<int:id_user>", methods=["GET"])
def get_user(id_user):
    user = query_one(
        f"SELECT {USER_PUBLIC_FIELDS} FROM user WHERE id_user = %s", (id_user,)
    )
    if user:
        return jsonify(user), 200
    return jsonify({"error": "Utente non trovato"}), 404


@app.route("/get-user", methods=["GET"])
def get_users():
    users = query_all(f"SELECT {USER_PUBLIC_FIELDS} FROM user")
    if users:
        return jsonify(users), 200
    return jsonify({"error": "Utenti non trovati"}), 404


@app.route("/get-trash", methods=["GET"])
def get_trash_all():
    trash = query_all("SELECT * FROM trash")
    if trash:
        return jsonify(trash), 200
    return jsonify({"error": "Rifiuto non trovato"}), 404


@app.route("/get-trash/<string:query>", methods=["GET"])
def get_trash(query):
    trash = query_all(
        "SELECT trash.* FROM trash "
        "JOIN category ON trash.id_category = category.id_category "
        "WHERE trash.name LIKE %s OR category.name LIKE %s",
        (f"%{query}%", f"%{query}%"),
    )
    if trash:
        return jsonify(trash), 200
    return jsonify({"error": "Rifiuto non trovato"}), 404


@app.route("/get-advice", methods=["GET"])
def get_advices():
    advices = query_all("SELECT * FROM advice")
    if advices:
        return jsonify(advices), 200
    return jsonify({"error": "Consigli non disponibili"}), 404


@app.route("/get-advice/<int:id_trash>", methods=["GET"])
def get_advice(id_trash):
    advices = query_all("SELECT * FROM advice WHERE id_trash = %s", (id_trash,))
    if advices:
        return jsonify(advices), 200
    return jsonify({"error": "Consigli non disponibili"}), 404


@app.route("/get-city", methods=["GET"])
def get_cities():
    cities = query_all("SELECT * FROM city")
    if cities:
        return jsonify(cities), 200
    return jsonify({"error": "Città non trovate"}), 404


@app.route("/get-city/<int:id_city>", methods=["GET"])
def get_city(id_city):
    city = query_one("SELECT * FROM city WHERE id_city = %s", (id_city,))
    if city:
        return jsonify(city), 200
    return jsonify({"error": "Città non trovata"}), 404


@app.route("/get-category", methods=["GET"])
def get_categories():
    categories = query_all("SELECT * FROM category")
    if categories:
        return jsonify(categories), 200
    return jsonify({"error": "Categorie non trovate"}), 404


@app.route("/get-category/<int:id_category>", methods=["GET"])
def get_category(id_category):
    category = query_one(
        "SELECT * FROM category WHERE id_category = %s", (id_category,)
    )
    if category:
        return jsonify(category), 200
    return jsonify({"error": "Categoria non trovata"}), 404


@app.route("/get-week", methods=["GET"])
def get_weeks():
    weeks = query_all("SELECT * FROM week")
    if weeks:
        return jsonify(weeks), 200
    return jsonify({"error": "Settimane non disponibili"}), 404


@app.route("/get-week/<int:id_week>", methods=["GET"])
def get_week(id_week):
    week = query_one("SELECT * FROM week WHERE id_week = %s", (id_week,))
    if week:
        return jsonify(week), 200
    return jsonify({"error": "Settimana non trovata"}), 404


@app.route("/get-calendar", methods=["GET"])
def get_calendar_all():
    calendar = query_all("SELECT * FROM calendar")
    if calendar:
        return jsonify(calendar), 200
    return jsonify({"error": "Impossibile ottenere calendario"}), 404


@app.route("/get-calendar/<int:id_city>", methods=["GET"])
def get_calendar(id_city):
    calendar = query_all("SELECT * FROM calendar WHERE id_city = %s", (id_city,))
    if calendar:
        return jsonify(calendar), 200
    return jsonify({"error": "Calendario non trovato"}), 404


@app.route("/get-filedata/<int:id_filedata>", methods=["GET"])
def get_filedata(id_filedata):
    file = query_one(
        "SELECT * FROM filedata WHERE id_filedata = %s", (id_filedata,)
    )
    if file:
        return jsonify(file), 200
    return jsonify({"error": "File dati non trovato"}), 404


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Campi obbligatori mancanti."}), 400

    # Cerco l'utente solo per email, poi verifico la password con l'hash
    user = query_one("SELECT * FROM user WHERE email = %s", (email,))

    if not user or not check_password(password, user["password"]):
        # Stesso messaggio in entrambi i casi: non rivela se l'email esiste
        return jsonify({"error": "Credenziali non valide"}), 401

    user.pop("password", None)
    return jsonify({"message": "Login riuscito!", "user": user}), 200


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    surname = data.get("surname")
    email = data.get("email")
    password = data.get("password")
    id_city = 1

    if not name or not surname or not email or not password:
        return jsonify({"error": "Campi obbligatori mancanti."}), 400

    if len(password) < 8:
        return jsonify({"error": "La password deve avere almeno 8 caratteri."}), 400

    if query_one("SELECT id_user FROM user WHERE email = %s", (email,)):
        return jsonify({"error": "Email già registrata."}), 409

    id_user = execute(
        "INSERT INTO user (name, surname, email, password, id_city) "
        "VALUES (%s, %s, %s, %s, %s)",
        (name, surname, email, hash_password(password), id_city),
    )

    # La risposta non contiene mai la password
    return (
        jsonify(
            {
                "message": "Registrazione riuscita!",
                "user": {
                    "id_user": id_user,
                    "name_user": name,
                    "surname_user": surname,
                    "email_user": email,
                    "id_city": id_city,
                },
            }
        ),
        201,
    )


@app.route("/update-city", methods=["PUT"])
def set_city():
    data = request.get_json(silent=True) or {}
    id_user = data.get("id_user")
    id_city = data.get("id_city")

    if not id_user:
        return jsonify({"error": "id_user mancante."}), 400

    if not id_city:
        return jsonify({"error": "id_city mancante."}), 400

    execute(
        "UPDATE user SET id_city = %s WHERE id_user = %s",
        (id_city, id_user),
    )
    return jsonify({"message": "Città aggiornata con successo!"}), 200


@app.route("/insert-user_trash", methods=["POST"])
def insert_user_trash():
    data = request.get_json(silent=True) or {}
    id_user = data.get("id_user")
    id_trash = data.get("id_trash")

    if not id_user:
        return jsonify({"error": "id_user mancante."}), 400

    if not id_trash:
        return jsonify({"error": "id_trash mancante."}), 400

    execute(
        "INSERT INTO user_trash (id_user, id_trash) VALUES (%s, %s)",
        (id_user, id_trash),
    )
    return (
        jsonify(
            {
                "message": f"Rifiuto {id_trash} scannerizzato da utente {id_user}!",
                "user_trash": {"id_user": id_user, "id_trash": id_trash},
            }
        ),
        201,
    )


@app.route("/get-user_trash-count/<int:id_user>", methods=["GET"])
def get_user_trash_count(id_user):
    count = query_one(
        "SELECT COUNT(*) AS 'count_rifiuti' FROM user_trash WHERE id_user = %s",
        (id_user,),
    )
    if count:
        return jsonify(count), 200
    return jsonify({"error": "Impossibile contare rifiuti scannerizzati"}), 404


@app.route("/get-user_trash-filter/<int:id_user>", methods=["GET"])
def get_user_trash_filter(id_user):
    trash = query_all(
        "SELECT id_trash FROM user_trash WHERE id_user = %s",
        (id_user,),
    )
    if trash:
        return jsonify(trash), 200
    return (
        jsonify(
            {"error": f"Impossibile ottenere i rifiuti scannerizzati dall'utente {id_user}"}
        ),
        404,
    )


if __name__ == "__main__":
    # Il debugger di Flask non va mai attivato su un server raggiungibile da altri
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
