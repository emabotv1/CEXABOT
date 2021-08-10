# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from PlusBinance import app, jwt_encode, jwt_decode
from Yardimcilar import PlusBinanceDB, md5_yap
from flask import render_template, request, jsonify, redirect, url_for, session

@app.route('/monitor', methods=['GET', 'POST'])
def monitor():
    if not session.get("token"):
        return redirect(url_for('giris_yap'))

    token     = jwt_decode(session.get('token'))
    database  = PlusBinanceDB()
    kullanici = lambda : database.kull_ver(token["mail"])

    if (request.method == 'POST') and (kullanici()['log']):
        return jsonify(kullanici()['log'][-1])

    if (not kullanici()["ayar"]['api_key']) or (not kullanici()["ayar"]['api_secret']):
        return redirect(url_for('ayar'))

    return render_template(
        'monitor.html',
        baslik     = "Monitör",
        endpoint   = f"http://binance.plusapi.org/webhook/{kullanici()['kull_adi']}?token={md5_yap(kullanici()['kull_adi'])}",
        loglar     = kullanici()['log'][:-1]
    )