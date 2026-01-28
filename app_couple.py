import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import os
import tempfile

# --- CONFIGURATION ---
st.set_page_config(page_title="Alliance Pro - Schémas", layout="wide", page_icon="✝️")
DB_FILE = "reponses_couple_expert.csv"

# --- 1. BASE DE CONNAISSANCES "EXPERT" (18 SCHÉMAS) ---
# Structure: Clinique | Théologique | Impact Couple | Piste Pratique

SCHEMA_DETAILS = {
    "ab": {
        "nom": "Abandon / Instabilité",
        "clinique": "Sentiment que les proches sont instables et vont inévitablement partir, mourir ou trouver mieux ailleurs.",
        "theologie": "La blessure de l'Exil. Difficulté fondamentale à croire en la permanence de l'Amour de Dieu (l'Alliance). Le cœur vit comme si Dieu était capricieux.",
        "couple": "La 'Danse de l'Agrippement'. Le patient étouffe son conjoint par jalousie ou besoin constant de réassurance. Paradoxalement, cela pousse l'autre à s'éloigner, confirmant la peur de l'abandon.",
        "pratique": "Exercice de 'Permanence de l'Objet' : Apprendre à s'apaiser seul quand l'autre est absent. Méditer Hébreux 13:5 ('Je ne te délaisserai point')."
    },
    "ma": {
        "nom": "Méfiance / Abus",
        "clinique": "Attente que les autres vont nous blesser, nous manipuler, nous humilier ou profiter de nous.",
        "theologie": "La blessure de Caïn. Le monde est perçu comme une jungle hostile. Incapacité à voir Dieu comme un Refuge ou un Père protecteur.",
        "couple": "La 'Forteresse'. Le patient teste constamment la loyauté du conjoint. Il interprète des erreurs maladroites comme des attaques malveillantes. Il garde des secrets et ne s'abandonne pas.",
        "pratique": "Arrêter la lecture de pensée ('Il a fait ça pour me nuire'). Oser une petite confiance vérifiable. Prière de guérison des mémoires d'abus."
    },
    "ca": {
        "nom": "Carence Affective",
        "clinique": "Croyance que nos besoins de soutien émotionnel, d'empathie ou de protection ne seront jamais comblés.",
        "theologie": "L'Orphelin spirituel. Sentiment d'être invisible aux yeux du Père. On croit devoir survivre sans 'manne' céleste.",
        "couple": "Le 'Trou Noir'. Le patient attend que l'autre devine ses besoins (télépathie) puis punit l'autre par le froid ou la colère quand il échoue. L'autre se sent impuissant et finit par ne plus donner.",
        "pratique": "Apprendre à demander clairement : 'J'ai besoin d'un câlin' au lieu de soupirer. Accepter que le conjoint ne soit pas Dieu : il a des limites."
    },
    "is": {
        "nom": "Isolement Social",
        "clinique": "Sentiment d'être différent, de ne pas appartenir au groupe, d'être exclu.",
        "theologie": "La blessure du Lépreux. Sentiment d'être hors du Corps du Christ, indigne de la communion fraternelle.",
        "couple": "Le 'Couple Ermite'. Le patient isole le couple, refusant les amis ou la famille. Il demande au conjoint d'être son 'seul univers', ce qui est une charge trop lourde.",
        "pratique": "S'engager dans un petit groupe (église, asso). Accepter les différences comme une richesse et non une preuve d'exclusion."
    },
    "im": {
        "nom": "Imperfection / Honte",
        "clinique": "Sentiment d'être intérieurement défectueux, mauvais, sans valeur. Peur qu'on découvre notre 'vraie' nature.",
        "theologie": "La honte d'Adam nu. Difficulté à accepter la Grâce inconditionnelle. On pense devoir 'payer' pour être aimé.",
        "couple": "La 'Fuite ou l'Attaque'. Très susceptible à la critique. Soit il s'écrase (confirme qu'il est nul), soit il contre-attaque violemment pour cacher sa honte. Cache son intimité.",
        "pratique": "Distinguer 'ce que je fais' (comportement) de 'qui je suis' (Identité en Christ). Pratiquer la confession et l'accueil du pardon."
    },
    "ed": {
        "nom": "Echec",
        "clinique": "Croyance d'être moins capable que les autres, inepte, voué à l'échec professionnel ou personnel.",
        "theologie": "La parabole des Talents enfouis. Peur de ne pas porter de fruit, vision de Dieu comme un maître sévère qui juge la performance.",
        "couple": "L'Enfant incompétent'. Se repose entièrement sur le conjoint pour les décisions 'sérieuses' (finances, admin), créant un déséquilibre parent/enfant dans le couple.",
        "pratique": "Redéfinir le succès selon le Royaume (fidélité vs performance). Oser des petites responsabilités sans demander validation."
    },
    "da": {
        "nom": "Dépendance / Incompétence",
        "clinique": "Incapacité à gérer le quotidien sans l'aide d'autrui. Se sent comme un enfant dans un monde d'adultes.",
        "theologie": "Refus de grandir (Syndrome de Pierre Pan). Ne pas assumer la responsabilité d'intendant que Dieu donne à l'homme.",
        "couple": "Le 'Fardeau'. L'un porte tout, l'autre suit. Au début c'est flatteur pour le 'fort', à la fin c'est épuisant et cela tue le désir sexuel (on ne désire pas un enfant).",
        "pratique": "Prendre des décisions seul, même petites. Accepter de se tromper. Le conjoint doit arrêter de 'sauver' systématiquement."
    },
    "vu": {
        "nom": "Vulnérabilité au Danger",
        "clinique": "Peur constante qu'une catastrophe (médicale, financière, criminelle) va survenir.",
        "theologie": "Manque de confiance en la Providence. Vie dominée par la peur de la mort plutôt que l'espérance de la Résurrection.",
        "couple": "La 'Prison de Sécurité'. Empêche le couple de prendre des risques, de voyager, d'investir. Le conjoint est utilisé comme un garde du corps.",
        "pratique": "Lâcher prise. Statistiques vs Réalité. Prière de remise : 'Seigneur, ma vie est dans tes mains'."
    },
    "fu": {
        "nom": "Fusion / Personnalité Atrophiée",
        "clinique": "Trop impliqué émotionnellement avec les parents ou le conjoint. Pas d'identité propre.",
        "theologie": "Idolâtrie relationnelle. Ne pas avoir 'quitté son père et sa mère'. L'autre prend la place de Dieu.",
        "couple": "Le 'Siamois'. Aucune intimité personnelle, tout est partagé. Si le conjoint est triste, le patient est dévasté. Étouffement mutuel.",
        "pratique": "Développer des hobbies séparés. Apprendre à dire 'Je' au lieu de 'Nous'. Couper le cordon émotionnel."
    },
    "ass": {
        "nom": "Assujettissement",
        "clinique": "Se soumettre au contrôle des autres par peur de la colère ou du rejet. Refoulement de ses propres besoins.",
        "theologie": "Servitude humaine vs Serviteur de Dieu. Peur de l'homme plutôt que crainte de Dieu.",
        "couple": "La 'Cocotte-Minute'. Dit 'oui' à tout (sexe, corvées) mais accumule une rancœur secrète (comportement passif-agressif). Finit par exploser.",
        "pratique": "Apprendre l'assertivité chrétienne : dire la vérité dans l'amour. Dire 'Non' est spirituel quand c'est pour protéger son cœur."
    },
    "ss": {
        "nom": "Sacrifice de Soi",
        "clinique": "Se concentrer excessivement sur les besoins des autres au détriment des siens (Syndrome du Sauveur).",
        "theologie": "Orgueil caché sous l'humilité. Penser qu'on est le messie de l'autre. Confusion entre amour et sacrifice destructeur.",
        "couple": "Le 'Martyr'. Donne tout, s'épuise, puis culpabilise le conjoint ('Après tout ce que j'ai fait pour toi !'). Crée une dette chez l'autre.",
        "pratique": "Recevoir est aussi important que donner. Si votre coupe est vide, vous ne donnez que du vent. Fixer des limites saines."
    },
    "ie": {
        "nom": "Inhibition Émotionnelle",
        "clinique": "Verrouillage des émotions, de la spontanéité. Paraît froid, rationnel, robotique.",
        "theologie": "Stoïcisme vs Incarnation. Jésus a pleuré. Refus de la condition humaine sensible créée par Dieu.",
        "couple": "Le 'Mur de Glace'. Le conjoint se sent seul et non-aimé. Pas de joie, pas de rire, pas de folie. La relation devient fonctionnelle et morte.",
        "pratique": "Journal des émotions. Apprendre le vocabulaire des sentiments. Oser dire 'Je suis triste' ou 'Je suis joyeux'."
    },
    "is_std": { 
        "nom": "Exigences Élevées / Critique",
        "clinique": "Standards de performance inatteignables. Perfectionnisme rigide. Jamais satisfait.",
        "theologie": "Justification par les œuvres. Refus de la Grâce. On juge les autres comme on pense que Dieu nous juge.",
        "couple": "Le 'Juge'. Rien n'est jamais assez bien (ménage, éducation, salaire). Le conjoint vit sous pression constante et finit par démissionner.",
        "pratique": "Célébrer 'l'assez bien'. Accepter l'imperfection comme une réalité de la Chute. Pratiquer la gratitude pour ce qui est là."
    },
    "dt": {
        "nom": "Droits Personnels / Grandiosité",
        "clinique": "Se sentir supérieur, spécial, au-dessus des lois. Manque d'empathie pour les besoins des autres.",
        "theologie": "Le péché originel : vouloir être 'comme des dieux'. Orgueil, narcissisme. Refus de servir.",
        "couple": "Le 'Tyran'. Le conjoint est un objet utilitaire. Colère si les besoins ne sont pas satisfaits immédiatement. Aucune réciprocité.",
        "pratique": "Développer l'empathie : 'Comment se sent l'autre ?'. Service humble et anonyme. Se rappeler que nous sommes tous poussière."
    },
    "ci": {
        "nom": "Contrôle de Soi Insuffisant",
        "clinique": "Impulsivité, intolérance à la frustration, addictions, procrastination.",
        "theologie": "Esclavage des pulsions. Manque de 'Fruit de l'Esprit' (Maîtrise de soi). Vie dictée par le plaisir immédiat.",
        "couple": "L'Enfant Capricieux'. On ne peut pas compter sur lui. Dépenses impulsives, paroles blessantes sous le coup de la colère, infidélité possible.",
        "pratique": "Apprendre la tolérance à la frustration. Jeûne. Mettre un temps d'arrêt entre l'impulsion et l'action."
    },
    "rc": {
        "nom": "Recherche d'Approbation",
        "clinique": "Recherche excessive de l'attention et de la validation des autres. Caméléon.",
        "theologie": "Gloire humaine vs Gloire de Dieu. Identité basée sur le regard de l'autre et non sur le regard du Père.",
        "couple": "L'Acteur'. Change de personnalité selon qui est là. Le conjoint ne sait plus qui il aime vraiment. Jalousie sociale.",
        "pratique": "Authenticité. Faire des choses 'en secret' pour Dieu seul. Oser déplaire pour rester fidèle à soi-même."
    },
    "neg": {
        "nom": "Négativisme / Pessimisme",
        "clinique": "Focalisation sur les aspects négatifs (douleur, mort, perte, conflit). Inquiétude chronique.",
        "theologie": "Manque d'Espérance. Cécité face à la bonté de la Création et à la Providence.",
        "couple": "Le 'Rabat-joie'. Éteint l'enthousiasme du conjoint. 'Ça ne marchera pas'. Ambiance lourde et déprimante à la maison.",
        "pratique": "Journal de gratitude (3 choses positives par jour). Se forcer à voir le verre à moitié plein. Louange."
    },
    "pu": {
        "nom": "Punition",
        "clinique": "Intolérance envers les erreurs (les siennes et celles des autres). Tendance à punir durement.",
        "theologie": "Légalisme. Refus de la Miséricorde. Dieu est vu comme un Père fouettard. Pas de place pour le pardon.",
        "couple": "Le 'Bourreau'. Rancunier. Sort les vieux dossiers lors des disputes. Le conjoint a peur de faire une erreur. Climat de peur.",
        "pratique": "Miséricorde. Pardonner c'est renoncer à se venger. Comprendre les circonstances atténuantes chez l'autre."
    }
}

