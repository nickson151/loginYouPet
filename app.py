#pip3 install Flask pyswip
#pip3 install pyswip 
#pip3 install Flask
#pip3 install Flask-MySQLdb
#pip3 install MySQL
#pip3 install mysql-connector
#pip3 install mysql-connector-python
#pip3 install mysql-connector-python-rf
#Flask --version
#pip3 install virtualenv
#pip3 install pyswip
#virtualenv env
#entorno virtual: cd env/Scripts
#pip3 install Flask-Mail

from functools import wraps
from flask import redirect, session, url_for
from datetime import timedelta, datetime
import re, os
import smtplib 
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
#activar entorno virtual:  .\activate
from MySQLdb import IntegrityError  # Importar la excepción
from mysql.connector.errors import IntegrityError
#llamado archivo 
from flask import Flask, flash, url_for, jsonify    
#render template:  llama carpeta de funciones
import mysql.connector
#redirect: llamados
#llamar funciones de GET y POST
from flask import  render_template, redirect, request, Response, session

# llamada a la BD
from flask_mysqldb import MySQL, MySQLdb
#llamada a la libreria de pyswip
from pyswip import Prolog
#python -m venv env
#Activar entorno virtual, llegar ruta, prompt:
#cd C:\xampp\htdocs\loginYouPet\env\Scripts\activate

# Flask-Mail para el envío de correos electrónicos
from flask_mail import Mail, Message
#from app import app, mysql, mail




#llamar a carpeta funcion Template  
# BD login, name:entrada
app = Flask(__name__, template_folder='template')
app.permanent_session_lifetime = timedelta(minutes=30)  # Sesión expira en 30 minutos de inactividad
app.config['MYSQL_HOST']='localhost'
app.config['MYSQL_USER']='root'
app.config['MYSQL_PASSWORD']=''
app.config['MYSQL_DB']='YouPet'
app.config['MYSQL_CURSORCLASS']='DictCursor'
#inicializar mysql vcb 
mysql = MySQL(app)


# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'youpetiauan@gmail.com'  
app.config['MAIL_PASSWORD'] = 'Campos20*'        
# Inicializar Flask-Mail
mail = Mail(app)


# Establece el directorio donde está instalado SWI-Prolog
os.environ['SWI_HOME_DIR'] = r'C:\Program Files\swipl'
os.environ['PATH'] += r';C:\Program Files\swipl\bin'

try:
    prolog = Prolog()
    print("Prolog inicializado correctamente.")
except Exception as e:
    print(f"Error al inicializar Prolog: {e}")


#la  " / "  indica el inicio usuario
@app.route('/')
def home():
    return render_template('index.html')
#-----------------------------------------------

