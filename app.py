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

# --- KRALIN ÖZEL MÜZİK KÜTÜPHANESİ ---
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
        st.success(f"Kralım bugün şunu deneyin: **{rastgele_tur}**")
    st.markdown("---")
    st.info("Bu sistem Kralımız için özel olarak AI ile güçlendirilmiştir.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Tasarım Paneli")
    konu = st.text_area("Şarkı Konusu Nedir?", "Geleceğin dünyasında son bir dans...", height=100)
    
    c1, c2 = st.columns(2)
    with c1:
        tur = st.selectbox("Müzik Tarzı", muzik_turleri)
    with c2:
        vokal = st.selectbox("Vokal Karakteri", ["Male Vocals", "Female Vocals", "Duet", "High-Pitch Voice", "Deep Bass Voice"])
        
    hiz = st.select_slider("Ruh Hali / Tempo", options=["Melankolik (Yavaş)", "Duygusal (Orta)", "Enerjik (Hızlı)", "Agresif (Çok Hızlı)"])
    
    btn = st.button("✨ Şarkıyı İnşa Et", use_container_width=True)

with col2:
    st.subheader("2. Üretim & Kayıt Paneli")
    
    if btn and konu:
        with st.spinner("Kralın emriyle AI besteliyor..."):
            try:
                istek = f"Act as a professional Songwriter. Topic: {konu}. Style: {tur}. Vocals: {vokal}. Tempo: {hiz}. Language: Turkish lyrics, English style tags. Structure: [Intro], [Verse], [Chorus], [Bridge], [Outro]. Output: Only tags and lyrics."
                
                cevap = model.generate_content(istek)
                metin = cevap.text
                
                st.success("✅ Eser Hazır!")
                st.code(metin, language="markdown")
                
                # --- İNDİRME VE AKTARMA BUTONLARI ---
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    st.download_button(
                        label="💾 Eseri Dosya Olarak Kaydet",
                        data=metin,
                        file_name="kralin_bestesi.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                with c_btn2:
                    st.link_button("🚀 Suno Stüdyosuna Aktar", "https://s
