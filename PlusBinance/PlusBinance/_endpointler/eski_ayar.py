# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from PlusBinance import app, jwt_encode, jwt_decode
from Yardimcilar import PlusBinanceDB
from flask import render_template, request, redirect, url_for, session

@app.route('/ayar', methods=['GET', 'POST'])
def ayar():
    if not session.get("token"):
        return redirect(url_for('giris_yap'))

    token     = jwt_decode(session.get('token'))
    database  = PlusBinanceDB()
    kullanici = database.kull_ver(token["mail"])

    if not kullanici:
        return redirect(url_for('giris_yap'))

    hata = ""
    if request.method == 'POST':
        # Güncelleme
        if not request.form['api_key']:
            hata = 'PlusBinance API key\'inizi düzgün giriniz..'
        elif not request.form['api_secret']:
            hata = 'PlusBinance SECRET key\'inizi düzgün giriniz..'
        elif (not request.form['emir_yuzde']) or (not request.form['emir_yuzde'].isdigit()):
            hata = 'Emir Yüzdesi Düzgün Belirtiniz (Sayı haricinde giriş yapamazsınız)..'
        else:
            database.ayar_guncelle(
                mail       = token["mail"],
                api_key    = request.form['api_key'],
                api_secret = request.form['api_secret'],
                emir_yuzde = request.form['emir_yuzde'],
                telegram   = request.form['telegram'] if request.form['telegram'] != '' else None
            )
            return redirect(url_for('monitor'))

    return render_template(
        'ayar.html',
        baslik     = "Bot Ayarları",
        api_key    = kullanici["ayar"]["api_key"],
        api_secret = kullanici["ayar"]["api_secret"],
        emir_yuzde = kullanici["ayar"]["emir_yuzde"],
        telegram   = kullanici["ayar"]["telegram"],
        hata       = hata,
        monitor    = bool(kullanici["ayar"]["api_key"] and kullanici["ayar"]["api_secret"])
    )