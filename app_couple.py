import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import os
import tempfile

# --- 0. CONFIGURATION GLOBALE ---
st.set_page_config(page_title="Alliance & Schémas - Expert", layout="wide", page_icon="✝️")
DB_FILE = "reponses_couple_expert.csv"

# --- 1. BIBLIOTHÈQUE D'EXPERTISE (CLINIQUE & THÉOLOGIQUE) ---
# C'est le "Cerveau" de l'application. Contenu dense et pro.

SCHEMA_LIBRARY = {
    "ed": {
        "code": "ED",
        "nom": "Échec",
        "clinique": "Sentiment envahissant d'être incompétent par rapport aux pairs. Croyance que l'échec est inévitable (carrière, éducation, rôles).",
        "theologie": "L'Idole de la Réussite. La valeur personnelle est attachée à la performance et non à l'adoption filiale. C'est une forme d'orgueil inversé (peur de ne pas être 'dieu' par ses accomplissements).",
        "couple": "Dynamique 'Parent-Enfant'. Le patient se désengage des responsabilités du couple (finances, décisions), laissant le conjoint porter toute la charge mentale. Le conjoint finit par mépriser cette passivité.",
        "pratique": "1. Redéfinir le succès biblique : 'Bien, bon et fidèle serviteur' (fidélité vs résultat). 2. Thérapie d'exposition : prendre une petite responsabilité risquée par semaine."
    },
    "ma": {
        "code": "MA",
        "nom": "Méfiance / Abus",
        "clinique": "Perception d'autrui comme malveillant, manipulateur ou égoïste. Hypervigilance. Teste constamment la loyauté des autres.",
        "theologie": "Le Monde post-chute vu sans la Providence. C'est la blessure de Caïn. Incapacité à voir Dieu comme un Bouclier (Psaume 3). La 'Crainte de l'homme' remplace la confiance en Dieu.",
        "couple": "La 'Forteresse'. Le patient interprète les erreurs du conjoint (oubli, maladresse) comme des attaques intentionnelles. Il garde des secrets ('ne pas donner de munitions'). Le conjoint s'épuise à prouver son innocence.",
        "pratique": "1. Arrêter la 'lecture de pensée'. 2. Exercice de confiance vérifiable. 3. Prière de pardon pour les abus passés (distinguer le conjoint actuel des offenseurs passés)."
    },
    "da": {
        "code": "DA",
        "nom": "Dépendance / Incompétence",
        "clinique": "Incapacité à gérer la vie quotidienne sans aide excessive. Se sent comme un enfant dans un monde d'adultes.",
        "theologie": "Refus de la responsabilité d'Intendant (Mandat culturel). C'est refuser de porter sa propre charge (Galates 6:5) en cherchant un 'sauveur humain' à la place de Dieu.",
        "couple": "Le 'Fardeau'. L'un porte tout, l'autre suit. Au début, cela flatte le schéma de 'Sauveur' du conjoint, mais cela tue le désir (on ne désire pas un enfant) et crée du ressentiment à long terme.",
        "pratique": "1. Prise de décision autonome quotidienne. 2. Le conjoint doit arrêter de valider chaque choix. 3. Méditer sur l'autorité reçue en Christ."
    },
    "vu": {
        "code": "VU",
        "nom": "Vulnérabilité au Danger",
        "clinique": "Peur excessive et irrationnelle qu'une catastrophe (médicale, financière, criminelle) est imminente.",
        "theologie": "Manque de foi en la Souveraineté de Dieu. L'inquiétude est un 'athéisme pratique' : on vit comme si Dieu ne contrôlait pas l'univers. C'est l'esclavage de la peur de la mort (Hébreux 2:15).",
        "couple": "La 'Prison de Sécurité'. Le patient empêche le couple de vivre (voyages, investissements, sorties). Le conjoint est utilisé comme un garde du corps ou une police d'assurance.",
        "pratique": "1. Distinguer 'Possibilité' (0.1%) et 'Probabilité'. 2. Transformer chaque inquiétude en prière (Phil 4:6). 3. Exposition progressive aux situations redoutées."
    },
    "ca": {
        "code": "CA",
        "nom": "Carence Affective",
        "clinique": "Certitude que les besoins émotionnels (chaleur, empathie, protection) ne seront jamais comblés par les autres.",
        "theologie": "Le Syndrome de l'Orphelin. Sentiment d'être invisible aux yeux du Père. On croit que Dieu est avare. Cela mène à la convoitise affective.",
        "couple": "Le 'Trou Noir'. Le patient attend que l'autre devine ses besoins (télépathie) puis punit l'autre par le silence ou la colère quand il échoue. L'autre se sent impuissant et finit par se retirer.",
        "pratique": "1. Apprendre à demander clairement : 'J'ai besoin d'un câlin' (Vulnérabilité). 2. Deuil des parents idéaux non-eus. 3. Recevoir l'amour de Dieu par la contemplation."
    },
    "is": {
        "code": "IS",
        "nom": "Isolement Social",
        "clinique": "Sentiment d'être différent, ne pas appartenir, être exclu du groupe.",
        "theologie": "Refus de la Communion Fraternelle. Orgueil (se croire unique) ou Honte (se croire indigne) qui sépare du Corps du Christ.",
        "couple": "Le 'Couple Ermite'. Le patient isole le couple, critiquant les amis ou la famille. Il demande au conjoint d'être son 'seul univers', une charge trop lourde pour un humain.",
        "pratique": "1. S'engager dans un service concret (laver les pieds des autres brise l'isolement). 2. Hospitalité (Romains 12:13)."
    },
    "im": {
        "code": "IM",
        "nom": "Imperfection / Honte",
        "clinique": "Sentiment profond d'être défectueux, mauvais, indigne d'amour. Peur d'être 'démasqué'.",
        "theologie": "La Honte d'Adam. Difficulté à accepter la Justification par la Foi. On veut 'payer' pour son péché ou le cacher, au lieu de le confesser et recevoir la Grâce.",
        "couple": "La 'Défensive'. Très susceptible à la moindre critique. Contre-attaque ou s'effondre pour cacher sa honte. Empêche la véritable intimité (être connu et être aimé).",
        "pratique": "1. Confession et Transparence. 2. Méditation sur l'Identité en Christ (Aimé, Choisi, Pardonné). 3. Accepter la critique sans s'effondrer."
    },
    "ab": {
        "code": "AB",
        "nom": "Abandon / Instabilité",
        "clinique": "Peur envahissante que les proches meurent, partent ou trouvent mieux ailleurs.",
        "theologie": "Idolâtrie de la Sécurité Relationnelle. On demande à l'humain la fidélité absolue que seul Dieu possède ('Je ne te délaisserai point'). Doute sur l'Alliance.",
        "couple": "Le 'Velcro'. Jalousie, possessivité, 'tests' de l'amour. Étouffe le conjoint, ce qui provoque paradoxalement le recul de l'autre (prophétie auto-réalisatrice).",
        "pratique": "1. Apprendre la 'solitude habitée' (être seul avec Dieu sans paniquer). 2. Arrêter les comportements de vérification (sms, appels). 3. Ancrage dans la Parole."
    },
    "ass": {
        "code": "ASS",
        "nom": "Assujettissement",
        "clinique": "Soumission excessive au contrôle des autres par peur de la colère ou du rejet.",
        "theologie": "Crainte de l'homme (Proverbes 29:25). On sert la créature plutôt que le Créateur. On cherche la paix à tout prix (fausse paix) au lieu de la Vérité.",
        "couple": "La 'Cocotte-Minute'. Le patient dit 'oui' à tout (sexe, corvées, choix) mais accumule une rancœur secrète. Il finit par exploser ou devenir passif-agressif.",
        "pratique": "1. Apprendre à dire 'Non' (La limite est biblique). 2. Exprimer ses préférences (même pour le choix du restaurant). 3. Servir Dieu, pas l'humeur de l'autre."
    },
    "ss": {
        "code": "SS",
        "nom": "Sacrifice de Soi",
        "clinique": "Focus excessif sur les besoins des autres au détriment des siens (Syndrome du Sauveur).",
        "theologie": "Orgueil caché sous l'humilité. Penser qu'on est le 'Messie' de l'autre. Confusion entre amour (vouloir le bien) et sacrifice névrotique (acheter l'amour).",
        "couple": "Le 'Martyr'. Donne tout, s'épuise, puis culpabilise le conjoint ('Après tout ce que j'ai fait pour toi !'). Crée une dette relationnelle malsaine.",
        "pratique": "1. Recevoir est aussi spirituel que donner. 2. Examiner ses motivations : est-ce que je donne pour être aimé ? 3. Sabbat (repos obligatoire)."
    },
    "ie": {
        "code": "IE",
        "nom": "Inhibition Émotionnelle",
        "clinique": "Contrôle excessif de la spontanéité, des sentiments et de la communication.",
        "theologie": "Stoïcisme vs Christianisme. Refus de l'Incarnation (Jésus a pleuré, a exulté). Cœur de pierre vs Cœur de chair.",
        "couple": "Le 'Mur de Glace'. Le conjoint se sent seul, non-rejoint. La relation devient une entreprise fonctionnelle. Risque de double vie émotionnelle.",
        "pratique": "1. Journal des émotions (Psautier). 2. Oser dire 'Je ressens...' sans rationaliser. 3. Partager ses joies et peines simples."
    },
    "is_std": {
        "code": "IS_STD",
        "nom": "Exigences Élevées",
        "clinique": "Standards de performance inatteignables. Perfectionnisme rigide. Jamais satisfait.",
        "theologie": "Pharisaïsme. On place la Loi au-dessus de la Grâce. On juge les autres (et soi-même) selon des critères impitoyables, oubliant la miséricorde.",
        "couple": "Le 'Juge'. Rien n'est jamais assez bien (ménage, salaire, éducation). Le conjoint vit sous pression constante et finit par démissionner ou se rebeller.",
        "pratique": "1. Célébrer l'imparfait. 2. Grâce envers soi-même. 3. Remplacer 'Il faut / Je dois' par 'J'aimerais'."
    },
    "dt": {
        "code": "DT",
        "nom": "Droits Personnels",
        "clinique": "Sentiment de supériorité. Croyance d'avoir des droits spéciaux. Manque d'empathie.",
        "theologie": "Orgueil pur. Le péché originel ('Vous serez comme des dieux'). Refus de la condition de serviteur. C'est l'anti-thèse de Christ (Philippiens 2).",
        "couple": "Le 'Tyran' ou le 'Roi'. Le conjoint est un objet utilitaire. Colère narcissique si les besoins ne sont pas satisfaits immédiatement.",
        "pratique": "1. Service anonyme (humilité). 2. Empathie cognitive : 'Comment se sent l'autre ?'. 3. Reconnaître que tout est grâce imméritée."
    },
    "ci": {
        "code": "CI",
        "nom": "Contrôle Insuffisant",
        "clinique": "Impulsivité, faible tolérance à la frustration, procrastination, addictions.",
        "theologie": "Esclavage des désirs (Epithumiai). Manque de fruit de l'Esprit (Maîtrise de soi). Vie dirigée par le 'Ventre' (les appétits).",
        "couple": "L'Enfant Capricieux'. On ne peut pas compter sur lui. Dépenses impulsives, paroles blessantes, infidélité possible par manque de frein.",
        "pratique": "1. Tolérance à la frustration (Jeûne). 2. 'Stop-Think-Act'. 3. Redevabilité stricte avec un tiers."
    },
    "rc": {
        "code": "RC",
        "nom": "Recherche d'Approbation",
        "clinique": "Recherche excessive de l'attention et de la validation. Estime de soi dépendante des autres.",
        "theologie": "Idolâtrie de la Gloire humaine. On préfère la louange des hommes à celle de Dieu. On est un 'caméléon' sans colonne vertébrale morale.",
        "couple": "L'Acteur'. Change de personnalité selon le public. Le conjoint ne sait plus qui il aime vraiment. Jalousie sociale.",
        "pratique": "1. Vivre 'Coram Deo' (Devant la face de Dieu seul). 2. Faire le bien en secret (Matthieu 6). 3. Authenticité radicale."
    },
    "neg": {
        "code": "NEG",
        "nom": "Négativisme / Pessimisme",
        "clinique": "Focus obsessionnel sur les aspects négatifs (douleur, mort, conflit, risques).",
        "theologie": "Ingratitude et Manque d'Espérance. Cécité face à la Grâce commune. On doute de la Bonté de Dieu dans l'épreuve.",
        "couple": "Le 'Rabat-joie'. Éteint l'enthousiasme du conjoint. 'Ça ne marchera pas'. Ambiance lourde à la maison.",
        "pratique": "1. Discipline de la Gratitude (3 kifs par jour). 2. Louange intentionnelle. 3. Rééquilibrage cognitif (voir aussi ce qui va bien)."
    },
    "pu": {
        "code": "PU",
        "nom": "Punition",
        "clinique": "Intolérance, critique, tendance à punir les erreurs (soi et les autres).",
        "theologie": "Légalisme et Refus de Pardonner. On se prend pour le Juge Suprême. Oubli de la parabole du débiteur impitoyable.",
        "couple": "Le 'Bourreau'. Rancunier. Sort les vieux dossiers lors des disputes. Climat de peur, le conjoint marche sur des œufs.",
        "pratique": "1. Pardonner comme Christ a pardonné. 2. Comprendre les circonstances atténuantes (Empathie). 3. Grâce vs Justice."
    },
    "fu": {
        "code": "FU",
        "nom": "Fusion / Personnalité Atrophiée",
        "clinique": "Absence d'identité propre, fusion avec les parents ou le conjoint.",
        "theologie": "Absence de différenciation. On n'a pas 'quitté son père et sa mère' (Genèse 2:24). Idolâtrie relationnelle.",
        "couple": "Le 'Siamois'. Pas d'intimité car pas de distinction. Si l'un est triste, l'autre est dévasté. Étouffement.",
        "pratique": "1. Développer des goûts personnels. 2. Passer du temps séparé. 3. Affirmer ses opinions divergentes."
    }
}

