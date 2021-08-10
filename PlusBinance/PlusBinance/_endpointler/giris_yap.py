# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from PlusBinance import app, jwt_encode, jwt_decode
from Yardimcilar import PlusBinanceDB
from flask import render_template, request, session, redirect, url_for

@app.route('/giris_yap', methods=['GET', 'POST'])
def giris_yap():
    if session:
        return redirect(url_for('ayar'))

    hata = ""
    if request.method == 'POST':
        if not request.form['mail']:
            hata = 'eposta giriniz..'
        elif not request.form['sifre']:
            hata = 'sifre giriniz..'
        elif not request.form.getlist('insan'):
            hata = 'insan değil misin?'
        else:
            database  = PlusBinanceDB()
            mail = request.form['mail']
            kullanici = database.db_ara({
                'mail': request.form['mail'],
                "sifre": request.form['sifre']
            })
            if kullanici:
                token = jwt_encode(mail)
                session['token'] = token
                if (kullanici[mail]["ayar"]['api_key']) and (kullanici[mail]["ayar"]['api_secret']):
                    return redirect(url_for('monitor'))
                else:
                    return redirect(url_for('ayar'))
            else:
                hata = 'Böyle bir kullanıcı bulunamadı..'

    return render_template(
        'giris_yap.html',
        baslik = "Giriş Sayfası",
        hata   = hata
    )

@app.route('/cikis_yap')
def cikis_yap():
    if session:
        session.clear()

    return redirect(url_for('ana_sayfa'))
