from hashlib import md5, sha256

md5_yap    = lambda kelime: md5(f"{kelime}+PlusBinance".encode()).hexdigest()
sha256_yap = lambda kelime: sha256(f"{kelime}+PlusBinance".encode()).hexdigest()