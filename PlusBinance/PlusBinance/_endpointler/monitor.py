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
    mail      = token["mail"]
    kullanici = lambda : database.kull_ver(mail)

    if (request.method == 'POST') and (kullanici()[mail]['log']):
        return jsonify(kullanici()[mail]['log'][-1])

    if (not kullanici()[mail]["ayar"]['api_key']) or (not kullanici()[mail]["ayar"]['api_secret']):
        return redirect(url_for('ayar'))

    def log():
        liste = []
        for i in kullanici()[mail]['log']:
            if i["adet_coin"] != "" and i["adet_coin"] != "Bu istek için imza geçerli değil.":
                liste.append(i)
        return liste

    return render_template(
        'monitor.html',
        baslik      = "Monitör",
        pariteler   = " | ".join(kullanici()[mail]["ayar"]["pariteler"]),
        doviz_tip   = kullanici()[mail]["ayar"]["doviz_tip"],
        miktar      = kullanici()[mail]["ayar"]["miktar"],
        satis_tip   = kullanici()[mail]["ayar"]['satis_tip'],
        kar_yuzde   = kullanici()[mail]["ayar"]['kar_yuzde'],
        zarar_yuzde = kullanici()[mail]["ayar"]['zarar_yuzde'],
        telegram    = kullanici()[mail]["ayar"]["telegram"],
        loglar      = log()
    )