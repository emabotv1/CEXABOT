# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from PlusBinance import app
from Yardimcilar import PlusBinanceDB
from flask import render_template, request, session, redirect, url_for

@app.route('/kayit_ol', methods=['GET', 'POST'])
def kayit_ol():
    if session:
        return redirect(url_for('ayar'))

    hata = ""
    if request.method == 'POST':
        if not request.form['ad_soyad']:
            hata = 'isim ve soyisim giriniz..'
        elif not request.form['kull_adi']:
            hata = 'kullanıcı adınızı giriniz..'
        elif not request.form['mail']:
            hata = 'eposta giriniz..'
        elif not request.form['sifre']:
            hata = 'sifre giriniz..'
        elif not request.form.getlist('insan'):
            hata = 'insan değil misin?'
        else:
            database = PlusBinanceDB()
            kayit = database.ekle(request.form['mail'], request.form['ad_soyad'], request.form['sifre'], request.form['kull_adi'])
            if kayit:
                return redirect(url_for('giris_yap'))
            else:
                hata = 'E-Posta Adresiniz veya Kullanıcı Adınız Kullanılıyor..'

    return render_template(
        'kayit_ol.html',
        baslik = "Kayıt Sayfası",
        hata   = hata
    )