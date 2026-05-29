import logging
from flask import Flask

from app.db.database import init_db
from app.api.clientes import clientes_bp
from app.api.webhooks import webhooks_bp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = Flask(__name__)
app.json.ensure_ascii = False

app.register_blueprint(clientes_bp)
app.register_blueprint(webhooks_bp)

init_db()


@app.get("/")
def health_check():
    return {"status": "ok", "service": "mundo-invest-api"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)