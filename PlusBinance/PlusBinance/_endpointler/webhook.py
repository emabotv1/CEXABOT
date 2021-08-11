# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from PlusBinance import app
from Yardimcilar import PlusBinanceDB, BinanceSAPI, sha256_yap, md5_yap, ondalik_kisalt
from flask import request, make_response, jsonify, abort

from datetime import datetime
from pytz import timezone

from requests import post
token = "1812551326:AAHlDX6oTU7UvXPy2DMz-m2l61wMZRrIGkU"
chat  = "-1001553338929"

tarih       = lambda : datetime.now(timezone("Turkey")).replace(tzinfo=None)
tarih_cevir = lambda tarih : datetime.strptime(tarih, "%d-%m-%Y %X")

son_sinyal = {
    "CAKEUSDT" : tarih(),
    "BTCUSDT"  : tarih(),
    "SOLUSDT"  : tarih(),
    "ETHUSDT"  : tarih(),
    "AXSUSDT"  : tarih(),
    "LUNAUSDT" : tarih(),
    "BNBUSDT"  : tarih(),
    "XVSUSDT"  : tarih(),
    "BTCSTUSDT": tarih(),
    "AVAXUSDT" : tarih(),
    "DOTUSDT"  : tarih(),
    "SUSHİUSDT": tarih(),
    "WAVESUSDT": tarih(),
    "DOGEUSDT" : tarih(),
    "ATOMUSDT" : tarih(),
    "CHZUSDT"  : tarih(),
    "SNXUSDT"  : tarih(),
    "EGLDUSDT" : tarih()
}
semboller = ["CAKEUSDT","BTCUSDT","SOLUSDT","XVSUSDT","AVAXUSDT","ETHUSDT","BTCSTUSDT","LUNAUSDT","BNBUSDT","AXSUSDT"]

@app.route("/webhook/<sembol>", methods=["GET", "POST"])
def webhook_statik(sembol):
    if sembol in semboller:

        # Metin Abinin Saçma Sİnyalinin Ayıklanması
        sacma_veri = request.data.decode('utf-8').split(', ')
        try:
            if sacma_veri[0] == "AL : olası ticaret fırsatı" or sacma_veri[0] == "SAT : olası ticaret fırsatı":
                duzgun_veri = {
                    'sembol': sembol,
                    'sinyal': sacma_veri[0].split(' :')[0],
                    'fiyat': round(float(sacma_veri[1].split(' ')[1].strip()),2),
                }

                global son_sinyal
                istek_zamani = tarih()

                fark    = istek_zamani - son_sinyal[duzgun_veri['sembol']]
                sn_fark = round(fark.total_seconds())

                if sn_fark < 10:
                    print("O kadar vakit geçmedi delikanlı..")
                    return "O kadar vakit geçmedi delikanlı.."
                else:
                    son_sinyal[duzgun_veri['sembol']] = istek_zamani
                    post(f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat}", data={'text': f'COIN: #{duzgun_veri["sembol"]}\nSignal: {duzgun_veri["sinyal"]}\nPrice: {duzgun_veri["fiyat"]}'})

                database     = PlusBinanceDB()
                kullanicilar = database.db_ara({"ayar.pariteler": {'$in': [duzgun_veri['sembol']]}})

                
                for mail in kullanicilar:
                    # Binance İşleri Burdan Sonra Yapılacak!
                    binance_kisi = BinanceSAPI(kullanicilar[mail]['ayar']['api_key'], kullanicilar[mail]['ayar']['api_secret'])


                    veri = {}
                    if duzgun_veri['sinyal'] == 'AL':
                        database.log_salla(
                            mail        = mail,
                            olay        = f"Sinyal » {duzgun_veri['sinyal']}",
                            parite      = duzgun_veri['sembol'],
                            adet_coin   = '',
                            tutar_doviz = '',
                            tutar_coin  = ondalik_kisalt(duzgun_veri['fiyat'])
                        )

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
                        database.log_salla(
                            mail        = mail,
                            olay        = f"Sinyal » {duzgun_veri['sinyal']}",
                            parite      = duzgun_veri['sembol'],
                            adet_coin   = '',
                            tutar_doviz = ondalik_kisalt(duzgun_veri['fiyat']),
                            tutar_coin  = ''
                        )

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
                    # print(dumps(veri, indent=2, ensure_ascii=False, sort_keys=False))

                return make_response(jsonify({'basarili' : [mail for mail in kullanicilar]}), 200)
            else:
                return make_response(jsonify({'işlem_YOK' : "işlem için gereken alarm çalmadı"}),200)
        except TypeError:
            pass
    else:
        post(f"https://api.telegram.org/bot{token}/sendMessage?chat_id=985257805", data={"text": f"Webhook sembolü listede yok, webhook sembolü '{sembol}'"})
        return make_response(jsonify({'Webhook_Bulunamadı' : "webhook kayıtlı değil"}),200)