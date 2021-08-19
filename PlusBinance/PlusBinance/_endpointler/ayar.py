# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from PlusBinance import app, jwt_encode, jwt_decode
from Yardimcilar import PlusBinanceDB, tg_botumuz
from flask import render_template, request, redirect, url_for, session

#from telebot.apihelper import ApiTelegramException
import telebot

@app.route('/ayar', methods=['GET', 'POST'])
def ayar():
    if not session.get("token"):
        return redirect(url_for('giris_yap'))

    token     = jwt_decode(session.get('token'))
    database  = PlusBinanceDB()
    mail      = token["mail"]
    kullanici = database.kull_ver(mail)[mail]

    if not kullanici:
        return redirect(url_for('giris_yap'))

    if not kullanici['ayar']['api_key']:
        return redirect(url_for('binance_kontrol'))

    hizmet_verilenler = [
        "CAKEUSDT",
        "BURGERUSDT",
        "BAKEUSDT",
        "BTCUSDT",
        "SOLUSDT",
        "ETHUSDT",
        "AXSUSDT",
        "LUNAUSDT",
        "BNBUSDT",
        "XVSUSDT",
        "BTCSTUSDT",
        "AVAXUSDT",
        "UNFIUSDT",
        "SUSHIUSDT",
        "WAVESUSDT",
        "DOGEUSDT",
        "ATOMUSDT", 
        "CHZUSDT", 
        "SNXUSDT",
        "EGLDUSDT"
    ]
    kalanlar = [parite for parite in hizmet_verilenler if parite not in kullanici["ayar"]["pariteler"]]

    hata = ""
    if request.method == 'POST':
        # Güncelleme
        if (not request.form['satis_tip']):
            hata = 'Lütfen Strateji Tipi Seçiniz..'
        elif (request.form['satis_tip'] == "spot") and (not request.form['kar_yuzde']):
            hata = 'Kâr Yüzdesi Düzgün Belirtiniz (Sayı haricinde giriş yapamazsınız)..'
        elif (request.form['satis_tip'] == "oco") and (not request.form['kar_yuzde'] or not request.form['zarar_yuzde']):
            hata = 'Kâr ve Zarar Yüzdesi Düzgün Belirtiniz (Sayı haricinde giriş yapamazsınız)..'
        elif (not request.form['miktar']) or (not request.form['miktar'].isdigit()):
            if request.form['doviz_tip'] == "yuzde":
                hata = 'Döviz Yüzdesini Düzgün Belirtiniz (Sayı haricinde giriş yapamazsınız)..'
            else:
                hata = 'Döviz Miktarını Düzgün Belirtiniz (Sayı haricinde giriş yapamazsınız)..'
        else:
            secilen_pariteler = [sec for sec in hizmet_verilenler if request.form.get(sec) != None]
            database.ayar_guncelle(
                mail        = token["mail"],
                api_key     = kullanici['ayar']['api_key'],
                api_secret  = kullanici['ayar']['api_secret'],
                pariteler   = secilen_pariteler,
                doviz_tip   = request.form['doviz_tip'],
                miktar      = request.form['miktar'],
                satis_tip   = request.form['satis_tip'],
                kar_yuzde   = request.form['kar_yuzde'] if 'kar_yuzde' in request.form else None,
                zarar_yuzde = request.form['zarar_yuzde'] if 'zarar_yuzde' in request.form else None,
                telegram    = request.form['telegram'] if request.form['telegram'] != '' else None
            )

            if request.form['telegram'] != '':
                if (request.form['telegram'][0] == '-' or request.form['telegram'][0].isdigit()):
                    chat  = request.form['telegram']
                else:
                    return redirect(url_for('monitor'))

                mesaj = "✅ *Stratejiniz Başarıyla Oluşturuldu !*\n\n"
                mesaj += "🌐 *Seçilen Parite :* `"
                mesaj += " | ".join(secilen_pariteler)
                mesaj += "`\n"
                if request.form['doviz_tip'] == 'yuzde':
                    mesaj += f"💰 *Bakiye :* `% {request.form['miktar']}`\n"
                else:
                    mesaj += f"💰 *Bakiye :* `{request.form['miktar']} $`\n"

                mesaj += f"🎯 *Strateji Tipi :* `{request.form['satis_tip'].title() if request.form['satis_tip'] != 'spot' else 'Stopsuz'}`\n"
                if 'kar_yuzde' in request.form:
                    mesaj += f"📉 *Kâr Oranı :* `% {request.form['kar_yuzde']}`\n"
                if 'zarar_yuzde' in request.form:
                    mesaj += f"📈 *Zarar Oranı :* `% {request.form['zarar_yuzde']}`\n"

                try:
                    tg_botumuz.send_message(chat, f"{mesaj}")
                except telebot.apihelper.ApiTelegramException:
                    hata = "Girmiş olduğunuz Telegram ID Geçersizdir! Lütfen Kontrol ediniz veya bota start veriniz!"
                    bot_adres = True
                    return render_template(
                        'ayar.html',
                        baslik      = "Bot Ayarları",
                        api_key     = kullanici["ayar"]["api_key"],
                        api_secret  = kullanici["ayar"]["api_secret"],
                        vip         = kullanici["ayar"]["vip"],
                        pariteler   = kullanici["ayar"]["pariteler"],
                        kalanlar    = kalanlar,
                        doviz_tip   = kullanici["ayar"]["doviz_tip"],
                        miktar      = kullanici["ayar"]["miktar"],
                        satis_tip   = kullanici["ayar"]['satis_tip'],
                        kar_yuzde   = kullanici["ayar"]['kar_yuzde'],
                        zarar_yuzde = kullanici["ayar"]['zarar_yuzde'],
                        telegram    = kullanici["ayar"]["telegram"],
                        hata        = hata,
                        bot_adres   = bot_adres,
                        monitor     = bool(kullanici["ayar"]["api_key"] and kullanici["ayar"]["api_secret"])
                    )

            return redirect(url_for('monitor'))

    return render_template(
        'ayar.html',
        baslik      = "Bot Ayarları",
        api_key     = kullanici["ayar"]["api_key"],
        api_secret  = kullanici["ayar"]["api_secret"],
        vip         = kullanici["ayar"]["vip"],
        pariteler   = kullanici["ayar"]["pariteler"],
        kalanlar    = kalanlar,
        doviz_tip   = kullanici["ayar"]["doviz_tip"],
        miktar      = kullanici["ayar"]["miktar"],
        satis_tip   = kullanici["ayar"]['satis_tip'],
        kar_yuzde   = kullanici["ayar"]['kar_yuzde'],
        zarar_yuzde = kullanici["ayar"]['zarar_yuzde'],
        telegram    = kullanici["ayar"]["telegram"],
        hata        = hata,
        monitor     = bool(kullanici["ayar"]["api_key"] and kullanici["ayar"]["api_secret"])
    )