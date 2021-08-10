# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from PlusBinance import app
from Yardimcilar import PlusBinanceDB, BinanceSAPI, sha256_yap, md5_yap, ondalik_kisalt
from flask import request, make_response, jsonify, abort

@app.route("/webhook/<kull_adi>", methods=["GET", "POST"])
def dinamik(kull_adi):
    database  = PlusBinanceDB()
    kullanici = database.db_ara({"kull_adi": kull_adi})

    if (not kullanici) or (not request.args.get("token")):
        return abort(404)

    token = md5_yap(kullanici['kull_adi'])

    if token != request.args.get("token"):
        return make_response(jsonify({'hata': 'Geçersiz Token!'}), 403)

    # Metin Abinin Saçma Sİnyalinin Ayıklanması
    sacma_veri = request.data.decode('utf-8').split(', ')

    duzgun_veri = {
        'sembol': sacma_veri[0].strip(),
        'sinyal': sacma_veri[1].split('=')[0].strip().rstrip(' Fiyati'),
        'fiyat': float(sacma_veri[1].split('=')[1].strip()),
    }

    # Binance İşleri Burdan Sonra Yapılacak!
    binance_kisi = BinanceSAPI(kullanici['ayar']['api_key'], kullanici['ayar']['api_secret'])

    veri = {}
    if duzgun_veri['sinyal'] == 'ALIS':
        database.log_salla(
            mail        = kullanici['mail'],
            olay        = f"Sinyal » {duzgun_veri['sinyal']}",
            parite      = duzgun_veri['sembol'],
            adet_coin   = '',
            tutar_doviz = '',
            tutar_coin  = ondalik_kisalt(duzgun_veri['fiyat'])
        )

        veri['spot_alim']  = binance_kisi.spot_alim(duzgun_veri['sembol'])
        if 'hata' in list(veri['spot_alim'].keys()):
            database.log_salla(
                mail        = kullanici['mail'],
                olay        = 'Hata',
                parite      = duzgun_veri['sembol'],
                adet_coin   = veri['spot_alim']['hata'],
                tutar_doviz = '',
                tutar_coin  = ''
            )
        else:
            database.log_salla(
                mail        = kullanici['mail'],
                olay        = 'Spot Alım',
                parite      = duzgun_veri['sembol'],
                adet_coin   = ondalik_kisalt(veri['spot_alim']['alinan_adet']),
                tutar_doviz = ondalik_kisalt(veri['spot_alim']['alim_tutari']),
                tutar_coin  = ondalik_kisalt(veri['spot_alim']['alis_fiyati'])
            )

        veri['spot_satis_emri'] = binance_kisi.spot_satis_emri(duzgun_veri['sembol'], float(duzgun_veri['fiyat'] + (duzgun_veri['fiyat'] * (int(kullanici['ayar']['emir_yuzde']) / 100))))
        if 'hata' in list(veri['spot_satis_emri'].keys()):
            database.log_salla(
                mail        = kullanici['mail'],
                olay        = 'Hata',
                parite      = duzgun_veri['sembol'],
                adet_coin   = veri['spot_satis_emri']['hata'],
                tutar_doviz = '',
                tutar_coin  = ''
            )
        else:
            database.log_salla(
                mail        = kullanici['mail'],
                olay        = 'Spot Satış Emri',
                parite      = duzgun_veri['sembol'],
                adet_coin   = ondalik_kisalt(veri['spot_satis_emri']['emir_adet']),
                tutar_doviz = ondalik_kisalt(veri['spot_satis_emri']['emir_sonuc']),
                tutar_coin  = ondalik_kisalt(veri['spot_satis_emri']['emir_fiyati'])
            )
    else:
        database.log_salla(
            mail        = kullanici['mail'],
            olay        = f"Sinyal » {duzgun_veri['sinyal']}",
            parite      = duzgun_veri['sembol'],
            adet_coin   = '',
            tutar_doviz = ondalik_kisalt(duzgun_veri['fiyat']),
            tutar_coin  = ''
        )

        veri['spot_satis'] = binance_kisi.acil_satis(duzgun_veri['sembol'])
        if 'hata' in list(veri['spot_satis'].keys()):
            database.log_salla(
                mail        = kullanici['mail'],
                olay        = 'Hata',
                parite      = duzgun_veri['sembol'],
                adet_coin   = veri['spot_satis']['hata'],
                tutar_doviz = '',
                tutar_coin  = ''
            )
        else:
            database.log_salla(
                mail        = kullanici['mail'],
                olay        = 'Spot Satış',
                parite      = duzgun_veri['sembol'],
                adet_coin   = ondalik_kisalt(veri['spot_satis']['satilan_adet']),
                tutar_doviz = ondalik_kisalt(veri['spot_satis']['satis_tutari']),
                tutar_coin  = ondalik_kisalt(veri['spot_satis']['satis_fiyati'])
            )
    # print(dumps(veri, indent=2, ensure_ascii=False, sort_keys=False))

    return make_response(jsonify({'basarili' : veri}), 200)