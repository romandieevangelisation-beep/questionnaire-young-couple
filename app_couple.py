import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import os
import tempfile
import re

# Lib Word (Optionnel)
try:
    from docx import Document
except ImportError:
    pass

# --- 0. CONFIGURATION ---
st.set_page_config(page_title="Alliance & Schémas - Ultimate", layout="wide", page_icon="✝️")
DB_FILE = "reponses_couple_ultimate.csv"

# --- 1. LE CERVEAU : BASE DE DONNÉES CLINIQUE, THÉOLOGIQUE & PASTORALE ---
# Structure fusionnée : Clinique | Couple | Théologie | Vérité Biblique | Conseil Pastoral | Pratique | Prière

SCHEMA_LIBRARY = {
    "ca": {
        "nom": "Carence Affective",
        "clinique": "Sentiment profond que ses besoins de soutien, d'affection et d'empathie ne seront jamais comblés.",
        "couple": "Le 'Trou Noir'. Vous attendez que l'autre devine vos besoins (télépathie). S'il échoue, vous le punissez par le silence ou la froideur.",
        "theologie": "Croyance mensongère d'être invisible aux yeux du Père. C'est le syndrome de l'orphelin spirituel.",
        "verite_biblique": "« D'un amour éternel, je t'ai aimé. » (Jérémie 31:3)",
        "conseil_pastoral": "L'invitation chrétienne est d'oser la vulnérabilité. Votre conjoint n'est pas omniscient. Exprimez vos besoins sans accuser.",
        "pratique": "Exercice : Demandez clairement un besoin ('J'ai besoin d'un câlin') sans attendre qu'il le devine.",
        "priere": "Seigneur, donne-moi le courage de dire 'j'ai besoin' sans colère. Comble mon cœur pour que je n'exige pas l'impossible de mon conjoint."
    },
    "ab": {
        "nom": "Abandon / Instabilité",
        "clinique": "Peur intense et envahissante que les proches partent, meurent ou trouvent mieux ailleurs.",
        "couple": "Le 'Velcro'. Jalousie, possessivité, besoin constant de réassurance. Cela étouffe le conjoint qui finit par reculer pour respirer.",
        "theologie": "Une difficulté à intégrer la permanence de l'Amour de Dieu. Idolâtrie de la sécurité relationnelle humaine.",
        "verite_biblique": "« Je ne te délaisserai point, je ne t'abandonnerai point. » (Hébreux 13:5)",
        "conseil_pastoral": "Le défi est de passer de la 'peur du manque' à la 'confiance en l'Alliance'. Votre conjoint est limité, il ne peut pas combler le vide infini.",
        "pratique": "Apprendre la 'solitude habitée' avec Dieu. Arrêter les SMS de vérification compulsive.",
        "priere": "Seigneur, apaise mon cœur. Aide-moi à ne pas demander à mon conjoint d'être mon 'dieu' de sécurité."
    },
    "ma": {
        "nom": "Méfiance / Abus",
        "clinique": "Attente que les autres vont nuire, manipuler, humilier ou trahir. Hypervigilance constante.",
        "couple": "La 'Forteresse'. Vous interprétez les erreurs de l'autre comme des attaques malveillantes. Vous testez sa loyauté en permanence.",
        "theologie": "La blessure de Caïn. Le monde est vu comme une jungle hostile sans la protection de Dieu.",
        "verite_biblique": "« L'amour parfait bannit la crainte. » (1 Jean 4:18)",
        "conseil_pastoral": "Ce schéma verrouille le cœur. La guérison passe par le pardon progressif et le refus de la 'lecture de pensée'.",
        "pratique": "Oser une petite confiance vérifiable. Ne pas accuser l'autre d'intentions qu'il n'a pas verbalisées.",
        "priere": "Seigneur, guéris ma mémoire. Aide-moi à voir mon conjoint tel qu'il est aujourd'hui, et non à travers le filtre de mes blessures passées."
    },
    "is": {
        "nom": "Isolement Social",
        "clinique": "Sentiment d'être différent, de ne pas appartenir au groupe, d'être exclu ou inintéressant.",
        "couple": "Le 'Couple Ermite'. Vous isolez le couple en refusant la communauté. Vous demandez au conjoint d'être votre seul univers.",
        "theologie": "Refus de la Communion Fraternelle (Corps du Christ), souvent par honte ou orgueil caché.",
        "verite_biblique": "« Dieu donne une famille à ceux qui étaient abandonnés. » (Psaume 68:6)",
        "conseil_pastoral": "L'amour ne se vit pas en vase clos. Votre couple a besoin d'être irrigué par d'autres relations saines.",
        "pratique": "Inviter un autre couple ou rejoindre un groupe de maison. Pratiquer l'hospitalité.",
        "priere": "Seigneur, sors-moi de ma caverne. Montre-moi que j'ai ma place dans ta famille."
    },
    "im": {
        "nom": "Imperfection / Honte",
        "clinique": "Sentiment d'être intérieurement défectueux, mauvais, sans valeur. Peur d'être 'démasqué'.",
        "couple": "La 'Défensive'. Très susceptible à la critique. Vous contre-attaquez ou vous effondrez pour cacher votre 'honte'.",
        "theologie": "La Honte d'Adam. Difficulté à accepter la Justification par la Foi (Grâce). On veut 'payer' pour être aimé.",
        "verite_biblique": "« Il n'y a donc maintenant aucune condamnation pour ceux qui sont en Jésus-Christ. » (Romains 8:1)",
        "conseil_pastoral": "L'intimité, c'est 'être connu et être aimé'. Si vous cachez vos failles, vous ne pouvez pas vous sentir aimé pour qui vous êtes.",
        "pratique": "Pratiquer la transparence. Avouer une faiblesse sans se justifier.",
        "priere": "Seigneur, revêts-moi de ta justice. Que je n'aie plus besoin de me cacher ou de me défendre."
    },
    "ed": {
        "nom": "Échec",
        "clinique": "Croyance d'être moins capable que les autres, voué à l'échec professionnel ou personnel.",
        "couple": "L'Enfant incompétent'. Vous laissez le conjoint prendre toutes les décisions sérieuses, créant un déséquilibre parent/enfant.",
        "theologie": "L'Idole de la Réussite. Votre valeur est attachée à votre performance et non à votre adoption filiale.",
        "verite_biblique": "« C'est bien, bon et fidèle serviteur. » (Matthieu 25:21)",
        "conseil_pastoral": "Dieu ne regarde pas au succès mais à la fidélité. Reprenez votre place d'adulte responsable.",
        "pratique": "Prendre une responsabilité concrète par semaine (budget, papiers) sans demander de l'aide.",
        "priere": "Seigneur, libère-moi de la comparaison. Que je trouve ma valeur en Toi seul."
    },
    "da": {
        "nom": "Dépendance / Incompétence",
        "clinique": "Incapacité à gérer la vie quotidienne sans aide. Se sent comme un enfant dans un monde d'adultes.",
        "couple": "Le 'Fardeau'. L'un porte tout, l'autre suit. Cela tue le désir sexuel (on ne désire pas un enfant) et épuise le porteur.",
        "theologie": "Refus du mandat d'Intendant. Recherche d'un sauveur humain à la place de l'Esprit Saint.",
        "verite_biblique": "« Ce n'est pas un esprit de timidité que Dieu nous a donné, mais un esprit de force. » (2 Timothée 1:7)",
        "conseil_pastoral": "Grandir est un commandement spirituel. Votre conjoint a besoin d'un partenaire, pas d'une charge.",
        "pratique": "Prendre des décisions autonomes quotidiennes sans demander validation.",
        "priere": "Seigneur, donne-moi la force de porter ma propre charge et de marcher debout."
    },
    "vu": {
        "nom": "Vulnérabilité au Danger",
        "clinique": "Peur irrationnelle et constante qu'une catastrophe (maladie, argent, accident) va survenir.",
        "couple": "La 'Prison de Sécurité'. Vous empêchez le couple de vivre, de voyager, d'investir. Le conjoint devient un garde du corps.",
        "theologie": "Manque de foi en la Providence. C'est un 'athéisme pratique' (vivre comme si Dieu ne contrôlait rien).",
        "verite_biblique": "« Ne vous inquiétez de rien; mais en toute chose faites connaître vos besoins à Dieu. » (Philippiens 4:6)",
        "conseil_pastoral": "L'inquiétude ne change rien à demain, mais elle vide aujourd'hui de sa force.",
        "pratique": "Transformer chaque pensée de peur en prière. Exposition progressive aux risques.",
        "priere": "Seigneur, je te remets mes peurs. Je choisis de croire que ma vie est dans tes mains."
    },
    "fu": {
        "nom": "Fusion / Personnalité Atrophiée",
        "clinique": "Pas d'identité propre, sentiments en miroir. Si l'autre est triste, vous êtes dévasté.",
        "couple": "Le 'Siamois'. Étouffement mutuel. Aucune intimité réelle car il n'y a pas deux personnes distinctes.",
        "theologie": "Idolâtrie relationnelle. Ne pas avoir 'quitté son père et sa mère' (Genèse 2:24) pour s'attacher.",
        "verite_biblique": "« C'est pour la liberté que Christ nous a affranchis. » (Galates 5:1)",
        "conseil_pastoral": "Pour s'unir, il faut être deux. La différenciation est nécessaire à l'amour.",
        "pratique": "Développer des hobbies séparés. Utiliser 'Je' au lieu de 'Nous'.",
        "priere": "Seigneur, aide-moi à exister devant Toi pour pouvoir aimer l'autre librement."
    },
    "ass": {
        "nom": "Assujettissement",
        "clinique": "Soumission excessive par peur du conflit ou du rejet. On dit 'oui' alors qu'on pense 'non'.",
        "couple": "La 'Cocotte-Minute'. Vous accumulez la rancœur en silence, puis vous explosez ou devenez passif-agressif.",
        "theologie": "Crainte de l'homme (Proverbes 29:25). On achète une fausse paix au prix de la Vérité.",
        "verite_biblique": "« Si je plaisais encore aux hommes, je ne serais pas serviteur de Christ. » (Galates 1:10)",
        "conseil_pastoral": "La paix à tout prix n'est pas la paix de Dieu. Dire la vérité dans l'amour est un acte spirituel.",
        "pratique": "Apprendre à dire 'Non' gentiment. Exprimer ses préférences (restaurant, film).",
        "priere": "Seigneur, délivre-moi de la peur de déplaire. Que mon 'Oui' soit un vrai Oui."
    },
    "ss": {
        "nom": "Sacrifice de Soi",
        "clinique": "Se concentrer excessivement sur les besoins des autres au détriment des siens (Syndrome du Sauveur).",
        "couple": "Le 'Martyr'. Vous donnez tout, vous vous épuisez, puis vous culpabilisez le conjoint de ne pas en faire autant.",
        "theologie": "Confusion entre 'aimer son prochain' et 'se nier par peur'. Orgueil caché de vouloir être le Messie.",
        "verite_biblique": "« Tu aimeras ton prochain comme toi-même. » (Marc 12:31)",
        "conseil_pastoral": "Le service chrétien est un choix libre, pas une dette. Si votre coupe est vide, vous ne donnez que du vent.",
        "pratique": "Sabbat obligatoire (repos). Accepter de recevoir sans rendre immédiatement.",
        "priere": "Seigneur, aide-moi à discerner quand je sers par amour et quand je sers par peur."
    },
    "ie": {
        "nom": "Inhibition Émotionnelle",
        "clinique": "Verrouillage des émotions, froideur, rationalité excessive par peur de perdre le contrôle.",
        "couple": "Le 'Mur de Glace'. La relation devient fonctionnelle et administrative. Le conjoint se sent seul.",
        "theologie": "Stoïcisme vs Incarnation. Jésus a pleuré. Refus de la condition humaine sensible créée par Dieu.",
        "verite_biblique": "« Je vous donnerai un cœur nouveau, j'ôterai de votre corps le cœur de pierre. » (Ézéchiel 36:26)",
        "conseil_pastoral": "Les émotions sont le langage du cœur. Sans elles, il n'y a pas de connexion profonde.",
        "pratique": "Partager une joie et une peine chaque jour. Ne pas rationaliser les émotions de l'autre.",
        "priere": "Seigneur, brise ma carapace. Donne-moi un cœur de chair capable de ressentir avec Toi."
    },
    "is_std": {
        "nom": "Exigences Élevées",
        "clinique": "Perfectionnisme rigide. Jamais satisfait. Critique constante envers soi et les autres.",
        "couple": "Le 'Juge'. Le conjoint vit sous pression constante de ne pas être à la hauteur et finit par démissionner.",
        "theologie": "Une forme d'idolâtrie de la performance et un refus de la Grâce. Pharisaïsme.",
        "verite_biblique": "« Car c'est par la grâce que vous êtes sauvés... cela ne vient pas de vous. » (Éphésiens 2:8)",
        "conseil_pastoral": "L'invitation est de lâcher prise. Acceptez l'imperfection de votre conjoint comme une école de grâce.",
        "pratique": "Célébrer ce qui est 'assez bien'. S'abstenir de corriger l'autre pendant une semaine.",
        "priere": "Seigneur, délivre-moi de l'orgueil de croire que tout dépend de ma perfection."
    },
    "dt": {
        "nom": "Droits Personnels / Grandeur",
        "clinique": "Sentiment de supériorité, d'être spécial. Manque d'empathie. Colère si frustré.",
        "couple": "Le 'Tyran'. Le conjoint est traité comme un objet utilitaire. Aucune réciprocité.",
        "theologie": "Orgueil pur (le péché originel). Refus de la condition de serviteur.",
        "verite_biblique": "« Que l'humilité vous fasse regarder les autres comme étant au-dessus de vous-mêmes. » (Philippiens 2:3)",
        "conseil_pastoral": "L'amour ne cherche pas son propre intérêt. Redécouvrez la joie du service caché.",
        "pratique": "Actes de service anonymes. Se demander : 'Comment se sent l'autre en face de moi ?'.",
        "priere": "Seigneur, brise mon orgueil. Donne-moi un cœur de serviteur comme Jésus."
    },
    "ci": {
        "nom": "Contrôle de Soi Insuffisant",
        "clinique": "Impulsivité, intolérance à la frustration, procrastination. Difficulté à se discipliner.",
        "couple": "L'Enfant Capricieux'. On ne peut pas compter sur vous. Parole blessante lâchée sous le coup de l'émotion.",
        "theologie": "Esclavage des pulsions (le 'Ventre'). Manque de fruit de l'Esprit (Maîtrise de soi).",
        "verite_biblique": "« Comme une ville forcée et sans murailles, ainsi est l'homme qui n'est pas maître de lui-même. » (Proverbes 25:28)",
        "conseil_pastoral": "La liberté n'est pas de faire ce qu'on veut, mais de faire ce qui est bon.",
        "pratique": "Apprendre la tolérance à la frustration (Jeûne). Compter jusqu'à 10 avant de réagir.",
        "priere": "Seigneur, sois le Maître de mes désirs. Donne-moi la maîtrise de moi par ton Esprit."
    },
    "rc": {
        "nom": "Recherche d'Approbation",
        "clinique": "Estime de soi dépendante du regard des autres. Caméléon social.",
        "couple": "L'Acteur'. Vous changez de personnalité selon le public. Le conjoint ne sait plus qui vous êtes vraiment.",
        "theologie": "Idolâtrie de la Gloire humaine. On préfère la louange des hommes à celle de Dieu.",
        "verite_biblique": "« Comment pouvez-vous croire, vous qui tirez votre gloire les uns des autres ? » (Jean 5:44)",
        "conseil_pastoral": "Votre valeur a été fixée à la Croix. Elle ne dépend pas des 'likes' ou des compliments.",
        "pratique": "Faire le bien en secret (Matthieu 6). Oser une opinion impopulaire mais vraie.",
        "priere": "Seigneur, que ton regard me suffise. Guéris-moi du besoin maladif de plaire."
    },
    "neg": {
        "nom": "Négativisme / Pessimisme",
        "clinique": "Focalisation sur le négatif (douleur, risque, perte). Inquiétude chronique.",
        "couple": "Le 'Rabat-joie'. Vous éteignez l'enthousiasme du conjoint. Ambiance lourde et plaignante.",
        "theologie": "Ingratitude et Manque d'Espérance. Cécité face à la bonté de Dieu dans le quotidien.",
        "verite_biblique": "« Rendez grâces en toutes choses, car c'est à votre égard la volonté de Dieu. » (1 Thess 5:18)",
        "conseil_pastoral": "La plainte obscurcit le regard. La louange le clarifie.",
        "pratique": "Tenir un journal de gratitude (3 choses par jour). S'interdire de se plaindre pendant 24h.",
        "priere": "Seigneur, ouvre mes yeux à tes bontés. Change mes plaintes en louanges."
    },
    "pu": {
        "nom": "Punition",
        "clinique": "Intolérance, critique, tendance à punir durement les erreurs (soi et les autres).",
        "couple": "Le 'Bourreau'. Rancunier. Vous sortez les vieux dossiers lors des disputes. Climat de peur.",
        "theologie": "Légalisme. Refus de la Miséricorde. Oubli de sa propre dette infinie envers Dieu.",
        "verite_biblique": "« Soyez bons... vous pardonnant réciproquement, comme Dieu vous a pardonné en Christ. » (Éphésiens 4:32)",
        "conseil_pastoral": "Pardonner, c'est renoncer à se venger. La grâce est un scandale, mais c'est notre seul espoir.",
        "pratique": "Méditer la parabole du débiteur impitoyable. Faire un geste de grâce envers une erreur de l'autre.",
        "priere": "Seigneur, aide-moi à relâcher la dette. Que je sois un canal de ta miséricorde."
    }
}
SCHEMAS_ORDER = list(SCHEMA_LIBRARY.keys())

