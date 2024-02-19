activate_this = '/var/www/html/SistemaVentasFlask/env/bin/activate_this.py'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
    
import sys
sys.path.insert(0, '/var/www/html/SistemaVentasFlask/')

from app import create_app
application = create_app('default')