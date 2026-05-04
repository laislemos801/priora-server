from neo4j import GraphDatabase
from contextlib import contextmanager
import os
from dotenv import load_dotenv

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

if not all([NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD]):
    raise ValueError("Variáveis do Neo4j não configuradas corretamente")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

@contextmanager
def get_session():
    session = driver.session(database=NEO4J_DATABASE)
    tx = session.begin_transaction()
    try:
        yield tx
        tx.commit()
    except Exception:
        tx.rollback()
        raise
    finally:
        session.close()

def verify_connection():
    try:
        driver.verify_connectivity()
        print("Neo4j Aura conectado com sucesso")
    except Exception as e:
        print(f"Erro ao conectar no Neo4j Aura: {e}")
        raise