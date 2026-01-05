import streamlit as st
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# suno-api PyPI paketi
try:
    import suno
except ImportError:
    st.error("⚠️ 'suno-api' paketi yüklü değil. requirements.txt'e ekleyin: suno-api>=0.1.2")
    st.stop()

# Sayfa Ayarları
st.set_page_config(page_title="SongAI - Kişiye Özel Müzik", page_icon="🎵", layout="wide")

# API Keys
api_key = st.secrets.get("GEMINI_API_KEY") or (load_dotenv() or os.getenv("GEMINI_API_KEY"))
suno_cookie = st.secrets.get("SUNO_COOKIE") or os.getenv("SUNO_COOKIE")

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

# SUNO CLIENT
@st.cache_resource
def get_suno_client():
    if not suno_cookie:
        return None
    try:
        client = suno.Suno(cookie=suno_cookie)
        return client
    except Exception as e:
        st.error(f"Suno client hatası: {e}")
        st.info("💡 Cookie: F12 → Network → Yenile → 'client?_clerk' → Headers → Cookie satırı")
        return None

# UI
st.title("🎵 SongAI: Hayalindeki Şarkıyı Yarat")
st.markdown(f"**Yapay Zeka Motoru: {aktif_model} ile çalışıyor.**")

with st.sidebar:
    st.header("📢 Menü")
    st.info("💡 İletişim: info@songai.com")
    
    with st.expander("⚙️ Suno Durumu"):
        if suno_cookie:
            test_client = get_suno_client()
            if test_client:
                try:
                    credits = test_client.get_credits()
                    st.success(f"✅ Bağlı | Kredi: {credits}")
                except Exception as e:
                    st.warning(f"⚠️ Cookie sorunlu: {str(e)[:100]}")
                    st.info("👉 Cookie'yi Network sekmesinden al")
            else:
                st.error("❌ Client başlatılamadı")
        else:
            st.error("❌ SUNO_COOKIE bulunamadı")
            with st.expander("📖 Cookie Nasıl Alınır?"):
                st.markdown("""
                1. **suno.com/create** → Giriş yap
                2. **F12** → **Network** sekmesi
                3. **F5** ile sayfayı yenile
                4. Ara: `client?_clerk_js_version`
                5. İsteğe tıkla → **Headers**
                6. **Cookie:** satırını TAMAMEN kopyala
                
                Örnek:
                ```
                __client=eyJ...; __session=abc...; mp_=...
                ```
                """)

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🎹 Tasarım Stüdyosu")
    konu = st.text_area("Şarkı kime/neye özel olsun?", "İstanbul'da aşk...", height=100)
    tur = st.selectbox("Müzik Tarzı", ["Turkish Pop", "Rap", "Rock", "Deep House", "Ballad"])
    vokal = st.selectbox("Vokal", ["Erkek", "Kadın", "Düet"])
    baslik = st.text_input("Şarkı Başlığı", "")
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
        
        # 2. SUNO ENTEGRASYONU
        if suno_cookie:
            st.divider()
            client = get_suno_client()
            
            if client:
                try:
                    st.info("🎵 Suno AI ile müzik üretiliyor...")
                    
                    # Prompt hazırla
                    suno_prompt = f"{tur} song in Turkish. {vokal} vocals. About: {konu}"
                    song_title = baslik or f"{tur} - {konu[:30]}"
                    
                    # Şarkı oluştur
                    with st.spinner("🎼 Üretiliyor..."):
                        clips = client.songs.generate(
                            prompt=suno_prompt,
                            is_custom=False
                        )
                    
                    if clips and len(clips) > 0:
                        clip = clips[0]
                        clip_id = clip.id
                        
                        st.success(f"🎼 Üretiliyor... ID: {clip_id}")
                        
                        # Tamamlanana kadar bekle
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        max_wait = 180
                        start_time = time.time()
                        
                        while time.time() - start_time < max_wait:
                            song_data = client.songs.get(clip_id)
                            
                            elapsed = int(time.time() - start_time)
                            progress = min(elapsed / max_wait, 0.95)
                            progress_bar.progress(progress)
                            
                            if song_data.audio_url:
                                progress_bar.progress(1.0)
                                status_text.success("✅ Şarkı hazır!")
                                
                                st.audio(song_data.audio_url, format="audio/mp3")
                                st.markdown(f"[⬇️ MP3 İndir]({song_data.audio_url})")
                                
                                st.balloons()
                                break
                            
                            status_text.info(f"🎵 Üretiliyor... ({elapsed}s)")
                            time.sleep(3)
                        else:
                            st.warning("⏱️ Zaman aşımı")
                    else:
                        st.error("Şarkı oluşturulamadı")
                        
                except Exception as e:
                    st.error(f"Suno hatası: {e}")
                    st.info("💡 Sözleri kopyalayıp manuel kullanabilirsiniz")
                    if st.button("📋 Sözleri Kopyala"):
                        st.code(sozler)
            else:
                st.error("⚠️ Suno client başlatılamadı")
                st.info("Cookie'yi kontrol edin (Network sekmesinden alın)")
        else:
            st.warning("⚠️ Suno entegrasyonu için cookie gerekli!")
            if st.button("📋 Sözleri Göster"):
                st.code(sozler)
    
    elif btn_olustur:
        st.warning("Lütfen şarkı konusunu yazın!")
