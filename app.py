import streamlit as st
from openai import OpenAI
import base64
from pathlib import Path
import os
from dotenv import load_dotenv
import json
from datetime import datetime
from collections import defaultdict
import bcrypt

# Wczytaj API key z Streamlit Secrets
api_key = st.secrets["OPENAI_API_KEY"]
client = OpenAI(api_key=api_key)
HISTORY_FILE = "translation_history.json"

def img_to_bytes(img_path):
    """Konwertuje obraz na ciąg bajtów zakodowany w Base64."""
    try:
        img_bytes = Path(img_path).read_bytes()
        return base64.b64encode(img_bytes).decode()
    except FileNotFoundError:
        st.error(f"Błąd: Nie znaleziono pliku obrazu '{img_path}'.")
        return ""

def load_history(username):
    """Wczytuje historię tłumaczeń dla użytkownika."""
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get(username, [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_history(username, history):
    """Zapisuje historię tłumaczeń dla użytkownika."""
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data[username] = history
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def translate_text(text, source_lang, target_lang):
    """Tłumaczy tekst z języka źródłowego na docelowy."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Jesteś tłumaczem. Przetłumacz tekst z {source_lang} na {target_lang}."},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Błąd: {e}"

def verify_password(password, hashed_password):
    """Sprawdza, czy hasło pasuje do zahashowanego."""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())

def login_page():
    """Ekran logowania."""
    st.title("Logowanie")
    st.write("Wpisz swoje dane, aby się zalogować.")
    username = st.text_input("Nazwa użytkownika")
    password = st.text_input("Hasło", type="password")
    if st.button("Zaloguj"):
        users = st.secrets["users"]
        if username in users and verify_password(password, users[username]):
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.rerun()
        else:
            st.error("Nieprawidłowe dane logowania!")

def main():
    # Nagłówek z obrazem
    img_path = "logo.png"
    encoded_image = img_to_bytes(img_path)
    if encoded_image:
        header_html = f"""
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <img src="data:image/png;base64,{encoded_image}" width="100" height="100" style="margin-right: 20px;">
            <h1>POMOCNIK JĘZYKOWY PIONIERA</h1>
            <div>
                Zalogowany: {st.session_state['username']}
                <button style="margin-left: 10px;" onclick="window.location.reload()">Wyloguj</button>
            </div>
        </div>
        """
        st.markdown(header_html, unsafe_allow_html=True)
    else:
        st.title("POMOCNIK JĘZYKOWY PIONIERA")

    # Wczytaj historię
    username = st.session_state["username"]
    history = load_history(username)

    # Grupowanie historii według dat
    grouped_history = defaultdict(list)
    for entry in history:
        date = entry["timestamp"].split()[0]
        grouped_history[date].append(entry)

    # Sidebar z historią
    st.sidebar.header("Historia tłumaczeń")
    if history:
        for date in sorted(grouped_history.keys(), reverse=True):
            with st.sidebar.expander(f" {date}"):
                for entry in grouped_history[date]:
                    time = entry["timestamp"].split()[1]
                    st.sidebar.write(f" **{time}**")
                    st.sidebar.write(f" **{entry['source_lang']}:** {entry['original']}")
                    st.sidebar.write(f" **{entry['target_lang']}:** {entry['translation']}")
                    st.sidebar.divider()
    else:
        st.sidebar.write("Brak historii.")

    # Lista języków
    languages = {
        "polski": "polski",
        "angielski": "angielski",
        "francuski": "francuski",
        "niemiecki": "niemiecki",
        "hiszpański": "hiszpański",
        "włoski": "włoski",
        "chiński": "chiński",
        "japoński": "japoński",
        "rosyjski": "rosyjski",
        "arabski": "arabski",
        "portugalski": "portugalski",
        "koreański": "koreański",
        "holenderski": "holenderski",
        "szwedzki": "szwedzki",
        "grecki": "grecki",
        "czeski": "czeski",
        "turecki": "turecki",
        "węgierski": "węgierski",
        "fiński": "fiński",
        "indonezyjski": "indonezyjski",
        "tajski": "tajski",
        "wietnamski": "wietnamski",
        "hebrajski": "hebrajski",
        "perski": "perski",
        "ukraiński": "ukraiński",
        "rumuński": "rumuński",
        "bułgarski": "bułgarski",
        "słowacki": "słowacki",
        "chorwacki": "chorwacki"
    }

    # Wybór języków
    col1, col2 = st.columns(2)
    with col1:
        source_lang = st.selectbox("Język oryginalny:", list(languages.keys()))
    with col2:
        target_lang = st.selectbox("Język tłumaczenia:", list(languages.keys()))

    # Pole tekstowe
    text = st.text_area("Twój tekst:", height=150, max_chars=5000, placeholder="Tutaj wpisz lub wklej tekst...")

    # Tłumaczenie
    translation = ""
    if st.button("Tłumacz"):
        if text:
            if source_lang == target_lang:
                st.warning("Język źródłowy i docelowy nie mogą być takie same!")
            else:
                with st.spinner("Trwa tłumaczenie... Proszę czekać."):
                    translation = translate_text(text, languages[source_lang], languages[target_lang])
                    # Zapisz do historii
                    history.append({
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "original": text,
                        "translation": translation,
                        "source_lang": source_lang,
                        "target_lang": target_lang
                    })
                    save_history(username, history)
        else:
            st.warning("Pole tekstowe jest puste!")

    st.text_area("Twoje tłumaczenie:", value=translation, height=150)

    # Liczba znaków
    if text:
        st.write(f"**Liczba znaków (oryginał):** {len(text)}")
    if translation:
        st.write(f"**Liczba znaków (tłumaczenie):** {len(translation)}")

# Logowanie
if "logged_in" not in st.session_state:
    login_page()
else:
    main()