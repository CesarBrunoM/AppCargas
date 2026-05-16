"""
Script de inicialização e seed do banco de dados.
Popula o banco com dados de exemplo para testes.

Uso:
    python init_db.py
"""
import sys
import os
import logging
from datetime import date, timedelta
import random

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    from app.database import init_db, SessionLocal
    from app.models import Carga, StatusCarga
    from app.services import criar_usuario

    logger.info("Inicializando banco de dados...")
    init_db()

    db = SessionLocal()

    try:
        # Criar usuário de demonstração adicional
        criar_usuario(db, "operador", "Operador de Cargas", "op123456")
        logger.info("Usuário 'operador' criado.")

        # Verificar se já existem cargas
        total = db.query(Carga).count()
        if total > 0:
            logger.info(f"Banco já possui {total} cargas. Pulando seed.")
            return

        # Dados de exemplo
        clientes = ["Frutas Brasil Ltda", "Exporta SP", "Norte Frutas", "Sul Agrícola", "Centro-Oeste Exp."]
        carregadores = ["Carlos Silva", "Maria Oliveira", "João Santos", "Ana Costa"]
        motoristas = ["Pedro Souza", "Lucas Lima", "Rafael Mendes", "Thiago Alves", "Bruno Rocha"]
        destinos = ["São Paulo/SP", "Rio de Janeiro/RJ", "Belo Horizonte/MG", "Porto Alegre/RS", "Curitiba/PR"]
        tamanhos = ["Carreta Simples", "Caminhão Truck", "Bitrem", "Carreta Eixo Extendido"]
        placas = ["ABC1234", "DEF5678", "GHI9012", "JKL3456", "MNO7890", "PQR1B23", "STU4C56"]
        status_list = [s.value for s in StatusCarga]

        cargas_exemplo = []
        for i in range(20):
            dias_offset = random.randint(-30, 30)
            data_carga = date.today() + timedelta(days=dias_offset)
            status = random.choice(status_list)

            c = Carga(
                data_carregamento=data_carga,
                cliente=random.choice(clientes),
                carregador=random.choice(carregadores),
                tamanho=random.choice(tamanhos),
                motorista=random.choice(motoristas),
                placa=random.choice(placas),
                destino=random.choice(destinos),
                preco=random.uniform(3000, 25000),
                status=status,
                quantidade_frutas=random.uniform(10000, 50000) if status != StatusCarga.AGENDADO.value else None,
                peso_caminhao=random.uniform(15000, 40000) if status not in [StatusCarga.AGENDADO.value, StatusCarga.EM_CARREGAMENTO.value] else None,
            )
            cargas_exemplo.append(c)

        db.add_all(cargas_exemplo)
        db.commit()
        logger.info(f"✅ {len(cargas_exemplo)} cargas de exemplo criadas com sucesso!")

    except Exception as e:
        db.rollback()
        logger.error(f"Erro: {e}")
    finally:
        db.close()

    logger.info("✅ Banco de dados inicializado com sucesso!")
    logger.info("   Admin: username=admin | senha=admin123")
    logger.info("   Operador: username=operador | senha=op123456")


if __name__ == "__main__":
    main()
