import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import os
import tempfile

# --- CONFIGURATION ---
st.set_page_config(page_title="Alliance & Schémas - Expert", layout="wide", page_icon="✝️")
DB_FILE = "reponses_couple_ultimate.csv"

# --- 1. CONTENU "COUNSELING BIBLIQUE" & STRUCTURE ---

SCHEMA_DETAILS = {
    "ed": {
        "nom": "Echec",
        "theologie": "L'Idole de la Réussite. On mesure sa valeur à sa performance et non à son adoption filiale en Christ.",
        "conseil": "Redéfinir le succès : la fidélité est plus importante que le résultat (Matthieu 25:21).",
    },
    "ma": {
        "nom": "Mefiance / Abus",
        "theologie": "Crainte de l'homme excessive. On ne croit pas que Dieu est un bouclier suffisant (Psaume 3).",
        "conseil": "Apprendre à remettre le jugement à Dieu pour ne plus vivre sur la défensive.",
    },
    "da": {
        "nom": "Dependance",
        "theologie": "Refus de la responsabilité d'intendant. On cherche un 'sauveur humain' au lieu de s'appuyer sur l'Esprit.",
        "conseil": "Porter sa propre charge (Galates 6:5) tout en s'appuyant sur Dieu.",
    },
    "vu": {
        "nom": "Vulnerabilite",
        "theologie": "Manque de foi en la Providence. L'inquiétude est une forme d'athéisme pratique (Matthieu 6:25).",
        "conseil": "Transformer l'inquiétude en prière (Philippiens 4:6).",
    },
    "ca": {
        "nom": "Carence Affective",
        "theologie": "Idole du Confort Émotionnel. On exige de l'autre qu'il comble un vide que seul Christ peut remplir.",
        "conseil": "Apprendre à donner ce qu'on aimerait recevoir (Actes 20:35).",
    },
    "is": {
        "nom": "Isolement Social",
        "theologie": "Refus de la communion fraternelle. Orgueil ou peur qui sépare du Corps du Christ.",
        "conseil": "L'amour couvre une multitude de péchés. Oser l'hospitalité.",
    },
    "im": {
        "nom": "Imperfection / Honte",
        "theologie": "Mauvaise compréhension de la Justification. On se regarde soi-même au lieu de regarder à la justice de Christ.",
        "conseil": "Il n'y a plus de condamnation (Romains 8:1). Sortir de la cachette.",
    },
    "ab": {
        "nom": "Abandon",
        "theologie": "Idole de la Sécurité Relationnelle. On ne croit pas à la promesse 'Je ne te délaisserai point'.",
        "conseil": "S'ancrer dans l'Alliance éternelle de Dieu pour ne plus étouffer son conjoint.",
    },
    "ass": {
        "nom": "Assujettissement",
        "theologie": "Crainte de l'homme (Proverbes 29:25). On sert l'autre pour acheter la paix, pas par amour pour Dieu.",
        "conseil": "Chercher à plaire à Dieu plutôt qu'aux hommes.",
    },
    "ss": {
        "nom": "Sacrifice de Soi",
        "theologie": "Orgueil du 'Messie'. Croire qu'on est indispensable pour sauver les autres.",
        "conseil": "L'humilité consiste à reconnaître ses limites créaturelles.",
    },
    "ie": {
        "nom": "Inhibition Emotionnelle",
        "theologie": "Cœur de pierre. Refus de la vulnérabilité de l'incarnation. On se protège par le cynisme ou la froideur.",
        "conseil": "Ôter le cœur de pierre et recevoir un cœur de chair (Ezéchiel 36:26).",
    },
    "is_std": {
        "nom": "Exigences Elevees",
        "theologie": "Pharisaïsme. On place la Loi au-dessus de la Grâce. On écrase les autres sous des fardeaux.",
        "conseil": "Apprendre la miséricorde plutôt que le sacrifice.",
    },
    "dt": {
        "nom": "Droits Personnels",
        "theologie": "Orgueil et égoïsme. Se croire l'exception. C'est l'anti-thèse de l'esprit de service de Christ (Phil 2).",
        "conseil": "Regarder les autres comme supérieurs à soi-même.",
    },
    "ci": {
        "nom": "Controle Insuffisant",
        "theologie": "Esclavage des désirs (Epithumiai). Manque de fruit de l'Esprit (Maîtrise de soi).",
        "conseil": "Marcher par l'Esprit pour ne pas accomplir les désirs de la chair.",
    },
    "rc": {
        "nom": "Recherche Approbation",
        "theologie": "Idolâtrie de la Gloire humaine. On préfère la louange des hommes à celle de Dieu.",
        "conseil": "Vivre Coram Deo (devant la face de Dieu seul).",
    },
    "neg": {
        "nom": "Negativisme",
        "theologie": "Ingratitude. Refus de voir la Grâce commune et la bonté de Dieu dans le quotidien.",
        "conseil": "Rendre grâces en toutes choses (1 Thess 5:18).",
    },
    "pu": {
        "nom": "Punition",
        "theologie": "Refus de pardonner. Se mettre à la place du Juge suprême. Oubli de sa propre dette.",
        "conseil": "Pardonner comme Christ nous a pardonné.",
    },
    "fu": {
        "nom": "Fusion",
        "theologie": "Absence de différenciation. On n'a pas quitté 'père et mère' émotionnellement.",
        "conseil": "Devenir une personne distincte pour pouvoir aimer librement.",
    }
}
SCHEMAS_ORDER = list(SCHEMA_DETAILS.keys())

