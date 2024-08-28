# Importamos las funciones y módulos necesarios de Flask y mysql.connector.
from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector


# Creamos una instancia de la aplicación Flask.
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para usar flash messages


# Configuración de la base de datos
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'soldadores'
}



# Ruta principal que muestra la página de inicio.
@app.route('/')
def index():
    return render_template('index.html')



# Ruta que muestra la lista de trabajadores en la base de datos.
@app.route('/trabajadores')
def trabajadores():
    # Conectamos a la base de datos usando la configuración establecida.
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    # Ejecutamos una consulta para obtener todos los registros de la tabla "soldadores".
    cursor.execute("SELECT * FROM soldadores")
    trabajadores = cursor.fetchall()# Recuperamos todos los registros como una lista de diccionarios.
    cursor.close()
    conn.close()
    # Renderizamos la plantilla 'trabajadores.html', pasando la lista de trabajadores como contexto.
    return render_template('trabajadores.html', trabajadores=trabajadores)



def validar_rut(rut):
    """
    Validación de un RUT .
    """
    rut = rut.upper().replace(".", "").replace("-", "")
    if len(rut) < 2:
        return False
    cuerpo = rut[:-1]
    dv = rut[-1]
    try:
        cuerpo = int(cuerpo)
    except ValueError:
        return False
    suma = 0
    multiplicador = 2
    for c in reversed(str(cuerpo)):
        suma += int(c) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2
    resto = suma % 11
    dv_calculado = 11 - resto
    if dv_calculado == 11:
        dv_calculado = '0'
    elif dv_calculado == 10:
        dv_calculado = 'K'
    else:
        dv_calculado = str(dv_calculado)
    return dv == dv_calculado




# Ruta para eliminar un trabajador según el número al cual fue asignado.
@app.route('/eliminar/<n>', methods=['POST'])
def eliminar(n):
    # Conectamos a la base de datos y ejecutamos la consulta para eliminar el trabajador con el numero al que se le asigno la base de datos automaticamente.
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM soldadores WHERE N = %s", (n,))
    conn.commit()# Confirmamos la transacción.
    cursor.close()
    conn.close()
    # Mostramos un mensaje de éxito y redirigimos a la lista de trabajadores.
    flash('Registro eliminado exitosamente.', 'success')
    return redirect(url_for('trabajadores'))



# Ruta para editar los datos de un trabajador.
@app.route('/editar/<n>', methods=['GET', 'POST'])
def editar(n):
    conn = mysql.connector.connect(**db_config)
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



# Ruta para consultar los datos de un trabajador por su RUT.
@app.route('/consultar', methods=['POST', 'GET'])
def consultar():
    if request.method == 'POST':
        criterio = request.form.get('criterio')
        valor = request.form.get('valor')

        # Validar que se han proporcionado criterio y valor
        if not criterio or not valor:
            flash('Debe ingresar un criterio y un valor para la búsqueda.', 'warning')
            return redirect(url_for('consultar'))

        # Validar RUT si el criterio es RUT
        if criterio == "RUT":
            if not validar_rut(valor):
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
        conn = mysql.connector.connect(**db_config)
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




def validar_rut(rut):
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


# Ruta para agregar un nuevo trabajador.
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
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
        conn = mysql.connector.connect(**db_config)
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



# Inicia la aplicación Flask si se ejecuta este script directamente.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
