from flask import Flask, render_template, request, redirect, session
import pymysql
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "oriana123"


import os
import pymysql

conn = pymysql.connect(
    host=os.environ.get("DB_HOST"),
    port=int(os.environ.get("DB_PORT")),
    user=os.environ.get("DB_USER"),
    password=os.environ.get("DB_PASSWORD"),
    database=os.environ.get("DB_NAME")
)


@app.route('/')
def inicio():
    return redirect('/articulos')

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        nombre = request.form['nombre']
        correo = request.form['correo']
        contraseña = request.form['contraseña']

        cursor = conn.cursor()

        sql = """
        INSERT INTO users (nombre, correo, contraseña)
        VALUES (%s, %s, %s)
        """

        cursor.execute(sql, (nombre, correo, contraseña))
        conn.commit()

        return "Usuario registrado correctamente"

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        correo = request.form['correo']
        contraseña = request.form['contraseña']

        cursor = conn.cursor()

        sql = """
        SELECT * FROM users
        WHERE correo=%s AND contraseña=%s
        """

        cursor.execute(sql, (correo, contraseña))

        usuario = cursor.fetchone()

        if usuario:
            session["nombre"] = usuario[1]
            session["correo"] = usuario[2]
            session["rol"] = usuario[4]

            if usuario[4] == 'admin':
                return redirect('/admin')

            else:
                return redirect('/usuario')

        else:
            return "Correo o contraseña incorrectos"

    return render_template('login.html')
@app.route('/usuario')
def usuario():
    return render_template("usuario.html")
@app.route('/crear_articulo', methods=['GET', 'POST'])
def crear_articulo():

    if request.method == 'POST':

        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        categoria = request.form['categoria']

        imagen = request.files['imagen']

        nombre_imagen = secure_filename(imagen.filename)

        ruta = os.path.join('static', 'uploads', nombre_imagen)

        imagen.save(ruta)

        cursor = conn.cursor()

        sql = """
        INSERT INTO articulos
        (titulo, descripcion, precio, categoria, imagen)
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(
            sql,
            (titulo, descripcion, precio, categoria, nombre_imagen)
        )

        conn.commit()

        return redirect('/usuario')

    return render_template('crear_articulo.html')
@app.route('/articulos')
def articulos():

    cursor = conn.cursor()

    buscar = request.args.get('buscar')

    if buscar:

        sql = """
        SELECT * FROM articulos
        WHERE titulo LIKE %s
        OR descripcion LIKE %s
        OR categoria LIKE %s
        """

        dato = "%" + buscar + "%"

        cursor.execute(sql, (dato, dato, dato))

    else:

        cursor.execute("SELECT * FROM articulos")

    articulos = cursor.fetchall()

    return render_template(
        'articulos.html',
        articulos=articulos
    )
@app.route("/articulo/<int:id>")
def ver_articulo(id):

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM articulos WHERE id=%s", (id,))

    articulo = cursor.fetchone()

    return render_template(
        "ver_articulo.html",
        articulo=articulo
    )
@app.route('/eliminar/<int:id>')
def eliminar(id):

    cursor = conn.cursor()

    sql = "DELETE FROM articulos WHERE id=%s"

    cursor.execute(sql, (id,))

    conn.commit()

    return redirect('/articulos')
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):

    cursor = conn.cursor()

    if request.method == 'POST':

        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        categoria = request.form['categoria']

        sql = """
        UPDATE articulos
        SET titulo=%s,
            descripcion=%s,
            precio=%s,
            categoria=%s
        WHERE id=%s
        """

        cursor.execute(
            sql,
            (titulo, descripcion, precio, categoria, id)
        )

        conn.commit()

        return redirect('/admin  ')

    sql = "SELECT * FROM articulos WHERE id=%s"

    cursor.execute(sql, (id,))

    articulo = cursor.fetchone()

    return render_template(
        'editar_articulo.html',
        articulo=articulo
    )

@app.route('/admin')
def admin():
    if "rol" not in session or session["rol"] != "admin":
     return redirect('/login')

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    usuarios = cursor.fetchall()

    cursor.execute("SELECT * FROM articulos")
    articulos = cursor.fetchall()

    return render_template(
        'admin.html',
        usuarios=usuarios,
        articulos=articulos
    )
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
@app.route('/eliminar_articulo/<int:id>')
def eliminar_articulo(id):

    cursor = conn.cursor()

    sql = "DELETE FROM articulos WHERE id=%s"

    cursor.execute(sql, (id,))

    conn.commit()

    return redirect('/admin')
if __name__ == '__main__':
    app.run(debug=True)