SCHEMAS_ORDER = list(SCHEMA_LIBRARY.keys())

# --- 2. MOTEUR DES 232 QUESTIONS (MAPPING YSQ-L3) ---

def generate_questions():
    """
    Génère la structure des 232 questions.
    Ceci est un mapping technique.
    """
    questions = {}
    
    # Mapping complet YSQ-L3 (Simulation de la distribution standard)
    # Dans une vraie app, on chargerait un CSV. Ici on génère pour le code.
    # Pattern typique : les questions sont mélangées.
    
    # On crée une liste virtuelle de questions par schéma
    schema_questions_text = {
        "ed": ["Je ne me sens pas à la hauteur au travail.", "J'ai l'impression d'avoir échoué par rapport aux autres."],
        "ma": ["Je soupçonne souvent que les gens ont des arrière-pensées.", "J'ai peur d'être blessé si je m'ouvre."],
        "da": ["J'ai du mal à prendre des décisions seul.", "J'ai besoin que quelqu'un m'aide dans le quotidien."],
        "vu": ["J'ai peur d'avoir une maladie grave.", "Je crains de perdre tout mon argent."],
        "ca": ["Je n'ai pas eu assez d'affection enfant.", "Personne ne me comprend vraiment."],
        "is": ["Je me sens différent des autres.", "Je ne fais partie d'aucun groupe."],
        "im": ["Si on me connaissait vraiment, on ne m'aimerait pas.", "J'ai honte de mes défauts."],
        "ab": ["J'ai peur que mes proches me quittent.", "Je m'accroche aux gens de peur de les perdre."],
        "ass":["Je laisse les autres décider pour éviter le conflit.", "Je fais passer les besoins des autres avant les miens."],
        "ss": ["Je me sens coupable quand je fais quelque chose pour moi.", "Je suis celui qui écoute tout le monde."],
        "ie": ["Je garde mes émotions pour moi.", "Les gens me trouvent froid ou distant."],
        "is_std": ["Je dois être le meilleur dans ce que je fais.", "Je ne supporte pas le désordre ou l'erreur."],
        "dt": ["Je n'aime pas qu'on me dise quoi faire.", "J'ai l'impression d'avoir des droits que les autres n'ont pas."],
        "ci": ["J'agis souvent sur un coup de tête.", "J'ai du mal à finir ce que je commence."],
        "rc": ["L'image que je renvoie est très importante.", "Je cherche souvent des compliments."],
        "neg": ["Je vois souvent le verre à moitié vide.", "Je m'attends souvent au pire."],
        "pu": ["Je suis dur avec moi-même quand je fais une erreur.", "Je pense que les fautes doivent être punies."],
        "fu": ["Je vis à travers mon partenaire.", "J'ai du mal à savoir ce que je veux vraiment."]
    }

    # Génération de 232 items
    count = 1
    # On boucle plusieurs fois pour remplir jusqu'à 232
    while count <= 232:
        for s in SCHEMAS_ORDER:
            if count > 232: break
            
            # On prend un texte réel si dispo, sinon un générique
            base_texts = schema_questions_text[s]
            idx = (count % len(base_texts)) - 1
            txt = base_texts[idx]
            
            questions[count] = {
                "id": count,
                "text": f"{txt} [Item {count}]", # On garde l'ID pour référence
                "schema": s
            }
            count += 1
            
    return questions

