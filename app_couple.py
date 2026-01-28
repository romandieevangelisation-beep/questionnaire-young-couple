import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import os

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="Alliance Couple - Pro", layout="wide", page_icon="❤️")
DB_FILE = "reponses_couple.csv"

# --- 2. BASE DE DONNÉES CONTENU (PSYCHO & SPIRITUEL) ---
SCHEMA_CONTENT = {
    "Abandon / Instabilité": {
        "clinique": "Peur intense que l'autre parte ou ne soit pas fiable.",
        "theologie": "Difficulté à intégrer la permanence de l'Amour de Dieu.",
        "conseil": "Passer de la 'peur du manque' à la 'confiance en l'Alliance'.",
        "biblique": "Je ne te délaisserai point (Hébreux 13:5)",
        "exemple": "Quand l'un rentre tard, l'autre panique et harcèle ou s'effondre."
    },
    "Carence Affective": {
        "clinique": "Sentiment que ses besoins d'affection ne seront jamais comblés.",
        "theologie": "Croyance mensongère d'être invisible aux yeux du Père.",
        "conseil": "Oser la vulnérabilité : 'Demandez et l'on vous donnera'.",
        "biblique": "D'un amour éternel, je t'ai aimé (Jérémie 31:3)",
        "exemple": "Soupire en espérant que l'autre devine, puis devient froid par déception."
    },
    "Sacrifice de Soi": {
        "clinique": "Se concentrer excessivement sur les besoins des autres (Sauveur).",
        "theologie": "Confusion entre 'aimer son prochain' et 'se nier par peur'.",
        "conseil": "Le service chrétien est un choix libre, pas une dette.",
        "biblique": "Tu aimeras ton prochain comme toi-même (Marc 12:31)",
        "exemple": "Accepte tout jusqu'à l'épuisement, puis explose de colère."
    },
    "Contrôle / Perfectionnisme": {
        "clinique": "Besoin de tout maîtriser, rigidité, critique.",
        "theologie": "Idolâtrie de la performance, manque de confiance en la Providence.",
        "conseil": "Acceptez l'imperfection de l'autre comme une école de grâce.",
        "biblique": "C'est en vain que vous vous levez matin... (Psaume 127:2)",
        "exemple": "Repasse derrière l'autre pour corriger ou critique sa façon de faire."
    },
    "Méfiance / Abus": {
        "clinique": "S'attendre à ce que l'autre nous blesse ou nous manipule.",
        "theologie": "Blessure empêchant de voir Dieu comme Protecteur.",
        "conseil": "Ne pas interpréter chaque erreur comme une malveillance.",
        "biblique": "L'amour parfait bannit la crainte (1 Jean 4:18)",
        "exemple": "Interprète une remarque neutre comme une attaque et contre-attaque."
    }
}
SCHEMAS_LIST = list(SCHEMA_CONTENT.keys())

# --- 3. GESTION DES DONNÉES (CSV) ---
def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    else:
        return pd.DataFrame(columns=["Code_Couple", "Nom", "Date", "Role"] + SCHEMAS_LIST)

def save_response(code, nom, responses):
    df = load_data()
    # Vérifier si ce nom existe déjà pour ce code (mise à jour)
    mask = (df['Code_Couple'] == code) & (df['Nom'] == nom)
    
    new_row = {
        "Code_Couple": code,
        "Nom": nom,
        "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "Role": "Partenaire" # On pourrait définir A ou B, mais ici on laisse flexible
    }
    new_row.update(responses)
    
    if not df[mask].empty:
        # Update existing
        for key, val in new_row.items():
            df.loc[mask, key] = val
    else:
        # Add new
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    df.to_csv(DB_FILE, index=False)

# --- 4. GÉNÉRATION PDF ---
class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Alliance & Schémas - Rapport de Couple', 0, 1, 'C')
        self.ln(5)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(0, 10, title, 0, 1, 'L', 1)
        self.ln(4)

    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 6, body)
        self.ln()

def generate_pdf(nom_A, data_A, nom_B, data_B):
    pdf = PDFReport()
    pdf.add_page()
    
    # Intro
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Couple : {nom_A} & {nom_B}", 0, 1)
    pdf.cell(0, 10, f"Date du rapport : {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.ln(10)
    
    # Analyse des Schémas Critiques
    pdf.chapter_title("Analyse des Schémas Actifs (Score >= 4)")
    
    schemas_actifs = False
    for s in SCHEMAS_LIST:
        score_A = data_A[s]
        score_B = data_B[s]
        
        if score_A >= 4 or score_B >= 4:
            schemas_actifs = True
            qui = []
            if score_A >= 4: qui.append(f"{nom_A} ({score_A}/6)")
            if score_B >= 4: qui.append(f"{nom_B} ({score_B}/6)")
            acteurs = " et ".join(qui)
            
            content = SCHEMA_CONTENT[s]
            
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 10, f"{s.upper()} - Détecté chez : {acteurs}", 0, 1)
            
            pdf.set_font('Arial', 'I', 10)
            pdf.multi_cell(0, 5, f"Exemple concret : {content['exemple']}")
            pdf.ln(2)
            
            pdf.set_font('Arial', '', 10)
            txt = (f"Clinique : {content['clinique']}\n"
                   f"Racine Spirituelle : {content['theologie']}\n"
                   f"Conseil Pastoral : {content['conseil']}\n"
                   f"Verset : {content['biblique']}")
            
            pdf.multi_cell(0, 6, txt)
            pdf.ln(5)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(5)

    if not schemas_actifs:
        pdf.chapter_body("Aucun schéma critique majeur détecté. Le couple semble avoir de bonnes ressources.")
        
    return pdf.output(dest='S').encode('latin-1', 'replace') # Retourne les bytes du PDF

