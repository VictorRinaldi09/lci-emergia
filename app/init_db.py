from main import app, db, FatorEmergia

def inicializar_banco_de_dados():
    with app.app_context():
        print("🔨 Estruturando tabelas no MySQL...")
        # Cria todas as tabelas mapeadas (usuarios, fatores_emergia, logs_acesso)
        db.create_all()
        print("✔ Tabelas criadas com sucesso!")

        # Inserindo os fatores científicos iniciais para o comparativo Moto x Bike
        print("🌱 Populado fatores de emergia padrão...")
        
        fatores_iniciais = [
            FatorEmergia(material_energia="Eletricidade (Rede)", transformidade=2.2e5, unidade="j"),
            FatorEmergia(material_energia="Bateria de Íon-Lítio", transformidade=1.8e12, unidade="g"),
            FatorEmergia(material_energia="Cobre (Motor)", transformidade=6.8e11, unidade="g"),
            FatorEmergia(material_energia="Alumínio (Quadro/Componentes)", transformidade=1.6e10, unidade="g"),
            FatorEmergia(material_energia="Aço/Ferro", transformidade=4.2e9, unidade="g")
        ]

        for fator in fatores_iniciais:
            # Evita duplicar se você rodar o script mais de uma vez
            existente = FatorEmergia.query.filter_by(material_energia=fator.material_energia).first()
            if not existente:
                db.session.add(fator)
        
        db.session.commit()
        print("✔ Fatores de emergia inseridos com sucesso!")
        print("\n🚀 Banco de dados pronto para o ambiente de desenvolvimento!")

if __name__ == '__main__':
    inicializar_banco_de_dados()