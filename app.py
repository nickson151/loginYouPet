#pip3 install Flask
#pip3 install Flask-MySQLdb
#pip3 install MySQL
#Flask --version
#pip3 install virtualenv
#virtualenv env
#entorno virtual:          cd env/Scripts
#activar entorno virtual:  .\activate

#llamado archivo 
from flask import Flask    
#render template:  llama carpeta de funciones
#redirect: llamados
#llamar funciones de GET y POST
from flask import  render_template, redirect, request, Response, session
# llamada a la BD
from flask_mysqldb import MySQL, MySQLdb  

#llamar a carpeta funcion Template  
# BD login, name:entrada
app = Flask(__name__, template_folder='template')

app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='login'
app.config['MYSQL_CURSORCLASS']='DictCursor'
#inicializar mysql
mysql = MySQL(app)

#la  " / "  indica el inicio usuario
@app.route('/')
def home():
    return render_template('index.html')

#función para redireccionear a pagina  admin.html
@app.route('/admin')
def admin():
    return render_template('admin.html')

#Funcion de LOGIN que se puso en el metodo POST
#del FORM Class Action -> route
@app.route('/acceso-login', methods = ["GET","POST"])
def login():
    #funcion pregunta y recibe por POST correo
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        #variable llamado por request correo y password
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']
        #llamar a la funcion de conectar BD
        cur = mysql.connection.cursor()
        #llamar a la BD   y consulta
        cur.execute('SELECT * FROM usuarios WHERE correo = %s AND password = %s ' , (_correo , _password))
        #variable como inicio de sesion, ejecuta toda la consulta
        account = cur.fetchone()

        #variable al ingresar con datos correctos se logee
        if account:
            #rescata un inicio de sesion
            session['logueado'] = True
            #el account es de la BD guardada en variable session
            session['id'] = account['id']
            session['id_rol'] = account['id_rol']

            if session['id_rol'] == 1:
                return render_template("admin.html")
            elif session['id_rol'] == 2:
                #cuando inice sesion que envia a formulario
                return render_template("usuario.html")
        else:
            return render_template('index.html', mensaje ="Usuario o contraseña incorrecto")


if __name__ == '__main__':
    #clave secreta  
    app.secret_key = "Campos20*"
    #crear de manera local, servidor al correr
    app.run(debug = True, host = '0.0.0.0', port = 5000, threaded = True)



