# Bu araç @keyiflerolsun tarafından | @KekikAkademi için yazılmıştır.

from PlusBinance import app, onemli
from os import environ

port = int(environ.get("PORT", 80))
host = "0.0.0.0"

if __name__ == '__main__':
    # app.run(debug = True, host = '0.0.0.0', port = port)

    onemli(f'\nBinance [bold red]{host}[yellow]:[/]{port}[/]\'de başlatılmıştır...\n')

    from waitress import serve
    serve(app, host=host, port=port)