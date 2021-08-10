# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from PlusBinance import app, jwt_encode, jwt_decode
from Yardimcilar import PlusBinanceDB, BinanceSAPI
from flask import render_template, request, redirect, url_for, session
from deep_translator import GoogleTranslator

@app.route('/binance_kontrol', methods=['GET', 'POST'])
def binance_kontrol():
    if not session.get("token"):
        return redirect(url_for('giris_yap'))

    token     = jwt_decode(session.get('token'))
    database  = PlusBinanceDB()
    mail      = token["mail"]
    kullanici = database.kull_ver(mail)[mail]

    if not kullanici:
        return redirect(url_for('giris_yap'))

    if kullanici['ayar']['api_key']:
        return redirect(url_for('ayar'))

    hata     = None

    if request.method == 'POST':
        # Güncelleme
        if not request.form['api_key']:
            hata = 'PlusBinance API key\'inizi düzgün giriniz..'
        elif not request.form['api_secret']:
            hata = 'PlusBinance SECRET key\'inizi düzgün giriniz..'
        else:
            try:
                binance = BinanceSAPI(request.form['api_key'], request.form['api_secret'])
                hata = binance._kac_para_var('USDT')
                database.ayar_guncelle(
                    mail        = mail,
                    api_key     = request.form['api_key'],
                    api_secret  = request.form['api_secret'],
                    pariteler   = [],
                    doviz_tip   = None,
                    miktar      = None,
                    satis_tip   = None,
                    kar_yuzde   = None,
                    zarar_yuzde = None,
                    telegram    = None
                )
                return redirect(url_for('ayar'))
            except Exception as h:
                hata = GoogleTranslator(source='en', target='tr').translate(f"{h.message}").strip()
                # hata = f"{type(h).__name__} | {h}"

    return render_template(
        'binance_kontrol.html',
        baslik = 'Binance Bağlantısı',
        hata   = hata
    )