# Mapping simplifié des questions (Simulation du YSQ-L3 pour la démo)
# Dans un vrai déploiement, vous mettriez ici le mapping exact des 232 questions.
# Ex: 'ab': [1, 19, 37...]
SCHEMAS_ORDER = list(SCHEMA_DETAILS.keys())

# --- 2. FONCTIONS UTILITAIRES ---

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Code_Couple", "Nom", "Role", "Date"] + SCHEMAS_ORDER)

def save_response(code, nom, responses_dict):
    df = load_data()
    new_row = {"Code_Couple": code, "Nom": nom, "Role": "Partenaire", "Date": datetime.now().strftime("%Y-%m-%d")}
    new_row.update(responses_dict)
    
    # Suppression ancienne réponse si existe (mise à jour)
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
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 6])), template="plotly_white")
    return fig

# --- 3. GÉNÉRATEUR PDF AVANCÉ ---

class PDFExpert(FPDF):
    def header(self):
        # Bandeau de couleur
        self.set_fill_color(52, 73, 94) # Bleu nuit
        self.rect(0, 0, 210, 25, 'F')
        self.set_font('Arial', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'ANALYSE THÉRAPEUTIQUE DU COUPLE', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} - Document Confidentiel - Généré par Alliance Pro', 0, 0, 'C')

    def chapter_title(self, label, icon=""):
        self.set_font('Arial', 'B', 14)
        self.set_fill_color(230, 230, 230)
        self.set_text_color(0, 0, 0)
        self.cell(0, 10, f"{icon} {label}", 0, 1, 'L', 1)
        self.ln(4)

    def card_schema(self, schema_code, score_A, score_B, nom_A, nom_B):
        details = SCHEMA_DETAILS[schema_code]
        
        # Titre Schema
        self.set_font('Arial', 'B', 12)
        self.set_text_color(192, 57, 43) # Rouge brique
        self.cell(0, 8, f"{details['nom'].upper()}", 0, 1)
        
        # Scores
        self.set_font('Arial', 'B', 10)
        self.set_text_color(0)
        txt_scores = f"Scores : {nom_A} = {score_A}/6  |  {nom_B} = {score_B}/6"
        self.cell(0, 6, txt_scores, 0, 1)
        self.ln(2)
        
        # Corps
        self.set_font('Arial', '', 10)
        
        # Clinique
        self.set_font('Arial', 'B', 10)
        self.write(5, "Dimension Clinique : ")
        self.set_font('Arial', '', 10)
        self.write(5, details['clinique'] + "\n\n")
        
        # Théologie
        self.set_font('Arial', 'B', 10)
        self.write(5, "Racine Spirituelle : ")
        self.set_font('Arial', '', 10)
        self.write(5, details['theologie'] + "\n\n")

        # Couple
        self.set_fill_color(240, 248, 255) # AliceBlue
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, " L'Impact sur votre Couple :", 0, 1, 'L', 1)
        self.set_font('Arial', 'I', 10)
        self.multi_cell(0, 5, details['couple'])
        self.ln(2)

        # Pratique
        self.set_fill_color(235, 250, 235) # LightGreenish
        self.set_font('Arial', 'B', 10)
        self.cell(0, 6, " Piste de Travail :", 0, 1, 'L', 1)
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 5, details['pratique'])
        
        self.ln(5)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(5)

