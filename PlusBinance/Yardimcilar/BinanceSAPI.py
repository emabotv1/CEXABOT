# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from binance.client import Client
from binance.exceptions import BinanceAPIException
from deep_translator import GoogleTranslator
from typing import Dict, List
from Yardimcilar import PlusBinanceDB

class Hata:
    SEMBOL_YOK = 'Bu Sembol Kayıtlı Değildir...'
    BIRIM_YOK  = 'Bu Birim Kayıtlı Değildir..'

    @staticmethod
    def tr_ver(metin:str) -> str:
        return GoogleTranslator(source='en', target='tr').translate(metin).strip()

class BinanceSAPI:
    def __init__(self, api_key:str, api_secret:str):
        self.client = Client(api_key, api_secret)

    @staticmethod
    def _sembol_ayikla(sembol:str) -> Dict[str, str]:
        if sembol.endswith('TRY'):
            return {'alinacak': sembol, 'satilacak': 'TRY'}
        elif sembol.endswith('USDT'):
            return {'alinacak': sembol, 'satilacak': 'USDT'}
        else:
            return {'hata': Hata.SEMBOL_YOK}

    def _kac_para_var(self, birim:str,mail:str) -> str:
        liste = []
        database  = PlusBinanceDB()
        kullanici = lambda : database.kull_ver(mail)
        a = kullanici()[mail]['log']
        for i in a:
            if i["parite"] == birim and i["adet_coin"] != "Bu istek için imza geçerli değil.":
                if i["adet_coin"] != "Hesapta istenen işlem için yeterli bakiye yok.":
                    if i["adet_coin"] != "" :
                        liste.append(i)
        if liste != []:
            coin_adet = float(liste[-1]["adet_coin"])
            return coin_adet

    def spot_alim(self, sembol:str, doviz_tip:str=None, miktar:int=None, mail:str=None) -> Dict[str, str]:
        ayikla = self._sembol_ayikla(sembol)
        if 'hata' in list(ayikla.keys()):
            return {'hata': Hata.SEMBOL_YOK}

        try:
            if not doviz_tip:
                spot_al = self.client.order_market_buy(
                    symbol        = sembol,
                    quoteOrderQty = self._kac_para_var(ayikla['satilacak'],mail=mail) if not miktar else miktar
                )

                return {
                    'alis_fiyati' : spot_al['fills'][0]['price'],
                    'alinan_adet' : spot_al['fills'][0]['qty'],
                    'alim_tutari' : spot_al['cummulativeQuoteQty']
                }
            else:
                if doviz_tip == 'yuzde':
                    paranin_hepsi = self._kac_para_var(ayikla['satilacak'],mail=mail)
                    if miktar:
                        paranin_yuzdesi = (paranin_hepsi * miktar) / 100
                    else:
                        paranin_yuzdesi = 100
                    spot_al = self.client.order_market_buy(
                        symbol        = sembol,
                        quoteOrderQty = paranin_hepsi if not miktar else paranin_yuzdesi
                    )

                    return {
                        'alis_fiyati' : spot_al['fills'][0]['price'],
                        'alinan_adet' : spot_al['fills'][0]['qty'],
                        'alim_tutari' : spot_al['cummulativeQuoteQty']
                    }
                elif doviz_tip == 'miktar':
                    paranin_hepsi = self._kac_para_var(ayikla['satilacak'],mail=mail)
                    if miktar:
                        paranin_miktari = miktar
                    else:
                        paranin_miktari = paranin_hepsi
                    spot_al = self.client.order_market_buy(
                        symbol        = sembol,
                        quoteOrderQty = paranin_hepsi if not miktar else paranin_miktari
                    )

                    return {
                        'alis_fiyati' : spot_al['fills'][0]['price'],
                        'alinan_adet' : spot_al['fills'][0]['qty'],
                        'alim_tutari' : spot_al['cummulativeQuoteQty']
                    }
                else:
                    return {'hata': 'Tip Belirlemesi Yanlış!'}
        except BinanceAPIException as hata:
            hata = hata.__dict__
            return {'hata' : Hata.tr_ver(hata['message']), 'kod' : str(hata['code'])}

    def spot_satis_emri(self, sembol:str, satis_fiyati:float,mail:str) -> Dict[str, str]:
        ayikla = self._sembol_ayikla(sembol)
        if 'hata' in list(ayikla.keys()):
            return {'hata': Hata.SEMBOL_YOK}

        try:
            satis_emri = self.client.order_limit_sell(
                symbol    = sembol,
                quantity  = self._kac_para_var(ayikla['alinacak'],mail=mail),
                price     = "{:.2f}".format(satis_fiyati)
            )

            return {
                'emir_id'     : satis_emri['orderId'],
                'emir_fiyati' : satis_emri['price'],
                'emir_adet'   : satis_emri['origQty'],
                'emir_sonuc'  : f"{self._kac_para_var(ayikla['alinacak'],mail=mail) * float(satis_fiyati)}"
            }
        except BinanceAPIException as hata:
            hata = hata.__dict__
            return {'hata' : Hata.tr_ver(hata['message']), 'kod' : str(hata['code'])}

    def oco_satis_emri(self, sembol:str, alis_sinyali:float, kar_yuzde:int=5, zarar_yuzde:int=5,mail:str=None) -> Dict[str, str]:
        ayikla = self._sembol_ayikla(sembol)
        if 'hata' in list(ayikla.keys()):
            return {'hata': Hata.SEMBOL_YOK}

        try:
            kar_fiyati   = float(alis_sinyali + (alis_sinyali * (int(kar_yuzde) / 100)))
            zarar_fiyati = float(alis_sinyali - (alis_sinyali * (int(zarar_yuzde) / 100)))
            oco_satis_emri = self.client.order_oco_sell(
                symbol         = sembol,
                quantity       = self._kac_para_var(ayikla['alinacak'],mail=mail),
                price          = "{:.2f}".format(kar_fiyati),
                stopPrice      = "{:.2f}".format(zarar_fiyati),  # String olucak ama yüzdeleri nasıl hesaplanıcak :)
                stopLimitPrice = "{:.2f}".format(zarar_fiyati),  # String olucak ama yüzdeleri nasıl hesaplanıcak :)
                stopLimitTimeInForce = "GTC",
                # recvWindow = int(time.time() * 1000 - self.client.get_server_time()['serverTime'])
            )

            return {
                'kar_fiyati'   : "{:.2f}".format(kar_fiyati),
                'zarar_fiyati' : "{:.2f}".format(zarar_fiyati),
                'alis_sinyali' : str(alis_sinyali),
            }
        except BinanceAPIException as hata:
            hata = hata.__dict__
            return {'hata' : Hata.tr_ver(hata['message']), 'kod' : str(hata['code'])}

    @property
    def _acik_emirler(self) -> List[Dict[str, str]]:
        return self.client.get_open_orders()

    def acik_emirler_iptal(self, sembol:str) -> List[Dict[str, str]]:
        ayikla = self._sembol_ayikla(sembol)
        if 'hata' in list(ayikla.keys()):
            return [{'hata': Hata.SEMBOL_YOK}]

        iptaller = []
        for gez in self._acik_emirler:
            if gez['symbol'] == sembol:
                try:
                    emir_iptal = self.client.cancel_order(
                        symbol  = sembol,
                        orderId = gez['orderId']
                    )
                except BinanceAPIException as hata:
                    hata = hata.__dict__
                    return [{'hata' : Hata.tr_ver(hata['message']), 'kod' : str(hata['code'])}]
                iptaller.append({
                    'emir_id'     : gez['orderId'],
                    'emir_turu'   : 'SATIS' if gez['side'] == 'SELL' else 'ALIS',
                    'emir_fiyati' : gez['price'],
                    'emir_adet'   : gez['origQty'],
                })

        return iptaller

    def acil_satis(self, sembol:str,mail:str) -> Dict:
        ayikla = self._sembol_ayikla(sembol)
        if 'hata' in list(ayikla.keys()):
            return {'hata': Hata.SEMBOL_YOK}

        kapatilan_emirler = self.acik_emirler_iptal(sembol)

        try:
            spot_sat = self.client.order_market_sell(
                symbol   = sembol,
                quantity = self._kac_para_var(ayikla['alinacak'],mail=mail),
                recvWindow = "60000"
            )
            return {
                'kapatilan_emirler' : kapatilan_emirler,
                'satis_fiyati' : spot_sat['fills'][0]['price'],
                'satilan_adet' : spot_sat['fills'][0]['qty'],
                'satis_tutari' : spot_sat['cummulativeQuoteQty']
            }
        except BinanceAPIException as hata:
            print(hata)
            hata = hata.__dict__
            return {'hata' : Hata.tr_ver(hata['message']), 'kod' : str(hata['code'])}

    def oto_al(self, sembol:str, sinyal:float, emir_carpan:float) -> dict:
        ayikla = self._sembol_ayikla(sembol)
        if 'hata' in list(ayikla.keys()):
            return {'hata': Hata.SEMBOL_YOK}

        try:
            return {
                'spot_alim' : self.spot_alim(sembol),
                'spot_satis_emri' : self.spot_satis_emri(sembol, float(sinyal + (sinyal * emir_carpan)))
            }
        except BinanceAPIException as hata:
            hata = hata.__dict__
            return {'hata' : Hata.tr_ver(hata['message']), 'kod' : str(hata['code'])}
        except Exception as hata:
            return {'hata' : type(hata).__name__, 'kod': hata}
