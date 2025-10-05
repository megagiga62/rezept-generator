# streamlit_rezeptgenerator.py
# KI-gestützter Rezept-Generator (Streamlit)
# Einfache, praktische Demo: verwendet OpenAI (wenn API-Key vorhanden), sonst ein regelbasiertes Fallback.

import streamlit as st
import os
import openai
from dotenv import load_dotenv
from typing import List

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

st.set_page_config(page_title="KI Rezept-Generator 🍳", layout="centered")

st.title("🍽️ Kreativer KI-Rezeptgenerator")
st.markdown("Gib deine Zutaten ein und erhalte **fantasievolle, genau erklärte Rezepte** mit schönen Namen und Schritt-für-Schritt-Anleitung! 🤖✨")

ingredients_input = st.text_area("🧄 Zutaten (Komma- oder Zeilen-getrennt)", placeholder="z.B. Kartoffeln, Zwiebel, Tomaten, Feta")
diet = st.selectbox("🥦 Ernährungspräferenz (optional)", ["Keine", "Vegetarisch", "Vegan", "Glutenfrei", "Laktosefrei", "Low-Carb"])
cuisine = st.text_input("🍜 Küchenrichtung (optional)", placeholder="z.B. Italienisch, Asiatisch, Mediterran")
num_recipes = st.slider("📚 Anzahl Rezepte", 1, 5, 3)

def parse_ingredients(text: str) -> List[str]:
    return [p.strip().lower() for p in text.replace('\n', ',').split(',') if p.strip()]

def build_system_prompt(num_recipes: int) -> str:
    return f"""
Du bist ein kreativer Sternekoch und Rezeptentwickler.
Erstelle bis zu {num_recipes} **originelle und schmackhafte Rezepte** auf Deutsch.
Jedes Rezept soll Folgendes enthalten:

### FORMAT
1. **Name des Gerichts** – fantasievoll und einprägsam (z. B. „Feurige Gemüse-Symphonie“)
2. **Kurzbeschreibung** – 1–2 Sätze, die Lust machen
3. **Zutatenliste** – mit sinnvollen Mengenangaben
4. **Zubereitung** – klar nummerierte, ausführliche Schritte (mind. 5–8 Schritte)
5. **Zubereitungszeit** – in Minuten (realistisch)
6. **Optionale Einkaufsliste** für Zutaten, die wahrscheinlich fehlen

### REGELN
- Verwende möglichst nur die angegebenen Zutaten + Basiszutaten (Salz, Öl, Pfeffer, Wasser etc.)
- Sei kreativ: Nutze Gewürze, Kombis und Ideen, die lecker und neu sind.
- Lass die Rezepte klingen wie aus einem modernen Kochbuch.
- Antworte **in schönem Markdown-Format**, mit klarer Trennung zwischen Rezepten.
"""

def build_user_prompt(ingredients: List[str], diet: str, cuisine: str, num_recipes: int) -> str:
    ing_text = ", ".join(ingredients)
    diet_text = f"Ernährungspräferenz: {diet}." if diet and diet != "Keine" else ""
    cuisine_text = f"Küche: {cuisine}." if cuisine else ""
    return f"Hier sind meine Zutaten: {ing_text}. {diet_text} {cuisine_text} Erstelle {num_recipes} kreative Rezepte."

def call_openai_chat(system: str, user: str, model: str = "gpt-4o-mini") -> str:
    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY nicht gesetzt.")
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user}
    ]
    resp = openai.ChatCompletion.create(model=model, messages=messages, temperature=1.0, max_tokens=1000)
    return resp.choices[0].message.content

if st.button("✨ Kreative Rezepte generieren"):
    ingredients = parse_ingredients(ingredients_input)
    if not ingredients:
        st.warning("Bitte gib mindestens eine Zutat ein.")
    else:
        with st.spinner("Ich zaubere kreative Ideen... 🍲"):
            try:
                system_prompt = build_system_prompt(num_recipes)
                user_prompt = build_user_prompt(ingredients, diet, cuisine, num_recipes)
                result_text = call_openai_chat(system_prompt, user_prompt)
            except Exception as e:
                st.error(f"Fehler: {e}")
                result_text = "⚠️ Die KI konnte keine Rezepte erzeugen. Überprüfe deinen API-Key."

            st.markdown(result_text)
            st.download_button("📥 Rezepte herunterladen", result_text, file_name="kreative_rezepte.txt")

st.markdown("---")
st.caption("💡 Tipp: Wenn du den OpenAI-API-Key setzt, bekommst du hochwertige, kreative Rezepte mit fantasievollen Namen und genauen Schritten.")