# --- LISTE DES 232 QUESTIONS (SIMULATION) ---
# NOTE : Remplacez les textes génériques par les vraies questions YSQ-L3 si vous avez la licence.
ALL_QUESTIONS = {}
counter = 1
for s in SCHEMAS_ORDER:
    # Génère ~13 questions par schéma pour atteindre ~232
    for i in range(13): 
        ALL_QUESTIONS[counter] = {
            "text": f"Question n°{counter} (Test pour le schéma {SCHEMA_DETAILS[s]['nom']})...",
            "schema": s
        }
        counter += 1

# --- 2. FONCTIONS UTILITAIRES ---

def clean_text(text):
    if not isinstance(text, str): return str(text)
    clean_punct = {"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "…": "...", "œ": "oe", "«": '"', "»": '"'}
    for char, replacement in clean_punct.items():
        text = text.replace(char, replacement)
    return text.encode('latin-1', 'replace').decode('latin-1')

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Code_Couple", "Nom", "Date"] + SCHEMAS_ORDER)

def save_response(code, nom, scores_calcules):
    df = load_data()
    # Création propre de la nouvelle ligne
    new_row = {
        "Code_Couple": code, 
        "Nom": nom, 
        "Date": datetime.now().strftime("%Y-%m-%d")
    }
    new_row.update(scores_calcules)
    
    # Mise à jour si existe déjà, sinon ajout
    df = df[~((df['Code_Couple'] == code) & (df['Nom'] == nom))] 
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def create_radar_chart(data_A, data_B, nom_A, nom_B):
    categories = [SCHEMA_DETAILS[s]['nom'] for s in SCHEMAS_ORDER]
    values_A = [data_A.get(s, 0) for s in SCHEMAS_ORDER]
    values_B = [data_B.get(s, 0) for s in SCHEMAS_ORDER]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values_A, theta=categories, fill='toself', name=nom_A, line_color='#1f77b4'))
    fig.add_trace(go.Scatterpolar(r=values_B, theta=categories, fill='toself', name=nom_B, line_color='#ff7f0e'))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 6])), 
        template="plotly_white", 
        margin=dict(t=20, b=20, l=40, r=40)
    )
    return fig

# --- 3. GÉNÉRATEUR PDF (ROBUSTE) ---