#función para redireccionear a pagina  admin.html
@app.route('/admin', methods=["GET", "POST"])
def admin():
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        confirmar_password = request.form['confirmar_password']

        # Validar que las contraseñas coincidan
        if password != confirmar_password:
            mensaje = "Las contraseñas no coinciden"
            return render_template('admin.html', mensaje=mensaje)

        # Insertar el nuevo registro en la base de datos
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO usuarios (nombre, correo, password, id_rol) 
            VALUES (%s, %s, %s, '2')
        """, (nombre, correo, password))
        mysql.connection.commit()
        cur.close()

    # Obtener la lista de usuarios para mostrar
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuarios")
    usuarios = cur.fetchall()
    cur.close()

    return render_template('admin.html', usuarios=usuarios)

#--------- Editar usuario
@app.route('/editar/<int:id>', methods=["GET", "POST"])
def editar_usuario(id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        password = request.form['password']
        confirmar_password = request.form['confirmar_password']
        
        # Recuperar los datos actuales del usuario antes de actualizar
        cur.execute("SELECT nombre, correo FROM usuarios WHERE id = %s", (id,))
        usuario_actual = cur.fetchone()

        actualizaciones = []
        valores = []

        # Verificar si se ingresó un nuevo nombre y si es diferente al actual
        if nombre and nombre != usuario_actual['nombre']:
            actualizaciones.append("nombre = %s")
            valores.append(nombre)

        # Verificar si se ingresó un nuevo correo y si es diferente al actual
        if correo and correo != usuario_actual['correo']:
            actualizaciones.append("correo = %s")
            valores.append(correo)

        # Verificar si se ingresó una nueva contraseña
        if password:
            if password != confirmar_password:
                mensaje = "Las contraseñas no coinciden"
                return render_template('editar_usuario.html', mensaje=mensaje, usuario=usuario_actual)

            # Hashear la contraseña antes de actualizarla
            hashed_password = generate_password_hash(password)
            actualizaciones.append("password = %s")
            valores.append(hashed_password)

        # Si hay actualizaciones, ejecutar la consulta
        if actualizaciones:
            valores.append(id)
            query = f"UPDATE usuarios SET {', '.join(actualizaciones)} WHERE id = %s"
            cur.execute(query, tuple(valores))
            mysql.connection.commit()

        cur.close()

        return redirect('/admin')

    cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cur.fetchone()
    cur.close()

    return render_template('editar_usuario.html', usuario=usuario)


#---- eliminar usuario
@app.route('/eliminar/<int:id>', methods=["POST"])
def eliminar_usuario(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        mysql.connection.commit()
    except MySQLdb.Error as e:
        app.logger.error(f"Error eliminando usuario: {str(e)}")
    finally:
        cur.close()
    return redirect('/admin')

#---------------------------------------------------


# ---------------------------------------------------
# Ruta para la vista premium con lista de mascotas asociadas al usuario premium
@app.route('/premium')
def premium():
    id_usuario = session.get('id')  # Obtener el id del usuario autenticado

    if not id_usuario:
        return redirect(url_for('login'))

    # Obtener los archivos PDF subidos por el usuario autenticado
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM archivos WHERE id_usuario = %s", (id_usuario,))
    archivos = cur.fetchall()

    # Obtener las fotos de las mascotas del usuario autenticado
    cur.execute("SELECT f.* FROM fotos f JOIN mascotas m ON f.id_mascota = m.id_mascota WHERE m.id_usuario = %s", (id_usuario,))
    fotos = cur.fetchall()
    cur.close()

    return render_template('premium.html', archivos=archivos, fotos=fotos)



# Ruta para agregar una nueva mascota
@app.route('/agregar-mascota', methods=['POST'])
def agregar_mascota():
    nombre = request.form['nombre']
    especie = request.form['especie']
    edad = request.form['edad']
    raza = request.form['raza']
    id_usuario = session.get('id')

    if not id_usuario:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    try:
        # Validar que el usuario no exceda el límite de mascotas
        cur = mysql.connection.cursor()
        cur.execute("SELECT COUNT(*) as total FROM mascotas WHERE id_usuario = %s", (id_usuario,))
        total_mascotas = cur.fetchone()['total']
        if total_mascotas >= 3:
            return jsonify({'error': 'No puedes tener más de 3 mascotas'}), 400

        # Agregar la nueva mascota
        cur.execute("""
            INSERT INTO mascotas (id_usuario, nombre, especie, edad, raza) 
            VALUES (%s, %s, %s, %s, %s)
        """, (id_usuario, nombre, especie, edad, raza))
        mysql.connection.commit()

        # Obtener el id de la mascota recién insertada
        cur.execute("SELECT LAST_INSERT_ID() as id_mascota")
        id_mascota = cur.fetchone()['id_mascota']
        cur.close()

        # Retornar los datos de la mascota recién agregada
        mascota = {
            'id_mascota': id_mascota,
            'nombre': nombre,
            'especie': especie,
            'edad': edad,
            'raza': raza
        }

        return jsonify({'success': 'Mascota agregada correctamente', 'mascota': mascota}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# Ruta para mostrar el formulario de edición
@app.route('/editar-mascota/<int:id_mascota>', methods=['GET'])
def editar_mascota(id_mascota):
    try:
        cur = mysql.connection.cursor()
        # Verificar si la mascota existe y está asociada al usuario actual
        cur.execute("SELECT * FROM mascotas WHERE id_mascota = %s", (id_mascota,))
        mascota = cur.fetchone()
        
        # Validación de permisos usando id_usuario en la sesión
        if not mascota:
            return redirect(url_for('premium'))  # Redirigir si no encuentra la mascota
        if mascota['id_usuario'] != session['id_usuario']:
            return redirect(url_for('premium'))  # Redirigir si no es el usuario propietario

        # Obtener las fotos y PDFs asociados a la mascota
        cur.execute("SELECT * FROM fotos WHERE id_mascota = %s", (id_mascota,))
        fotos = cur.fetchall()
        
        cur.execute("SELECT * FROM archivos WHERE id_mascota = %s", (id_mascota,))
        archivos = cur.fetchall()
        
        cur.close()
        return render_template('editar_mascota.html', mascota=mascota, fotos=fotos, archivos=archivos)
    except Exception as e:
        return redirect(url_for('premium'))  # Redirigir en caso de error


# Ruta para actualizar una mascota
@app.route('/actualizar-mascota/<int:id_mascota>', methods=['POST'])
def actualizar_mascota(id_mascota):
    nombre = request.form.get('nombre')
    especie = request.form.get('especie')
    edad = request.form.get('edad')
    raza = request.form.get('raza')
    
    # Validación de los datos requeridos
    if not all([nombre, especie, edad, raza]):
        return jsonify({'success': False, 'error': 'Todos los campos son obligatorios'}), 400

    try:
        cur = mysql.connection.cursor()

        # Verificar si la mascota existe y está asociada al usuario actual
        cur.execute("SELECT id_usuario FROM mascotas WHERE id_mascota = %s", (id_mascota,))
        resultado = cur.fetchone()

        # Validación de permisos usando id_usuario en la sesión
        if not resultado:
            return jsonify({'success': False, 'error': 'Mascota no encontrada'}), 404
        if resultado['id_usuario'] != session['id_usuario']:
            return jsonify({'success': False, 'error': 'Acceso denegado'}), 403

        # Actualizar la mascota
        cur.execute("""
            UPDATE mascotas 
            SET nombre = %s, especie = %s, edad = %s, raza = %s 
            WHERE id_mascota = %s
        """, (nombre, especie, edad, raza, id_mascota))
        mysql.connection.commit()
        cur.close()

        # Redirigir al usuario a la vista premium o a la vista de edición
        return redirect(url_for('premium'))  # O redirigir de nuevo al formulario de edición con url_for('editar_mascota', id_mascota=id_mascota)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500





# Ruta para eliminar una mascota (validando diagnósticos)
@app.route('/eliminar-mascota/<int:id_mascota>', methods=['POST'])
def eliminar_mascota(id_mascota):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM diagnosticos WHERE id_mascota = %s", (id_mascota,))
        diagnosticos = cur.fetchone()

        if diagnosticos:
            return jsonify({'success': False, 'error': 'No puedes eliminar una mascota con diagnósticos.'}), 400

        cur.execute("DELETE FROM mascotas WHERE id_mascota = %s", (id_mascota,))
        mysql.connection.commit()
        cur.close()

        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# Ruta para obtener las mascotas del usuario autenticado
@app.route('/obtener_mascotas', methods=['GET'])
def obtener_mascotas():
    id_usuario = session.get('id')

    if not id_usuario:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_mascota, nombre, especie, edad, raza FROM mascotas WHERE id_usuario = %s", (id_usuario,))
        mascotas = cur.fetchall()
        cur.close()

        # Convertir el resultado a una lista de diccionarios
        mascotas_list = []
        for mascota in mascotas:
            mascotas_list.append({
                'id_mascota': mascota['id_mascota'],
                'nombre': mascota['nombre'],
                'especie': mascota['especie'],
                'edad': mascota['edad'],
                'raza': mascota['raza']
            })

        return jsonify(mascotas_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


#---------------------------------------------------

@app.route('/cambiarRol', methods=['POST'])
def cambiar_rol():
    data = request.get_json()
    nuevo_rol = data.get('nuevoRol')

    # Verificar si el usuario está autenticado
    if 'id' not in session:
        return jsonify({'success': False, 'message': 'Usuario no autenticado.'}), 403

    user_id = session['id']

    try:
        # Conexión a la base de datos
        cursor = mysql.connection.cursor()
        # Actualizar el rol del usuario a 'premium'
        cursor.execute("""
            UPDATE usuarios 
            SET id_rol = (SELECT id_rol FROM roles WHERE descripcion = %s) 
            WHERE id = %s
        """, (nuevo_rol, user_id))
        mysql.connection.commit()

        # Confirmar si la actualización fue exitosa
        if cursor.rowcount == 0:
            return jsonify({'success': False, 'message': 'No se pudo cambiar el rol.'})
        
        return jsonify({'success': True})

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return jsonify({'success': False, 'message': 'Error al actualizar el rol.'})
    
    finally:
        cursor.close()


#---------------------------------------------------


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
        
        # Si existe un usuario con el correo ya ingresado
        if account:
            hashed_password = account['password']

            # Si la contraseña en la BD es texto plano (usuarios de prueba)
            if hashed_password in ['Campos20*', '123']:  # Lista de contraseñas de texto plano 
                if hashed_password == _password:
                    # Iniciar sesión para usuarios de prueba
                    session['logueado'] = True
                    session['id'] = account['id']
                    session['id_rol'] = account['id_rol']
                    session['usuario'] = _correo  # Establece el usuario en la sesión

                    # Redirigir según el rol del usuario
                    if session['id_rol'] == 1:
                        return render_template("admin.html")
                    elif session['id_rol'] == 2:
                        return render_template("usuario.html")
                    elif session['id_rol'] == 3:
                        return render_template("premium.html")
                else:
                    return render_template('index.html', mensaje="Usuario o contraseña incorrectos")
            else:
                # Para contraseñas hasheadas
                if check_password_hash(hashed_password, _password):
                    # Iniciar sesión para usuarios con contraseñas hasheadas
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

# Logout endpoint
@app.route('/logout')
def logout():
    # Elimina la sesión del usuario
    session.pop('usuario', None)
    session.clear()

    # Mensaje emergente (popup) de éxito con 
    flash('Has cerrado sesión exitosamente.', 'success')
    #re dirije al index
    return redirect(url_for('home'))

#---------------------------------------------------
#--- Botón NAV Listar mascotas ------
@app.route('/listar_mascotas', methods=["GET"])
def listar_mascotas():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.id_mascota, m.nombre, m.especie, m.raza, m.edad, u.nombre AS propietario
        FROM mascotas m
        JOIN usuarios u ON m.id_usuario = u.id
    """)
    mascotas = cur.fetchall()
    cur.close()

    return render_template("listar_mascotas.html", mascotas=mascotas)

