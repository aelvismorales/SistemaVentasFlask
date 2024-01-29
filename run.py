from app import create_app
import os

#app=create_app('default')
app=create_app('default')
if __name__=="__main__":
    app.run()