def generate_full_pdf(nom_A, data_A, nom_B, data_B, code_couple):
    pdf = PDFExpert()
    pdf.add_page()
    
    # Page de Garde
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f"Dossier : {code_couple}", 0, 1)
    pdf.cell(0, 10, f"Partenaires : {nom_A} & {nom_B}", 0, 1)
    pdf.cell(0, 10, f"Date : {datetime.now().strftime('%d/%m/%Y')}", 0, 1)
    pdf.ln(5)
    
    # Graphique
    try:
        fig = create_radar_chart(data_A, data_B, nom_A, nom_B)
        # On utilise tempfile pour gérer l'image proprement
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmpfile:
            fig.write_image(tmpfile.name, format="png", width=800, height=600, scale=2)
            pdf.image(tmpfile.name, x=15, y=70, w=180)
            tmp_path = tmpfile.name
        os.remove(tmp_path) # Nettoyage
    except Exception as e:
        pdf.set_text_color(255, 0, 0)
        pdf.cell(0, 10, "Note: Le graphique n'a pas pu être généré (Librairie manquante).", 0, 1)
        pdf.set_text_color(0)

    pdf.add_page()
    
    # Analyse Détaillée
    pdf.chapter_title("Analyse Approfondie des Schémas Actifs")
    pdf.set_font('Arial', 'I', 10)
    pdf.multi_cell(0, 5, "Cette section détaille les schémas qui dépassent le seuil clinique (Score > 3.5) chez l'un ou l'autre des partenaires.")
    pdf.ln(5)

    count = 0
    for s in SCHEMAS_ORDER:
        val_A = data_A.get(s, 0)
        val_B = data_B.get(s, 0)
        
        if val_A >= 3.5 or val_B >= 3.5:
            pdf.card_schema(s, val_A, val_B, nom_A, nom_B)
            count += 1
            if pdf.get_y() > 250: # Saut de page si bas
                pdf.add_page()
    
    if count == 0:
        pdf.multi_cell(0, 10, "Aucun schéma majeur détecté. Vos scores sont tous dans la moyenne basse, signe d'une grande stabilité.")

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 4. INTERFACE UTILISATEUR ---