#---------------------------------------------------

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
        
        # Comprobar si el correo ya está registrado
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
        usuario_existente = cur.fetchone()  # Almacena el usuario si existe
        cur.close()

        if usuario_existente:
            return render_template('registro.html', mensaje="El correo ya está registrado. Por favor intenta con otro.")

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

            
            # Obtener los datos actuales del usuario recién registrado
            cur.execute("SELECT nombre, correo FROM usuarios WHERE correo = %s", (correo,))
            usuario_actual = cur.fetchone()  # Almacena los datos actuales del usuario en un diccionario

            if usuario_actual:
                nombre_usuario = usuario_actual['nombre']
                correo_usuario = usuario_actual['correo']

            cur.close()

            # Enviar correo de bienvenida con el nombre del usuario
            try:
                mensaje_bienvenida = f"Hola {nombre_usuario}, gracias por registrarte en YouPet. ¡Esperamos que disfrutes de la plataforma!"
                msg = Message("Bienvenido a YouPet", sender=app.config['MAIL_USERNAME'], recipients=[correo_usuario])
                msg.body = mensaje_bienvenida
                mail.send(msg)
            except smtplib.SMTPAuthenticationError:
                app.logger.error("Error de autenticación SMTP al intentar enviar el correo. Verifica tus credenciales.")

            return render_template("index.html", mensaje2="Registro exitoso")


        except IntegrityError as e:
            if "Duplicate entry" in str(e):
                return render_template('registro.html', mensaje="El correo ya está registrado.")
            else:
                # Loguear el error inesperado para futura referencia
                app.logger.error(f"Error inesperado: {str(e)}")
                return render_template('registro.html', mensaje="El correo ya está registrado.")

    return render_template('registro.html')
