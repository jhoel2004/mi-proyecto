from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave-secreta-facebook-clone'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///facebook.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos de la base de datos
# Tabla de asociación para amistades
amistad = db.Table('amistad',
    db.Column('usuario_id_1', db.Integer, db.ForeignKey('usuario.id')),
    db.Column('usuario_id_2', db.Integer, db.ForeignKey('usuario.id'))
)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    foto_perfil = db.Column(db.String(200), default='default.jpg')
    bio = db.Column(db.Text, default='')
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relaciones
    publicaciones = db.relationship('Publicacion', backref='autor', lazy=True)
    comentarios = db.relationship('Comentario', backref='autor', lazy=True)
    likes = db.relationship('Like', backref='usuario', lazy=True)
    
    # Amistades (muchos a muchos)
    amigos = db.relationship('Usuario', 
                             secondary=amistad,
                             primaryjoin=id == amistad.c.usuario_id_1,
                             secondaryjoin=id == amistad.c.usuario_id_2,
                             backref=db.backref('amigos_de', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Usuario {self.email}>'
    
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

class Publicacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    imagen = db.Column(db.String(200), nullable=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    # Relaciones
    comentarios = db.relationship('Comentario', backref='publicacion', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='publicacion', lazy=True, cascade='all, delete-orphan')
    
    def contar_likes(self):
        return len(self.likes)
    
    def contar_comentarios(self):
        return len(self.comentarios)

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    publicacion_id = db.Column(db.Integer, db.ForeignKey('publicacion.id'), nullable=False)

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    publicacion_id = db.Column(db.Integer, db.ForeignKey('publicacion.id'), nullable=False)
    
    # Evitar likes duplicados
    __table_args__ = (db.UniqueConstraint('usuario_id', 'publicacion_id', name='unique_like'),)

# Función para crear usuarios de prueba
def crear_usuarios_prueba():
    usuarios_data = [
        {'nombre': 'Juan', 'apellido': 'Pérez', 'email': 'juan.perez@email.com', 'password': '123456', 'bio': 'Amante de la tecnología y los viajes'},
        {'nombre': 'María', 'apellido': 'García', 'email': 'maria.garcia@email.com', 'password': '123456', 'bio': 'Fotógrafa profesional 📸'},
        {'nombre': 'Carlos', 'apellido': 'Rodríguez', 'email': 'carlos.rodriguez@email.com', 'password': '123456', 'bio': 'Desarrollador de software'},
        {'nombre': 'Ana', 'apellido': 'Martínez', 'email': 'ana.martinez@email.com', 'password': '123456', 'bio': 'Estudiante de medicina'},
        {'nombre': 'Luis', 'apellido': 'Sánchez', 'email': 'luis.sanchez@email.com', 'password': '123456', 'bio': 'Chef y emprendedor'},
        {'nombre': 'Elena', 'apellido': 'López', 'email': 'elena.lopez@email.com', 'password': '123456', 'bio': 'Diseñadora gráfica'},
        {'nombre': 'Pedro', 'apellido': 'González', 'email': 'pedro.gonzalez@email.com', 'password': '123456', 'bio': 'Músico y compositor'},
        {'nombre': 'Sofía', 'apellido': 'Díaz', 'email': 'sofia.diaz@email.com', 'password': '123456', 'bio': 'Viajera del mundo 🌍'},
    ]
    
    for user_data in usuarios_data:
        existing_user = Usuario.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            nuevo_usuario = Usuario(
                nombre=user_data['nombre'],
                apellido=user_data['apellido'],
                email=user_data['email'],
                password=generate_password_hash(user_data['password']),
                bio=user_data['bio']
            )
            db.session.add(nuevo_usuario)
    
    db.session.commit()
    
    # Crear algunas amistades
    usuarios = Usuario.query.all()
    if len(usuarios) >= 2:
        # Juan es amigo de María y Carlos
        if usuarios[0] not in usuarios[1].amigos_de:
            usuarios[0].amigos_de.append(usuarios[1])
            usuarios[1].amigos_de.append(usuarios[0])
        
        if usuarios[0] not in usuarios[2].amigos_de:
            usuarios[0].amigos_de.append(usuarios[2])
            usuarios[2].amigos_de.append(usuarios[0])
        
        # María es amiga de Ana
        if usuarios[1] not in usuarios[3].amigos_de:
            usuarios[1].amigos_de.append(usuarios[3])
            usuarios[3].amigos_de.append(usuarios[1])
    
    db.session.commit()
    
    # Crear publicaciones de prueba
    if Publicacion.query.count() == 0:
        publicaciones_data = [
            {'usuario_email': 'juan.perez@email.com', 'contenido': '¡Hola a todos! Este es mi primer post en esta nueva red social. ¡Espero conectar con viejos amigos!', 'imagen': None},
            {'usuario_email': 'maria.garcia@email.com', 'contenido': 'Hermoso atardecer en la playa hoy 🌅', 'imagen': 'https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=500'},
            {'usuario_email': 'carlos.rodriguez@email.com', 'contenido': 'Acabo de terminar un nuevo proyecto en Python. ¡La programación es increíble!', 'imagen': None},
            {'usuario_email': 'ana.martinez@email.com', 'contenido': 'Estudiando para los exámenes finales. ¡Wish me luck! 📚', 'imagen': None},
            {'usuario_email': 'elena.lopez@email.com', 'contenido': 'Nuevo diseño que acabo de crear. ¿Qué opinan?', 'imagen': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?w=500'},
            {'usuario_email': 'sofia.diaz@email.com', 'contenido': 'Explorando las calles de París 🇫🇷', 'imagen': 'https://images.unsplash.com/photo-1502602898657-3e91760cbb34?w=500'},
            {'usuario_email': 'pedro.gonzalez@email.com', 'contenido': 'Grabando nuevas canciones en el estudio 🎵', 'imagen': None},
            {'usuario_email': 'luis.sanchez@email.com', 'contenido': 'Probando una nueva receta de pasta italiana 🍝', 'imagen': 'https://images.unsplash.com/photo-1473093295043-cdd812d0e601?w=500'},
        ]
        
        for pub_data in publicaciones_data:
            usuario = Usuario.query.filter_by(email=pub_data['usuario_email']).first()
            if usuario:
                nueva_publicacion = Publicacion(
                    contenido=pub_data['contenido'],
                    imagen=pub_data['imagen'],
                    autor=usuario
                )
                db.session.add(nueva_publicacion)
                
                # Agregar algunos likes
                if pub_data['usuario_email'] in ['maria.garcia@email.com', 'sofia.diaz@email.com']:
                    otros_usuarios = [u for u in usuarios if u.email != pub_data['usuario_email']]
                    for otro in otros_usuarios[:3]:
                        like = Like(usuario=otro, publicacion=nueva_publicacion)
                        db.session.add(like)
        
        db.session.commit()

# Rutas
@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect(url_for('feed'))
    return redirect(url_for('login'))

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not all([nombre, apellido, email, password]):
            flash('Todos los campos son requeridos', 'error')
            return render_template('registro.html')
        
        if Usuario.query.filter_by(email=email).first():
            flash('El email ya está registrado', 'error')
            return render_template('registro.html')
        
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            password=generate_password_hash(password)
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro exitoso. Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and check_password_hash(usuario.password, password):
            session['usuario_id'] = usuario.id
            flash(f'Bienvenido/a {usuario.nombre_completo()}!', 'success')
            return redirect(url_for('feed'))
        else:
            flash('Email o contraseña incorrectos', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('login'))

@app.route('/feed')
def feed():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuario_actual = Usuario.query.get(session['usuario_id'])
    publicaciones = Publicacion.query.order_by(Publicacion.fecha.desc()).all()
    
    return render_template('feed.html', 
                         usuario=usuario_actual, 
                         publicaciones=publicaciones)

@app.route('/publicar', methods=['POST'])
def publicar():
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    contenido = request.form.get('contenido')
    imagen = request.form.get('imagen')
    
    if contenido:
        nueva_publicacion = Publicacion(
            contenido=contenido,
            imagen=imagen if imagen else None,
            usuario_id=session['usuario_id']
        )
        db.session.add(nueva_publicacion)
        db.session.commit()
        flash('Publicación creada exitosamente', 'success')
    
    return redirect(url_for('feed'))

@app.route('/like/<int:publicacion_id>')
def like(publicacion_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    existing_like = Like.query.filter_by(
        usuario_id=session['usuario_id'],
        publicacion_id=publicacion_id
    ).first()
    
    if existing_like:
        db.session.delete(existing_like)
    else:
        like = Like(
            usuario_id=session['usuario_id'],
            publicacion_id=publicacion_id
        )
        db.session.add(like)
    
    db.session.commit()
    return redirect(url_for('feed'))

@app.route('/comentar/<int:publicacion_id>', methods=['POST'])
def comentar(publicacion_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    contenido = request.form.get('contenido')
    
    if contenido:
        comentario = Comentario(
            contenido=contenido,
            usuario_id=session['usuario_id'],
            publicacion_id=publicacion_id
        )
        db.session.add(comentario)
        db.session.commit()
        flash('Comentario agregado', 'success')
    
    return redirect(url_for('feed'))

@app.route('/perfil/<int:usuario_id>')
def perfil(usuario_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    usuario_actual = Usuario.query.get(session['usuario_id'])
    publicaciones = Publicacion.query.filter_by(usuario_id=usuario_id).order_by(Publicacion.fecha.desc()).all()
    
    es_amigo = usuario_actual in usuario.amigos_de
    
    return render_template('perfil.html', 
                         usuario=usuario, 
                         usuario_actual=usuario_actual,
                         publicaciones=publicaciones,
                         es_amigo=es_amigo)

@app.route('/agregar_amigo/<int:usuario_id>')
def agregar_amigo(usuario_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuario_a_agregar = Usuario.query.get_or_404(usuario_id)
    usuario_actual = Usuario.query.get(session['usuario_id'])
    
    if usuario_a_agregar not in usuario_actual.amigos_de:
        usuario_actual.amigos_de.append(usuario_a_agregar)
        usuario_a_agregar.amigos_de.append(usuario_actual)
        db.session.commit()
        flash(f'Ahora eres amigo de {usuario_a_agregar.nombre_completo()}', 'success')
    
    return redirect(url_for('perfil', usuario_id=usuario_id))

@app.route('/eliminar_amigo/<int:usuario_id>')
def eliminar_amigo(usuario_id):
    if 'usuario_id' not in session:
        return redirect(url_for('login'))
    
    usuario_a_eliminar = Usuario.query.get_or_404(usuario_id)
    usuario_actual = Usuario.query.get(session['usuario_id'])
    
    if usuario_a_eliminar in usuario_actual.amigos_de:
        usuario_actual.amigos_de.remove(usuario_a_eliminar)
        usuario_a_eliminar.amigos_de.remove(usuario_actual)
        db.session.commit()
        flash(f'Has dejado de ser amigo de {usuario_a_eliminar.nombre_completo()}', 'info')
    
    return redirect(url_for('perfil', usuario_id=usuario_id))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        crear_usuarios_prueba()
    
    print("=" * 50)
    print("📘 Facebook Clone - Red Social")
    print("=" * 50)
    print("\nUsuarios de prueba disponibles:")
    print("- juan.perez@email.com / 123456")
    print("- maria.garcia@email.com / 123456")
    print("- carlos.rodriguez@email.com / 123456")
    print("- ana.martinez@email.com / 123456")
    print("- luis.sanchez@email.com / 123456")
    print("- elena.lopez@email.com / 123456")
    print("- pedro.gonzalez@email.com / 123456")
    print("- sofia.diaz@email.com / 123456")
    print("\nAccede a: http://localhost:5000")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
