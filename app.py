import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Sayfa Ayarları (En üstte olmalı)
st.set_page_config(page_title="Music Producer AI", page_icon="🎧", layout="wide")

# 2. Şifre (API KEY) Kontrolü - Hem internet hem bilgisayar uyumlu
api_key = None

# Önce Streamlit Secrets'ı dene (İnternet için)
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
# Eğer yoksa .env dosyasını dene (Kendi bilgisayarın için)
else:
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

# 3. Model Bağlantısı
try:
    if not api_key:
        st.error("⚠️ API Anahtarı Bulunamadı! Streamlit Settings > Secrets kısmına anahtarı eklemelisin.")
        st.stop()
        
    genai.configure(api_key=api_key)
    
    def model_bul():
        try:
            # Mevcut modelleri tara
            for m in genai.list_models():
                if 'flash' in m.name: return m.name
            return "models/gemini-pro"
        except:
            return "models/gemini-pro"

    aktif_model = model_bul()
    model = genai.GenerativeModel(aktif_model)
    
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}")
    st.stop()

# --- ARAYÜZ TASARIMI ---
st.title("🎧 AI Müzik Prodüktörü")
st.caption(f"Aktif Motor: {aktif_model}")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Tasarım Paneli")
    konu = st.text_area("Şarkı Konusu Nedir?", "İstanbul'da yağmurlu bir gece...", height=100)
    
    c1, c2 = st.columns(2)
    with c1:
        tur = st.selectbox("Müzik Tarzı", ["Turkish Pop", "Rock", "Deep House", "Rap", "Slow"])
    with c2:
        vokal = st.selectbox("Vokal", ["Erkek", "Kadın", "Düet"])
        
    hiz = st.select_slider("Tempo", options=["Yavaş", "Orta", "Hızlı", "Çok Hızlı"])
    
    btn = st.button("✨ Şarkıyı Tasarla", use_container_width=True)

with col2:
    st.subheader("2. Üretim Paneli")
    
    if btn and konu:
        with st.spinner("AI şarkıyı kurguluyor..."):
            try:
                istek = f"Act as a professional Songwriter.\nTopic: {konu}\nStyle: {tur}\nVocals: {vokal}\nTempo: {hiz}\nLanguage: Turkish.\nStructure: [Verse], [Chorus], [Bridge], [Outro].\nOutput: Only lyrics and style tags."
                
                cevap = model.generate_content(istek)
                metin = cevap.text
                
                st.success("✅ Tasarım Hazır!")
                st.code(metin, language="markdown")
                
                st.info("👇 Şimdi Suno'yu aç ve bu kodu yapıştır:")
                st.link_button("🚀 Suno Stüdyosunu Aç", "https://suno.com/create", use_container_width=True)
            
            except Exception as e:
                st.error(f"Üretim Hatası: {e}")

    elif not btn:
        st.info("👈 Soldan ayarları yapıp butona basınız.")
