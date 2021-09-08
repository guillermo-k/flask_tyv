from flask import Flask,app,render_template,request,redirect,flash,url_for,session,send_from_directory
from flaskext.mysql import MySQL
import os
from datetime import datetime

# from pymysql.cursors import Cursor

app= Flask(__name__)
app.secret_key="18980413Guille"
mysql = MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost' # Configuración de host DB
app.config['MYSQL_DATABASE_USER']='root' # Configuración de usuario DB
app.config['MYSQL_DATABASE_PASSWORD']='' # Contraseña DB

mysql.init_app(app) # Inicialización de SQL
CARPETA= os.path.join('fotos') # Referencia a la carpeta
app.config['CARPETA']=CARPETA # Indicamos que vamos a guardar esta ruta de la carpeta


# creacion de DB
conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS `tyv`;")
cursor.execute("CREATE TABLE IF NOT EXISTS `tyv`.`usuarios` (`username` VARCHAR(16) NOT NULL , `password` VARCHAR(16) NOT NULL , PRIMARY KEY (`username`));")
cursor.execute("CREATE TABLE IF NOT EXISTS `tyv`.`categorias`(`id` INT(10) NOT NULL AUTO_INCREMENT, `nombre` VARCHAR(32) NOT NULL, `descripcion` VARCHAR(500) NOT NULL, PRIMARY KEY(`id`));")
cursor.execute("CREATE TABLE IF NOT EXISTS `tyv`.`productos` (`id` INT(20) NOT NULL AUTO_INCREMENT, `nombre` VARCHAR(50) NOT NULL, `descripcion` VARCHAR(500) NOT NULL , `precio` FLOAT(10) NOT NULL , `categoria` VARCHAR(500) NOT NULL , `foto` VARCHAR(500) NOT NULL , `stock` INT(5) NOT NULL , `destacado` INT(1) NOT NULL , PRIMARY KEY(`id`));")
cursor.execute("INSERT IGNORE `tyv`.`usuarios` (`username`,`password`) VALUES ('admin', 'admin');")
conn.commit()


#Sector visitas
@app.route('/base')
def base():
    return render_template('base.html')

@app.route('/tabla_productos')
def tabla_productos():
    return render_template('tabla_productos.html')

@app.route('/')
def index():
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute('SELECT*FROM `tyv`.`productos` WHERE `destacado` LIKE "1" ')
    semanal=cursor.fetchall()
    cursor.execute('SELECT*FROM `tyv`.`productos` WHERE `destacado` LIKE "2" ')
    destacados=cursor.fetchall()
    conn.commit()
    return render_template('index.html',semanal=semanal,productos=destacados)

@app.route('/productos/<categoria>')
def productos(categoria):
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute('SELECT*FROM `tyv`.`categorias` ORDER BY `nombre` ')
    categorias=cursor.fetchall()
    if categoria=='todos':
        cursor.execute('SELECT*FROM `tyv`.`productos` ORDER BY `nombre` ')
    else:
        cursor.execute('SELECT*FROM `tyv`.`productos` WHERE `categoria` LIKE %s ORDER BY `nombre` ', categoria)
    productos=cursor.fetchall()
    conn.commit()
    return render_template('productos.html',productos=productos, categorias=categorias)



#Sector administración
@app.route('/login')#'''Pagina para el login administrador'''
def login():
    return render_template('login.html')

@app.route('/registrarse')
def registrarse():
    flash('Debe registrarse antes')
    return redirect('/login')

@app.route('/validacion', methods=['POST'])
def validacion():
    username=request.form['username']
    password=request.form['pasword']
    sql=("SELECT*FROM `tyv`.`usuarios` WHERE `username` LIKE %s")
    conn=mysql.connect()
    cursor=conn.cursor()
    cursor.execute(sql,username)
    usuario=cursor.fetchone()
    conn.commit()
    if usuario!='' and password==usuario[0][0]:
        session['username']='username'
        flash("Registro exitoso")
    else:
        flash('Nombre de usuario o contraseña erroneo. Intente nuevamente')
        return redirect('/login')
    return redirect('/admin')

