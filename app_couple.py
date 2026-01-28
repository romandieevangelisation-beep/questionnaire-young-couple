import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# --- 1. BASE DE DONNÉES : CLINIQUE & THÉOLOGIQUE ---
# C'est ici que nous définissons le "Cerveau" du logiciel.
# Pour l'exemple, j'ai mis 5 schémas fréquents en couple.

SCHEMA_CONTENT = {
    "Abandon / Instabilité": {
        "clinique": "Peur intense que l'autre parte ou ne soit pas fiable. Crée de la jalousie et de l'agrippement.",
        "theologie": "Une difficulté à intégrer la permanence de l'Amour de Dieu.",
        "verite_biblique": "« Je ne te délaisserai point, je ne t'abandonnerai point. » (Hébreux 13:5)",
        "conseil_pastoral": "Le défi spirituel est de passer de la 'peur du manque' à la 'confiance en l'Alliance'. En couple, rappelez-vous que votre conjoint est humain et limité, il ne peut pas combler le vide infini que seul Dieu peut remplir.",
        "priere": "Seigneur, apaise mon cœur. Aide-moi à ne pas demander à mon conjoint d'être mon 'dieu' de sécurité."
    },
    "Carence Affective": {
        "clinique": "Sentiment que ses besoins de soutien et d'affection ne seront jamais comblés.",
        "theologie": "Croyance mensongère d'être invisible aux yeux du Père.",
        "verite_biblique": "« D'un amour éternel, je t'ai aimé. » (Jérémie 31:3)",
        "conseil_pastoral": "Vous avez tendance à attendre que l'autre devine vos besoins, puis à lui en vouloir. L'invitation chrétienne est d'oser la vulnérabilité : 'Demandez et l'on vous donnera'. Exprimez vos besoins sans accuser.",
        "priere": "Seigneur, donne-moi le courage de dire 'j'ai besoin d'un câlin' ou 'j'ai besoin d'être écouté' sans colère."
    },
    "Sacrifice de Soi": {
        "clinique": "Se concentrer excessivement sur les besoins des autres au détriment des siens (syndrome du sauveur).",
        "theologie": "Confusion entre 'aimer son prochain' et 'se nier soi-même par peur du rejet'.",
        "verite_biblique": "« Tu aimeras ton prochain comme toi-même. » (Marc 12:31)",
        "conseil_pastoral": "Le véritable service chrétien est un choix libre, pas une compulsion née de la culpabilité. Si vous vous épuisez, vous ne pouvez plus aimer. Apprenez à dire 'non' pour que vos 'oui' soient vrais.",
        "priere": "Seigneur, aide-moi à discerner quand je sers par amour et quand je sers par peur de ne plus être aimé."
    },
    "Contrôle / Perfectionnisme": {
        "clinique": "Besoin de tout maîtriser, difficulté à déléguer, rigidité.",
        "theologie": "Une forme d'idolâtrie de sa propre performance et un manque de confiance en la Providence.",
        "verite_biblique": "« C'est en vain que vous vous levez matin, que vous vous couchez tard... il en donne autant à ses bien-aimés pendant leur sommeil. » (Psaume 127:2)",
        "conseil_pastoral": "En couple, cela se traduit par la critique. L'invitation est de lâcher prise. Acceptez l'imperfection de votre conjoint comme une école de grâce.",
        "priere": "Seigneur, délivre-moi de l'orgueil de croire que tout dépend de moi."
    },
    "Méfiance / Abus": {
        "clinique": "S'attendre à ce que l'autre nous blesse, nous manipule ou nous humilie.",
        "theologie": "Une blessure profonde qui empêche de voir Dieu comme un Père protecteur.",
        "verite_biblique": "« L'amour parfait bannit la crainte. » (1 Jean 4:18)",
        "conseil_pastoral": "Ce schéma verrouille le cœur. La guérison passe par le pardon progressif. En couple, essayez de ne pas interpréter chaque erreur de l'autre comme une intention de nuire.",
        "priere": "Seigneur, guéris ma mémoire pour que je puisse voir mon conjoint tel qu'il est aujourd'hui, et non à travers le filtre de mes blessures passées."
    }
}

# --- 2. INTERFACE UTILISATEUR ---

st.set_page_config(page_title="Alliance & Schémas", layout="wide")

