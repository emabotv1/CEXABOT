# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from PlusBinance import app
from flask import render_template, jsonify

@app.route('/')
def ana_sayfa():

    return render_template(
        'ana_sayfa.html',
        baslik = "PlusBinance",
        icerik = "Otomasyon Paneli"
    )