@app.route('/admin')
def admin():
    if 'username' in session:
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute('SELECT*FROM `tyv`.`productos`')
        productos=cursor.fetchall()
        return render_template('admin.html',productos=productos)
    else:
        return redirect('/registrarse')

@app.route('/altas')
def altas():
    return render_template('altas.html')

@app.route('/cargaP', methods=['POST'])
def carga_producto():
    if 'username' in session:
        nombre=request.form['nombre']
        descripcion=request.form['descripcion']
        precio=request.form['precio']
        categoria=request.form['categoria']
        foto=request.files['foto']
        stock=request.form['stock']
        # destacado=0
        descripcionC=request.form['descripcionC']
        now=datetime.now() # Obtenemos la fecha para asignarla al nombre de la foto
        tiempo=now.strftime("_%Y%H%M%S") # Obtenemos de la fecha el año, la hora, los minutos y segundos
        extension=foto.filename.split(".") # Obtenemos la extensión del archivo
        if foto.filename !="": # Si el campo foto no esta vacío
            nuevoNombreFoto=nombre+tiempo+"."+extension[1] # Creamos el nombre de la foto
            foto.save("fotos/"+nuevoNombreFoto) # Guardamos la foto en la carpeta correspondiente
        if nombre=='' or descripcion=='' or precio=='' or categoria=='' or foto=='' or stock=='':
            flash('Todos los campos son obligatorios')
        else:
            datos=(nombre,descripcion,precio,categoria,nuevoNombreFoto,stock)
            sql='INSERT INTO `tyv`.`productos` (`id`,`nombre`,`descripcion`,`precio`,`categoria`,`foto`,`stock`,`destacado`) VALUES(NULL,%s,%s,%s,%s,%s,%s,0)'
            conn=mysql.connect()
            cursor=conn.cursor()
            cursor.execute(sql,datos)
            cursor.execute("SELECT `nombre` FROM `tyv`.`categorias`")
            categorias=cursor.fetchall()
            if categoria not in categorias:
                datos=(categoria, descripcionC)
                sql='INSERT INTO `tyv`.`categorias` (`id`,`nombre`,`descripcion`) VALUES(NULL,%s,%s)'
                cursor.execute(sql,datos)
            conn.commit()
            flash('Producto cargado con exito')
        return redirect('/admin')
    else:
        return redirect('/registrarse')

@app.route('/destacados', methods=['POST'])
def destacados():
    if 'username' in session:
        conn=mysql.connect()
        cursor=conn.cursor()
        cursor.execute("SELECT `id` FROM `tyv`.`productos`")
        productos=cursor.fetchall()
        for producto in productos:
            id=str(producto[0])
            print("-----------------------------")
            print(id)
            print("-----------------------------")
            destacado=request.form[id]
            print("-----------------------------")
            print(destacado)
            print("-----------------------------")
            if destacado!="":
                datos=(destacado,producto[0])
                # datos=(producto[0])
                cursor.execute("UPDATE `tyv`.`productos` SET `destacado`= %s WHERE `productos`.`id`=%s",datos)
                # cursor.execute("UPDATE `tyv`.`productos` SET `destacado` = '1' WHERE `productos`.`id` = 1")
                print('uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
        conn.commit()
        flash('Destacados cargado con exito')
        return redirect('/admin')
    else:
        return redirect('/registrarse')

# Borrado de productos
@app.route('/destroy/<int:id>') # Recibe como parámetro el id del producto
def destroy(id):
    if "username" in session: # Si es usuario registrado
        conn = mysql.connect() # Realiza la conexión mysql.init_app(app)
        cursor = conn.cursor() # Almacenaremos lo que ejecutamos
        cursor.execute("SELECT foto FROM `tyv`.`productos` WHERE id_producto=%s",id) # Buscamos la foto
        fila= cursor.fetchall() # Traemos toda la información
        os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) # Elimina la foto de la carpeta
        cursor.execute("DELETE FROM `tyv`.`productos` WHERE id_producto=%s", (id)) # Eliminamos el producto de la DB por su ID
        conn.commit() # Cerramos la conexión
        flash("Producto eliminado")
        return redirect('/admin') # Volvemos a la pagina de administración de DB
    else: # Si NO es usuario registrado
        return redirect('/') # Redireccionamos a Inicio

