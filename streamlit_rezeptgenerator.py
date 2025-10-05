# streamlit_rezeptgenerator.py
# KI-gestützter Rezept-Generator (Streamlit)
# Einfache, praktische Demo: verwendet OpenAI (wenn API-Key vorhanden), sonst ein regelbasiertes Fallback.

import streamlit as st
import os
import openai
from dotenv import load_dotenv
from typing import List

# Lade .env (falls vorhanden)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="KI Rezept-Generator", layout="centered")

st.title("KI-gestützter Rezept-Generator 🍳")
st.write("Gib die Zutaten ein, die du zu Hause hast — ich generiere dir kreative Rezepte dazu.")

# --- Eingaben ---
ingredients_input = st.text_area("Zutaten (Komma- oder Zeilen-getrennt)", placeholder="z.B. Kartoffeln, Zwiebel, Tomaten, Feta")
diet = st.selectbox("Ernährungspräferenz (optional)", ["Keine", "Vegetarisch", "Vegan", "Glutenfrei", "Laktosefrei", "Low-Carb"]) 
cuisine = st.text_input("Stil / Küche (optional)", placeholder="z.B. Italienisch, Mexikanisch, Asiatisch")
num_recipes = st.slider("Anzahl Rezepte", 1, 5, 3)
include_shopping = st.checkbox("Einkaufsliste für fehlende Hauptzutaten", value=True)

# --- Hilfsfunktionen ---

def parse_ingredients(text: str) -> List[str]:
    parts = [p.strip().lower() for p in text.replace('\n', ',').split(',')]
    return [p for p in parts if p]


def build_system_prompt(num_recipes: int) -> str:
    return ("Du bist ein hilfreicher Koch-Assistent. Du bekommst eine Liste von Zutaten,\n"
            "und sollst bis zu {n} kreative, praxistaugliche Rezepte vorschlagen, die möglichst nur\n"
            "die angegebenen Zutaten verwenden. Du darfst bis zu 2 übliche Vorratszutaten\n"
            "(z. B. Salz, Pfeffer, Öl, Wasser) hinzufügen. Für jedes Rezept liefere:\n"
            "- Titel und kurze Beschreibung\n"
            "- Zutatenliste (mit Mengen, wenn möglich)\n"
            "- Schritt-für-Schritt Zubereitung (nummeriert)\n"
            "- Geschätzte Zeit (Vorbereitung + Garzeit)\n"
            "- Wenn wichtige Zutaten fehlen, eine kurze Einkaufsliste\n\n"
            "Antworte auf Deutsch und verwende ein klares, praktisches Format.").format(n=num_recipes)


def build_user_prompt(ingredients: List[str], diet: str, cuisine: str, num_recipes: int) -> str:
    ing_text = ", ".join(ingredients) if ingredients else "keine Zutaten angegeben"
    diet_text = f"Ernährungspräferenz: {diet}." if diet and diet != "Keine" else ""
    cuisine_text = f"Küchenrichtung: {cuisine}." if cuisine else ""
    return (f"Zutaten: {ing_text}\n{diet_text} {cuisine_text}\n"
            f"Erstelle {num_recipes} Rezepte in Deutsch. Verwende möglichst nur die Zutaten. "
            "Wenn Mengen nicht angegeben sind, nenne sinnvolle Schätzmengen. Sei praktisch und kreativ.")


def call_openai_chat(system: str, user: str, model: str = "gpt-3.5-turbo") -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY nicht gesetzt.")
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]
    resp = openai.ChatCompletion.create(model=model, messages=messages, temperature=0.8, max_tokens=800)
    return resp.choices[0].message.content


# Einfacher Fallback, falls kein API-Key vorhanden ist

def simple_rule_based(ingredients: List[str], diet: str, cuisine: str, num_recipes: int) -> str:
    templates = [
        "Ofengericht mit {main}: Schneide {main} und kombiniere mit {others}. Würze mit Salz und Pfeffer, backe bei 200°C für 25-35 Minuten.",
        "Pfannengericht: Brate {main} mit {others} in etwas Öl. Füge Kräuter hinzu und serviere mit Brot oder Reis.",
        "Schnelle Suppe: Koche {main} und {others} in Wasser oder Brühe, püriere optional und schmecke ab."
    ]
    if not ingredients:
        ingredients = ["Kartoffeln", "Zwiebel"]
    mains = ingredients[0]
    others = ", ".join(ingredients[1:4]) if len(ingredients) > 1 else "Tomate"
    out = []
    for i in range(min(num_recipes, len(templates))):
        title = f"Rezept-Vorschlag {i+1}"
        body = templates[i].format(main=mains, others=others)
        ingr_list = "\n".join(f"- {ing}" for ing in ingredients)
        recipe = f"### {title}\n\n**Zutaten:**\n{ingr_list}\n\n**Zubereitung:**\n{body}\n"
        out.append(recipe)
    return "\n\n".join(out)


# --- UI / Ablauf ---

if st.button("Generiere Rezepte"):
    ingredients = parse_ingredients(ingredients_input)
    if not ingredients:
        st.warning("Bitte mindestens eine Zutat eingeben.")
    else:
        with st.spinner("Generiere Rezepte..."):
            system_prompt = build_system_prompt(num_recipes)
            user_prompt = build_user_prompt(ingredients, diet, cuisine, num_recipes)
            try:
                if OPENAI_API_KEY:
                    result_text = call_openai_chat(system_prompt, user_prompt)
                else:
                    result_text = simple_rule_based(ingredients, diet, cuisine, num_recipes)
            except Exception as e:
                st.error(f"Fehler beim Modellaufruf: {e}")
                result_text = simple_rule_based(ingredients, diet, cuisine, num_recipes)

            st.markdown(result_text)
            st.download_button("Rezept als Text herunterladen", result_text, file_name="rezepte.txt")

# Footer mit Hinweisen
st.markdown("---")
st.caption("Hinweis: Wenn du ein OpenAI API Key setzt (OPENAI_API_KEY), erzeugt die App reichhaltigere Rezepte. Ohne Key gibt es einen einfachen Regel-basierten Fallback.")