# --- 2. ENGINE : MAPPING EXACT (PETER PAN) ---
def get_schema_map_ordered():
    m = []
    m.extend(['ca'] * 9); m.extend(['ab'] * 17); m.extend(['ma'] * 17); m.extend(['is'] * 10)
    m.extend(['im'] * 15); m.extend(['ed'] * 9); m.extend(['da'] * 15); m.extend(['vu'] * 12)
    m.extend(['fu'] * 11); m.extend(['ass'] * 10); m.extend(['ss'] * 17); m.extend(['ie'] * 9)
    m.extend(['is_std'] * 16); m.extend(['dt'] * 11); m.extend(['ci'] * 15); m.extend(['rc'] * 14)
    m.extend(['neg'] * 15); m.extend(['pu'] * 10)
    return m

def parse_imported_text(text):
    matches = re.findall(r"\[(\d)/6\]", text)
    if not matches: return None, "Aucune note [x/6] trouvée."
    scores = [int(x) for x in matches]
    mapping = get_schema_map_ordered()
    limit = min(len(scores), len(mapping))
    sums = {s:0 for s in SCHEMAS_ORDER}; cnts = {s:0 for s in SCHEMAS_ORDER}
    for i in range(limit):
        sch = mapping[i]; sums[sch] += scores[i]; cnts[sch] += 1
    final = {s: (round(sums[s]/cnts[s], 2) if cnts[s]>0 else 0) for s in SCHEMAS_ORDER}
    return final, f"Succès ({limit} réponses)."

