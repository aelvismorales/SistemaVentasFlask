# SistemaVentasFlask
## Inicio
Para poder desarrollar el proyecto, antes debemos de seguir algunos pasos para configurar un ambiente con todas las dependencias necesarias, y que de esta manera, no tengamos problemas al momento de ejecutarlo localmente.

### Prerequisitos
* Instalar Visual Studio Code (IDE) o de tu preferencia
* Instalar Git
* Instalar Python 3.12, utilizado para el desarrollo del proyecto
* Instalacion de MySql Server y Workbench(IDE).

#### Instalando Visual Studio Code
Para iniciar con la instalacion debemos ingresar al siguiente link y descargar el recomendado para nuestro sistema operativo [VisualStudioCode](https://code.visualstudio.com/download).

#### Instalando Git

Para iniciar con la instalacion de GIT debemos ingresar al siguiente link y descargar el recomendado para nuestro sistema operativo [GIT](https://git-scm.com/downloads)

#### Instalando Python 3.12
En Windows ingresamos al siguiente link de descarga, [Python3.12](https://www.python.org/downloads/release/python-3120/)

#### Instalando MysqlServer y Workbench como IDE
Para instalar Workbench debemos primero de asegurarnos de tener actualizados nuestros paquetes de Visual C++ 2019 Redistributable si no lo tienes puedes descargarlo desde [C++](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist?view=msvc-170)

Teniendo esto de forma correcta, podemos instalar el workbench desde el siguiente enlace [WorkBench](https://dev.mysql.com/downloads/workbench/)

Ahora tambien instalaremos el Servidor de MySql como tal desde el siguiente link [MySql](https://dev.mysql.com/downloads/mysql/)


### Prerequisitos Instalados correctamente

#### Paso :one:
Teniendo todo instalado correctamente, podemos ingresar a nuestra consola de Mysql o desde el WorkBench y utilizamos los siguientes comandos:
```
CREATE DATABASE sistemaventas;
CREATE DATABASE sistemaventas_test;
```
De esta manera estaremos creando ambos 2 schemas para nuestra base de datos donde el test, se utilizara para probar funcionalidades y el otro sera para produccion.
![Creando los dos schemas desde consola](./mysql_create_database.png)

#### Paso :two:
Una vez completada la creacion las bases de datos podemos clonar el repositorio, porfavor ubicar su seleccion de desarrollo, en este caso lo clonaremos en el Escritorio :computer: 

Para clonar nuestros archivos utilizaremos el siguiente comando:
```
git clone https://github.com/aelvismorales/SistemaVentasFlask.git

#Ingresar a nuestra carpeta creada con 

cd SistemaVentasFlask
```
**No Olvidar** que debemos cambiar la rama que queremos utilizar con el siguiente comando:
```
git checkout desarrollo #windows
git checkout desarrollo_debian #Linux
```
#### Paso :three:
Ingresamos a nuestro IDE e instalamos la extension de Python, esto nos ayudara a reconocer los archivos .py y ayudarnos con las correcciones de codigo.

> Revisar si tenemos **virtualenv** instalado previamente y tambien **pip** con los siguiente comandos
```
virtualenv --version

pip -V

# En caso no tengas instalado estos puedes realizar desde la consola con el comando
pip install virtualenv
```
**Una** veza tengamos esto ya revisado podemos comenzar a crear nuestro ambiente virtual, **recordar** que en el IDE debemos estar en la altura de nuestra carpeta clonada y en la terminal escribir el comando:
```
python -m venv env
```
Esto nos permite crear un ambiente virtual para instalar todas las dependencias necesarios sin afectar a nuestro Python de entorno global.

**Activacion** de nuestro ambiente virtual:
Para activar nuestro ambiente virtual desde la terminal debemos utilizar el siguiente comando:
```
.\env\Scripts\activate
```
**Atención**
En caso existiria el siguiente error:
![error activacion scripts](./error_activacion_scripts.png)
Podemos darle solucion de manera rapida utilizando el siguiente comando desde PowerShell iniciandolo como Administrador:
```
Set-ExecutionPolicy Unrestricted
```
![solucion error scripts](./solucion_error_script.png)

Bueno solucionado este problema podemos proceder a activar con normalidad nuestro ambiente virtual con 
```
.\env\Scripts\activate
```
Una vez activado el ambiente debemos instalar los paquetes y dependencias necesarias utilizar el siguiente comando:
```
pip install -r requirements.txt
```

#### Ultimo Paso
Creamos un .env o un archivo de configuracion de variables de entorno, tener encuenta que esta informacion es privada, esto solo es un caso de prueba asi que puede utilizar la siguiente informacion. 
> El  archivo .env debe estar creada a la altura de la carpeta app
```
FLASK_APP="run:app"
APP_SETTINGS_MODULE="testing"
DATABASE_DEVELOPMENT="mysql+pymysql://root:admin@localhost/sistemaventas"
DATABASE_PRODUCTION="mysql+pymysql://root:admin@localhost/sistemaventas"
DATABASE_TEST="mysql+pymysql://root:admin@localhost/sistemaventas_test"
SECRET_KEY="k6Ptlzna2AGiBLFIhBwgWJ5tICXG5lJ9"
```

Bien, hecho teniendo todo lo anterior podemos utilizar el siguiente comando para correr el sistema.
```
python run.py 

#o

flask run
```
## Buen trabajo en este punto debes tener la vista de en la consola de la siguiente manera:
![consola](./flask_run_consola.png)
Teniendo esto ingresamos a la ruta que nos otorgan y veremos la siguiente pantalla de logeo.

![aplicacion](./aplicacion_login.png)

Si necesitas algo mas detallado ingresar al siguiente archivo [Notion](https://www.notion.so/Maquinas-Virtuales-en-Windows-con-VirtualBox-cdc73467eac34b82af9e713b391289dd?pvs=4)