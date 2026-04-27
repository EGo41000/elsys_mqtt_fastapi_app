from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from datetime import datetime
import json, requests, os, psycopg
from dotenv import load_dotenv  # pip install python-dotenv

load_dotenv()

app = FastAPI()

# Monter les fichiers statiques (optionnel)
#app.mount("/static", StaticFiles(directory="static"), name="static")

# Configurer les templates
templates = Jinja2Templates(directory="templates")

# Configuration TTN
TTN_APP_ID = os.getenv("TTN_APP_ID", "app_id")
TTN_DEVICE_ID = os.getenv("TTN_DEVICE_ID", "device_id")
TTN_API_KEY = os.getenv("TTN_API_KEY", "api_key")

# URL pour les données TTN (V3)
TTN_URL = f"https://eu1.cloud.thethings.network/api/v3/as/applications/{TTN_APP_ID}/devices/{TTN_DEVICE_ID}/packages/storage/uplink_message?last=24h"
headers={'Authorization': f"Bearer {TTN_API_KEY}", 'Accept': 'text/event-stream'}

print(f"{TTN_URL=}")

POSTGRES_URL = os.getenv("POSTGRES_URL")
print(f"{POSTGRES_URL=}")
try:
    conn_dict =  psycopg.conninfo.conninfo_to_dict(POSTGRES_URL)

    with psycopg.connect(**conn_dict) as conn:
        with conn.cursor() as cur:
            cur.execute("""select dt::varchar, "data"->'result'->'uplink_message'->'decoded_payload' as X from logs""")
            for row in cur:
                print(row)
except Exception:
    print('Exception...')

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):

    r = requests.get(TTN_URL, headers=headers)
    data=[]
    for line in r.text.split('\n\n'):
        #print(line)
        if not line : continue
        x=json.loads(line)
        result = x.get('result')
        dp = result.get('uplink_message').get('decoded_payload')
        #data.append({})
        dp['time'] = result.get('received_at')
        #print(json.dumps(dp, indent=2))
        data.append(dp)
    print(f"TTN [{r.status_code}] {len(data)} lines")

    # Préparer les données pour les graphiques
    times = [item["time"] for item in data]
    external_temp = [item["externalTemperature"] for item in data]
    temperature = [item["temperature"] for item in data]
    humidity = [item["humidity"] for item in data]
    pressure = [item["pressure"] for item in data]
    vdd = [item["vdd"] for item in data]

    # Préparer les données pour externalTemperature2 (3 séries)
    external_temp2_1 = [item["externalTemperature2"][0] for item in data]
    external_temp2_2 = [item["externalTemperature2"][1] for item in data]
    external_temp2_3 = [item["externalTemperature2"][2] for item in data]

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "times": json.dumps(times),
            "external_temp": json.dumps(external_temp),
            "temperature": json.dumps(temperature),
            "humidity": json.dumps(humidity),
            "pressure": json.dumps(pressure),
            "vdd": json.dumps(vdd),
            "external_temp2_1": json.dumps(external_temp2_1),
            "external_temp2_2": json.dumps(external_temp2_2),
            "external_temp2_3": json.dumps(external_temp2_3),
            "data_table": data
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
