from PlusBinance import app
from Yardimcilar import PlusBinanceDB, BinanceSAPI, ondalik_kisalt
from flask import request, make_response, jsonify

import json
from requests import post, get
from telegram.ext import Updater

token = "1812551326:AAHlDX6oTU7UvXPy2DMz-m2l61wMZRrIGkU"
chat  = "-1001553338929"

def webhook_telegram(coin,signal):
    
    url = f"https://s.tradingview.com/widgetembed/?frameElementId=tradingview_7930e&symbol=BINANCE%3A{coin}&interval=240&hidetoptoolbar=1&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=BB%40tv-basicstudies%1FMACD%40tv-basicstudies%1FStochasticRSI%40tv-basicstudies&theme=dark&style=8&timezone=Europe%2FIstanbul&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=tr&utm_source=localhost&utm_medium=widget&utm_campaign=chart&utm_term=BINANCE%3ADOGEUSDT"
    response = get("https://webshot.amanoteam.com/print", params=dict(q=url))

    path = '/root/Projects/PlusBinance/PlusBinance/_endpointler/coin.jpg'
  
    if response.status_code == 200:
        with open(path, 'wb') as file:
            for chunk in response:
                file.write(chunk)
    
    with open('/root/Projects/PlusBinance/PlusBinance/_endpointler/Kriptolar.json', "r", encoding="utf-8") as d:
      data = json.load(d)

    with open('/root/Projects/PlusBinance/PlusBinance/_endpointler/Alerts.json', "r", encoding="utf-8") as d:
      data2 = json.load(d)

    data = data[data2[coin]["COIN"]]['destek']
    caption = f"COIN: #{coin}\nSIGNAL: {data2[coin]['SIGNAL']}\nPRICE: {data2[coin]['PRICE']}\n\n"

    if signal  == "SAT" and data2[coin]["EntryPrice"] != "null":
        a = data2[coin]["EntryPrice"]
        b = data2[coin]["PRICE"]
        yuzde = round(((b-a)/a)*100,2)
        caption += f"PROFIT: {yuzde}%\n\n"
    
    caption += f"""Yapay Zekanın {coin} için güncel destek ve direnç bilgisi;

📉 Direnç (R3)  : {data['direnc3']}
📉 Direnç (R2)  : {data['direnc2']}
📉 Direnç (R1)  : {data['direnc1']}
📍 Pivot Noktası : {data['pivot']}
📈 Destek (S1)  : {data['destek1']}
📈 Destek (S2)  : {data['destek2']}
📈 Destek (S3)  : {data['destek3']}
    """

    updater = Updater(token)
    dp = updater.dispatcher
    dp.bot.send_photo(chat_id=chat, photo=open(path, 'rb'),caption=caption)
    
    import os
    os.remove(path) 


semboller = ["CAKEUSDT","BURGERUSDT","BAKEUSDT","BTCUSDT","SOLUSDT","XVSUSDT","AVAXUSDT","ETHUSDT","BTCSTUSDT","LUNAUSDT","BNBUSDT","AXSUSDT","UNFIUSDT","SUSHIUSDT","WAVESUSDT","DOGEUSDT","ATOMUSDT","CHZUSDT","SNXUSDT","EGLDUSDT"]