# --- 3. UTILS & DATA ---
def clean_text(text):
    if not isinstance(text, str): return str(text)
    replacements = {"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "…": "...", "œ": "oe", "«": '"', "»": '"', "€": "EUR"}
    for k,v in replacements.items(): text = text.replace(k,v)
    return text.encode('latin-1', 'replace').decode('latin-1')

def load_data():
    if os.path.exists(DB_FILE): return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Code_Couple", "Nom", "Date"] + SCHEMAS_ORDER)

def save_response(code, nom, scores):
    df = load_data()
    new_row = {"Code_Couple": code, "Nom": nom, "Date": datetime.now().strftime("%Y-%m-%d")}
    new_row.update(scores)
    df = df[~((df['Code_Couple'] == code) & (df['Nom'] == nom))]
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(DB_FILE, index=False)

def create_radar(d_A, d_B, n_A, n_B):
    cats = [SCHEMA_LIBRARY[s]['nom'] for s in SCHEMAS_ORDER]
    v_A = [d_A.get(s,0) for s in SCHEMAS_ORDER]; v_A += [v_A[0]]
    v_B = [d_B.get(s,0) for s in SCHEMAS_ORDER]; v_B += [v_B[0]]
    cats += [cats[0]]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=v_A, theta=cats, fill='toself', name=n_A, line_color='#2980b9'))
    fig.add_trace(go.Scatterpolar(r=v_B, theta=cats, fill='toself', name=n_B, line_color='#e74c3c'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 6])), template="plotly_white", margin=dict(t=30, b=30, l=40, r=40))
    return fig

