import unittest
from app import app, mysql

class YouPetTestCase(unittest.TestCase):
    
    def setUp(self):
        """Configurar el entorno de prueba"""
        app.config['TESTING'] = True
        self.app = app.test_client()
        self.app.testing = True

    def test_registro_usuario(self):
        """Prueba unitaria para registrar un usuario"""
        response = self.app.post('/crear-registro', data=dict(
            txtNombre='Test Usuario',
            txtCorreo='test@usuario.com',
            txtPassword='password123',
            txtConfirmPassword='password123'
        ), follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Registro exitoso', response.data)

    def test_login_usuario(self):
        """Prueba unitaria para iniciar sesión con un usuario"""
        response = self.app.post('/login', data=dict(
            correo='test@usuario.com',
            password='password123'
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Bienvenido', response.data)

    def test_agregar_mascota(self):
        """Prueba unitaria para agregar una mascota"""
        # Primero, registrar un usuario y obtener su ID
        self.test_registro_usuario()
        response = self.app.post('/agregar-mascota', data=dict(
            nombre='Firulais',
            especie='Perro',
            raza='Chihuahua',
            edad=3,
            id_usuario=1  # Ajustar según el ID que tengas en la base de datos
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Mascota agregada exitosamente', response.data)

    def tearDown(self):
        """Eliminar registros de prueba después de ejecutar las pruebas"""
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM mascotas WHERE nombre = 'Firulais'")
        cur.execute("DELETE FROM usuarios WHERE correo = 'test@usuario.com'")
        mysql.connection.commit()
        cur.close()

if __name__ == '__main__':
    unittest.main()