class PDFReport(FPDF):
    def header(self):
        self.set_fill_color(44, 62, 80) # Bleu foncé Counseling
        self.rect(0, 0, 210, 30, 'F')
        self.set_font('Arial', 'B', 18)
        self.set_text_color(255, 255, 255)
        self.set_y(10)
        self.cell(0, 10, clean_text('RAPPORT DE COUNSELING DE COUPLE'), 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 5, clean_text('Analyse Clinique & Pastorale des Schémas'), 0, 1, 'C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, clean_text(f'Page {self.page_no()}'), 0, 0, 'C')

def generate_pdf(nom_A, data_A, nom_B, data_B, code):
    pdf = PDFReport()
    pdf.add_page()
    
    # INFO
    pdf.set_font('Arial', 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(0, 10, clean_text(f"Couple : {nom_A} & {nom_B} (Ref: {code})"), 0, 1)
    pdf.ln(5)

    # GRAPHIQUE (Tentative d'insertion avec gestion d'erreur)
    try:
        fig = create_radar_chart(data_A, data_B, nom_A, nom_B)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            fig.write_image(tmp.name, format="png", width=800, height=500, scale=2, engine="kaleido")
            pdf.image(tmp.name, x=10, y=50, w=190)
            pdf.ln(100) # Espace réservé
    except Exception as e:
        pdf.set_text_color(200, 0, 0)
        pdf.set_font('Arial', 'I', 9)
        pdf.multi_cell(0, 5, clean_text(f"[Image non disponible: Le serveur ne possède pas le moteur graphique requis. Voir tableau de bord en ligne.]"))
        pdf.set_text_color(0)
        pdf.ln(10)

    # ANALYSE
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, clean_text("Analyse Théologique & Pratique"), 0, 1)
    pdf.ln(5)

    for s in SCHEMAS_ORDER:
        val_A = data_A.get(s, 0)
        val_B = data_B.get(s, 0)
        
        # Seuil d'affichage (Score > 3)
        if val_A >= 3 or val_B >= 3:
            d = SCHEMA_DETAILS[s]
            
            # En-tête
            pdf.set_fill_color(236, 240, 241) # Gris clair
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, clean_text(f"{d['nom'].upper()} (A:{val_A:.1f} | B:{val_B:.1f})"), 0, 1, 'L', 1)
            
            # Contenu
            pdf.set_font('Arial', 'B', 10)
            pdf.write(5, clean_text("Cœur & Idoles : "))
            pdf.set_font('Arial', '', 10)
            pdf.write(5, clean_text(d['theologie']) + "\n")
            
            pdf.set_font('Arial', 'B', 10)
            pdf.set_text_color(39, 174, 96) # Vert
            pdf.write(5, clean_text("Piste Biblique : "))
            pdf.set_font('Arial', '', 10)
            pdf.write(5, clean_text(d['conseil']) + "\n")
            
            pdf.set_text_color(0)
            pdf.ln(4)

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. INTERFACE UTILISATEUR ---

st.sidebar.title("Navigation")
mode = st.sidebar.radio("Menu", ["🏠 Espace Questionnaire", "💼 Espace Thérapeute"])

