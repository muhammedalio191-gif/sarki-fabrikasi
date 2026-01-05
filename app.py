import streamlit as st
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# 1. Sayfa Ayarları
st.set_page_config(page_title="SongAI - Kişiye Özel Müzik", page_icon="🎵", layout="wide")

# 2. Şifre (API KEY) Kontrolü
api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else (load_dotenv() or os.getenv("GEMINI_API_KEY"))

try:
    # --- KRİTİK DÜZELTME: AKILLI MODEL SEÇİCİ ---
    if not api_key:
        st.error("⚠️ API Anahtarı Bulunamadı!")
        st.stop()
        
    genai.configure(api_key=api_key)
    
    def model_bul():
        try:
            # Önce Flash modelini ara
            for m in genai.list_models():
                if 'flash' in m.name: return m.name
            # Bulamazsan Pro'yu ara
            for m in genai.list_models():
                if 'pro' in m.name: return m.name
            # Hiçbiri yoksa varsayılanı dene
            return "models/gemini-1.5-flash"
        except:
            return "models/gemini-pro"

    aktif_model = model_bul()
    model = genai.GenerativeModel(aktif_model)
    
except Exception as e:
    st.error(f"Sistem Bakımda: {e}")
    st.stop()

# --- REKLAM ALANLARI (HTML) ---
google_ads_html = """
<div style="background-color:#f8f9fa; padding:15px; text-align:center; border:1px solid #ddd; border-radius:10px; margin-bottom:15px;">
    <p style="color:#666; font-size:11px; margin:0;">REKLAM</p>
    <h5 style="margin:5px 0;">🎵 Kendi Müziğini Yap!</h5>
    <p style="font-size:12px;">Profesyonel ekipmanlar burada.</p>
</div>
"""

# --- ARAYÜZ ---
st.title("🎵 SongAI: Hayalindeki Şarkıyı Yarat")
st.markdown(f"**Yapay Zeka Motoru: {aktif_model} ile çalışıyor.**")
st.markdown("---")

# Yan Menü
with st.sidebar:
    st.header("📢 Sponsorlar")
    st.markdown(google_ads_html, unsafe_allow_html=True)
    st.markdown(google_ads_html, unsafe_allow_html=True)
    st.info("💡 İletişim: info@songai.com")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🎹 Tasarım Stüdyosu")
    konu = st.text_area("Şarkı kime/neye özel olsun?", "Sevgilim Ayşe için romantik bir doğum günü şarkısı...", height=100)
    
    c1, c2 = st.columns(2)
    with c1:
        tur = st.selectbox("Müzik Tarzı", ["Turkish Pop", "Slow & Damar", "Rap & Drill", "Anatolian Rock", "Deep House", "K-Pop", "Lo-Fi"])
    with c2:
        vokal = st.selectbox("Vokal", ["Erkek", "Kadın", "Düet"])
    
    st.markdown("---")
    st.caption("Fiyatlandırma:")
    st.success("🎫 Demo (15 Sn): **ÜCRETSİZ**")
    st.warning("💿 Full Sürüm (MP3): **50 TL**")
    
    btn_olustur = st.button("✨ Şarkıyı Üret (Demo)", use_container_width=True)

with col2:
    st.subheader("🎧 Dinleme & Satın Alma")
    
    if btn_olustur and konu:
        with st.spinner("Yapay Zeka sözleri yazıyor ve demoyu hazırlıyor..."):
            try:
                # 1. Söz Üretimi
                prompt = f"Write a Turkish song about {konu}. Style: {tur}. Output: Only Lyrics. Structure: [Chorus], [Verse]."
                res = model.generate_content(prompt)
                sozler = res.text
                
                # Simülasyon Beklemesi
                time.sleep(2) 
                
                st.success("✅ Demo Hazırlandı!")
                
                # 2
