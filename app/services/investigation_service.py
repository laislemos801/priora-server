from app.bayes.model import calculate_probabilities

def rank_suspects(evidence: dict):
    return calculate_probabilities(evidence)