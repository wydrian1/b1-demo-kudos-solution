"""Kudos – belépési pont. Indítás: `python3 app.py` → http://localhost:8000

Környezeti változók: PORT (alapértelmezés: 8000), KUDOS_DB (alapértelmezés: kudos.db).
"""
import os

from kudos.web import szerver_letrehoz


def main():
    port = int(os.environ.get("PORT", "8000"))
    adatbazis = os.environ.get("KUDOS_DB", "kudos.db")
    szerver = szerver_letrehoz("127.0.0.1", port, adatbazis)
    print(f"Kudos (DEMO) fut: http://localhost:{port}  –  adatbázis: {adatbazis}", flush=True)
    try:
        szerver.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        szerver.server_close()


if __name__ == "__main__":
    main()
