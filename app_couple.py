import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from fpdf import FPDF
import os
import tempfile

# --- CONFIGURATION ---
st.set_page_config(page_title="Alliance & Vérité - Outil Thérapeutique", layout="wide", page_icon="✝️")
DB_FILE = "reponses_couple_expert_v3.csv"

# --- 1. BASE DE DONNÉES "COUNSELING BIBLIQUE" & CLINIQUE ---

SCHEMA_DETAILS = {
    "ab": {
        "nom": "Abandon / Instabilite",
        "clinique": "Perception de l'instabilité de tout lien affectif. Peur viscérale que l'autre parte.",
        "idole": "L'Idole de la Sécurité Relationnelle. Je demande à la créature de m'offrir la fidélité absolue que seul le Créateur possède.",
        "couple": "Le cycle Agrippement/Fuite. Plus je serre l'autre par peur (jalousie, contrôle), plus l'autre étouffe et s'éloigne, confirmant ma peur.",
        "verset": "« Je ne te délaisserai point, et je ne t'abandonnerai point. » (Hébreux 13:5)",
        "pratique": "Apprendre à 'lâcher prise' sur le conjoint en s'ancrant dans l'Alliance éternelle. Exercice : tolérer l'absence sans panique."
    },
    "ma": {
        "nom": "Mefiance / Abus",
        "clinique": "Attente d'être blessé, manipulé ou trahi. Hypervigilance.",
        "idole": "L'Idole de l'Auto-Protection. Je suis mon propre rempart car je ne crois pas que Dieu soit un Refuge sûr.",
        "couple": "La Forteresse. Je teste la loyauté de l'autre en permanence. J'interprète ses erreurs comme des attaques. L'intimité est impossible.",
        "verset": "« Il est un bouclier pour tous ceux qui se confient en lui. » (Psaume 18:30)",
        "pratique": "Confesser le cynisme. Oser une petite confiance vérifiable. Ne pas faire de procès d'intention."
    },
    "ca": {
        "nom": "Carence Affective",
        "clinique": "Certitude que mes besoins d'amour ne seront jamais comblés.",
        "idole": "Le 'Puits Percé'. Je cherche à combler ma soif infinie avec des relations humaines finies.",
        "couple": "L'Attente Muette. J'attends que l'autre devine mes besoins. S'il échoue, je le punis par le silence. L'autre s'épuise à essayer de remplir le vide.",
        "verset": "« Car mon peuple a commis un double péché: Ils m'ont abandonné, moi la source d'eau vive, pour se creuser des citernes crevassées. » (Jérémie 2:13)",
        "pratique": "Sortir de la passivité. Exprimer ses besoins clairement ('J'aimerais un câlin') sans exiger."
    },
    "is": {
        "nom": "Isolement Social",
        "clinique": "Sentiment d'être exclu, différent, de ne pas appartenir.",
        "idole": "La Peur de l'Homme. La validation du groupe est devenue plus importante que l'adoption par Dieu.",
        "couple": "Le Couple Ermite. Je refuse d'intégrer le couple dans une communauté. Je fais peser sur mon conjoint tout mon besoin social.",
        "verset": "« Vous n'êtes plus des étrangers, ni des gens du dehors; mais vous êtes concitoyens des saints. » (Éphésiens 2:19)",
        "pratique": "S'exposer progressivement au groupe (église, amis). Accepter que la différence n'est pas un rejet."
    },
    "im": {
        "nom": "Imperfection / Honte",
        "clinique": "Sentiment profond d'être défectueux, indigne d'amour.",
        "idole": "L'Orgueil Blessé. Je refuse d'être aimé par Grâce, je veux être aimé pour ma performance.",
        "couple": "Le Masque. Je cache mes faiblesses à mon conjoint de peur qu'il me rejette. Je suis hypersensible à la moindre critique.",
        "verset": "« Il m'a revêtu des vêtements du salut, il m'a couvert du manteau de la justice. » (Ésaïe 61:10)",
        "pratique": "Confesser ses fautes à l'autre pour briser le pouvoir de la honte. Recevoir le pardon."
    },
    "ed": {
        "nom": "Echec",
        "clinique": "Sentiment d'incompétence par rapport aux pairs.",
        "idole": "L'Idole du Succès. Ma valeur dépend de mes accomplissements visibles.",
        "couple": "L'Enfant Assisté. Je laisse mon conjoint gérer les domaines 'sérieux' (finances, admin) car je me sens nul. Je démissionne.",
        "verset": "« Ma grâce te suffit, car ma puissance s'accomplit dans la faiblesse. » (2 Corinthiens 12:9)",
        "pratique": "Redéfinir le succès : la fidélité dans les petites choses. Prendre une responsabilité concrète dans le foyer."
    },
    "da": {
        "nom": "Dependance / Incompetence",
        "clinique": "Incapacité à gérer le quotidien sans aide.",
        "idole": "Le Confort. Refus de porter sa charge d'adulte responsable devant Dieu.",
        "couple": "Le Parent/Enfant. Mon conjoint devient mon 'parent'. Cela tue le désir sexuel et crée du ressentiment chez celui qui porte tout.",
        "verset": "« Car chacun portera son propre fardeau. » (Galates 6:5)",
        "pratique": "Prendre des décisions seul. Accepter de se tromper sans s'effondrer."
    },
    "vu": {
        "nom": "Vulnerabilite au Danger",
        "clinique": "Peur catastrophe imminente (maladie, accident).",
        "idole": "Le Contrôle de la Vie. Refus de la souveraineté de Dieu sur la vie et la mort.",
        "couple": "La Prison Dorée. J'empêche le couple de vivre, de voyager, de sortir par peur. J'utilise l'autre comme garde du corps.",
        "verset": "« Qui de vous, par ses inquiétudes, peut ajouter une coudée à la durée de sa vie? » (Matthieu 6:27)",
        "pratique": "Calculer le coût de la peur. Remettre sa vie à Dieu chaque matin."
    },
    "fu": {
        "nom": "Fusion / Pers. Atrophiee",
        "clinique": "Absence d'identité propre, fusion avec l'autre.",
        "idole": "L'Idole Relationnelle. Je n'existe qu'à travers le regard de l'autre.",
        "couple": "Le Vampirisme. Je n'ai pas d'avis, pas de goût propre. Si l'autre va mal, je m'effondre. Je l'étouffe.",
        "verset": "« C'est pour la liberté que Christ nous a affranchis. » (Galates 5:1)",
        "pratique": "Développer des goûts personnels. Passer du temps séparément. Dire 'Je' sans culpabilité."
    },
    "ass": {
        "nom": "Assujettissement",
        "clinique": "Soumission excessive par peur de la colère ou du rejet.",
        "idole": "La Crainte de l'Homme. La paix à tout prix (fausse paix) plutôt que la Vérité.",
        "couple": "La Cocotte-Minute. Je dis 'oui' à tout mais je développe une amertume secrète. Je finis par exploser ou devenir passif-agressif.",
        "verset": "« Si je plaisais encore aux hommes, je ne serais pas serviteur de Christ. » (Galates 1:10)",
        "pratique": "Apprendre à dire 'Non' gentiment. Exprimer ses préférences même mineures."
    },
    "ss": {
        "nom": "Sacrifice de Soi",
        "clinique": "Satisfaction excessive des besoins d'autrui au détriment des siens.",
        "idole": "Le Messianisme. Je veux être le sauveur de mon conjoint, rôle réservé à Christ.",
        "couple": "Le Martyr. Je donne trop, je m'épuise, puis je reproche à l'autre son égoïsme. Je crée une dette.",
        "verset": "« C'est la miséricorde que je désire, et non les sacrifices. » (Osée 6:6)",
        "pratique": "Reconnaître ses limites humaines. Arrêter de donner pour 'acheter' l'amour."
    },
    "ie": {
        "nom": "Inhibition Emotionnelle",
        "clinique": "Contrôle excessif des émotions, rationalité froide.",
        "idole": "Le Stoïcisme. Croire que l'émotion est une faiblesse ou un danger.",
        "couple": "Le Mur de Glace. Mon conjoint se sent seul. Je ne partage ni ma joie ni ma peine. La relation est fonctionnelle.",
        "verset": "« Réjouissez-vous avec ceux qui se réjouissent; pleurez avec ceux qui pleurent. » (Romains 12:15)",
        "pratique": "Tenir un journal des émotions. Partager une émotion par jour avec le conjoint."
    },
    "is_std": { 
        "nom": "Exigences Elevees",
        "clinique": "Perfectionnisme, règles rigides, devoir.",
        "idole": "L'Auto-Justification. Je me sens juste quand tout est parfait. Je juge les autres selon ma Loi.",
        "couple": "Le Tribunal. Je critique sans cesse mon conjoint (ménage, éducation). Rien n'est jamais assez bien.",
        "verset": "« Car tous ont péché et sont privés de la gloire de Dieu. » (Romains 3:23)",
        "pratique": "Apprendre à célébrer l'imperfection. Remercier l'autre pour ce qu'il fait au lieu de pointer ce qu'il manque."
    },
    "dt": {
        "nom": "Droits Personnels / Grandiosite",
        "clinique": "Sentiment de supériorité, d'avoir tous les droits.",
        "idole": "L'Auto-Adoration. Je me prends pour le centre de l'univers. Les autres sont des outils.",
        "couple": "Le Tyran Domestique. Je n'ai aucune empathie. Si je ne suis pas servi, je punis. Je ne me remets pas en question.",
        "verset": "« Que l'humilité vous fasse regarder les autres comme étant au-dessus de vous-mêmes. » (Philippiens 2:3)",
        "pratique": "Service concret et humble (faire la vaisselle, sortir les poubelles) sans attendre de merci."
    },
    "ci": {
        "nom": "Controle de Soi Insuffisant",
        "clinique": "Impulsivité, incapacité à tolérer la frustration.",
        "idole": "L'Hédonisme (Le Plaisir Roi). Je veux tout, tout de suite. Je refuse la discipline.",
        "couple": "Le Chaos. On ne peut pas compter sur moi. Dépenses, colères, oublis. Je déstabilise la sécurité du foyer.",
        "verset": "« Comme une ville forcée et sans murailles, ainsi est l'homme qui n'est pas maître de lui-même. » (Proverbes 25:28)",
        "pratique": "Apprendre la frustration. Jeûne. Attendre 10 minutes avant de céder à une impulsion."
    },
    "rc": {
        "nom": "Recherche d'Approbation",
        "clinique": "Quête excessive de l'attention et de la validation.",
        "idole": "La Gloire Humaine. Je préfère la louange des hommes à celle de Dieu.",
        "couple": "L'Acteur. Je soigne mon image publique au détriment de ma relation privée. Je suis jaloux si mon conjoint brille plus que moi.",
        "verset": "« Comment pouvez-vous croire, vous qui tirez votre gloire les uns des autres? » (Jean 5:44)",
        "pratique": "Faire le bien en secret (Matthieu 6). Être authentique sur ses failles."
    },
    "neg": {
        "nom": "Negativisme / Pessimisme",
        "clinique": "Focus constant sur le négatif, l'inquiétude.",
        "idole": "L'Incrédulité. Refus de voir la bonté et la providence de Dieu dans le quotidien.",
        "couple": "Le Nuage Noir. Je plombe l'ambiance. Je décourage les projets de mon conjoint par mes « oui mais ».",
        "verset": "« Goûtez et voyez combien l'Éternel est bon! » (Psaume 34:8)",
        "pratique": "Journal de Gratitude : noter 3 grâces chaque soir. Interdiction de se plaindre pendant 24h."
    },
    "pu": {
        "nom": "Punition",
        "clinique": "Intolérance, jugement sévère, difficulté à pardonner.",
        "idole": "La Justice Propre. Je me prends pour le Juge Suprême. Je refuse de faire grâce.",
        "couple": "Le Bourreau. Je garde les fautes de l'autre en mémoire (liste noire). Je suis dur et rancunier. L'ambiance est glaciale.",
        "verset": "« Soyez bons les uns envers les autres, compatissants, vous pardonnant réciproquement, comme Dieu vous a pardonné en Christ. » (Éphésiens 4:32)",
        "pratique": "Méditer sur sa propre dette envers Dieu. Choisir de ne pas rappeler une faute passée lors d'une dispute."
    }
}