# --- 4. PDF GENERATOR ---
class PDFExpert(FPDF):
    def header(self):
        self.set_fill_color(44, 62, 80); self.rect(0, 0, 210, 35, 'F')
        self.set_font('Arial', 'B', 22); self.set_text_color(255)
        self.set_xy(10, 10); self.cell(0, 10, clean_text("ALLIANCE & SCHEMAS"), 0, 1)
        self.set_font('Arial', 'I', 11); self.cell(0, 10, clean_text("Rapport Clinique & Pastoral"), 0, 1)
        self.ln(10)
    def footer(self):
        self.set_y(-15); self.set_font('Arial', '', 8); self.set_text_color(128)
        self.cell(0, 10, clean_text(f"Page {self.page_no()}"), 0, 0, 'C')
    def draw_box(self, title, content, r, g, b):
        self.set_fill_color(r, g, b); self.set_font('Arial', 'B', 11); self.set_text_color(0)
        self.cell(0, 8, clean_text(f"  {title}"), 0, 1, 'L', 1)
        self.set_font('Arial', '', 10); self.set_text_color(50)
        self.multi_cell(0, 6, clean_text(content), border='L'); self.ln(3)

def generate_pdf(nA, dA, nB, dB, code):
    pdf = PDFExpert(); pdf.set_auto_page_break(True, 15); pdf.add_page()
    pdf.set_font('Arial', 'B', 16); pdf.set_text_color(0)
    pdf.cell(0, 10, clean_text(f"Dossier : {code}"), 0, 1)
    pdf.set_font('Arial', '', 12); pdf.cell(0, 8, clean_text(f"Couple : {nA} & {nB}"), 0, 1); pdf.ln(5)
    
    try:
        fig = create_radar(dA, dB, nA, nB)
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as t:
            fig.write_image(t.name, format="png", width=800, height=600, scale=2, engine="kaleido")
            pdf.image(t.name, x=15, y=60, w=180)
        pdf.set_y(220)
    except: pdf.cell(0, 10, "[Graphique manquant]", 0, 1)

    pdf.add_page(); pdf.set_font('Arial', 'B', 18); pdf.set_text_color(41, 128, 185)
    pdf.cell(0, 10, clean_text("ANALYSE DETAILLEE"), 0, 1); pdf.ln(5)
    
    def get_max(s): return max(dA.get(s,0), dB.get(s,0))
    ordered = sorted(SCHEMAS_ORDER, key=get_max, reverse=True)
    
    for s in ordered:
        mx = get_max(s)
        if mx >= 3.0:
            inf = SCHEMA_LIBRARY[s]
            pdf.ln(5); pdf.set_font('Arial', 'B', 14); pdf.set_text_color(192, 57, 43)
            icon = "(!)" if mx >= 5 else ""
            pdf.cell(0, 10, clean_text(f"{inf['nom'].upper()} {icon}"), 0, 1)
            pdf.set_font('Arial', 'B', 10); pdf.set_text_color(100)
            pdf.cell(0, 6, clean_text(f"Scores: {nA}={dA.get(s,0)} | {nB}={dB.get(s,0)}"), 0, 1); pdf.ln(2)
            
            pdf.draw_box("Dimension Clinique", inf['clinique'], 235, 245, 251)
            pdf.draw_box("Impact sur le Couple", inf['couple'], 253, 237, 236)
            pdf.draw_box("Racine Spirituelle", inf['theologie'], 245, 245, 245)
            pdf.draw_box("Conseil Pastoral", inf['conseil_pastoral'], 233, 247, 239)
            pdf.draw_box("Piste Pratique", inf['pratique'], 240, 255, 240)
            
            pdf.set_font('Arial', 'I', 10); pdf.set_text_color(39, 174, 96)
            pdf.multi_cell(0, 6, clean_text(f"Prière : {inf['priere']}")); pdf.ln(1)
            pdf.multi_cell(0, 6, clean_text(f"Vérité Biblique : {inf['versetite_biblique'] if 'verite_biblique' in inf else inf.get('verset','')}")); pdf.ln(5)
    return pdf.output(dest='S').encode('latin-1', 'replace')

