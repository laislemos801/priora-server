from fastapi import APIRouter
from app.services.investigation_service import rank_suspects

router = APIRouter()

@router.post("/rank")
def rank(evidence: dict):
    return rank_suspects(evidence)

@router.get("/test-neo4j")
def test_neo4j():
    from app.database.neo4j import get_session

    with get_session() as tx:
        result = tx.run("RETURN 'Neo4j funcionando 🚀' AS message")
        return {"result": result.single()["message"]}