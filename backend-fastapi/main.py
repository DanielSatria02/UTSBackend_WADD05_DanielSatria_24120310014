import json
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)


class BarangCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nama: StrictStr
    kategori: StrictStr
    jumlah_stok: StrictInt = Field(ge=0)
    lokasi_gudang: StrictStr


class BarangResponse(BarangCreate):
    id: StrictInt


DATA_FILE = Path(__file__).with_name("barang.json")
with DATA_FILE.open(encoding="utf-8") as file:
    barang_list = [BarangResponse.model_validate(item) for item in json.load(file)]


@app.get("/")
def baca_root():
    return {"pesan": "Backend FastAPI berjalan"}


@app.get("/barang", response_model=list[BarangResponse])
def ambil_semua_barang():
    return barang_list


@app.post(
    "/barang",
    response_model=BarangResponse,
    status_code=status.HTTP_201_CREATED,
)
def tambah_barang(barang: BarangCreate):
    next_id = max((item.id for item in barang_list), default=0) + 1
    barang_baru = BarangResponse(id=next_id, **barang.model_dump())
    barang_list.append(barang_baru)
    return barang_baru


@app.delete("/barang/{barang_id}", status_code=status.HTTP_204_NO_CONTENT)
def hapus_barang(barang_id: int):
    for index, barang in enumerate(barang_list):
        if barang.id == barang_id:
            barang_list.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Barang tidak ditemukan")
