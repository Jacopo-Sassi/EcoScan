♻️ EcoScan – Waste Management & Recycling Assistant
🚀 Overview

EcoScan è una web app full-stack pensata per migliorare la gestione dei rifiuti e aiutare gli utenti a capire come smaltire correttamente ogni tipo di materiale.

L’app combina:

Frontend in React → interfaccia utente moderna
Backend in Flask (Python) → API REST
Database MySQL → gestione dati (utenti, rifiuti, categorie, calendario, ecc.)

Spoiler: non è solo CRUD, c’è anche logica utile (ricerca rifiuti, consigli, tracking utenti).

🧠 Features principali
🔍 Ricerca rifiuti per nome o categoria
📅 Calendario raccolta per città
👤 Gestione utenti (login, registrazione)
♻️ Consigli su come smaltire i rifiuti
📊 Tracking rifiuti scannerizzati dall’utente
🏙️ Selezione città personalizzata
🏗️ Architettura
Frontend (React)

Routing gestito con react-router-dom:

/ricerca → ricerca rifiuti
/rifiuto → dettaglio rifiuto
/foto → (probabile feature scanner?)
/calendario → calendario raccolta (commentato… perché? 👀)
/comune → gestione città

Layout separati:

DefaultLayout
LayoutSecondario

👉 Nota: hai un conflitto Git NON risolto. Sistemalo prima di fare il fenomeno.

Backend (Flask API)

Server REST con connessione MySQL (pymysql).

Endpoint principali
👤 Utenti
GET /get-user/<id>
GET /get-user
POST /login
POST /register
PUT /update-city
♻️ Rifiuti
GET /get-trash
GET /get-trash/<query>
💡 Consigli
GET /get-advice
GET /get-advice/<id_trash>
🏙️ Città
GET /get-city
GET /get-city/<id>
📅 Calendario
GET /get-calendar
GET /get-calendar/<id_city>
📊 Tracking utente
POST /insert-user_trash
GET /get-user_trash-count/<id_user>
GET /get-user_trash-filter/<id_user>
🗄️ Database

Database: ecoscan

Tabelle principali:

user
trash
category
advice
city
calendar
week
user_trash
