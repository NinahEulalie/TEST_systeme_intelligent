from sentence_transformers import SentenceTransformer, util
import numpy as np
import re
import json

# Chargement du modèle
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# Calcul du score de similarité
def compute_matching_score(cv_text, offer_text):
    embeddings = model.encode([cv_text, offer_text], convert_to_tensor=True)
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    return round(score, 4)

# Catégorisation du texte
    # METHODE 1 : CLASSIFICATION DIRECTE
# def classify_section(text):
#     sections = {
#         "expérience": ["stage", "expérience", "projet", "CDI", "CDD", "alternance", "travail", "freelance"],
#         "formation": ["licence", "master", "diplôme", "bac", "université", "école", "doctorat", "professeur", "formation"],
#         "compétences": ["langage", "outil", "framework", "Python", "Excel", "compétences", "maîtrise", "senior", "confirmé", "junio", "débutant"],
#         "langues": ["anglais", "français", "espagnol", "langues parlées", "TOEIC", "DALF", "langues", "connaissances linguistiques"]
#     }
#     for label, keywords in sections.items():
#         if any(word.lower() in text.lower() for word in keywords):
#             return label
#     return "autre"

    # METHODE 2 : EMBEDDINGS ET SIMILARITE
# Textes représentatifs de chaque section
category_examples = {
    "formation": "J'ai obtenu ou je suis titulaire un master ou une licence ou un doctorat ou un PhD dans une université ou une école.",
    "expérience": "J'ai travaillé dans une entreprise sur des projets en CDI ou en CDD ou en stage ou en freelance.",
    "compétences": "Je maîtrise des outils ou des langages comme Python, Excel, Docker, etc.",
    "langues": "Je parle plusieurs langues comme le français, l'anglais ou l'espagnol.",
}

# Embeddings pré-calculés pour chaque catégorie
category_embeddings = {
    label: model.encode(text) for label, text in category_examples.items()
}

def classify_section(text):
    text_embedding = model.encode(text)
    similarities = {
        label: util.cos_sim(text_embedding, cat_embedding).item()
        for label, cat_embedding in category_embeddings.items()
    }
    best_label = max(similarities, key=similarities.get)
    return best_label


# Recommandation RH
def recommend_action(score):
    if score > 0.75:
        return "À contacter"
    elif score > 0.5:
        return "À évaluer manuellement"
    else:
        return "À rejeter"

# Extraction du nom sur chaque CV
def extract_name(cv_text):
    lines = cv_text.splitlines()
    for line in lines[:20]:  # Examiner les 20 premières lignes
        cleaned = line.strip()

        # Filtrer les lignes trop courtes ou contenant des infos non pertinentes
        if len(cleaned) < 3:
            continue
        if any(keyword in cleaned.lower() for keyword in ["email", "@", "téléphone", "adresse", "linkedin", "www.", "contact", "permis"]):
            continue

        # Cas 1 : ligne avec deux mots, tous majuscules ou type Nom Prénom
        if re.match(r"^([A-Z][a-zà-ÿA-Z\-']{1,})\s+([A-Z][a-zà-ÿA-Z\-']{1,})$", cleaned):
            return cleaned

        # Cas 2 : ligne entièrement en majuscules avec 2-3 mots (ex: MARIE NORET)
        if re.match(r"^([A-ZÉÈÂÊÎÔÛÄËÏÖÜ]{2,}\s+){1,3}$", cleaned):
            return cleaned.title()

    return "Nom impossible à détecter"

# Fonction principale de traitement
def process_application(cv_text, offer_text, job_level, sector):
    score = compute_matching_score(cv_text, offer_text)
    label = classify_section(cv_text)
    rec = recommend_action(score)
    nom = extract_name(cv_text)

    result = {
        "nom": nom,
        "matching_score": score,
        "label_section": label,
        "recommendation": rec,
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