# --- 5. INTERFACE UTILISATEUR ---

st.sidebar.title("Navigation")
mode = st.sidebar.radio("Accès", ["👥 Espace Patient", "🔒 Espace Thérapeute"])

# === MODE PATIENT ===
if mode == "👥 Espace Patient":
    st.title("Questionnaire des Schémas")
    st.markdown("Veuillez entrer le **Code Couple** fourni par votre accompagnant.")
    
    with st.form("login_patient"):
        code_couple = st.text_input("Code Couple (ex: DUPONT24)").strip().upper()
        nom_patient = st.text_input("Votre Prénom")
        
        submitted_login = st.form_submit_button("Commencer le questionnaire")
    
    if code_couple and nom_patient:
        st.divider()
        st.subheader(f"Bonjour {nom_patient}")
        st.info("Répondez spontanément. Il n'y a pas de bonne ou mauvaise réponse.")
        
        with st.form("questionnaire"):
            reponses = {}
            for schema in SCHEMAS_LIST:
                reponses[schema] = st.slider(f"{schema}", 1, 6, 1, key=schema)
            
            valid_final = st.form_submit_button("Envoyer mes réponses")
            
            if valid_final:
                save_response(code_couple, nom_patient, reponses)
                st.success("✅ Vos réponses ont été enregistrées avec succès ! Vous pouvez fermer cette page.")
                st.balloons()

# === MODE THÉRAPEUTE ===
elif mode == "🔒 Espace Thérapeute":
    st.title("Tableau de Bord Thérapeute")
    password = st.sidebar.text_input("Mot de passe", type="password")
    
    if password == "admin": # A changer
        df = load_data()
        
        if df.empty:
            st.warning("Aucune donnée enregistrée pour le moment.")
        else:
            # Grouper par Code Couple
            codes = df['Code_Couple'].unique()
            
            st.write(f"📂 **{len(codes)} Dossiers Couples trouvés**")
            
            for code in codes:
                subset = df[df['Code_Couple'] == code]
                participants = subset['Nom'].tolist()
                
                with st.expander(f"Dossier : {code} ({len(participants)} réponses)", expanded=False):
                    st.table(subset[['Nom', 'Date']])
                    
                    if len(participants) == 2:
                        st.success("✅ Dossier Complet (2 partenaires)")
                        
                        nom_A = participants[0]
                        nom_B = participants[1]
                        data_A = subset[subset['Nom'] == nom_A].iloc[0]
                        data_B = subset[subset['Nom'] == nom_B].iloc[0]
                        
                        # Visualisation Rapide
                        col_viz, col_actions = st.columns([2, 1])
                        
                        with col_viz:
                            # Mini Radar
                            values_A = [data_A[s] for s in SCHEMAS_LIST]
                            values_B = [data_B[s] for s in SCHEMAS_LIST]
                            
                            fig = go.Figure()
                            fig.add_trace(go.Scatterpolar(r=values_A, theta=SCHEMAS_LIST, fill='toself', name=nom_A))
                            fig.add_trace(go.Scatterpolar(r=values_B, theta=SCHEMAS_LIST, fill='toself', name=nom_B))
                            fig.update_layout(height=300, margin=dict(t=20, b=20, l=40, r=40))
                            st.plotly_chart(fig, use_container_width=True)

                        with col_actions:
                            st.write("### Actions")
                            # Générer PDF
                            pdf_bytes = generate_pdf(nom_A, data_A, nom_B, data_B)
                            st.download_button(
                                label="📄 Télécharger Rapport PDF",
                                data=pdf_bytes,
                                file_name=f"Rapport_{code}.pdf",
                                mime="application/pdf"
                            )
                            
                            # Télécharger CSV bruts
                            csv_data = subset.to_csv(index=False).encode('utf-8')
                            st.download_button(
                                label="📊 Télécharger Données Brutes",
                                data=csv_data,
                                file_name=f"Donnees_{code}.csv",
                                mime="text/csv"
                            )
                    else:
                        st.warning(f"En attente du 2ème partenaire. (Actuellement : {', '.join(participants)})")
    
    else:
        st.info("Veuillez entrer le mot de passe pour accéder aux dossiers.")
