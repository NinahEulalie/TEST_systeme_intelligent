import streamlit as st
from app.recommender import process_application, process_batch

st.set_page_config(page_title="Recrutement Intelligent", layout="wide")

st.title("Système de Recrutement Intelligent")
st.markdown("Analyse automatique des CVs en fonction d'une offre d'emploi.")

# Partie gauche : description du poste
with st.sidebar:
    st.header("Description de l'offre")
    offer_text = st.text_area("Contenu de l'offre d'emploi", height=250)
    job_level = st.selectbox("Niveau du poste", ["Stage", "Junior", "Confirmé", "Senior"])
    sector = st.selectbox("Secteur d'activité", ["IT", "Finance", "Marketing", "Autre"])

st.subheader("Analyse d’un seul CV")

cv_text = st.text_area("Texte brut du CV du candidat", height=200)

if st.button("Analyser ce CV"):
    if offer_text and cv_text:
        result = process_application(cv_text, offer_text, job_level, sector)
        st.success("Analyse terminée")
        st.json(result)
    else:
        st.warning("Veuillez remplir à la fois le texte du CV et l'offre d'emploi.")

st.markdown("---")

st.subheader("Analyse par lot de CVs")

uploaded_file = st.file_uploader("Importer un fichier texte contenant plusieurs CVs (1 par ligne)", type=["txt"])

if uploaded_file is not None:
    content = uploaded_file.read().decode("utf-8")
    cvs = [line.strip() for line in content.strip().split("\n") if line.strip()]

    if st.button("Analyser tous les CVs"):
        if offer_text and cvs:
            batch_results = process_batch(cvs, offer_text, job_level, sector)
            st.success(f"{len(batch_results)} CVs analysés.")
            for idx, res in enumerate(batch_results, 1):
                with st.expander(f"CV #{idx}"):
                    st.json(res)
        else:
            st.warning("Veuillez remplir la description de l’offre.")