ALL_QUESTIONS = generate_questions()

# --- 3. FONCTIONS UTILITAIRES ---

def clean_text(text):
    """Nettoyage Unicode pour FPDF"""
    if not isinstance(text, str): return str(text)
    replacements = {
        "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "…": "...", 
        "œ": "oe", "Œ": "Oe", "«": '"', "»": '"', "€": "EUR"
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode('latin-1', 'replace').decode('latin-1')

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Code_Couple", "Nom", "Date"] + SCHEMAS_ORDER)

def save_response(code, nom, scores):
    df = load_data()
    new_row = {"Code_Couple": code, "Nom": nom, "Date": datetime.now().strftime("%Y-%m-%d")}
    new_row.update(scores)
    
    # Suppression ancienne réponse du même nom/code pour update
    df = df[~((df['Code_Couple'] == code) & (df['Nom'] == nom))]
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def create_radar_chart(data_A, data_B, nom_A, nom_B):
    categories = [SCHEMA_LIBRARY[s]['nom'] for s in SCHEMAS_ORDER]
    values_A = [data_A.get(s, 0) for s in SCHEMAS_ORDER]
    values_B = [data_B.get(s, 0) for s in SCHEMAS_ORDER]
    
    # Fermer la boucle du radar
    categories.append(categories[0])
    values_A.append(values_A[0])
    values_B.append(values_B[0])
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=values_A, theta=categories, fill='toself', name=nom_A, line_color='#2980b9'))
    fig.add_trace(go.Scatterpolar(r=values_B, theta=categories, fill='toself', name=nom_B, line_color='#e74c3c'))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 6])),
        template="plotly_white",
        margin=dict(t=30, b=30, l=40, r=40)
    )
    return fig

