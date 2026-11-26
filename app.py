import os
from src import create_app
from src.config import Config

app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", Config.PORT))
    app.run(host="0.0.0.0", port=port)
