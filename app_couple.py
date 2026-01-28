import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURATION & STATE MANAGEMENT ---
st.set_page_config(page_title="Alliance & Schémas - Pro", layout="wide")

# Initialisation des variables de session (mémoire de l'application)
if 'step' not in st.session_state:
    st.session_state.step = 1  # 1=Partner A, 2=Partner B, 3=Login Thérapeute, 4=Résultats
if 'data_A' not in st.session_state:
    st.session_state.data_A = {}
if 'data_B' not in st.session_state:
    st.session_state.data_B = {}
if 'infos' not in st.session_state:
    st.session_state.infos = {"date": datetime.now().strftime("%d/%m/%Y")}

# --- 2. BASE DE DONNÉES ENRICHIE (AVEC EXEMPLES CONCRETS) ---
SCHEMA_CONTENT = {
    "Abandon / Instabilité": {
        "clinique": "Peur intense que l'autre parte ou ne soit pas fiable.",
        "theologie": "Difficulté à intégrer la permanence de l'Amour de Dieu.",
        "verite_biblique": "Je ne te délaisserai point (Hébreux 13:5)",
        "conseil_pastoral": "Passer de la 'peur du manque' à la 'confiance en l'Alliance'.",
        "priere": "Seigneur, apaise mon cœur face au silence de l'autre.",
        "exemple_concret": "Quand l'un rentre tard sans prévenir, l'autre panique, appelle 10 fois, puis fait une crise de colère (attaque) ou s'effondre (soumission) au retour."
    },
    "Carence Affective": {
        "clinique": "Sentiment que ses besoins de soutien et d'affection ne seront jamais comblés.",
        "theologie": "Croyance mensongère d'être invisible aux yeux du Père.",
        "verite_biblique": "D'un amour éternel, je t'ai aimé (Jérémie 31:3)",
        "conseil_pastoral": "Oser la vulnérabilité : 'Demandez et l'on vous donnera'.",
        "priere": "Seigneur, donne-moi le courage de dire mes besoins sans accuser.",
        "exemple_concret": "L'un soupire bruyamment en espérant que l'autre demande 'qu'est-ce qui ne va pas ?'. Si l'autre ne réagit pas, il se sent rejeté et devient froid."
    },
    "Sacrifice de Soi": {
        "clinique": "Se concentrer excessivement sur les besoins des autres (Syndrome du sauveur).",
        "theologie": "Confusion entre 'aimer son prochain' et 'se nier par peur'.",
        "verite_biblique": "Tu aimeras ton prochain comme toi-même (Marc 12:31)",
        "conseil_pastoral": "Le service chrétien est un choix libre, pas une dette.",
        "priere": "Seigneur, aide-moi à discerner quand je sers par amour ou par peur.",
        "exemple_concret": "L'un accepte toutes les invitations et corvées pour 'faire plaisir' au couple, jusqu'à l'épuisement, puis explose en reprochant à l'autre son égoïsme."
    },
    "Contrôle / Perfectionnisme": {
        "clinique": "Besoin de tout maîtriser, difficulté à déléguer, rigidité.",
        "theologie": "Idolâtrie de la performance, manque de confiance en la Providence.",
        "verite_biblique": "C'est en vain que vous vous levez matin... (Psaume 127:2)",
        "conseil_pastoral": "Acceptez l'imperfection de votre conjoint comme une école de grâce.",
        "priere": "Seigneur, délivre-moi de l'orgueil de croire que tout dépend de moi.",
        "exemple_concret": "L'un repasse derrière l'autre pour corriger la façon dont le lave-vaisselle est rempli ou critique la manière d'habiller les enfants."
    },
    "Méfiance / Abus": {
        "clinique": "S'attendre à ce que l'autre nous blesse ou nous manipule.",
        "theologie": "Blessure empêchant de voir Dieu comme Protecteur.",
        "verite_biblique": "L'amour parfait bannit la crainte (1 Jean 4:18)",
        "conseil_pastoral": "Ne pas interpréter chaque erreur comme une malveillance.",
        "priere": "Seigneur, guéris ma mémoire pour voir mon conjoint tel qu'il est.",
        "exemple_concret": "Si l'un fait une remarque neutre, l'autre l'interprète immédiatement comme une attaque cachée ou une humiliation et contre-attaque violemment."
    }
}

schemas_list = list(SCHEMA_CONTENT.keys())

# --- 3. FONCTIONS UTILITAIRES ---

def reset_app():
    st.session_state.step = 1
    st.session_state.data_A = {}
    st.session_state.data_B = {}
    st.rerun()

def convert_df(df):
    return df.to_csv(index=False).encode('utf-8')

# --- 4. LOGIQUE DE L'APPLICATION (WORKFLOW) ---

st.sidebar.title("Navigation Clinique")
if st.sidebar.button("🔄 Nouvelle Session (Reset)"):
    reset_app()

# --- ÉTAPE 1 : PARTENAIRE A ---
if st.session_state.step == 1:
    st.header("👤 Étape 1 : Premier Partenaire")
    st.info("Merci de remplir ce questionnaire seul(e), sans consulter votre conjoint(e).")
    
    with st.form("form_A"):
        nom_A = st.text_input("Votre Prénom")
        reponses_A = {}
        st.write("---")
        for schema in schemas_list:
            reponses_A[schema] = st.slider(f"Dans quelle mesure cela vous correspond ? ({schema})", 1, 6, 1)
        
        submitted_A = st.form_submit_button("Valider et Passer au Partenaire Suivant")
        
        if submitted_A and nom_A:
            st.session_state.data_A = reponses_A
            st.session_state.infos['nom_A'] = nom_A
            st.session_state.step = 2
            st.rerun()