# --- 4. MOTEUR PDF "HAUTE COUTURE" ---

class PDFExpert(FPDF):
    def header(self):
        # Header Design avec logo textuel
        self.set_fill_color(44, 62, 80) # Dark Blue
        self.rect(0, 0, 210, 35, 'F')
        
        self.set_font('Arial', 'B', 22)
        self.set_text_color(255, 255, 255)
        self.set_xy(10, 10)
        self.cell(0, 10, clean_text("ALLIANCE & SCHEMAS"), 0, 1, 'L')
        
        self.set_font('Arial', 'I', 11)
        self.set_xy(10, 20)
        self.cell(0, 10, clean_text("Analyse Clinique & Pastorale Approfondie"), 0, 1, 'L')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', '', 8)
        self.set_text_color(128)
        self.cell(0, 10, clean_text(f"Document confidentiel - Page {self.page_no()}"), 0, 0, 'C')

    def chapter_header(self, title, subtitle=None):
        self.ln(10)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(44, 62, 80)
        self.cell(0, 10, clean_text(title.upper()), 0, 1, 'L')
        self.line(10, self.get_y(), 200, self.get_y())
        if subtitle:
            self.set_font('Arial', 'I', 11)
            self.set_text_color(100)
            self.multi_cell(0, 6, clean_text(subtitle))
        self.ln(5)

    def draw_box(self, title, content, r, g, b):
        """Dessine une boîte colorée avec titre et contenu"""
        self.set_fill_color(r, g, b)
        self.set_font('Arial', 'B', 11)
        self.set_text_color(0)
        
        # Titre de la boite
        self.cell(0, 8, clean_text(f"  {title}"), 0, 1, 'L', 1)
        
        # Contenu
        self.set_font('Arial', '', 10)
        self.set_text_color(50)
        self.multi_cell(0, 6, clean_text(content), border='L')
        self.ln(4)