#-----------


# Ruta de subida de archivos
UPLOAD_FOLDER_PDF = 'static/uploads/pdfs/'
app.config['UPLOAD_FOLDER_PDF'] = UPLOAD_FOLDER_PDF

# Subir archivo PDF
@app.route('/subir-archivo', methods=['POST'])
def subir_archivo():
    id_usuario = session.get('id')

    if not id_usuario:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    if 'archivo' not in request.files or request.files['archivo'].filename == '':
        return jsonify({'error': 'No se seleccionó ningún archivo'}), 400

    mascota_id = request.form.get('mascota_id')
    if not mascota_id:
        return jsonify({'error': 'No se seleccionó ninguna mascota'}), 400

    archivo = request.files['archivo']
    if not archivo.filename.endswith('.pdf'):
        return jsonify({'error': 'Formato no permitido. Solo archivos PDF son permitidos.'}), 400

    try:
        # Verificar que la mascota pertenece al usuario autenticado
        cur = mysql.connection.cursor()
        cur.execute("SELECT id_mascota FROM mascotas WHERE id_usuario = %s AND id_mascota = %s", (id_usuario, mascota_id))
        mascota = cur.fetchone()

        if not mascota:
            return jsonify({'error': 'La mascota no pertenece al usuario autenticado'}), 403

        # Asegurar el nombre del archivo y guardarlo
        filename = secure_filename(archivo.filename)
        ruta_archivo = os.path.join(app.config['UPLOAD_FOLDER_PDF'], filename)
        archivo.save(ruta_archivo)

        # Guardar la información en la base de datos
        cur.execute("""
            INSERT INTO archivos (id_mascota, id_usuario, nombre_archivo, ruta_archivo, fecha_subida)
            VALUES (%s, %s, %s, %s, %s)
            """, (mascota_id, id_usuario, filename, ruta_archivo, datetime.now()))
        mysql.connection.commit()

        # Ruta relativa para el frontend
        ruta_relativa = f"/{ruta_archivo}"

        return jsonify({'success': 'Archivo PDF subido exitosamente', 'filename': filename, 'ruta': ruta_relativa}), 200

    except Exception as e:
        return jsonify({'error': f'Error al subir el archivo: {str(e)}'}), 500

    finally:
        cur.close()
    

