import streamlit as st
import google.generativeai as genai
import os
import time
import requests
import json
from dotenv import load_dotenv

# Sayfa Ayarları
st.set_page_config(page_title="SongAI - Kişiye Özel Müzik", page_icon="🎵", layout="wide")

# API Anahtarları
api_key = st.secrets.get("GEMINI_API_KEY") or (load_dotenv() or os.getenv("GEMINI_API_KEY"))
hf_token = st.secrets.get("HUGGINGFACE_API_TOKEN") or os.getenv("HUGGINGFACE_API_TOKEN")

# Gemini Setup
try:
    if not api_key:
        st.error("⚠️ Gemini API Anahtarı Bulunamadı!")
        st.stop()
        
    genai.configure(api_key=api_key)
    
    def model_bul():
        try:
            for m in genai.list_models():
                if 'flash' in m.name: return m.name
            for m in genai.list_models():
                if 'pro' in m.name: return m.name
            return "models/gemini-1.5-flash"
        except:
            return "models/gemini-pro"

    aktif_model = model_bul()
    model = genai.GenerativeModel(aktif_model)
    
except Exception as e:
    st.error(f"Sistem Bakımda: {e}")
    st.stop()

# HUGGING FACE MUSİC GENERATION
def generate_music_hf(prompt, duration=30):
    """Hugging Face MusicGen ile müzik üret"""
    
    # Model seçenekleri (sırası önemli - en iyiden başla)
    models = [
        "facebook/musicgen-large",  # En iyi kalite
        "facebook/musicgen-medium", # Orta kalite, hızlı
        "facebook/musicgen-small"   # Düşük kalite, çok hızlı
    ]
    
    headers = {}
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
    
    for model_name in models:
        try:
            API_URL = f"https://api-inference.huggingface.co/models/{model_name}"
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "duration": duration,
                    "temperature": 1.0,
                    "top_k": 250
                }
            }
            
            response = requests.post(
                API_URL, 
                headers=headers, 
                json=payload,
                timeout=180
            )
            
            if response.status_code == 200:
                return response.content, model_name
            elif response.status_code == 503:
                # Model yükleniyor, bekle
                st.info(f"⏳ {model_name} yükleniyor, alternatif model deneniyor...")
                continue
            else:
                st.warning(f"⚠️ {model_name}: {response.status_code}")
                continue
                
        except Exception as e:
            st.warning(f"Model hatası: {model_name}")
            continue
    
    return None, None

# UI
st.title("🎵 SongAI: Hayalindeki Şarkıyı Yarat")
st.markdown(f"**Yapay Zeka Motoru: {aktif_model} + Hugging Face MusicGen**")

with st.sidebar:
    st.header("📢 Menü")
    st.info("💡 İletişim: info@songai.com")
    
    with st.expander("⚙️ API Durumu"):
        if api_key:
            st.success("✅ Gemini bağlı")
        else:
            st.error("❌ Gemini API key gerekli")
        
        st.success("✅ Hugging Face bağlı (ÜCRETSIZ)")
        
        if hf_token:
            st.info("🔑 HF Token aktif (daha hızlı)")
        else:
            st.warning("⚠️ HF Token yok (yavaş olabilir)")
            with st.expander("📖 Token Nasıl Alınır? (Opsiyonel)"):
                st.markdown("""
                **Token olmadan da çalışır ama yavaştır!**
                
                Hızlandırmak için:
                1. **huggingface.co** → Sign up
                2. **Settings** → **Access Tokens**
                3. **New token** → Kopyala
                4. Secrets'a ekle: `HUGGINGFACE_API_TOKEN`
                """)
    
    with st.expander("🎵 Ses Ayarları"):
        duration = st.slider("Şarkı Süresi (saniye)", 10, 60, 30)
        st.info("⚡ Daha kısa = Daha hızlı üretim")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🎹 Tasarım Stüdyosu")
    konu = st.text_area("Şarkı kime/neye özel olsun?", "İstanbul'da aşık olmak...", height=100)
    tur = st.selectbox("Müzik Tarzı", ["Turkish Pop", "Rap", "Rock", "Deep House", "Ballad", "Jazz", "Reggae"])
    vokal = st.selectbox("Vokal", ["Erkek", "Kadın", "Düet"])
    
    # Kalite seçeneği
    quality = st.radio("Kalite", ["Hızlı (15 sn)", "Normal (30 sn)", "Yüksek (60 sn)"], index=1)
    
    btn_olustur = st.button("✨ Şarkıyı Üret", use_container_width=True)

with col2:
    st.subheader("🎧 Sonuç")
    
    if btn_olustur and konu:
        
        # 1. GEMİNİ - SÖZLER
        with st.spinner("🤖 Gemini sözleri yazıyor..."):
            prompt_sozler = f"""Write a {tur} song in Turkish about: {konu}

Vocal: {vokal}
Style: {tur}

Requirements:
- Complete lyrics with verses, chorus, bridge
- Emotional and fitting for {tur}
- Natural Turkish language
- Include [Verse], [Chorus], [Bridge] markers

Output only Turkish lyrics."""

            res = model.generate_content(prompt_sozler)
            sozler = res.text
            
            st.success("✅ Sözler Hazır!")
            with st.expander("📝 Sözleri Gör"):
                st.code(sozler, language="text")
        
        # 2. HUGGING FACE MUSİC GENERATION
        st.divider()
        st.info("🎵 Hugging Face ile müzik üretiliyor...")
        
        # Süre ayarı
        duration_map = {
            "Hızlı (15 sn)": 15,
            "Normal (30 sn)": 30,
            "Yüksek (60 sn)": 60
        }
        selected_duration = duration_map[quality]
        
        # Müzik prompt'u hazırla (İngilizce olmalı - model bunu bekliyor)
        music_prompt = f"{tur} music, {vokal} vocals, Turkish style, emotional, modern production, about {konu}, upbeat melody"
        
        with st.spinner(f"🎼 MusicGen çalışıyor... ({selected_duration} saniye sürecek)"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Üretim
            start_time = time.time()
            audio_data, model_used = generate_music_hf(music_prompt, selected_duration)
            elapsed = int(time.time() - start_time)
            
            progress_bar.progress(100)
        
        if audio_data:
            st.success(f"🎉 Şarkı hazır! (Model: {model_used}, Süre: {elapsed}s)")
            
            # Audio player
            st.audio(audio_data, format="audio/wav")
            
            # Download button
            st.download_button(
                label="⬇️ MP3 İndir",
                data=audio_data,
                file_name=f"songai_{konu[:20]}.wav",
                mime="audio/wav"
            )
            
            # Sözleri göster
            with st.expander("📝 Şarkı Sözleri"):
                st.code(sozler)
                st.info("💡 Bu instrumental bir versiyondur. Sözleri vokal kaydetmek için kullanabilirsiniz.")
            
            st.balloons()
            
        else:
            st.error("😔 Müzik üretilemedi. Lütfen tekrar deneyin.")
            st.info("💡 Hugging Face modelleri ilk çalıştırmada yavaş olabilir (yükleniyor)")
            
            # Sözleri yine de göster
            with st.expander("📝 Şarkı Sözleri (Manuel kullanın)"):
                st.code(sozler)
                st.info("Bu sözleri kopyalayıp suno.ai'de manuel kullanabilirsiniz")
    
    elif btn_olustur:
        st.warning("Lütfen şarkı konusunu yazın!")

# Footer
st.markdown("---")
st.caption("🎵 SongAI | Gemini + Hugging Face MusicGen | Tamamen Ücretsiz")