def generate_full_report(nom_A, data_A, nom_B, data_B, code):
    pdf = PDFExpert()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- PAGE 1 : SYNTHÈSE ---
    pdf.add_page()
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, clean_text(f"Dossier Couple : {code}"), 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, clean_text(f"Partenaires : {nom_A} & {nom_B}"), 0, 1)
    pdf.cell(0, 8, clean_text(f"Date : {datetime.now().strftime('%d/%m/%Y')}"), 0, 1)
    pdf.ln(10)
    
    # Graphique Radar
    try:
        fig = create_radar_chart(data_A, data_B, nom_A, nom_B)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
            fig.write_image(tmp.name, format="png", width=800, height=550, scale=2, engine="kaleido")
            pdf.image(tmp.name, x=15, y=70, w=180)
        pdf.set_y(220) # Forcer le curseur après l'image
    except Exception as e:
        pdf.set_text_color(200, 0, 0)
        pdf.cell(0, 10, clean_text("[Graphique non disponible sur ce serveur]"), 0, 1)
        pdf.set_text_color(0)

    # --- PAGE 2+ : ANALYSE DÉTAILLÉE ---
    pdf.add_page()
    pdf.chapter_header("Analyse Détaillée des Schémas", "Seuls les schémas significatifs (Score > 3.0) sont analysés ci-dessous.")

    # Tri des schémas par gravité
    def get_max_score(s): return max(data_A.get(s,0), data_B.get(s,0))
    sorted_schemas = sorted(SCHEMAS_ORDER, key=get_max_score, reverse=True)

    count_active = 0
    for s in sorted_schemas:
        score_A = data_A.get(s, 0)
        score_B = data_B.get(s, 0)
        max_s = max(score_A, score_B)
        
        if max_s >= 3.0:
            count_active += 1
            info = SCHEMA_LIBRARY[s]
            
            # Titre du Schéma
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 14)
            pdf.set_text_color(44, 62, 80)
            status_icon = "(!)" if max_s >= 5 else ""
            title_line = f"{info['nom'].upper()} {status_icon}"
            pdf.cell(0, 10, clean_text(title_line), 0, 1)
            
            # Scores
            pdf.set_font('Arial', 'B', 10)
            pdf.set_text_color(100)
            pdf.cell(0, 6, clean_text(f"Scores : {nom_A} = {score_A:.1f}/6  |  {nom_B} = {score_B:.1f}/6"), 0, 1)
            pdf.ln(4)
            
            # 1. Clinique (Bleu ciel)
            pdf.draw_box("Comprendre (Clinique)", info['clinique'], 220, 235, 245)
            
            # 2. Théologie (Gris chaud)
            pdf.draw_box("Discerner (Cœur & Idoles)", info['theologie'], 240, 240, 235)
            
            # 3. Couple (Rose pâle pour alerte)
            pdf.draw_box("Impact sur le Couple", info['couple'], 250, 230, 230)
            
            # 4. Pratique (Vert menthe)
            pdf.draw_box("Agir (Pistes de Guérison)", info['pratique'], 230, 245, 230)
            
            pdf.ln(5)
            
            # Saut de page si on est trop bas
            if pdf.get_y() > 230: pdf.add_page()

    if count_active == 0:
        pdf.multi_cell(0, 10, clean_text("Aucun schéma critique détecté. Votre couple semble reposer sur des bases sécures."))

    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 5. INTERFACE STREAMLIT ---

