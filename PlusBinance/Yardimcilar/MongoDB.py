# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

import pymongo, datetime, pytz

import telebot

tg_botumuz = telebot.TeleBot("1752680475:AAFr3lgJeaXl9GTxLav9YLRFcBcJLGEWEBg")

class PlusBinanceDB():
    tarih = lambda : datetime.datetime.now(pytz.timezone("Turkey")).strftime("%d-%m-%Y %X")

    def __init__(self):
        client     = pymongo.MongoClient("mongodb+srv://WebCexaBot:28sEAS3rQUS6MkL@webcexabots.v1usl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db         = client['WebCexaBots']
        self.collection = db['PlusBinance']

    def db_ara(self, sorgu:dict):
        say = self.collection.count_documents(sorgu)
        # if say == 1:
        #     return self.collection.find_one(sorgu, {'_id': 0})
        #         # print(f"{say} Adet Kaydın İlki;\n{ara}")
        if say:
            cursor = self.collection.find(sorgu, {'_id': 0})
            return {
                bak['mail'] : {
                    "ad_soyad" : bak['ad_soyad'],
                    "kull_adi" : bak['kull_adi'],
                    "sifre"    : bak['sifre'],
                    "ayar"     : bak['ayar'],
                    "log"      : bak['log']
                }
                for bak in cursor
            } 
                # print(f"{say} Adet Kaydın İlki;\n{ara[0]}")
        else:
            return None

    def ekle(self, mail, ad_soyad, sifre, kull_adi):
        if (not self.db_ara({'mail': mail})) and (not self.db_ara({'kull_adi': kull_adi})):
            return self.collection.insert_one({
                "mail"      : mail.strip(),
                "kull_adi"  : kull_adi.strip(),
                "ad_soyad"  : ad_soyad.strip(),
                "sifre"     : sifre.strip(),
                "ayar": {
                    "api_key"     : None,
                    "api_secret"  : None,
                    "vip"         : False,
                    "pariteler"   : [],
                    "doviz_tip"   : None,
                    "miktar"      : None,
                    "satis_tip"   : None,
                    "kar_yuzde"   : None,
                    "zarar_yuzde" : None,
                    "telegram"    : None
                },
                "log"       : [],
            })
        else:
            return None

    def sil(self, mail):
        if not self.db_ara({'mail': mail}):
            return None
        else:
            self.collection.delete_one({'mail': mail})
            return True

    def ayar_guncelle(self, mail, api_key, api_secret, pariteler, doviz_tip, miktar, satis_tip ,kar_yuzde ,zarar_yuzde , telegram=None):
        kullanici = self.db_ara({'mail': mail})
        if not kullanici:
            return None
        else:
            self.collection.update_one({'mail': mail},
                {
                    "$set" : {
                        "ayar": {
                            "api_key"     : api_key.strip(),
                            "api_secret"  : api_secret.strip(),
                            "vip"         : kullanici[mail]["ayar"]["vip"],
                            "pariteler"   : pariteler,
                            "doviz_tip"   : doviz_tip,
                            "miktar"      : miktar,
                            "satis_tip"   : satis_tip,
                            "kar_yuzde"   : kar_yuzde,
                            "zarar_yuzde" : zarar_yuzde,
                            "telegram"    : telegram
                        }
                    }
                }
            )
            return self.db_ara({'mail': mail})

    def log_salla(self, mail, olay, parite, adet_coin, tutar_doviz, tutar_coin):
        kullanici = self.db_ara({'mail': mail})
        if not kullanici:
            return None
        else:
            self.collection.update_one({'mail': mail},
                {
                    "$push" : {
                        "log": {
                            "tarih"       : PlusBinanceDB.tarih(),
                            "olay"        : olay,
                            "parite"      : parite,
                            "adet_coin"   : adet_coin if adet_coin not in ['Geçersiz miktar.', 'Filtre hatası: MIN_NOTIONAL', 'Hesap, istenen işlem için yeterli bakiyeye sahip değil.'] else "Yetersiz Bakiye!",
                            "tutar_doviz" : tutar_doviz,
                            "tutar_coin"  : tutar_coin
                        }
                    }
                }, upsert = True
            )

            telegram = kullanici[mail]['ayar']['telegram']
            mesaj = f"📰 *{olay}*\n\n"
            if (tutar_doviz == '') and (tutar_coin == ''):
                if str(adet_coin) in ['Geçersiz miktar.', 'Filtre hatası: MIN_NOTIONAL', 'Hesap, istenen işlem için yeterli bakiyeye sahip değil.']:
                    mesaj += f"⁉️ *Hata :* `Yetersiz Bakiye!`\n"
                else:
                    mesaj += f"⁉️ *Hata :* `{str(adet_coin)}`\n"
            else:
                if parite:
                    mesaj += f"💱 *Parite :* _{parite}_\n"
                if not 'OCO' in olay:
                    if tutar_coin:
                        mesaj += f"🤑 *Alış Fiyatı :* _{tutar_coin}_\n"
                    if adet_coin:
                        mesaj += f"💰 *Alınan Adet :* _{adet_coin}_\n"
                    if tutar_doviz:
                        mesaj += f"💲 *Alım Tutarı :* _{tutar_doviz}_\n"
                else:
                    if tutar_coin:
                        mesaj += f"🤑 *Alış Fiyatı :* _{tutar_coin}_\n"
                    if adet_coin:
                        mesaj += f"💰 *Kâr Fiyatı :* _{adet_coin}_\n"
                    if tutar_doviz:
                        mesaj += f"💲 *Zarar Fiyatı :* _{tutar_doviz}_\n"

            if (telegram) and (telegram[0] == '-' or telegram[0].isdigit()):
                tg_botumuz.send_message(telegram, f"{mesaj}")

            return self.db_ara({'mail': mail})[mail]

    def kull_ver(self, mail:str):
        data = self.db_ara({'mail': mail})
        if not data:
            return None
        else:
            return data

# database  = PlusBinanceDB()
# database.log_salla('keyiflerolsun@gmail.com', '123', '123', '11', '123')
