from app import create_app
from os import environ

config_name=environ.get('APP_SETTINGS_MODULE') or "testing"
app = create_app(config_name)
if __name__=="__main__":
    app.run()
