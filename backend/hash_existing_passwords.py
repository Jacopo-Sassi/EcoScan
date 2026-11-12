"""Da eseguire una sola volta: trasforma in hash bcrypt le password
già salvate in chiaro nel database (per esempio gli utenti di ecoscan.sql)."""

from api import get_db_connection, hash_password

connection = get_db_connection()
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT id_user, password FROM user")
        users = cursor.fetchall()
        updated = 0
        for user in users:
            if not user["password"].startswith("$2"):  # non è ancora un hash bcrypt
                cursor.execute(
                    "UPDATE user SET password = %s WHERE id_user = %s",
                    (hash_password(user["password"]), user["id_user"]),
                )
                updated += 1
    connection.commit()
    print(f"Password aggiornate: {updated}")
finally:
    connection.close()
