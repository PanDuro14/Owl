# Se importan los frameworks 
from flask import Flask, g, render_template, request, redirect, url_for, session, json, jsonify
from functools import wraps
from flask_mysqldb import MySQL,MySQLdb
import pymysql

# Nombre de la aplicación para la ejecución 
app = Flask(__name__)

# sesion
app.secret_key = 'mysecretkey'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'owldb_v1'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)


# Clase de usuarios
class User:
    def __init__(self,id_usuario, nom_usuario, correo, passw):
        self.id_usuario = id_usuario
        self.nom_usuario = nom_usuario
        self.correo = correo 
        self.passw = passw        
    def __repr__(self):
        return '<User:{self.id_usuario}'
    
#Objeto de la clase usuarios
users=[]
no_auth_routes = ['login', 'singup','/']#No necesitan permisos

# Inicio de la web (index, hub, hobby)
@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='POST':        
        return render_template('index.html')
    return render_template('index.html')

# Comprobar la sesión
def login_required(f):
    # Generar funcón decorada (eso implica que solo se podrá ejecutar en secuencias específias 
    # con el método '@login_requiered')
    @wraps(f) 
    def decorated_function(*args, **kwargs):
        # Comprueba que la varibale session no esté vacía, en caso de que lo esté, mandará a logear
        if 'id_usuario' not in session:
            error = "Error: 403 Acceso no autorizado | Inicia sesión para ver"
            return render_template("error_usuario.html", des_error=error, paginaant='/login')
        
        # En caso de que lo esté, asignarle el valor con el 'id_usuario' que viene de la clase User
        id_usuario = session['id_usuario']
        # En caso de que no esté instanciado el 'id_usuario' mandará a logear para instanciarlo 
        if not isinstance(id_usuario, (int, float)):
            error = "Error: 403 Acceso no autorizado | Inicia sesión para ver"
            return render_template("error_usuario.html", des_error=error, paginaant='/login')
        
        # Hace la validación del usuario llenando los parámtros de la clase users con las tuplas 
        # de la tabla usuario en la db
        conn = pymysql.connect(host='localhost', user='root', passwd='', db='owldb_v1')
        cursor = conn.cursor()
        cursor.execute('select id_usuario, nom_usuario, correo, passw from usuarios where id_usuario=%s', 
                       (session['id_usuario']))
        dato = cursor.fetchone()
        users.clear() # Vacía la clase users para evitar conflictos 
        users.append(User(id_usuario=dato[0], nom_usuario=[1], correo=[2], passw=[3]))
        # Devuelve la variable global user, tomando el valor de users[0] que es el id del usuario
        g.user = users[0]
        # Devuelve los valores como atributos
        return f(*args, **kwargs)
    return(decorated_function)


# Crear una cuenta para iniciar sesión
@app.route('/singup', methods=['GET','POST'])
def singup(): 
    if request.method=='POST':        
        aux_nom_usuario = request.form['nom_usuario']
        aux_nombre = request.form['nombre']
        aux_ap_paterno = request.form['ap_paterno']
        aux_ap_materno = request.form['ap_materno']
        aux_correo = request.form['correo']
        aux_passw = request.form['passw']
        
        conn = pymysql.connect(host='localhost', user='root', passwd='', db='owldb_v1' )
        cursor = conn.cursor()
        # Tomar únicamente los usuarios para comprobar si existe (probablemente se pueda simplificar
        # en una sola linea de código )
        cursor.execute('select nom_usuario from usuarios where nom_usuario=%s', (aux_nom_usuario))
        comp_u=cursor.fetchone()
        # Tomar únicamente los correos para comprobar si existe (probablemente se pueda simplificar
        # en una sola linea de código )
        cursor.execute('select correo from usuarios where correo=%s', (aux_correo))
        comp_c=cursor.fetchone()
        
        # Comprobar usuario existente
        if comp_u is not None:
            error="Usuario no está dispoible"
            return render_template("error_usuario.html", des_error=error, paginaant='/singup')
        
        # Comprobar correo existente
        elif (comp_c is not None):
            error="Correo no está dispoible"
            return render_template("error_usuario.html", des_error=error, paginaant='/singup')
        
        # Comprobar ambos (puede ser un poco inutil, posible de descartar)
        elif (comp_u and comp_c is not None):
            error="Usuario y correo no están dispoibles"
            return render_template("error_usuario.html", des_error=error, paginaant='/singup')
        
        # Fin de validación. Hacer alta
        else:
            cursor.execute('insert into usuarios '
                        ' (nom_usuario, nombre, ap_paterno, ap_materno, correo, passw) '
                        ' VALUES (%s, %s, %s, %s, %s, %s) ', 
                        (aux_nom_usuario, aux_nombre, aux_ap_paterno, aux_ap_materno, aux_correo, aux_passw))
        conn.commit()
        conn.close()
    return render_template('singup.html')

