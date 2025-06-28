import streamlit as st
import json
from app.recommender import process_application, process_batch
from app.utils import extract_text_from_pdf
from app.db import create_table, save_result
create_table() 

st.set_page_config(page_title="Recrutement Intelligent", layout="wide")

st.title("Système de Recrutement Intelligent")
st.markdown("Analyse automatique des CVs en fonction d'une offre d'emploi.")

# Partie gauche : description du poste
with st.sidebar:
    st.header("Description de l'offre")
    offer_text = st.text_area("Contenu de l'offre d'emploi", height=250)
    job_level = st.selectbox("Niveau du poste", ["Stage", "Junior", "Confirmé", "Senior"])
    sector = st.text_area("Secteur d'activité", height=80)

st.subheader("Analyse d’un seul CV")

cv_input_type = st.radio(
    "Quel est le format du CV ?",
    ["PDF", "Texte brut"],
    horizontal=True,
    key="cv_input_type"
)

final_cv_text = ""

if cv_input_type == "PDF":
    uploaded_pdf = st.file_uploader("Uploader le fichier PDF du CV", type=["pdf"])
    if uploaded_pdf:
        final_cv_text = extract_text_from_pdf(uploaded_pdf)
        st.success("Texte extrait avec succès.")
        st.text_area("Texte extrait du CV (modifiable si besoin)", final_cv_text, height=200)
        if st.button("Analyser ce CV"):
            if offer_text and final_cv_text:
                result = process_application(final_cv_text, offer_text, job_level, sector)
                st.json(result)
                # Après analyse
                save_result(result)
                #Téléchargement sf JSON
                json_result = json.dumps(result, ensure_ascii=False, indent=2)
                st.download_button(
                    label="Télécharger le résultat",
                    data=json_result,
                    file_name="resultat_analyse_cv.json",
                    mime="application/json"
                )
            else:
                st.warning("Veillez à bien remplir l’offre et le CV.")
else:
    cv_text = st.text_area("Texte brut du CV à analyser", height=200)
    if st.button("Analyser ce CV"):
        if offer_text and cv_text:
            result = process_application(cv_text, offer_text, job_level, sector)
            st.json(result)
            # Après analyse
            save_result(result)
            #Téléchargement sf JSON
            json_result = json.dumps(result, ensure_ascii=False, indent=2)
            st.download_button(
                label="Télécharger le résultat",
                data=json_result,
                file_name="resultat_analyse_cv.json",
                mime="application/json"
            )
        else:
            st.warning("Bien remplir l’offre et le CV.")



st.markdown("---")

st.subheader("Analyse par lot de CVs")

batch_input_type = st.radio(
    "Format des CVs pour le traitement par lot :",
    ["PDF (plusieurs fichiers)", "Fichier texte brut (1 CV par ligne)"],
    horizontal=True,
    key="batch_input_type"
)

# === PDF MULTIPLES ===
if batch_input_type == "PDF (plusieurs fichiers)":
    uploaded_pdfs = st.file_uploader("Uploader plusieurs fichiers PDF", type=["pdf"], accept_multiple_files=True)
    if uploaded_pdfs:
        all_cv_texts = [extract_text_from_pdf(pdf) for pdf in uploaded_pdfs]
        st.success("Texte extrait avec succès.")
        st.text_area("Texte extrait des CV", "\n\n---\n\n".join(all_cv_texts), height=400)  # affichage propre

        if st.button("Analyser le lot de CVs"):
            batch_results = process_batch(all_cv_texts, offer_text, job_level, sector)
            st.success(f"{len(batch_results)} CVs analysés.")
            
            for i, res in enumerate(batch_results, 1):
                with st.expander(f"CV PDF #{i}"):
                    st.json(res)

            # Sauvegarde en base : un par un
            for result in batch_results:
                save_result(result)

            # Téléchargement groupé JSON
            json_result = json.dumps(batch_results, ensure_ascii=False, indent=2)
            st.download_button(
                label="Télécharger tous les résultats",
                data=json_result,
                file_name="resultats_analyse_batch.json",
                mime="application/json"
            )

# === TEXTE MULTIPLE ===
else:
    uploaded_txt = st.file_uploader("Uploader un fichier texte brut contenant plusieurs CVs (1 par ligne)", type=["txt"])
    if uploaded_txt and st.button("Analyser le fichier texte"):
        content = uploaded_txt.read().decode("utf-8")
        cvs = [line.strip() for line in content.strip().split("\n") if line.strip()]

        batch_results = process_batch(cvs, offer_text, job_level, sector)
        st.success(f"{len(batch_results)} CVs analysés.")

        for i, res in enumerate(batch_results, 1):
            with st.expander(f"CV texte #{i}"):
                st.json(res)

        # Sauvegarde en base : un par un
        for result in batch_results:
            save_result(result)

        # Téléchargement JSON
        json_result = json.dumps(batch_results, ensure_ascii=False, indent=2)
        st.download_button(
            label="Télécharger tous les résultats",
            data=json_result,
            file_name="resultats_analyse_batch.json",
            mime="application/json"
        )