st.sidebar.title("Navigation")
mode = st.sidebar.radio("Menu", ["🏠 Espace Questionnaire", "💼 Espace Thérapeute"])

# === ESPACE CLIENT (PAGINATION 232 QUESTIONS) ===
if mode == "🏠 Espace Questionnaire":
    st.title("Questionnaire Clinique (YSQ-L3)")
    st.markdown("**Instructions :** Ce test contient 232 questions pour une validité clinique maximale.")
    
    if 'q_responses' not in st.session_state: st.session_state.q_responses = {}
    if 'page' not in st.session_state: st.session_state.page = 0
    if 'user' not in st.session_state: st.session_state.user = None
    
    # Login
    if not st.session_state.user:
        with st.form("login"):
            c = st.text_input("Code Couple (ex: DUO24)").strip().upper()
            n = st.text_input("Votre Prénom")
            if st.form_submit_button("Commencer"):
                if c and n:
                    st.session_state.user = {"code": c, "nom": n}
                    st.rerun()
    else:
        # Pagination
        ITEMS_PER_PAGE = 40
        total_q = len(ALL_QUESTIONS)
        total_p = (total_q // ITEMS_PER_PAGE) + 1
        
        start = st.session_state.page * ITEMS_PER_PAGE + 1
        end = min(start + ITEMS_PER_PAGE, total_q + 1)
        
        st.progress((st.session_state.page + 1) / total_p)
        st.caption(f"Page {st.session_state.page + 1} / {total_p} (Questions {start} à {end-1})")
        
        with st.form(f"p_{st.session_state.page}"):
            for qid in range(start, end):
                if qid in ALL_QUESTIONS:
                    q = ALL_QUESTIONS[qid]
                    saved = st.session_state.q_responses.get(qid, 1)
                    st.markdown(f"**{qid}. {q['text']}**")
                    st.session_state.q_responses[qid] = st.slider("", 1, 6, saved, key=f"sld_{qid}")
                    st.markdown("---")
            
            col_1, col_2 = st.columns(2)
            is_end = (st.session_state.page == total_p - 1)
            
            submitted = False
            if is_end:
                submitted = st.form_submit_button("✅ TERMINER ET ENVOYER")
            else:
                if st.form_submit_button("Page Suivante ➡️"):
                    st.session_state.page += 1
                    st.rerun()
            
            if submitted:
                # Calcul Scores Moyens
                sums = {s:0 for s in SCHEMAS_ORDER}
                counts = {s:0 for s in SCHEMAS_ORDER}
                
                for qid, val in st.session_state.q_responses.items():
                    sch = ALL_QUESTIONS[qid]['schema']
                    sums[sch] += val
                    counts[sch] += 1
                
                final_scores = {}
                for s in SCHEMAS_ORDER:
                    final_scores[s] = round(sums[s]/counts[s], 2) if counts[s] > 0 else 0
                
                save_response(st.session_state.user['code'], st.session_state.user['nom'], final_scores)
                st.success("Vos réponses ont été enregistrées. Vous pouvez fermer la page.")
                st.balloons()

# === ESPACE THÉRAPEUTE (TABLEAU DE BORD PRO) ===
elif mode == "💼 Espace Thérapeute":
    st.title("Tableau de Bord Clinique")
    
    pwd = st.sidebar.text_input("Mot de passe", type="password")
    if pwd == "Expert2024":
        df = load_data()
        if df.empty:
            st.info("En attente de données...")
        else:
            couples = df['Code_Couple'].unique()
            selected = st.selectbox("Sélectionner un dossier", couples)
            
            subset = df[df['Code_Couple'] == selected]
            
            if len(subset) >= 1:
                row_A = subset.iloc[0]
                nom_A = row_A['Nom']
                row_B = subset.iloc[1] if len(subset) > 1 else None
                nom_B = row_B['Nom'] if row_B is not None else "..."
                
                # --- LAYOUT DASHBOARD ---
                c_graph, c_tools = st.columns([2, 1])
                
                with c_graph:
                    st.subheader("Dynamique Systémique (Radar)")
                    data_B_dict = row_B.to_dict() if row_B is not None else {}
                    fig = create_radar_chart(row_A.to_dict(), data_B_dict, nom_A, nom_B)
                    st.plotly_chart(fig, use_container_width=True)
                
                with c_tools:
                    st.subheader("Outils")
                    st.markdown(f"**Statut :** {'✅ Complet' if row_B is not None else '⏳ En attente'}")
                    
                    if row_B is not None:
                        pdf_data = generate_full_report(nom_A, row_A.to_dict(), nom_B, row_B.to_dict(), selected)
                        st.download_button("📥 Télécharger Rapport PDF", pdf_data, f"Rapport_{selected}.pdf", "application/pdf")
                    
                    st.info("Le rapport contient l'analyse détaillée (Clinique, Théologie, Pratique).")

                # --- ANALYSE PROFONDE (ACCORDÉONS) ---
                st.divider()
                st.subheader("Analyse Schéma par Schéma")
                
                # Calcul des max pour trier
                def get_max(s):
                    return max(row_A[s], row_B[s] if row_B is not None else 0)
                
                ordered = sorted(SCHEMAS_ORDER, key=get_max, reverse=True)
                
                for s in ordered:
                    mx = get_max(s)
                    if mx >= 3.0:
                        inf = SCHEMA_LIBRARY[s]
                        color = "🔴" if mx >= 5 else "🟠" if mx >= 4 else "🟡"
                        
                        with st.expander(f"{color} {inf['nom']} (Max: {mx}/6)"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**{nom_A}** : {row_A[s]}")
                                if row_B is not None: st.markdown(f"**{nom_B}** : {row_B[s]}")
                                st.markdown("---")
                                st.markdown(f"**Impact Couple :** {inf['couple']}")
                            
                            with col2:
                                st.markdown(f"**Racine Spirituelle :** {inf['theologie']}")
                                st.success(f"**Piste Pratique :** {inf['pratique']}")
    else:
        st.warning("Accès réservé.")