st.title("💖 Alliance & Schémas : Analyse Systémique")
st.markdown("""
Cet outil analyse la dynamique de votre couple sous un angle **psychologique** (Schémas de Young) 
et **spirituel** (Pistes pastorales).
""")

# Simulation des entrées (dans la version finale, ce sera le questionnaire complet)
st.subheader("1. Évaluation Rapide des Profils")
col1, col2 = st.columns(2)

schemas_list = list(SCHEMA_CONTENT.keys())
scores_A = {}
scores_B = {}

with col1:
    st.info("👤 Partenaire A")
    nom_A = st.text_input("Prénom Partenaire A", "Jean")
    for schema in schemas_list:
        scores_A[schema] = st.slider(f"{schema} (A)", 1, 6, 3, key=f"A_{schema}")

with col2:
    st.info("👤 Partenaire B")
    nom_B = st.text_input("Prénom Partenaire B", "Marie")
    for schema in schemas_list:
        scores_B[schema] = st.slider(f"{schema} (B)", 1, 6, 3, key=f"B_{schema}")

# --- 3. VISUALISATION (Le Radar Comparatif) ---

st.divider()
st.subheader("2. La 'Chimie' de votre Couple")

categories = schemas_list
values_A = list(scores_A.values())
values_B = list(scores_B.values())

fig = go.Figure()

fig.add_trace(go.Scatterpolar(
    r=values_A,
    theta=categories,
    fill='toself',
    name=nom_A,
    line=dict(color='blue')
))

fig.add_trace(go.Scatterpolar(
    r=values_B,
    theta=categories,
    fill='toself',
    name=nom_B,
    line=dict(color='orange')
))

fig.update_layout(
    polar=dict(
        radialaxis=dict(
            visible=True,
            range=[0, 6]
        )),
    showlegend=True
)

st.plotly_chart(fig, use_container_width=True)

# --- 4. GÉNÉRATION DU RAPPORT PASTORAL ---

st.divider()
st.subheader("3. Pistes Cliniques & Pastorales")

# Fonction pour détecter les zones critiques
seuil_critique = 4  # Score à partir duquel on considère le schéma activé

# On cherche les schémas élevés chez A ou B
schemas_actifs = []
for s in schemas_list:
    if scores_A[s] >= seuil_critique or scores_B[s] >= seuil_critique:
        schemas_actifs.append(s)

if not schemas_actifs:
    st.success("Aucun schéma majeur détecté avec ces scores simulés. Tout semble équilibré !")
else:
    for s in schemas_actifs:
        content = SCHEMA_CONTENT[s]
        
        # Titre dynamique
        qui_est_touche = []
        if scores_A[s] >= seuil_critique: qui_est_touche.append(nom_A)
        if scores_B[s] >= seuil_critique: qui_est_touche.append(nom_B)
        acteurs = " et ".join(qui_est_touche)
        
        with st.expander(f"🔴 Zone de Vigilance : {s.upper()} ({acteurs})", expanded=True):
            col_clin, col_theo = st.columns(2)
            
            with col_clin:
                st.markdown("#### 🧠 Dimension Clinique")
                st.write(f"**Le mécanisme :** {content['clinique']}")
                st.write(f"**Impact Couple :** Si ce score est élevé, il y a un risque que ce partenaire perçoive la relation à travers ce filtre déformant, réagissant de manière disproportionnée à des déclencheurs neutres.")
            
            with col_theo:
                st.markdown("#### 🕊️ Dimension Pastorale")
                st.write(f"**Racine Spirituelle :** {content['theologie']}")
                st.info(f"💡 **Conseil :** {content['conseil_pastoral']}")
                st.markdown(f"**📖 Vérité à méditer :** *{content['verite_biblique']}*")
                st.markdown(f"**🙏 Piste de prière :** *{content['priere']}*")

# --- 5. INTERACTION SYSTÉMIQUE (Bonus) ---
# Détection simple d'une collision classique
if scores_A["Abandon / Instabilité"] >= 4 and scores_B["Contrôle / Perfectionnisme"] >= 4:
    st.error(f"⚠️ **COLLISION DÉTECTÉE :** Le schéma d'Abandon de {nom_A} risque d'être activé par la froideur ou la rigidité du schéma de Contrôle de {nom_B}. {nom_B} essaie de 'gérer' la situation, ce que {nom_A} ressent comme un éloignement.")
