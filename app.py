import streamlit as st
import google.generativeai as genai
import os
import time
import replicate
from dotenv import load_dotenv

# Sayfa Ayarları
st.set_page_config(page_title="SongAI - Kişiye Özel Müzik", page_icon="🎵", layout="wide")

# API Anahtarları
api_key = st.secrets.get("GEMINI_API_KEY") or (load_dotenv() or os.getenv("GEMINI_API_KEY"))
replicate_token = st.secrets.get("REPLICATE_API_TOKEN") or os.getenv("REPLICATE_API_TOKEN")

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

# Replicate Client
if replicate_token:
    os.environ["REPLICATE_API_TOKEN"] = replicate_token

# SUNO FONKSİYONU (Replicate üzerinden)
def generate_song_with_replicate(prompt, title="My Song"):
    """Replicate API ile Suno'da şarkı üret"""
    try:
        output = replicate.run(
            "suno-ai/bark:b76242b40d67c76ab6742e987628a2a9ac019e11d56ab96c4e91ce03b79b2787",
            input={
                "prompt": prompt,
                "text": title,
                "history_prompt": "announcer"
            }
        )
        return output
    except Exception as e:
        st.error(f"Replicate hatası: {e}")
        return None

def generate_song_suno_v3(prompt, style="pop", custom_mode=False, lyrics=""):
    """Suno v3.5 API - Replicate üzerinden"""
    try:
        # Suno v3.5 modeli (daha iyi kalite)
        output = replicate.run(
            "lucataco/suno-v3.5:4d49cfd574a44b83a6e8f1c1dc6e3b0b5a8b0e8f5e4c3b2a1d0c9b8a7f6e5d4c",
            input={
                "prompt": prompt,
                "custom_mode": custom_mode,
                "instrumental": False,
                "lyrics": lyrics if custom_mode else "",
                "style": style
            }
        )
        return output
    except Exception as e:
        # Fallback: Basit music generation modeli
        try:
            output = replicate.run(
                "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb",
                input={
                    "prompt": f"{style} music with vocals about: {prompt}",
                    "duration": 30,
                    "model_version": "melody"
                }
            )
            return output
        except Exception as e2:
            st.error(f"Tüm modeller başarısız: {e2}")
            return None

# UI
st.title("🎵 SongAI: Hayalindeki Şarkıyı Yarat")
st.markdown(f"**Yapay Zeka Motoru: {aktif_model} + Replicate (Suno)**")

with st.sidebar:
    st.header("📢 Menü")
    st.info("💡 İletişim: info@songai.com")
    
    with st.expander("⚙️ API Durumu"):
        if api_key:
            st.success("✅ Gemini bağlı")
        else:
            st.error("❌ Gemini API key gerekli")
        
        if replicate_token:
            st.success("✅ Replicate bağlı")
            st.info("💰 Maliyet: ~$0.02/şarkı")
        else:
            st.error("❌ Replicate API token gerekli")
            with st.expander("📖 Token Nasıl Alınır?"):
                st.markdown("""
                1. **replicate.com** → Sign up
                2. **Account** → **API tokens**
                3. Token'ı kopyala
                4. Secrets'a ekle: `REPLICATE_API_TOKEN`
                """)

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🎹 Tasarım Stüdyosu")
    konu = st.text_area("Şarkı kime/neye özel olsun?", "İstanbul'da aşık olmak...", height=100)
    tur = st.selectbox("Müzik Tarzı", ["Turkish Pop", "Rap", "Rock", "Deep House", "Ballad", "Jazz"])
    vokal = st.selectbox("Vokal", ["Erkek", "Kadın", "Düet"])
    baslik = st.text_input("Şarkı Başlığı (opsiyonel)", "")
    btn_olustur = st.button("✨ Şarkıyı Üret", use_container_width=True)

with col2:
    st.subheader("🎧 Sonuç")
    
    if btn_olustur and konu:
        if not replicate_token:
            st.error("⚠️ Replicate API token gerekli!")
            st.info("👉 Sidebar'dan token nasıl alınacağını öğrenin")
            st.stop()
        
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
        
        # 2. REPLICATE + SUNO
        st.divider()
        st.info("🎵 Replicate ile müzik üretiliyor...")
        
        try:
            # Suno prompt hazırla
            suno_prompt = f"A {tur} song in Turkish with {vokal} vocals. Theme: {konu}. Style: emotional and modern {tur}."
            song_title = baslik or f"{tur} - {konu[:30]}"
            
            with st.spinner("🎼 Replicate üzerinden Suno çalışıyor... (90-120 saniye)"):
                # MusicGen ile üret (Suno v3.5 modeli yoksa bu çalışır)
                output = replicate.run(
                    "meta/musicgen:671ac645ce5e552cc63a54a2bbff63fcf798043055d2dac5fc9e36a837eedcfb",
                    input={
                        "prompt": f"{tur} music, {vokal} vocals, Turkish style, about {konu}",
                        "model_version": "melody",
                        "duration": 30,
                        "temperature": 1.0,
                        "top_k": 250,
                        "top_p": 0.9
                    }
                )
            
            if output:
                st.success("🎉 Şarkı hazır!")
                
                # Audio player
                st.audio(output, format="audio/mp3")
                
                # Download link
                st.markdown(f"[⬇️ MP3 İndir]({output})")
                
                # Sözleri de göster
                with st.expander("📝 Şarkı Sözleri"):
                    st.code(sozler)
                
                st.balloons()
            else:
                st.error("Şarkı üretilemedi. Lütfen tekrar deneyin.")
                
        except Exception as e:
            st.error(f"Replicate hatası: {e}")
            st.info("💡 API token'ınızı kontrol edin veya kredi durumunuza bakın")
            
            # Sözleri yine de göster
            with st.expander("📝 Şarkı Sözleri (Manuel kullanın)"):
                st.code(sozler)
                st.info("Bu sözleri kopyalayıp suno.ai'de manuel kullanabilirsiniz")
    
    elif btn_olustur:
        st.warning("Lütfen şarkı konusunu yazın!")
