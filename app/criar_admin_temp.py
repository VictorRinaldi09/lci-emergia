from main import app, db, Usuario, bcrypt

def criar_primeiro_admin():
    with app.app_context():
        #verificação se ha um admin ja
        existente = Usuario.query.filter_by(email="admin@emergia.com").first()
        if existente:
            print('Usuário admin já existe!')
            return
        
        senha_plana = 'unip123'
        hash_senha = bcrypt.generate_password_hash(senha_plana).decode('utf-8')

        novo_admin = Usuario(
            nome='Administrador APS',
            email='admin@emergia.com',
            senha_hash=hash_senha,
            perfil='admin'
        )

        db.session.add(novo_admin)
        db.session.commit()
        print('✔ Usuário Admin criado com sucesso!')
        print(f'Hash gerado: {hash_senha}')

if __name__ == '__main__':
    criar_primeiro_admin()