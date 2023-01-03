from app import create_app
import os

#app=create_app('default')
app=create_app(os.getenv('APP_SETTINGS_MODULE'))
if __name__=="__main__":
    app.run()