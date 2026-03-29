from neo4j import GraphDatabase

URI = "bolt://localhost:7687"
USER = "neo4j"
PASSWORD = "test123"

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

def get_session():
    return driver.session()