from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
import sqlite3, os, uuid
from ics import Calendar, Event

app = FastAPI()
DATA_DIR = os.getenv("DATA_DIR", "/data")
DB_PATH = os.path.join(DATA_DIR, "agenda.sqlite")
ICS_PATH = os.path.join(DATA_DIR, "agenda.ics")

# Crear carpeta y base de datos si no existen
os.makedirs(DATA_DIR, exist_ok=True)
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("""CREATE TABLE IF NOT EXISTS appointments(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT, phone TEXT, reason TEXT,
 start_ts TEXT, end_ts TEXT, created_at TEXT );""")
conn.commit()
conn.close()

# Función para exportar el calendario .ics
def export_ics():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT name, reason, start_ts, end_ts FROM appointments ORDER BY start_ts;")
    rows = cur.fetchall()
    conn.close()
    cal = Calendar()
    for (name, reason, start_ts, end_ts) in rows:
        e = Event()
        e.name = f"Cita: {name}"
        e.begin = start_ts
        e.end = end_ts
        e.description = reason or ""
        cal.events.add(e)
    with open(ICS_PATH, "w") as f:
        f.writelines(cal)

# Ruta de prueba
@app.get("/")
def health():
    return {"ok": True, "msg": "voicebot orchestrator listo"}

# Endpoint para procesar el audio (simulado ahora)
@app.post("/turn")
async def turn(audio: UploadFile, call_id: str = Form(...), turn: str = Form(...)):
    tmp_id = str(uuid.uuid4())[:8]
    raw_path = os.path.join(DATA_DIR, f"{call_id}_{turn}_{tmp_id}.wav")

    # Guardamos el audio que llega
    with open(raw_path, "wb") as f:
        f.write(await audio.read())

    # Simulamos respuesta del bot (luego la IA real irá aquí)
    prompts = {
        "turn1": "Hola 👋 Soy el asistente de reservas. ¿Para qué día y a qué hora quieres la cita?",
        "turn2": "Perfecto. ¿A nombre de quién la apunto y cuál es el motivo?",
        "turn3": "Genial. Te confirmo la reserva. ¿Quieres que te enviemos un recordatorio?"
    }
    bot_text = prompts.get(turn, "Gracias. Tu cita queda registrada. ¡Hasta pronto!")

    return JSONResponse({
        "user_text": "(ASR simulado)",
        "bot_text": bot_text,
