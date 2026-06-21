from fastapi import FastAPI

from aeros.kernel.simulation.humidity_excursion import generate_humidity_excursion
from aeros.kernel.simulation.plant_topology import build_osd_topology

app = FastAPI(title="Areos Kernel API", version="0.1.0")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "aeros-kernel"}


@app.get("/topology")
def topology() -> dict:
    return build_osd_topology()


@app.get("/scenario/humidity-excursion")
def humidity_excursion() -> dict:
    return generate_humidity_excursion()