# --- 5. INTERFACE THERAPEUTE (AVEC COLONNES & COULEURS) ---
st.sidebar.title("Navigation")
mode = st.sidebar.radio("Mode", ["🏠 Questionnaire", "💼 Espace Expert"])

if mode == "🏠 Questionnaire":
    st.title("Questionnaire")
    st.info("Utilisez l'espace expert pour importer.")

elif mode == "💼 Espace Expert":
    st.title("Tableau de Bord Expert")
    pwd = st.sidebar.text_input("Mot de passe", type="password")
    
    if pwd == "Expert2024":
        # IMPORT TEXTE
        with st.expander("📥 IMPORTER (Copier-Coller)", expanded=True):
            c1, c2 = st.columns(2)
            nA = c1.text_input("Nom A"); tA = c1.text_area("Contenu A", height=100)
            nB = c2.text_input("Nom B"); tB = c2.text_area("Contenu B", height=100)
            code = st.text_input("Code Dossier").strip().upper()
            if st.button("Analyser"):
                if tA and tB and code:
                    sA, mA = parse_imported_text(tA); sB, mB = parse_imported_text(tB)
                    if sA and sB:
                        save_response(code, nA, sA); save_response(code, nB, sB)
                        st.success("Dossier créé !"); st.write(mA, mB)
                    else: st.error("Erreur de format.")

        # DASHBOARD
        st.divider()
        df = load_data()
        if not df.empty:
            sel = st.selectbox("Dossier", df['Code_Couple'].unique())
            sub = df[df['Code_Couple']==sel]
            if len(sub)>=2:
                rA = sub.iloc[0]; rB = sub.iloc[1]
                nom_A = rA['Nom']; nom_B = rB['Nom']
                
                # RADAR & PDF
                c1, c2 = st.columns([2,1])
                with c1: st.plotly_chart(create_radar(rA.to_dict(), rB.to_dict(), nom_A, nom_B), use_container_width=True)
                with c2:
                    st.write("### Outils")
                    pdf = generate_pdf(nom_A, rA.to_dict(), nom_B, rB.to_dict(), sel)
                    st.download_button("📥 Télécharger Rapport PDF", pdf, f"Rap_{sel}.pdf", "application/pdf")

                # ANALYSE TYPE "COLONNES" (Style demandé)
                st.markdown("---")
                st.subheader("Analyse Clinique & Pastorale")
                
                def get_max(s): return max(rA[s], rB[s])
                ordered = sorted(SCHEMAS_ORDER, key=get_max, reverse=True)
                
                # Seuil critique demandé (5 ou 6)
                for s in ordered:
                    mx = get_max(s)
                    if mx >= 3: # On affiche à partir de 3
                        inf = SCHEMA_LIBRARY[s]
                        
                        # Qui est touché ? (Score >= 4 pour être mentionné)
                        qui = []
                        if rA[s] >= 4: qui.append(f"{nom_A} ({rA[s]})")
                        if rB[s] >= 4: qui.append(f"{nom_B} ({rB[s]})")
                        txt_acteurs = " & ".join(qui) if qui else "Faible intensité"
                        
                        # Couleur & Icône selon sévérité
                        if mx >= 5: # CRITIQUE (5-6)
                            color_icon = "🔴"
                            label = f"ZONE CRITIQUE : {inf['nom'].upper()} ({txt_acteurs})"
                            is_expanded = True
                        else: # MOYEN (3-4)
                            color_icon = "🟠"
                            label = f"Schéma Actif : {inf['nom']} (Max: {mx})"
                            is_expanded = False
                        
                        with st.expander(f"{color_icon} {label}", expanded=is_expanded):
                            # MISE EN PAGE 2 COLONNES (Style Original Retrouvé)
                            col_clin, col_theo = st.columns(2)
                            
                            with col_clin:
                                st.markdown("#### 🧠 Dimension Clinique")
                                st.write(f"**Le mécanisme :** {inf['clinique']}")
                                st.write(f"**Impact Couple :** {inf['couple']}")
                                if mx >= 5:
                                    st.warning(f"⚠️ Ce schéma est très intense (>5). Il risque de dicter les réactions de {txt_acteurs} de manière automatique.")
                            
                            with col_theo:
                                st.markdown("#### 🕊️ Dimension Pastorale")
                                st.write(f"**Racine Spirituelle :** {inf['theologie']}")
                                st.success(f"💡 **Conseil :** {inf['conseil_pastoral']}")
                                st.info(f"🛠️ **Pratique :** {inf['pratique']}")
                            
                            # Pied de page de l'expander (Prière & Verset)
                            st.markdown("---")
                            c_p, c_v = st.columns(2)
                            with c_p: st.markdown(f"**🙏 Prière :** *{inf['priere']}*")
                            with c_v: st.markdown(f"**📖 Vérité :** *{inf['verite_biblique']}*")

                # COLLISIONS
                st.markdown("---"); st.subheader("⚠️ Collisions Systémiques")
                collision = False
                if rA['ab']>=4 and rB['is_std']>=4: st.error(f"⚔️ **Abandon vs Exigence :** {nom_A} cherche la réassurance, {nom_B} met de la distance/critique."); collision=True
                if rB['ab']>=4 and rA['is_std']>=4: st.error(f"⚔️ **Abandon vs Exigence :** {nom_B} cherche la réassurance, {nom_A} met de la distance/critique."); collision=True
                if not collision: st.info("Pas de collision majeure détectée.")
