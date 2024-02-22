from app import create_app
from os import environ

config_name=environ.get('APP_SETTINGS_MODULE') or "default"
app = create_app(config_name)
if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