st.sidebar.title("Navigation")
mode = st.sidebar.radio("Menu", ["🏠 Accueil & Questionnaire", "💼 Espace Thérapeute"])

# === MODE PATIENT ===
if mode == "🏠 Accueil & Questionnaire":
    st.title("Questionnaire Clinique de Schémas")
    st.markdown("""
    Bienvenue. Ce questionnaire approfondi nous permettra de comprendre les dynamiques profondes de votre couple.
    
    **Instructions :**
    1. Entrez le **Code Couple** donné par votre thérapeute.
    2. Répondez seul(e), honnêtement.
    3. Il y a **232 questions** (simulation ici pour démonstration).
    """)
    
    with st.form("login_patient"):
        code_input = st.text_input("Code Couple").strip().upper()
        nom_input = st.text_input("Votre Prénom")
        start_btn = st.form_submit_button("Démarrer l'évaluation")
    
    if start_btn and code_input and nom_input:
        st.session_state['user_code'] = code_input
        st.session_state['user_nom'] = nom_input
        st.session_state['q_step'] = 1

    if 'user_code' in st.session_state:
        st.divider()
        st.subheader(f"Session de {st.session_state['user_nom']}")
        
        # SIMULATION DU QUESTIONNAIRE LONG (Pour l'exemple technique)
        # Dans la réalité, on chargerait les 232 questions ici.
        # Pour l'UX, on groupe par 18 schémas pour que ce soit digeste.
        
        with st.form("main_q"):
            responses_temp = {}
            st.info("Veuillez évaluer de 1 (Faux) à 6 (Parfaitement Vrai)")
            
            # On boucle sur les schémas pour l'exemple
            for schema_code in SCHEMAS_ORDER:
                details = SCHEMA_DETAILS[schema_code]
                st.markdown(f"#### Catégorie : {details['nom']}")
                # On simule 2 questions par schéma pour la démo technique
                # Remplacez par votre liste de 232 items
                responses_temp[schema_code] = st.slider(f"Je ressens souvent... ({details['nom']})", 1, 6, 1, key=f"{schema_code}_1")
            
            finish = st.form_submit_button("Terminer et Envoyer")
            
            if finish:
                save_response(st.session_state['user_code'], st.session_state['user_nom'], responses_temp)
                st.success("Réponses enregistrées ! Merci.")
                st.balloons()