# --- ÉTAPE 2 : PARTENAIRE B ---
elif st.session_state.step == 2:
    st.header("👤 Étape 2 : Second Partenaire")
    st.warning("Assurez-vous que le premier partenaire ne regarde pas l'écran.")
    
    with st.form("form_B"):
        nom_B = st.text_input("Votre Prénom")
        reponses_B = {}
        st.write("---")
        for schema in schemas_list:
            reponses_B[schema] = st.slider(f"Dans quelle mesure cela vous correspond ? ({schema})", 1, 6, 1)
        
        submitted_B = st.form_submit_button("Valider et Verrouiller les Réponses")
        
        if submitted_B and nom_B:
            st.session_state.data_B = reponses_B
            st.session_state.infos['nom_B'] = nom_B
            st.session_state.step = 3
            st.rerun()

# --- ÉTAPE 3 : ACCÈS THÉRAPEUTE ---
elif st.session_state.step == 3:
    st.header("🔒 Accès Réservé au Thérapeute")
    st.info("Les questionnaires sont terminés. Veuillez saisir le code pour générer l'analyse.")
    
    password = st.text_input("Code d'accès", type="password")
    
    if st.button("Générer le Rapport"):
        if password == "1234":  # Code simple pour l'exemple, à changer
            st.session_state.step = 4
            st.rerun()
        else:
            st.error("Code incorrect")

# --- ÉTAPE 4 : RÉSULTATS & DOSSIER ---
elif st.session_state.step == 4:
    st.success("✅ Analyse générée avec succès")
    
    nom_A = st.session_state.infos['nom_A']
    nom_B = st.session_state.infos['nom_B']
    
    # --- ZONE DE TÉLÉCHARGEMENT (DOSSIER THÉRAPEUTE) ---
    with st.expander("📂 ESPACE DOSSIER (Téléchargements)", expanded=True):
        col_dl1, col_dl2 = st.columns(2)
        
        # Création des DataFrames pour export
        df_A = pd.DataFrame([st.session_state.data_A])
        df_A['Nom'] = nom_A
        df_B = pd.DataFrame([st.session_state.data_B])
        df_B['Nom'] = nom_B
        
        with col_dl1:
            st.download_button(
                label=f"📥 Télécharger Réponses de {nom_A} (CSV)",
                data=convert_df(df_A),
                file_name=f"Resultats_{nom_A}.csv",
                mime='text/csv',
            )
        with col_dl2:
            st.download_button(
                label=f"📥 Télécharger Réponses de {nom_B} (CSV)",
                data=convert_df(df_B),
                file_name=f"Resultats_{nom_B}.csv",
                mime='text/csv',
            )
        st.caption("Ces fichiers peuvent être archivés dans votre dossier patient sécurisé.")

    st.divider()

    # --- LE RAPPORT VISUEL (A IMPRIMER EN PDF) ---
    st.title(f"Rapport d'Alliance : {nom_A} & {nom_B}")
    st.write(f"Date de l'évaluation : {st.session_state.infos['date']}")
    
    # 1. RADAR CHART
    st.subheader("1. La Dynamique des Schémas")
    values_A = list(st.session_state.data_A.values())
    values_B = list(st.session_state.data_B.values())
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values_A, theta=schemas_list, fill='toself', name=nom_A, line=dict(color='blue')))
    fig.add_trace(go.Scatterpolar(r=values_B, theta=schemas_list, fill='toself', name=nom_B, line=dict(color='orange')))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 6])), showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # 2. ANALYSE DÉTAILLÉE
    st.subheader("2. Analyse Clinique, Pastorale & Concrète")
    
    seuil_critique = 4
    schemas_actifs = []
    for s in schemas_list:
        if st.session_state.data_A[s] >= seuil_critique or st.session_state.data_B[s] >= seuil_critique:
            schemas_actifs.append(s)
            
    if not schemas_actifs:
        st.info("Aucun schéma critique majeur détecté. Le couple semble avoir de bonnes ressources.")
    
    for s in schemas_actifs:
        content = SCHEMA_CONTENT[s]
        score_A = st.session_state.data_A[s]
        score_B = st.session_state.data_B[s]
        
        # Déterminer qui porte le schéma
        qui = []
        if score_A >= seuil_critique: qui.append(f"{nom_A} (Score: {score_A})")
        if score_B >= seuil_critique: qui.append(f"{nom_B} (Score: {score_B})")
        titre_qui = " et ".join(qui)
        
        st.markdown(f"### 🔴 {s.upper()}")
        st.markdown(f"**Activé chez :** {titre_qui}")
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🧠 Comprendre")
            st.write(f"**Mécanisme :** {content['clinique']}")
            st.info(f"👉 **Exemple Concret dans le couple :**\n{content['exemple_concret']}")
            
        with c2:
            st.markdown("#### 🕊️ Guérir & Grandir")
            st.write(f"**Racine Spirituelle :** {content['theologie']}")
            st.success(f"💡 **Piste Pastorale :** {content['conseil_pastoral']}")
            st.markdown(f"📖 *{content['verite_biblique']}*")
        
        st.markdown("---")
        
    st.info("💡 Pour sauvegarder ce rapport : Faites un clic droit sur la page > 'Imprimer' > 'Enregistrer au format PDF'.")