SCHEMAS_ORDER = list(SCHEMA_DETAILS.keys())

# --- 2. GÉNÉRATION DES 232 QUESTIONS (MAPPING) ---
# Pour simuler les 232 questions tout en restant gérable dans ce code,
# nous créons une fonction qui génère les questions par bloc.

def get_full_questionnaire():
    """
    Génère un dictionnaire de questions par schéma.
    Dans une version de prod, charger depuis un fichier JSON/CSV externe.
    Ici, nous mettons environ 5 à 10 questions clés par schéma pour la démonstration robuste.
    """
    q = {}
    
    # Exemples représentatifs (à étendre à 232 lignes réelles si vous avez le fichier texte)
    # Format: q['code'] = ["Question 1", "Question 2", ...]
    
    q['ab'] = [
        "Je m'inquiète beaucoup à l'idée que les gens que j'aime vont me quitter.",
        "J'ai besoin que les autres soient très proches de moi, sinon j'ai peur.",
        "Je tombe souvent amoureux de gens qui ne peuvent pas s'engager.",
        "Quand je sens que quelqu'un s'éloigne, je deviens désespéré.",
        "Je m'agrippe aux gens parce que j'ai peur d'être seul."
    ]
    q['ma'] = [
        "J'ai le sentiment qu'il faut se méfier des autres.",
        "Si je ne fais pas attention, les gens vont profiter de moi.",
        "Je teste souvent les gens pour voir s'ils sont vraiment de mon côté.",
        "J'ai beaucoup de mal à faire confiance à mon conjoint.",
        "Je suis sûr que les autres ont des arrières-pensées cachées."
    ]
    q['ca'] = [
        "Je n'ai pas reçu assez d'amour ou d'affection quand j'étais enfant.",
        "J'ai souvent l'impression que personne ne me comprend vraiment.",
        "Je me sens souvent vide émotionnellement.",
        "J'attends souvent que les autres devinent mes besoins.",
        "Je ne me sens pas spécial pour quelqu'un."
    ]
    # ... Pour que le code tienne ici, je complète les autres avec des placeholders génériques
    # mais vous pouvez coller ici vos 232 questions réelles.
    for s in SCHEMAS_ORDER:
        if s not in q:
            nom = SCHEMA_DETAILS[s]['nom']
            q[s] = [
                f"Question 1 spécifique au schéma {nom}",
                f"Question 2 spécifique au schéma {nom}",
                f"Question 3 spécifique au schéma {nom}",
                f"Question 4 spécifique au schéma {nom}",
                f"Question 5 spécifique au schéma {nom}"
            ]
    return q

QUESTIONS_DB = get_full_questionnaire()

# --- 3. FONCTIONS UTILITAIRES ---

def clean_text(text):
    if not isinstance(text, str): return str(text)
    replacements = {
        "’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-",
        "…": "...", "œ": "oe", "Œ": "Oe", "«": '"', "»": '"'
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text.encode('latin-1', 'replace').decode('latin-1')

def load_data():
    if os.path.exists(DB_FILE):
        return pd.read_csv(DB_FILE)
    return pd.DataFrame(columns=["Code_Couple", "Nom", "Role", "Date"] + SCHEMAS_ORDER)

def save_response(code, nom, responses_dict):
    df = load_data()
    # Calcul des moyennes par schéma
    averages = {}
    for schema, scores_list in responses_dict.items():
        if scores_list:
            averages[schema] = sum(scores_list) / len(scores_list)
        else:
            averages[schema] = 0
            
    new_row = {"Code_Couple": code, "Nom": nom, "Role": "Part
