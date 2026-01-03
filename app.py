import streamlit as st
import google.generativeai as genai
import os
import random
from dotenv import load_dotenv

# 1. Sayfa Ayarları
st.set_page_config(page_title="Music Producer AI", page_icon="🎧", layout="wide")

# 2. Şifre (API KEY) Kontrolü
api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else (load_dotenv() or os.getenv("GEMINI_API_KEY"))

try:
    if not api_key:
        st.error("⚠️ API Anahtarı Bulunamadı!")
        st.stop()
    genai.configure(api_key=api_key)
    def model_bul():
        try:
            for m in genai.list_models():
                if 'flash' in m.name: return m.name
            return "models/gemini-pro"
        except: return "models/gemini-pro"
    model = genai.GenerativeModel(model_bul())
except Exception as e:
    st.error(f"Bağlantı Hatası: {e}"); st.stop()

# --- MÜZİK KÜTÜPHANESİ ---
muzik_turleri = [
    "Turkish Pop", "Anatolian Rock", "Deep House", "Arabesk Rap", "Cinematic Orchestral", 
    "K-Pop Arabesk", "Synthwave (80s)", "Lo-Fi Hip Hop", "Symphonic Metal", "Jazz Fusion", 
    "Techno Tribal", "Neo-Classical", "Reggaeton", "Country Folk", "Cyberpunk Industrial",
    "Phonk", "Disco Nostalgia", "R&B Soul", "Hardstyle", "Acoustic Ballad"
]

# --- ARAYÜZ ---
st.title("👑 Kralın Müzik Fabrikası v2")
st.markdown("---")

# Yan Menü: İlham Butonu
with st.sidebar:
    st.header("🎭 İlham Köşesi")
    if st.button("🎲 Rastgele Tarz Öner"):
        rastgele_tur = random.choice(muzik_turleri)
        st.success(f"Rastgele Müzik Türü: **{rastgele_tur}**")
    st.markdown("---")
    st.info("Bu sistem AI ile güçlendirilmiştir.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Tasarım Paneli")
    konu = st.text_area("Şarkı Konusu Nedir?", "Geleceğin dünyasında son bir dans...", height=100)
    
    c1, c2 = st.columns(2)
    with c1:
        tur = st.selectbox("Müzik Tarzı", muzik_turleri)
    with c2:
        vokal = st.selectbox("Vokal", ["Male Vocals", "Female Vocals", "Duet", "High-Pitch", "Deep Bass"])
        
    hiz = st.select_slider("Tempo", options=["Slow", "Mid", "Fast", "Very Fast"])
    btn = st.button("✨ Şarkıyı İnşa Et", use_container_width=True)

with col2:
    st.subheader("2. Üretim Paneli")
    
    if btn and konu:
        with st.spinner("AI besteliyor..."):
            try:
                istek = f"Topic: {konu}. Style: {tur}. Vocals: {vokal}. Tempo: {hiz}. Structure: [Verse], [Chorus]. Output: Lyrics and tags."
                cevap = model.generate_content(istek)
                metin = cevap.text
                
                st.success("✅ Eser Hazır!")
                st.code(metin, language="markdown")
                
                # İndirme ve Link Butonları
                st.download_button(label="💾 Kaydet", data=metin, file_name="beste.txt", use_container_width=True)
                st.link_button("🚀 Suno'ya Git", "https://suno.com/create", use_container_width=True)
            
            except Exception as e:
                st.error(f"Hata: {e}")
    else:
        st.info("👈 Ayarları yapıp butona basın.")

# Kod Sonu - Burayı da kopyaladığınızdan emin olun

