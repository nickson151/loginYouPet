#pip3 install Flask
#pip3 install Flask-MySQLdb
#pip3 install MySQL
#Flask --version
#pip3 install virtualenv
#virtualenv env
#entorno virtual:          cd env/Scripts
import re
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash  # Importar para hacer hashing 
#activar entorno virtual:  .\activate
from MySQLdb import IntegrityError  # Importar la excepción
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
app.config['MYSQL_DB']='YouPet'
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
    # Si se recibe una solicitud POST y se encuentran los campos de correo y contraseña
    if request.method == 'POST' and 'txtCorreo' in request.form and 'txtPassword' in request.form:
        # Capturar los datos enviados en el formulario
        _correo = request.form['txtCorreo']
        _password = request.form['txtPassword']
        
        # Conectar a la base de datos y realizar la consulta
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM usuarios WHERE correo = %s', (_correo,))
        account = cur.fetchone()
        
        # Si existe un usuario con el correo ingresado
        if account:
            # Verificar la contraseña ingresada con el hash almacenado en la base de datos
            if check_password_hash(account['password'], _password):
                # Iniciar la sesión si la contraseña es correcta
                session['logueado'] = True
                session['id'] = account['id']
                session['id_rol'] = account['id_rol']

                # Redirigir según el rol del usuario
                if session['id_rol'] == 1:
                    return render_template("admin.html")
                elif session['id_rol'] == 2:
                    return render_template("usuario.html")
                elif session['id_rol'] == 3:
                    return render_template("premium.html")
            else:
                # Contraseña incorrecta
                return render_template('index.html', mensaje="Usuario o contraseña incorrectos")
        else:
            # No se encontró ninguna cuenta con ese correo
            return render_template('index.html', mensaje="Usuario o contraseña incorrectos")

#registro
@app.route('/registro')
def registro():
    return render_template('registro.html')

# Función de registro
@app.route('/crear-registro', methods=["GET", "POST"])
def crear_registro():
    if request.method == 'POST':
        # Obtener los datos del formulario
        nombre = request.form['txtNombre']
        correo = request.form['txtCorreo']
        password = request.form['txtPassword']
        confirmar_password = request.form['txtConfirmPassword']

        # Validar que el formato del correo sea válido
        if not re.match(r"[^@]+@[^@]+\.[^@]+", correo):
            return render_template('registro.html', mensaje="El correo no es válido")

        # Validar que la contraseña cumpla con los requisitos (mínimo 8 caracteres, al menos 1 mayúscula, 1 minúscula, 1 número y 1 símbolo)
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$', password):
            return render_template('registro.html', mensaje="La contraseña debe tener al menos 8 caracteres, incluyendo una letra mayúscula, una minúscula, un número y un símbolo")

        # Validar que las contraseñas coincidan
        if password != confirmar_password:
            return render_template('registro.html', mensaje="Las contraseñas no coinciden")

        try:
            # Hashear la contraseña antes de guardarla en la base de datos
            hashed_password = generate_password_hash(password)

            # Insertar el nuevo registro en la base de datos (sin almacenar confirmar_password)
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO usuarios (nombre, correo, password, id_rol) 
                VALUES (%s, %s, %s, '2')
            """, (nombre, correo, hashed_password))
            mysql.connection.commit()

            return render_template("index.html", mensaje2="Registro exitoso")

        except IntegrityError:
            # Manejar la excepción cuando el correo ya existe
            return render_template('registro.html', mensaje="El correo ya está registrado")

    return render_template('registro.html')
#-----------
#--- Listar usuarios ------
@app.route('/listar', methods=["GET", "POST"])
def listar():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    #preguntar si existe el dato
    usuarios = cur.fetchall()
    cur.close()

    return render_template("listar_usuarios.html", usuarios = usuarios)

#---------------

if __name__ == '__main__':
    #clave secreta  
    app.secret_key = "Campos20*"
    #crear de manera local, servidor al correr
    app.run(debug = True, host = '0.0.0.0', port = 5000, threaded = True)



