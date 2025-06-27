from sentence_transformers import SentenceTransformer, util
import numpy as np
import datetime
import json

# Chargement du modèle
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Calcul du score de similarité
def compute_matching_score(cv_text, offer_text):
    embeddings = model.encode([cv_text, offer_text], convert_to_tensor=True)
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    return round(score, 4)

# Catégorisation du texte
def classify_section(text):
    sections = {
        "expérience": ["stage", "expérience", "projet", "CDI", "CDD", "alternance", "travail", "freelance"],
        "formation": ["licence", "master", "diplôme", "bac", "université", "école"],
        "compétences": ["langage", "outil", "framework", "Python", "Excel", "compétences", "maîtrise"],
        "langues": ["anglais", "français", "espagnol", "langues parlées", "TOEIC", "DALF"]
    }
    for label, keywords in sections.items():
        if any(word.lower() in text.lower() for word in keywords):
            return label
    return "autre"

# Recommandation RH
def recommend_action(score):
    if score > 0.75:
        return "À contacter"
    elif score > 0.5:
        return "À évaluer manuellement"
    else:
        return "À rejeter"

# Fonction principale de traitement
def process_application(cv_text, offer_text, job_level, sector):
    score = compute_matching_score(cv_text, offer_text)
    label = classify_section(cv_text)
    rec = recommend_action(score)

    result = {
        "matching_score": score,
        "label_section": label,
        "recommendation": rec,
        "job_level": job_level,
        "sector": sector,
        "timestamp": datetime.datetime.now().isoformat()
    }
    return result

# Traitement par lot de CVs
def process_batch(cvs_list, offer_text, job_level, sector):
    return [
        process_application(cv, offer_text, job_level, sector) for cv in cvs_list
    ]

# Sauvegarder les résultats dans un fichier JSONL
def save_result(result, filename="results.jsonl"):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
