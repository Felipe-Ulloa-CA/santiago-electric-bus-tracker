from fastapi import FastAPI, HTTPException
from typing import List
import pandas as pd
from pathlib import Path
from math import radians, sin, cos, asin, sqrt

app = FastAPI(title="Santiago Electric Bus Tracker API", version="0.1.0")
DATA = Path(__file__).resolve().parents[1] / "data" / "sample_buses.csv"
df = pd.read_csv(DATA)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = radians(lat1), radians(lat2)
    dphi = radians(lat2 - lat1)
    dlambda = radians(lon2 - lon1)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dlambda/2)**2
    return 2*R*asin(sqrt(a))

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/buses")
def buses(limit: int = 50):
    return df.head(limit).to_dict(orient="records")

@app.get("/eta")
def eta(bus_id: str):
    rec = df[df["bus_id"] == bus_id]
    if rec.empty:
        raise HTTPException(status_code=404, detail="bus_id not found")
    r = rec.iloc[0]
    dist_km = haversine(r.latitude, r.longitude, r.next_stop_lat, r.next_stop_lon)
    speed = max(5.0, float(r.speed_kph))
    eta_min = (dist_km / speed) * 60.0 * max(0.7, min(1.6, float(r.traffic_index)))
    return {"bus_id": bus_id, "route": r.route, "distance_km": round(dist_km,3), "eta_min_est": round(eta_min,2)}