# === MODE THERAPEUTE ===
elif mode == "💼 Espace Thérapeute":
    st.title("Tableau de Bord Expert")
    pwd = st.sidebar.text_input("Mot de passe", type="password")
    
    if pwd == "Expert2024":
        df = load_data()
        if not df.empty:
            couples = df['Code_Couple'].unique()
            selected_couple = st.selectbox("Sélectionner un dossier", couples)
            
            subset = df[df['Code_Couple'] == selected_couple]
            
            if len(subset) == 2:
                row_A = subset.iloc[0]
                row_B = subset.iloc[1]
                
                # --- AFFICHAGE DASHBOARD ---
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown("### 📊 Radar Comparatif")
                    fig = create_radar_chart(row_A, row_B, row_A['Nom'], row_B['Nom'])
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.markdown("### 📥 Actions")
                    st.info("Le rapport PDF inclura l'analyse théologique et pastorale complète.")
                    
                    pdf_data = generate_full_pdf(row_A['Nom'], row_A, row_B['Nom'], row_B, selected_couple)
                    
                    st.download_button(
                        "📄 Télécharger Rapport EXPERT (PDF)",
                        data=pdf_data,
                        file_name=f"Rapport_{selected_couple}_Expert.pdf",
                        mime="application/pdf"
                    )
                
                # Aperçu rapide des zones rouges
                st.markdown("### 🚨 Zones de Vigilance Immédiate")
                for s in SCHEMAS_ORDER:
                    if row_A[s] >= 4 or row_B[s] >= 4:
                        content = SCHEMA_DETAILS[s]
                        with st.expander(f"🔴 {content['nom'].upper()}", expanded=False):
                            c1, c2 = st.columns(2)
                            c1.markdown(f"**Impact Couple :** {content['couple']}")
                            c2.markdown(f"**Piste :** {content['pratique']}")

            else:
                st.warning(f"Dossier incomplet. {len(subset)}/2 partenaires ont répondu.")
        else:
            st.info("Aucun dossier en cours.")
    else:
        st.write("Veuillez vous identifier.")