# Ruta para obtener los archivos de una mascota específica
@app.route('/api/archivos/<int:id_mascota>', methods=['GET'])
def obtener_archivos(id_mascota):
    try:
        query = "SELECT id_archivo, nombre_archivo FROM archivos WHERE id_mascota = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (id_mascota,))
        archivos = cursor.fetchall()
        return jsonify(archivos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ruta para eliminar archivos o fotos
@app.route('/api/eliminar/<string:tipo>/<int:id>', methods=['DELETE'])
def eliminar(tipo, id):
    try:
        if tipo == 'archivo':
            query = "DELETE FROM archivos WHERE id_archivo = %s"
        elif tipo == 'foto':
            query = "DELETE FROM fotos WHERE id_foto = %s"
        else:
            return jsonify({"error": "Tipo no válido"}), 400

        cursor = mysql.connection.cursor()
        cursor.execute(query, (id,))
        mysql.connection.commit()
        return jsonify({"message": f"{tipo.capitalize()} eliminado correctamente"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Ruta de subida de fotos
UPLOAD_FOLDER_FOTOS = 'static/uploads/fotos/'
app.config['UPLOAD_FOLDER_FOTOS'] = UPLOAD_FOLDER_FOTOS

# Subir fotos
@app.route('/subir-fotos', methods=['POST'])
def subir_fotos():
    id_usuario = session.get('id')

    if not id_usuario:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    if 'fotos' not in request.files:
        return jsonify({'error': 'No se seleccionaron fotos'}), 400
    
    fotos = request.files.getlist('fotos')
    mascota_id = request.form.get('mascota_id')

    if not mascota_id:
        return jsonify({'error': 'No se seleccionó ninguna mascota'}), 400

    # Verificar que la mascota pertenece al usuario autenticado
    cur = mysql.connection.cursor()
    cur.execute("SELECT id_mascota FROM mascotas WHERE id_usuario = %s AND id_mascota = %s", (id_usuario, mascota_id))
    mascota = cur.fetchone()

    if not mascota:
        return jsonify({'error': 'La mascota no pertenece al usuario autenticado'}), 403

    # Verificar si ya hay 4 fotos asociadas a esta mascota
    cur.execute("SELECT COUNT(*) as total_fotos FROM fotos WHERE id_mascota = %s", (mascota_id,))
    total_fotos = cur.fetchone()['total_fotos']

    if total_fotos >= 4:
        return jsonify({'error': 'No puedes subir más de 4 fotos por mascota'}), 400

    for foto in fotos:
        if foto.filename != '' and foto.content_type.startswith('image/'):
            filename = secure_filename(foto.filename)
            ruta_foto = os.path.join(app.config['UPLOAD_FOLDER_FOTOS'], filename)
            foto.save(ruta_foto)

            # Guardar la ruta de la foto en la base de datos
            cur.execute("""
                INSERT INTO fotos (id_mascota, ruta_foto, fecha_subida)
                VALUES (%s, %s, %s)
                """, (mascota_id, ruta_foto, datetime.now()))
    
    mysql.connection.commit()
    cur.close()

    return jsonify({'success': 'Fotos subidas exitosamente'}), 200



# Ruta para obtener las fotos de una mascota específica
@app.route('/api/fotos/<int:id_mascota>', methods=['GET'])
def obtener_fotos(id_mascota):
    try:
        query = "SELECT id_foto, ruta_foto FROM fotos WHERE id_mascota = %s"
        cursor = mysql.connection.cursor()
        cursor.execute(query, (id_mascota,))
        fotos = cursor.fetchall()
        return jsonify(fotos), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        

# Eliminar foto
@app.route('/eliminar-foto/<int:id_foto>', methods=['DELETE'])
def eliminar_foto(id_foto):
    id_usuario = session.get('id')

    if not id_usuario:
        return jsonify({'error': 'Usuario no autenticado'}), 401

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT f.id_foto, f.ruta_foto 
        FROM fotos f 
        JOIN mascotas m ON f.id_mascota = m.id_mascota 
        WHERE m.id_usuario = %s AND f.id_foto = %s
        """, (id_usuario, id_foto))
    foto = cur.fetchone()

    if not foto:
        return jsonify({'error': 'No tienes permiso para eliminar esta foto'}), 403

    cur.execute("DELETE FROM fotos WHERE id_foto = %s", (id_foto,))
    mysql.connection.commit()
    cur.close()

    # Opcional: eliminar la foto del sistema de archivos
    if os.path.exists(foto['ruta_foto']):
        os.remove(foto['ruta_foto'])

    return jsonify({'success': 'Foto eliminada exitosamente'}), 200



#---------------
#Consulta del chatbot
@app.route('/consulta-chatbot', methods=['POST'])
def consulta_chatbot():
    data = request.get_json()
    pregunta = data.get('pregunta', '')

    # Consultar Prolog
    respuesta = list(prolog.query(f'responder_pregunta("{pregunta}", Respuesta)'))
    if respuesta:
        return jsonify({'respuesta': respuesta[0]['Respuesta']})
    else:
        return jsonify({'respuesta': 'No puedo responder a esta pregunta.'})


#---------------

if __name__ == '__main__':
    #clave secreta  
    app.secret_key = "Campos20*"
    #crear de manera local, servidor al correr
    app.run(debug = True, host = '0.0.0.0', port = 5000, threaded = True)