@app.route("/webhook/<sembol>", methods=["GET", "POST"])
def webhook_statik(sembol):
    if sembol in semboller:
    
        # Metin Abinin Saçma Sİnyalinin Ayıklanması
        sacma_veri = request.data.decode('utf-8').split(', ')
        
        if sacma_veri[0] == "AL : olası ticaret fırsatı" or sacma_veri[0] == "SAT : olası ticaret fırsatı":
            duzgun_veri = {
                'sembol': sembol,
                'sinyal': sacma_veri[0].split(' :')[0],
                'fiyat': round(float(sacma_veri[1].split(' ')[1].strip()),2),
            }
            coin = sembol
            alert = duzgun_veri['sinyal']

            with open('/root/Projects/PlusBinance/PlusBinance/_endpointler/Alerts.json') as f:
                veri = json.load(f)
            if veri[coin]["SIGNAL"] == alert:
                post(f"https://api.telegram.org/bot{token}/sendMessage?chat_id=-1001434966274", data={'text': f'{coin} sinyal geldi ama şuanki sinyalle aynı.\nŞuanki sinyal : {alert}'})

            elif veri[coin]["SIGNAL"] != alert:
                if alert == "AL":
                    veri[coin]["EntryPrice"] = duzgun_veri["fiyat"]
                # dataya sinyali ve fiyatı kaydetme işlemi
                veri[coin]["SIGNAL"] = alert
                veri[coin]["PRICE"] = duzgun_veri["fiyat"]
                with open('/root/Projects/PlusBinance/PlusBinance/_endpointler/Alerts.json', 'w') as json_dosya:
                    json.dump(veri, json_dosya)


                database     = PlusBinanceDB()
                kullanicilar = database.db_ara({"ayar.pariteler": {'$in': [duzgun_veri['sembol']]}})

                if kullanicilar != None:
                    for mail in kullanicilar:
                        print("for döngüsü içindeyim sj")
                    # Binance İşleri Burdan Sonra Yapılacak!
                        binance_kisi = BinanceSAPI(kullanicilar[mail]['ayar']['api_key'], kullanicilar[mail]['ayar']['api_secret'])


                        veri = {}
                        if duzgun_veri['sinyal'] == 'AL':

                            veri['spot_alim']   = binance_kisi.spot_alim(duzgun_veri['sembol'], kullanicilar[mail]['ayar']['doviz_tip'], int(kullanicilar[mail]['ayar']['miktar']),mail=mail)
                            if 'hata' in list(veri['spot_alim'].keys()):
                                database.log_salla(
                                    mail        = mail,
                                    olay        = 'Spot Alım',
                                    parite      = duzgun_veri['sembol'],
                                    adet_coin   = veri['spot_alim']['hata'],
                                    tutar_doviz = '',
                                    tutar_coin  = ''
                                )
                            else:
                                database.log_salla(
                                    mail        = mail,
                                    olay        = 'Spot Alım',
                                    parite      = duzgun_veri['sembol'],
                                    adet_coin   = ondalik_kisalt(veri['spot_alim']['alinan_adet']),
                                    tutar_doviz = ondalik_kisalt(veri['spot_alim']['alim_tutari']),
                                    tutar_coin  = ondalik_kisalt(veri['spot_alim']['alis_fiyati'])
                                )
                            if kullanicilar[mail]['ayar']['satis_tip'] == 'spot':
                                veri['spot_satis_emri'] = binance_kisi.spot_satis_emri(duzgun_veri['sembol'], float(duzgun_veri['fiyat'] + (duzgun_veri['fiyat'] * (int(kullanicilar[mail]['ayar']['kar_yuzde']) / 100))),mail=mail)
                                if 'hata' in list(veri['spot_satis_emri'].keys()):
                                    database.log_salla(
                                        mail        = mail,
                                        olay        = 'Spot Satış Emri',
                                        parite      = duzgun_veri['sembol'],
                                        adet_coin   = veri['spot_satis_emri']['hata'],
                                        tutar_doviz = '',
                                        tutar_coin  = ''
                                    )
                                else:
                                    database.log_salla(
                                        mail        = mail,
                                        olay        = 'Spot Satış Emri',
                                        parite      = duzgun_veri['sembol'],
                                        adet_coin   = ondalik_kisalt(veri['spot_satis_emri']['emir_adet']),
                                        tutar_doviz = ondalik_kisalt(veri['spot_satis_emri']['emir_sonuc']),
                                        tutar_coin  = ondalik_kisalt(veri['spot_satis_emri']['emir_fiyati'])
                                    )
                            elif kullanicilar[mail]['ayar']['satis_tip'] == 'oco':
                                veri['oco_satis_emri'] = binance_kisi.oco_satis_emri(duzgun_veri['sembol'], float(ondalik_kisalt(duzgun_veri['fiyat'])), kullanicilar[mail]['ayar']['kar_yuzde'], kullanicilar[mail]['ayar']['zarar_yuzde'],mail=mail)
                                if 'hata' in list(veri['oco_satis_emri'].keys()):
                                    database.log_salla(
                                        mail        = mail,
                                        olay        = 'OCO Satış Emri',
                                        parite      = duzgun_veri['sembol'],
                                        adet_coin   = veri['oco_satis_emri']['hata'],
                                        tutar_doviz = '',
                                        tutar_coin  = ''
                                    )
                                else:
                                    database.log_salla(
                                        mail        = mail,
                                        olay        = 'OCO Satış Emri',
                                        parite      = duzgun_veri['sembol'],
                                        adet_coin   = ondalik_kisalt(veri['oco_satis_emri']['kar_fiyati']),
                                        tutar_doviz = ondalik_kisalt(veri['oco_satis_emri']['zarar_fiyati']),
                                        tutar_coin  = veri['oco_satis_emri']['alis_sinyali']
                                    )
                        else:

                                if kullanicilar[mail]['ayar']['satis_tip'] != 'oco':
                                    veri['spot_satis'] = binance_kisi.acil_satis(duzgun_veri['sembol'],mail=mail)
                                if 'hata' in list(veri['spot_satis'].keys()):
                                    database.log_salla(
                                        mail        = mail,
                                        olay        = 'Spot Satış',
                                        parite      = duzgun_veri['sembol'],
                                        adet_coin   = veri['spot_satis']['hata'],
                                        tutar_doviz = '',
                                        tutar_coin  = ''
                                )
                                else:
                                    database.log_salla(
                                        mail        = mail,
                                        olay        = 'Spot Satış',
                                        parite      = duzgun_veri['sembol'],
                                        adet_coin   = ondalik_kisalt(veri['spot_satis']['satilan_adet']),
                                        tutar_doviz = ondalik_kisalt(veri['spot_satis']['satis_tutari']),
                                        tutar_coin  = ondalik_kisalt(veri['spot_satis']['satis_fiyati'])
                                    )

                        return make_response(jsonify({'basarili' : [mail for mail in kullanicilar]}), 200)
                    else:
                        print(f"{sembol} coinini kimse bot olarak kullanmıyor")
                webhook_telegram(sembol,alert)
                return make_response(jsonify({'basarili' : "telegrama mesaj gönderildi işlem tamam çikipov"}))
            
            return make_response(jsonify({'işlem_YOK' : "işlem için gereken alarm çalmadı"}),200)
        else:
            
            return make_response(jsonify({'işlem_YOK' : "işlem için gereken alarm çalmadı"}),200)
    else:
        post(f"https://api.telegram.org/bot{token}/sendMessage?chat_id=985257805", data={"text": f"Webhook sembolü listede yok, webhook sembolü '{sembol}'"})
        return make_response(jsonify({'Webhook_Bulunamadı' : "webhook kayıtlı değil"}),200)
    