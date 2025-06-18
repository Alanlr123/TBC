from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from werkzeug.utils import secure_filename
import sqlite3

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

UPLOAD_FOLDER = 'static/galeria'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Categorías disponibles
CATEGORIAS = ['Eventos Escolares', 'Actividades Deportivas y Culturales', 'Calendario Escolar', 'calificaciones', 'Proyectos Escolares']
AVISOS = []  # Avisos temporales en memoria

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/galeria')
def galeria():
    return render_template('galeria.html', categorias=CATEGORIAS)

@app.route('/galeria/<categoria>')
def galeria_categoria(categoria):
    categoria = categoria.strip()
    ruta_categoria = os.path.join(app.static_folder, 'galeria', categoria)
    if not os.path.exists(ruta_categoria):
        os.makedirs(ruta_categoria)
    imagenes = os.listdir(ruta_categoria)
    return render_template('galeria_categoria.html', imagenes=imagenes, categoria=categoria)

@app.route('/login/director', methods=['GET', 'POST'])
def login_director():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contraseña = request.form['contraseña']

        if usuario == 'TBC' and contraseña == '1234':
            session['director_logueado'] = True
            return redirect(url_for('panel_director'))
        else:
            error = 'Usuario o contraseña incorrectos'
            return render_template('login_director.html', error=error)

    return render_template('login_director.html')

@app.route('/panel/director', methods=['GET', 'POST'])
def panel_director():
    if not session.get('director_logueado'):
        return redirect(url_for('login_director'))

    if request.method == 'POST':
        mensaje_id = request.form.get('mensaje_id')
        if mensaje_id:
            conn = sqlite3.connect('mensajes.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM mensajes WHERE id = ?', (mensaje_id,))
            conn.commit()
            conn.close()
            flash('Mensaje eliminado correctamente.', 'success')
            return redirect(url_for('panel_director'))

    imagenes_por_categoria = {}
    for categoria in CATEGORIAS:
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], categoria)
        os.makedirs(ruta, exist_ok=True)
        imagenes = os.listdir(ruta)
        imagenes_por_categoria[categoria] = imagenes

    conn = sqlite3.connect('mensajes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, nombre, correo, contenido FROM mensajes')
    mensajes = cursor.fetchall()
    conn.close()

    return render_template(
        'panel_director.html',
        categorias=CATEGORIAS,
        imagenes_por_categoria=imagenes_por_categoria,
        avisos=AVISOS,
        mensajes=mensajes
    )

@app.route('/subir-imagen-general', methods=['POST'])
def subir_imagen_general():
    if not session.get('director_logueado'):
        return redirect(url_for('login_director'))

    categoria = request.form.get('categoria')
    archivo = request.files.get('imagen')

    if categoria not in CATEGORIAS:
        flash('Categoría no válida.', 'error')
        return redirect(url_for('panel_director'))

    if not archivo or archivo.filename == '':
        flash('No seleccionaste ninguna imagen.', 'error')
        return redirect(url_for('panel_director'))

    filename = secure_filename(archivo.filename)
    ruta_categoria = os.path.join(app.config['UPLOAD_FOLDER'], categoria)
    os.makedirs(ruta_categoria, exist_ok=True)
    archivo.save(os.path.join(ruta_categoria, filename))

    flash(f'Imagen subida correctamente a {categoria}.', 'success')
    return redirect(url_for('panel_director'))

@app.route('/eliminar-imagen/<categoria>/<nombre_imagen>', methods=['POST'])
def eliminar_imagen(categoria, nombre_imagen):
    if not session.get('director_logueado'):
        return redirect(url_for('login_director'))

    if categoria not in CATEGORIAS:
        flash('Categoría no válida', 'error')
        return redirect(url_for('panel_director'))

    ruta_imagen = os.path.join(app.config['UPLOAD_FOLDER'], categoria, nombre_imagen)
    if os.path.exists(ruta_imagen):
        os.remove(ruta_imagen)
        flash('Imagen eliminada correctamente.', 'success')
    else:
        flash('La imagen no existe.', 'error')

    return redirect(url_for('panel_director'))

@app.route('/agregar-aviso', methods=['POST'])
def agregar_aviso():
    if not session.get('director_logueado'):
        return redirect(url_for('login_director'))

    nuevo_aviso = request.form['aviso']
    if nuevo_aviso:
        AVISOS.append(nuevo_aviso)
    return redirect(url_for('panel_director'))

@app.route('/eliminar-aviso/<int:indice>', methods=['POST'])
def eliminar_aviso(indice):
    if not session.get('director_logueado'):
        return redirect(url_for('login_director'))

    if 0 <= indice < len(AVISOS):
        AVISOS.pop(indice)
    return redirect(url_for('panel_director'))

@app.route('/avisos')
def ver_avisos():
    return render_template('ver_avisos.html', avisos=AVISOS)

@app.route('/logout')
def logout():
    session.pop('director_logueado', None)
    return redirect(url_for('index'))

# Páginas alumnos y otras secciones

@app.route('/alumnos/categoria')
def alumnos():
    return render_template('alumnos_categoria.html')

@app.route('/becas')
def becas():
    return render_template('becas.html')

@app.route('/reglamento')
def reglamento():
    return render_template('reglamento.html')

@app.route('/servicios')
def servicios():
    return render_template('servicios.html') 

@app.route('/paraescolares')
def paraescolares():
    return render_template('paraescolares.html')

@app.route('/ceremonias')
def ceremonias():
    return render_template('ceremonias.html')

@app.route('/aniversario')
def aniversario():
    return render_template('aniversario.html')

@app.route('/tbc')
def tbc():
    return render_template('tbc.html')

@app.route('/misión')
def misión():
    return render_template('misión.html')

@app.route('/equipo')
def equipo():
    return render_template('equipo.html')

@app.route('/mensaje', methods=['GET', 'POST'])
def mensaje():
    mensaje_enviado = False
    if request.method == 'POST':
        nombre = request.form['nombre']
        correo = request.form['correo']
        contenido = request.form['mensaje']

        try:
            conn = sqlite3.connect('mensajes.db')
            cursor = conn.cursor()
            cursor.execute('INSERT INTO mensajes (nombre, correo, contenido) VALUES (?, ?, ?)',
                           (nombre, correo, contenido))
            conn.commit()
            conn.close()
            mensaje_enviado = True
            flash('Mensaje enviado correctamente.', 'success')
        except Exception as e:
            flash(f'Error al enviar mensaje: {e}', 'error')

    return render_template('mensaje.html', mensaje_enviado=mensaje_enviado)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

