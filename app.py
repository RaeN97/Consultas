from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector


class App:
    def __init__(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'supersecretkey'
        self.db_config = {
            'user': 'root',
            'password': '',
            'host': 'localhost',
            'database': 'soldadores'
        }

        # Inicialización del LoginManager
        self.login_manager = LoginManager(self.app)
        self.login_manager.login_view = 'login'

        # Definición de user_loader
        @self.login_manager.user_loader
        def load_user(user_id):
            conn = self._get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                return User(user['id'], user['username'])
            return None

        self._setup_routes()
        
    def validar_rut(self, rut):
        """Valida el formato del RUT chileno."""
        rut = rut.replace('.', '').replace('-', '').upper()
        if len(rut) < 2:
            return False

        cuerpo = rut[:-1]
        dv = rut[-1]

        if not cuerpo.isdigit() or not (dv.isdigit() or dv in 'Kk'):
            return False

        suma = 0
        multiplicador = 2

        for i in reversed(cuerpo):
            suma += int(i) * multiplicador
            multiplicador = multiplicador + 1 if multiplicador < 7 else 2

        dv_calculado = 11 - (suma % 11)
        if dv_calculado == 11:
            dv_calculado = '0'
        elif dv_calculado == 10:
            dv_calculado = 'K'
        else:
            dv_calculado = str(dv_calculado)

        return dv == dv_calculado

    def _setup_routes(self):
        self.app.add_url_rule('/', view_func=self.index)
        self.app.add_url_rule('/trabajadores', view_func=self.trabajadores)
        self.app.add_url_rule('/eliminar/<n>', view_func=self.eliminar, methods=['POST'])
        self.app.add_url_rule('/editar/<n>', view_func=self.editar, methods=['GET', 'POST'])
        self.app.add_url_rule('/consultar', view_func=self.consultar, methods=['POST', 'GET'])
        self.app.add_url_rule('/agregar', view_func=self.agregar, methods=['GET', 'POST'])
        self.app.add_url_rule('/login', view_func=self.login, methods=['GET', 'POST'])
        self.app.add_url_rule('/logout', view_func=self.logout)
        self.app.add_url_rule('/register', view_func=self.register, methods=['GET', 'POST'])

    def _get_db_connection(self):
        return mysql.connector.connect(**self.db_config)

    def index(self):
        return render_template('index.html')

    @login_required
    def trabajadores(self):
        conn = self._get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM soldadores")
        trabajadores = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('trabajadores.html', trabajadores=trabajadores)

    @login_required
    def eliminar(self, n):
        # Conectamos a la base de datos y ejecutamos la consulta para eliminar el trabajador con el numero al que se le asigno la base de datos automaticamente.
        conn = self._get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM soldadores WHERE N = %s", (n,))
        conn.commit()# Confirmamos la transacción.
        cursor.close()
        conn.close()
        # Mostramos un mensaje de éxito y redirigimos a la lista de trabajadores.
        flash('Registro eliminado exitosamente.', 'success')
        return redirect(url_for('trabajadores'))

    @login_required
    def editar(self, n):
        conn = self._get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        if request.method == 'POST':
            # Obtener datos del formulario
            numero_estampa = request.form.get('NUMERO_ESTAMPA')
            nombre = request.form.get('NOMBRE')
            turno = request.form.get('TURNO')
            cargo = request.form.get('CARGO')
            alcance = request.form.get('ALCANCE')
            estampa = request.form.get('ESTAMPA')
            fecha_calificacion = request.form.get('FECHA_CALIFICACION')
            informe_laboratorio = request.form.get('INFORME_LABORATORIO')
            estado_pago_cesmec = request.form.get('ESTADO_DE_PAGO_CESMEC')
            habilitado_para_soldar = request.form.get('HABILITADO_PARA_SOLDAR')
            rango_diametros_espesores = request.form.get('RANGO_DE_DIAMETROS_O_ESPESORES')
            wpq_ava = request.form.get('WPQ_AVA')
            posicion_calificada = request.form.get('POSICION_CALIFICADA')
            material_base = request.form.get('MATERIAL_BASE')
            aporte = request.form.get('Aporte')
            proceso = request.form.get('PROCESO')
            norma = request.form.get('NORMA')
            wps = request.form.get('WPS')
            pqr = request.form.get('PQR')
            estatus = request.form.get('ESTATUS')
            contratado_finiquitado = request.form.get('CONTRATADO_FINIQUITADO_O_NO_HABILITADO')
            observaciones = request.form.get('OBSERVACIONES')
            
            # Validar campos obligatorios
            if not nombre or not turno or not cargo or not alcance:
                flash('Por favor, completa todos los campos obligatorios.')
                return redirect(url_for('editar', n=n))
            
            # Actualizar el registro en la base de datos
            query = """UPDATE soldadores SET NUMERO_ESTAMPA=%s,
                        NOMBRE=%s, TURNO=%s, CARGO=%s, ALCANCE=%s, ESTAMPA=%s, FECHA_CALIFICACION=%s,
                        INFORME_LABORATORIO=%s, ESTADO_DE_PAGO_CESMEC=%s, HABILITADO_PARA_SOLDAR=%s,
                        RANGO_DE_DIAMETROS_O_ESPESORES=%s, WPQ_AVA=%s, POSICION_CALIFICADA=%s,
                        MATERIAL_BASE=%s, Aporte=%s, PROCESO=%s, NORMA=%s, WPS=%s, PQR=%s,
                        ESTATUS=%s, CONTRATADO_FINIQUITADO_O_NO_HABILITADO=%s, OBSERVACIONES=%s
                        WHERE N=%s"""
            values = (numero_estampa, nombre, turno, cargo, alcance, estampa, fecha_calificacion,
                    informe_laboratorio, estado_pago_cesmec, habilitado_para_soldar,
                    rango_diametros_espesores, wpq_ava, posicion_calificada,
                    material_base, aporte, proceso, norma, wps, pqr, estatus,
                    contratado_finiquitado, observaciones, n)
            cursor.execute(query, values)
            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Registro actualizado exitosamente.')
            return redirect(url_for('trabajadores'))

        else:
            #Cargamos los datos actuales del trabajador para mostrarlos en el formulario.
            cursor.execute("SELECT * FROM soldadores WHERE N = %s", (n,))
            trabajador = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if trabajador:
                return render_template('editar.html', trabajador=trabajador)
            else:
                flash('Trabajador no encontrado.')
                return redirect(url_for('trabajadores'))

    @login_required
    def consultar(self):
        conn = self._get_db_connection()
        if request.method == 'POST':
            criterio = request.form.get('criterio')
            valor = request.form.get('valor')

            # Validar que se han proporcionado criterio y valor
            if not criterio or not valor:
                flash('Debe ingresar un criterio y un valor para la búsqueda.', 'warning')
                return redirect(url_for('consultar'))

            # Validar RUT si el criterio es RUT
            if criterio == "RUT":
                if not self.validar_rut(valor):
                    flash('RUT inválido. Por favor, ingrese un RUT válido.', 'warning')
                    return redirect(url_for('consultar'))
                query = "SELECT * FROM soldadores WHERE RUT = %s"
                params = (valor,)
            elif criterio == "NOMBRE":
                query = "SELECT * FROM soldadores WHERE NOMBRE LIKE %s"
                params = (f'%{valor}%',)
            else:
                flash('Criterio de búsqueda no válido.', 'warning')
                return redirect(url_for('consultar'))

            # Ejecutar la consulta
            conn = self._get_db_connection()
            cursor = conn.cursor(dictionary=True)

            try:
                cursor.execute(query, params)
                trabajadores = cursor.fetchall()  # Obtener todos los resultados

                if not trabajadores:
                    flash(f"No se encontró ningún trabajador con {criterio.lower()} {valor}", 'warning')
                    return redirect(url_for('consultar'))

                return render_template('consultar.html', trabajadores=trabajadores)
            finally:
                cursor.close()
                conn.close()
        
        # Para solicitudes GET, solo se renderiza el formulario
        return render_template('consultar.html')

    @login_required
    def agregar(self):
        if request.method == 'POST':
            # Obtener datos del formulario
            numero_estampa = request.form.get('NUMERO_ESTAMPA')
            rut = request.form.get('RUT')
            nombre = request.form.get('NOMBRE')
            turno = request.form.get('TURNO')
            cargo = request.form.get('CARGO')
            alcance = request.form.get('ALCANCE')
            estampa = request.form.get('ESTAMPA')
            fecha_calificacion = request.form.get('FECHA_CALIFICACION')
            informe_laboratorio = request.form.get('INFORME_LABORATORIO')
            estado_pago_cesmec = request.form.get('ESTADO_DE_PAGO_CESMEC')
            habilitado_para_soldar = request.form.get('HABILITADO_PARA_SOLDAR')
            rango_diametros_espesores = request.form.get('RANGO_DE_DIAMETROS_O_ESPESORES')
            wpq_ava = request.form.get('WPQ_AVA')
            posicion_calificada = request.form.get('POSICION_CALIFICADA')
            material_base = request.form.get('MATERIAL_BASE')
            aporte = request.form.get('Aporte')
            proceso = request.form.get('PROCESO')
            norma = request.form.get('NORMA')
            wps = request.form.get('WPS')
            pqr = request.form.get('PQR')
            estatus = request.form.get('ESTATUS')
            contratado_finiquitado = request.form.get('CONTRATADO_FINIQUITADO_O_NO_HABILITADO')
            observaciones = request.form.get('OBSERVACIONES')
            
            # Validar campos obligatorios
            if not rut or not nombre or not turno or not cargo or not alcance:
                flash('Por favor, completa todos los campos obligatorios.')
                return redirect(url_for('agregar'))
            
            # Insertar el nuevo trabajador en la base de datos
            conn = self._get_db_connection()
            cursor = conn.cursor()
            query = """INSERT INTO soldadores (NUMERO_ESTAMPA, RUT, NOMBRE, TURNO, CARGO, ALCANCE, ESTAMPA, FECHA_CALIFICACION,
                        INFORME_LABORATORIO, ESTADO_DE_PAGO_CESMEC, HABILITADO_PARA_SOLDAR, RANGO_DE_DIAMETROS_O_ESPESORES,
                        WPQ_AVA, POSICION_CALIFICADA, MATERIAL_BASE, Aporte, PROCESO, NORMA, WPS, PQR, ESTATUS,
                        CONTRATADO_FINIQUITADO_O_NO_HABILITADO, OBSERVACIONES)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (numero_estampa, rut, nombre, turno, cargo, alcance, estampa, fecha_calificacion,
            informe_laboratorio, estado_pago_cesmec, habilitado_para_soldar,
            rango_diametros_espesores, wpq_ava, posicion_calificada,
            material_base, aporte, proceso, norma, wps, pqr, estatus,
            contratado_finiquitado, observaciones)

            cursor.execute(query, values)

            conn.commit()
            cursor.close()
            conn.close()
            
            flash('Trabajador agregado exitosamente.')
            return redirect(url_for('trabajadores'))
        
        return render_template('agregar.html')

    def login(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            conn = self._get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            cursor.close()
            conn.close()

            if user:
                # Debug: imprime las contraseñas
                print(f"Contraseña hasheada en la base de datos: {user['password']}")
                print(f"Contraseña ingresada: {password}")

                # Comprobación de contraseña
                if check_password_hash(user['password'], password):
                    print("Contraseña válida")
                    user_obj = User(user['id'], user['username'])
                    login_user(user_obj)
                    flash('Inicio de sesión exitoso.', 'success')
                    return redirect(url_for('trabajadores'))
                else:
                    print("Contraseña no válida")
                    flash('Credenciales inválidas.', 'danger')
            else:
                print(f"Usuario {username} no encontrado en la base de datos")
                flash('Credenciales inválidas.', 'danger')

        return render_template('index.html')

    @login_required
    def logout(self):
        logout_user()
        flash('Cierre de sesión exitoso.', 'success')
        return redirect(url_for('login'))

    def register(self):
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Generar el hash de la contraseña para mayor seguridad
            hashed_password = generate_password_hash(password)

            # Conexión a la base de datos
            conn = self._get_db_connection()
            cursor = conn.cursor()

            # Comprobar si el usuario ya existe
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash('El nombre de usuario ya está en uso. Elige otro.', 'danger')
                return redirect(url_for('register'))

            # Insertar el nuevo usuario en la base de datos
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            conn.commit()
            cursor.close()
            conn.close()

            # Redirigir a la página de inicio con un mensaje de confirmación
            flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
            return redirect(url_for('index'))  # Redirige a la página de inicio

        return render_template('index.html')

    def run(self):
        self.app.run(host='0.0.0.0', port=5000, debug=True)



class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username


if __name__ == '__main__':
    app_instance = App()
    app_instance.run()
