import streamlit as st
import requests
from flores200_codes import flores_codes
from languages import lang_names


# Page configuration
st.set_page_config(page_title="Sema Tranlator", page_icon="💸",)

st.title("Sema Translator")
st.write("Discover seamless, instant translation at your fingertips with Sema.")


public_url = "https://2228-54-243-246-120.ngrok-free.app"

tab1, tab2 = st.tabs(["Detect", "Enter"])

def translate_detect(userinput, target_lang):
    trg_lang = flores_codes[target_lang]
    url = public_url + "/translate_detect/"
    data = {
        "userinput": userinput,
        "target_lang": trg_lang,
    }
    response = requests.post(url, json=data)
    result = response.json()
    src_lang = result['source_language']
    source_lang = lang_names[src_lang]
    translation = result['translated_text']
    return source_lang, translation

def translate_enter(userinput, source_lang, target_lang):
    src_lang = flores_codes[source_lang]
    trg_lang = flores_codes[target_lang]
    url = public_url + "/translate_enter/"
    data = {
        "userinput": userinput,
        "source_lang": src_lang,
        "target_lang": trg_lang,
    }
    response = requests.post(url, json=data)
    result = response.json()
    translation = result['translated_text']
    return translation

lang_codes = list(flores_codes.keys())

# Language Dropdown
st.sidebar.title("Supported Languages 🚀")
selected_language = st.sidebar.selectbox("Select a language", lang_codes)

with tab1:
  st.header("Detect source language")
  user_input_detect = st.text_area("Enter text to ttranslate")
  target_lang_detect = st.selectbox("Targe Language", lang_codes, index=lang_codes.index('Swahili'))
  if st.button("Translatee"):
        source_lang, translation = translate_detect(user_input_detect, target_lang_detect)
        st.write(f"Source language: {source_lang}")
        st.write(f"Translated Text: {translation}")

with tab2:
  st.header("Enter source Language")
  user_input_enter = st.text_area("Enter text to translate")
  source_lang_enter = st.selectbox("Source Language", lang_codes, index=lang_codes.index('English'))
  target_lang_enter = st.selectbox("Target Language", lang_codes, index=lang_codes.index('Swahili'))
  if st.button("Translate"):
        translation_enter = translate_enter(user_input_enter, source_lang_enter, target_lang_enter)
        st.write(f"Translated Text: {translation_enter}")
# Footer
st.sidebar.write("Created by Lewis Kamau Kimaru")