# Módulo para iniciar sesión 
# Validar credenciales (que son correo y passw) y asignar el tipo de sesión
# dependiendo de si es un usuario o un admin
@app.route('/login', methods=['GET','POST'])
def login():
    session.pop('id_usuario', None)
    if request.method=='POST':
        correo = request.form['correo']
        passw = request.form['passw']
        conn = pymysql.connect(host='localhost', user='root', passwd='', db='owldb_v1' )
        cursor = conn.cursor()
        #Verificación de usario 
        cursor.execute('select id_usuario, nom_usuario, passw from usuarios where correo=%s and passw=%s', (correo, passw))
        usuario=cursor.fetchone() 
        # En caso de error
        # En caso de que las credenciales no coincidan, mandará el siguiente error       
        if (usuario==None):            
            conn.close()
            error="usuario y/o contraseña no son conrrectos"
            return render_template("error_usuario.html", des_error=error, paginaant='/login')
        # En caso de que se valide correctamente
        # En caso de que el usuario sea un administrador, el array usuario se establece como admin
        elif (usuario=='admin'):
            session['admin']=usuario[0]                    
            return render_template('index.html')
        
        # En caso de que sea un usuario común, la sesión se establece como usuario 
        else:            
            session['id_usuario']=usuario[0]     
            return render_template('index.html')        
    return render_template('login.html')

# Conseguir el id de la sesión de la variable "session" dejada 
# a partir de validar la sesión en el proceso "login_requiered"
def get_user(): 
    id=session.get('id_usuario')
    if id is not None and (id, (int, float)):
        g.id_us=int(id)
        return print(g.id_us)
    return g.id_us

# Cerrar sesión
# limpia la sesión y a los usuarios
@app.route('/logout')
def logout():
    session.clear()
    users.clear()
    return render_template("login.html")

# Módulo de pacientes 
@app.route('/paciente')
@login_required #Comprobar la sesión
def pacientes():        
    get_user() # Tomar el id del usuario
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='owldb_v1')
    cursor = conn.cursor()  
    id_aux = g.id_us # Definir el id como parámetro condiconal 

    cursor.execute(' select id_paciente, nombre_cliente, ap_pa, ap_ma, fecha_nacimiento, genero, id_usuario '
                   ' from Paciente '
                   ' where id_usuario=%s', (id_aux))
    datos = cursor.fetchall()
    conn.close()
    return render_template("pacientes.html", pacientes=datos) 

# Módulo para agregar pacientes
@app.route('/nuevo_paciente', methods=['GET', 'POST'])
def nuevo_paciente():
    get_user()        
    if request.method=='POST':        
        id_aux=g.id_us
        aux_regis = request.form ['regis_on']
        aux_nombre_paciente = request.form['nom_cliente']
        aux_ap_pa = request.form['ap_pa']
        aux_ap_ma = request.form['ap_ma']
        aux_fecha_nacimiento = request.form['fecha_nacimiento']
        aux_genero = request.form['genero']
        aux_civil = request.form['civil']        
        aux_antecedentes = request.form['antecedentes']    
        aux_medicamentos = request.form['medicamentos']
        
        conn = pymysql.connect(host='localhost', user='root', passwd='', db='owldb_v1')        
        cursor = conn.cursor()
                
        
        cursor.execute( ' INSERT INTO Paciente (registro_online, id_usuario, nombre_cliente, '
                        ' ap_pa, ap_ma, fecha_nacimiento, genero, estado_civil, antecedentes_medicos, '
                        ' medicamentos_actuales) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',  
                        (aux_regis, id_aux, aux_nombre_paciente, aux_ap_pa, aux_ap_ma, aux_fecha_nacimiento,
                        aux_genero, aux_civil, aux_antecedentes, aux_medicamentos))
        conn.commit()
        conn.close()        
    return render_template("nuevo_paciente.html")

# Borrar a un paciente 
@app.route('/bor_paciente/<string:id>')
def bor_paciente(id): 
    conn = pymysql.connect(host='localhost', user='root', passwd='', db='owldb_v1')        
    cursor = conn.cursor()    
    cursor.execute('delete from paciente where id_paciente ={0}'.format(id))    
    conn.commit()
    conn.close()
    return redirect(url_for('home'))

# fin del programa
if __name__ == '__main__':
    app.run(port=5000, debug=True)
    
    #En caso de cambiar el port, notificar al resto del equipo