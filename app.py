import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv

# 1. Ayarları Yükle
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# 2. Sayfa Ayarları
st.set_page_config(page_title="Music Producer AI", page_icon="🎧", layout="wide")

# 3. Model Bağlantısı (Otomatik Seçici)
try:
    if not api_key:
        st.error("⚠️ API Anahtarı Yok! .env dosyasını kontrol et.")
        st.stop()
        
    genai.configure(api_key=api_key)
    
    # Hangi model varsa onu bul
    def model_bul():
        try:
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

# --- ARAYÜZ ---
st.title("🎧 AI Müzik Prodüktörü")
st.caption(f"Motor: {aktif_model}")
st.markdown("---")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Tasarım Paneli")
    konu = st.text_area("Şarkı Konusu:", "İstanbul'da yağmurlu bir gece...", height=100)
    
    c1, c2 = st.columns(2)
    with c1:
        tur = st.selectbox("Tarz", ["Turkish Pop", "Rock", "Deep House", "Rap", "Slow"])
    with c2:
        vokal = st.selectbox("Vokal", ["Erkek", "Kadın", "Düet"])
        
    hiz = st.select_slider("Hız", options=["Yavaş", "Orta", "Hızlı", "Çok Hızlı"])
    
    btn = st.button("✨ Şarkıyı Tasarla", use_container_width=True)

with col2:
    st.subheader("2. Üretim Paneli")
    
    if btn and konu:
        with st.spinner("Yapay Zeka çalışıyor..."):
            try:
                # Prompt'u parça parça oluşturuyoruz (Hata riskini sıfırlar)
                istek = "Act as a professional Songwriter.\n"
                istek += f"Topic: {konu}\n"
                istek += f"Style: {tur}\n"
                istek += f"Vocals: {vokal}\n"
                istek += f"Tempo: {hiz}\n"
                istek += "Language: Turkish (Lyrics), English (Style Tags).\n"
                istek += "Structure: [Verse], [Chorus], [Bridge], [Outro].\n"
                istek += "Output: Only lyrics and tags."

                cevap = model.generate_content(istek)
                metin = cevap.text
                
                st.success("✅ Tasarım Hazır!")
                st.code(metin, language="markdown")
                
                st.info("👇 Aşağıdaki butona bas, Suno'yu aç ve yapıştır:")
                st.link_button("🚀 Suno Stüdyosunu Aç", "https://suno.com/create", use_container_width=True)
            
            except Exception as e:
                st.error(f"Üretim Hatası: {e}")

    elif not btn:
        st.info("👈 Soldan ayarları yapıp butona bas.")