# Renderización de pagina de editado de productos
@app.route('/edit/<int:x>') # Recibe como parámetro el id del producto
def edit(x):
    if "username" in session: # Si es usuario registrado
        conn = mysql.connect() # Realiza la conexión mysql.init_app(app)
        cursor = conn.cursor() # Almacenaremos lo que ejecutamos
        cursor.execute("SELECT * FROM `tyv`.`productos`, `tyv`.`categorias` WHERE productos.id=%s AND `categorias`.`id`=`productos`.`id`", x) # Buscamos el producto de la DB por su id
        producto=cursor.fetchone() # Traemos toda la información
        cursor.execute("SELECT * FROM `tyv`.`categorias`;") # Buscar todas las categorías de la tabla "categorías"
        categorias=cursor.fetchall() # Almacenamos lo que ejecutamos
        conn.commit() #Cerramos la conexión
        return render_template('/edit.html', producto=producto,categorias=categorias) # Renderizar edit.html con la información obtenida
    else: # Si NO es usuario registrado
        return redirect('/registrarse') # Redireccionamos a Inicio

# Editado de productos
@app.route('/update', methods=['POST']) # Recibimos los datos desde el formulario de edición, del producto a editar
def update():
    if "username" in session: # Si es usuario registrado
        # Obtenemos los datos correspondientes y los almacenamos
        id=request.form['id']
        nombre=request.form['nombre']
        descripcion=request.form['descripcion']
        precio=request.form['precio']
        categoria=request.form['categoria']
        foto=request.files['foto']
        stock=request.form['stock']
        sql = "UPDATE `tyv`.`productos` SET `nombre`=%s ,`descripcion`=%s ,`precio`=%s, `categoria`=%s , `stock`=%s   WHERE id=%s;" # Definimos la actualización del producto
        datos=(nombre, descripcion, precio, categoria, stock, id) # Definimos los nuevos valores del producto
        conn = mysql.connect() # Se conecta a la conexión mysql.init_app(app)
        cursor = conn.cursor() # Almacenaremos lo que ejecutamos
        cursor.execute("SELECT foto FROM `tyv`.`productos`   WHERE id=%s", id) #Buscamos la foto
        fila= cursor.fetchall() #Traemos toda la información
        if foto.filename !="": # Si el campo foto no esta vacío
            now= datetime.now() # Obtenemos la fecha y la hora actuales, para definir el nombre de la foto, y evitar repetir este
            tiempo= now.strftime("_%Y%H%M%S") #dia mes horas minutos y segundos
            extension=foto.filename.split(".") # Recuperamos la extensión del archivo foto
            nuevoNombreFoto=nombre+tiempo+"."+extension[1] # Renombramos la foto
            foto.save("fotos/"+nuevoNombreFoto) # Guardamos la foto nueva
            os.remove(os.path.join(app.config['CARPETA'], fila[0][0])) # Borramos la foto vieja
            data=(nuevoNombreFoto, id) # Definimos los valores a actualizar
            cursor.execute("UPDATE `tyv`.`productos` SET `foto`=%s WHERE id=%s", data) # Actualizamos la foto del producto
        cursor.execute(sql,datos) # Actualizamos los datos del producto
        conn.commit() #Cerramos la conexión
        flash("Producto modificado con exito")
        return redirect('/admin')  # Volvemos a la pagina de administración de DB
    else:  # Si NO es usuario registrado
        return redirect('/registrarse') # Redireccionamos a inicio

@app.route('//productos/fotos/<nombreFoto>')
@app.route('/fotos/<nombreFoto>') #Recibimos como parametro el nombre de la foto
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

if __name__=="__main__":
    app.run(debug=True, host="192.168.100.3", port=5002)
