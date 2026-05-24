from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
import os
import logging
from datetime import datetime

app = Flask(__name__)

#Configuração do arquivo de log
logging.basicConfig(
    filename='auditoria.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# CONFIGURAÇÃO DO BANCO
DATABASE_URL = os.getenv('DATABASE_URL')

if DATABASE_URL:
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
    if "?" in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.split("?")[0]
        
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "connect_args": {"ssl": {"ssl_mode": "REQUIRED"}}
    }
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:@localhost/calculadora_emergia'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.secret_key = ''
with app.app_context():
    db.create_all()

# DEFINIÇÃO DA TABELA (Precisa estar aqui para o criar_admin.py funcionar)
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    perfil = db.Column(db.String(20), default='usuario')

class FatorEmergia(db.Model):
    __tablename__ = 'fatores_emergia'
    id = db.Column(db.Integer, primary_key=True)
    material_energia = db.Column(db.String(100), unique=True, nullable=False)
    transformidade = db.Column(db.Float, nullable=False) 
    unidade = db.Column(db.String(20), nullable=False)  

class LogAcesso(db.Model):
    __tablename__ = 'logs_acesso'
    id = db.Column(db.Integer, primary_key=True)
    data_hora = db.Column(db.DateTime, default=db.func.now())
    usuario = db.Column(db.String(100), nullable=False)
    evento = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), nullable=False)

app.config['SECRET_KEY'] = 'uma_chave_aleatoria'

#NOVAS ROTAS

@app.route('/')
def home():
    #Página pública que explica sobre emergia
    return render_template('home.html')


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        email = request.form.get('email')
        senha = request.form.get('password')
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and bcrypt.check_password_hash(usuario.senha_hash, senha):
            session['usuario_id'] = usuario.id
            session['nome_usuario'] = usuario.nome
            session['perfil'] = usuario.perfil
            logging.info(f"LOGIN SUCESSO: {email}")
            return redirect(url_for('calculadora'))
        else:
            logging.warning(f"FALHA DE LOGIN: {email}")
            flash("Credenciais inválidas.")
            return redirect(url_for('login_page'))
            
    return render_template('acesso.html', tipo_erro='login')

@app.route('/cadastro', methods=['POST'])
def cadastro():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('password')

    usuario_existente = Usuario.query.filter_by(email=email).first()
    if usuario_existente:
        flash('Este endereço de e-mail já está registrado!')
        # Devolve para a mesma página sinalizando que o erro foi na aba de cadastro
        return render_template('acesso.html', tipo_erro='cadastro')

    hash_senha = bcrypt.generate_password_hash(senha).decode('utf-8')
    novo_usuario = Usuario(nome=nome, email=email, senha_hash=hash_senha, perfil='usuario')
    
    db.session.add(novo_usuario)
    db.session.commit()
    logging.info(f"NOVO CADASTRO: {email}")

    flash('Conta criada com sucesso! Faça login.')
    return redirect(url_for('login_page'))


@app.route('/calculadora', methods=['GET', 'POST'])
def calculadora():
    #Verifica se o usuario esta logado antes de mostrar a calculadora
    if 'usuario_id' not in session:
        return redirect(url_for('login_page'))

    resultados = None

    if request.method == 'POST':
        # Coleta de dados - Bicicleta Elétrica
        bike_bateria = float(request.form.get('bike_bateria') or 0)
        bike_motor = float(request.form.get('bike_motor') or 0)
        bike_energia = float(request.form.get('bike_energia') or 0)

        # Coleta de dados - Motocicleta Elétrica
        moto_bateria = float(request.form.get('moto_bateria') or 0)
        moto_motor = float(request.form.get('moto_motor') or 0)
        moto_energia = float(request.form.get('moto_energia') or 0)

        # Busca os fatores científicos diretamente do MySQL
        f_bateria = FatorEmergia.query.filter_by(material_energia="Bateria de Íon-Lítio").first().transformidade
        f_motor = FatorEmergia.query.filter_by(material_energia="Cobre (Motor)").first().transformidade
        f_energia = FatorEmergia.query.filter_by(material_energia="Eletricidade (Rede)").first().transformidade

        # Cálculos de Emergia - Bike (Convertendo massa para gramas se inserido em kg)
        emergia_bike_bat = (bike_bateria * 1000) * f_bateria
        emergia_bike_mot = (bike_motor * 1000) * f_motor
        emergia_bike_eng = bike_energia * f_energia
        total_bike = emergia_bike_bat + emergia_bike_mot + emergia_bike_eng

        # Cálculos de Emergia - Moto
        emergia_moto_bat = (moto_bateria * 1000) * f_bateria
        emergia_moto_mot = (moto_motor * 1000) * f_motor
        emergia_moto_eng = moto_energia * f_energia
        total_moto = emergia_moto_bat + emergia_moto_mot + emergia_moto_eng

        # Organiza os resultados em formato científico/legível
        resultados = {
            'bike': {
                'bateria': f"{emergia_bike_bat:.2e}",
                'motor': f"{emergia_bike_mot:.2e}",
                'energia': f"{emergia_bike_eng:.2e}",
                'total': f"{total_bike:.2e}"
            },
            'moto': {
                'bateria': f"{emergia_moto_bat:.2e}",
                'motor': f"{emergia_moto_mot:.2e}",
                'energia': f"{emergia_moto_eng:.2e}",
                'total': f"{total_moto:.2e}"
            },
            'vantagem': "Bicicleta Elétrica" if total_bike < total_moto else "Motocicleta Elétrica",
            'proporcao': round(total_moto / total_bike if total_bike > 0 else 1, 1)
        }

    return render_template('calculadora.html', resultados=resultados)



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


@app.route('/admin')
def painel_admin():
    #So entra se estiver logado e for admin
    if 'usuario_id' not in session or session.get('perfil') != 'admin':
        #LOG DE VIOLAÇÃO DE ACESSO
        user_tentativa = session.get('nome_usuario', 'Anônimo')
        logging.error(f'ACESSO NEGADO: Usuário "{user_tentativa}" tentou entrar no /admin sem permissão.')
        
        flash('Acesso restrito para administradores!')
        return redirect(url_for('login_page'))

    #Busca todos os utilizadores para listar na tabela
    usuarios = Usuario.query.all()
    return render_template('admin.html', usuarios=usuarios)
    
    #return "<h1>Painel do Administrador</h1><a href='/calculadora'>Voltar</a>"

    
if __name__ == '__main__':
    app.run(debug=True) #APOS FINALIZAÇÃO DO PROJETO MUDE O DEBUG PARA False ##############
