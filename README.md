# SistemaVentasFlask

## Inicio
Para poder desarrollar el proyecto, antes debemos de seguir algunos pasos para configurar un ambiente con todas las dependencias necesarias, y que de esta manera, no tengamos problemas al momento de ejecutarlo localmente.

### Prerequisitos
Primero que nada, se debe de tener instalado Conda en el ordenador donde se desplegará este proyecto. Para ello, 
puede guiarse de la documentación oficial haciendo click [aquí](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

Una vez ya se halla instalado Conda, podemos continuar con la instalacion.

### Conda Prompt

1. Iniciaremos con la cloncacion del proyecto:
``` git clone https://github.com/aelvismorales/FlaskWebDev
    cd FlaskWebDev
````
2. Crearemos un ambiente con Conda de la siguiente manera:
```
  conda create --name flask_web python=3.8.13
```
3. Una vez creado el ambiente, debemos añadir las siguientes variables de entorno al mismo:
```
  conda activate flask_Web
  conda env config vars set FLASK_APP="run:app"
  conda env config vars set APP_SETTINGS_MODULE="default"
```
5. Luego, continuamos con la instalación de las dependencias necesarias, las cuales 
 ya se encuentran en el archivo **requirements.txt**, por lo que solo tendríamos que aplicar el siguiente comando:
 ```
 pip install -r requirements.txt
 ```
 6. Cuando ya tengamos el ambiente creado y configurado con las dependencias ya podremos realizar las modificaioens pertinentes. Asimismo, se podra realizar la ejecuacion del proyecto con el comando:
 ```
 flask run o python app.py
 ```
 
   