# === MODE CLIENT (PAGINATION) ===
if mode == "🏠 Espace Questionnaire":
    st.title("Questionnaire des Schémas (YSQ-L3)")
    
    if 'q_data' not in st.session_state: st.session_state.q_data = {}
    if 'current_page' not in st.session_state: st.session_state.current_page = 0
    if 'user_info' not in st.session_state: st.session_state.user_info = None

    if st.session_state.user_info is None:
        st.info("Ce test comporte 232 questions. Prévoyez environ 20 minutes.")
        with st.form("login"):
            code = st.text_input("Code Couple").strip().upper()
            nom = st.text_input("Votre Prénom")
            if st.form_submit_button("Commencer"):
                if code and nom:
                    st.session_state.user_info = {"code": code, "nom": nom}
                    st.rerun()
    else:
        # Paging Logic
        QUESTIONS_PER_PAGE = 50
        total_questions = len(ALL_QUESTIONS)
        total_pages = (total_questions // QUESTIONS_PER_PAGE) + 1
        
        start_idx = st.session_state.current_page * QUESTIONS_PER_PAGE + 1
        end_idx = min(start_idx + QUESTIONS_PER_PAGE, total_questions + 1)
        
        st.progress((st.session_state.current_page + 1) / total_pages)
        st.caption(f"Page {st.session_state.current_page + 1} sur {total_pages}")
        
        with st.form(f"page_{st.session_state.current_page}"):
            for q_num in range(start_idx, end_idx):
                if q_num in ALL_QUESTIONS:
                    q_obj = ALL_QUESTIONS[q_num]
                    saved_val = st.session_state.q_data.get(q_num, 1)
                    st.session_state.q_data[q_num] = st.slider(
                        f"{q_num}. {q_obj['text']}", 1, 6, saved_val, key=f"q_{q_num}"
                    )
            
            col_prev, col_next = st.columns(2)
            is_last = (st.session_state.current_page == total_pages - 1)
            
            submitted = False
            if is_last:
                submitted = st.form_submit_button("💾 TERMINER ET ENVOYER")
            else:
                if st.form_submit_button("Page Suivante ➡️"):
                    st.session_state.current_page += 1
                    st.rerun()

            if submitted:
                # Calcul Moyennes
                final_scores = {}
                schema_sums = {s: 0 for s in SCHEMAS_ORDER}
                schema_counts = {s: 0 for s in SCHEMAS_ORDER}
                
                for q_num, score in st.session_state.q_data.items():
                    schema_code = ALL_QUESTIONS[q_num]['schema']
                    schema_sums[schema_code] += score
                    schema_counts[schema_code] += 1
                
                for s in SCHEMAS_ORDER:
                    if schema_counts[s] > 0:
                        final_scores[s] = round(schema_sums[s] / schema_counts[s], 2)
                    else:
                        final_scores[s] = 0
                
                save_response(st.session_state.user_info['code'], st.session_state.user_info['nom'], final_scores)
                st.success("✅ Réponses enregistrées avec succès ! Merci.")
                st.balloons()

# === MODE THERAPEUTE ===
elif mode == "💼 Espace Thérapeute":
    st.title("Tableau de Bord Thérapeute")
    pwd = st.sidebar.text_input("Mot de passe", type="password")
    
    if pwd == "Expert2024":
        df = load_data()
        if df.empty:
            st.warning("Aucune donnée disponible.")
        else:
            couples = df['Code_Couple'].unique()
            selected = st.selectbox("Sélectionner un dossier", couples)
            
            subset = df[df['Code_Couple'] == selected]
            
            if len(subset) >= 1:
                # Récupération données A et B
                row_A = subset.iloc[0]
                name_A = row_A['Nom']
                
                if len(subset) > 1:
                    row_B = subset.iloc[1]
                    name_B = row_B['Nom']
                else:
                    row_B = None
                    name_B = "En attente..."

                st.markdown("---")
                # COLONNES : GRAPHIQUE A GAUCHE, BOUTONS A DROITE
                col_graph, col_actions = st.columns([2, 1])
                
                with col_graph:
                    st.subheader("Radar des Schémas")
                    dict_B = row_B.to_dict() if row_B is not None else {}
                    fig = create_radar_chart(row_A.to_dict(), dict_B, name_A, name_B)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col_actions:
                    st.subheader("Actions")
                    st.info(f"Dossier : {selected}")
                    st.write(f"👤 {name_A}")
                    st.write(f"👤 {name_B}")
                    
                    if row_B is not None:
                        pdf_bytes = generate_pdf(name_A, row_A.to_dict(), name_B, row_B.to_dict(), selected)
                        st.download_button("📄 Télécharger Rapport PDF", pdf_bytes, f"Rapport_{selected}.pdf", "application/pdf")
                    else:
                        st.warning("Attente du 2ème partenaire pour générer le rapport.")

                # SECTION ANALYSE DETAILLEE
                st.markdown("---")
                st.subheader("Analyse Clinique & Pastorale")
                
                # Tri des schémas par score décroissant (Max score A ou B)
                def get_max(s):
                    sa = row_A[s]
                    sb = row_B[s] if row_B is not None else 0
                    return max(sa, sb)
                
                sorted_list = sorted(SCHEMAS_ORDER, key=get_max, reverse=True)
                
                for s in sorted_list:
                    score_max = get_max(s)
                    if score_max >= 3: # Filtre affichage
                        det = SCHEMA_DETAILS[s]
                        # Icone couleur
                        icon = "🔴" if score_max >= 4 else "🟠"
                        
                        with st.expander(f"{icon} {det['nom'].upper()} (Max: {score_max}/6)"):
                            c1, c2, c3 = st.columns([1, 2, 2])
                            with c1:
                                st.metric(name_A, f"{row_A[s]}")
                                if row_B is not None:
                                    st.metric(name_B, f"{row_B[s]}")
                            with c2:
                                st.markdown("**Diagnostic du Cœur :**")
                                st.write(det['theologie'])
                            with c3:
                                st.markdown("**Direction Biblique :**")
                                st.success(det['conseil'])
            else:
                st.error("Erreur de lecture du dossier.")
