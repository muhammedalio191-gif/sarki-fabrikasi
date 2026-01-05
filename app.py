import streamlit as st
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# PyPI Suno paketi
try:
    import suno
except ImportError:
    st.error("⚠️ 'suno-api' paketi yüklü değil. requirements.txt'e ekleyin: suno-api")
    st.stop()

# Sayfa Ayarları
st.set_page_config(page_title="SongAI - Kişiye Özel Müzik", page_icon="🎵", layout="wide")

# API Anahtarları
api_key = st.secrets.get("GEMINI_API_KEY") or (load_dotenv() or os.getenv("GEMINI_API_KEY"))
suno_cookie = st.secrets.get("SUNO_COOKIE") or os.getenv("SUNO_COOKIE")

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

# SUNO İSTEMCİSİ (PyPI Paketi)
@st.cache_resource
def get_suno_client():
    if not suno_cookie:
        return None
    try:
        client = suno.Suno(cookie=suno_cookie)
        return client
    except Exception as e:
        st.error(f"Suno client hatası: {e}")
        return None

# ARAYÜZ
st.title("🎵 SongAI: Hayalindeki Şarkıyı Yarat")
st.markdown(f"**Yapay Zeka Motoru: {aktif_model} ile çalışıyor.**")

with st.sidebar:
    st.header("📢 Menü")
    st.info("💡 İletişim: info@songai.com")
    
    with st.expander("⚙️ Suno Ayarları"):
        if suno_cookie:
            client = get_suno_client()
            if client:
                try:
                    credits = client.get_credits()
                    st.success(f"✅ Suno bağlı | Kredi: {credits}")
                except:
                    st.warning("⚠️ Suno cookie geçersiz olabilir")
            else:
                st.warning("⚠️ Suno bağlantısı kurulamadı")
        else:
            st.error("❌ Suno cookie bulunamadı")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🎹 Tasarım Stüdyosu")
    konu = st.text_area("Şarkı kime/neye özel olsun?", "İstanbul'da aşk...", height=100)
    tur = st.selectbox("Müzik Tarzı", ["Turkish Pop", "Rap", "Rock", "Deep House", "Ballad"])
    vokal = st.selectbox("Vokal", ["Erkek", "Kadın", "Düet"])
    baslik = st.text_input("Şarkı Başlığı (opsiyonel)", "")
    btn_olustur = st.button("✨ Şarkıyı Üret", use_container_width=True)

with col2:
    st.subheader("🎧 Sonuç")
    
    if btn_olustur and konu:
        # 1. GEMİNİ SÖZLER
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
            st.info("🎵 Suno AI ile müzik üretiliyor...")
            
            client = get_suno_client()
            
            if client:
                try:
                    # Suno prompt
                    suno_prompt = f"{tur} song in Turkish. {vokal} vocals. About: {konu}"
                    song_title = baslik or f"{tur} - {konu[:30]}"
                    
                    # Şarkı oluştur
                    with st.spinner("🎼 Suno'da şarkı üretiliyor..."):
                        songs = client.songs.generate(
                            prompt=suno_prompt,
                            custom=False,  # GPT mode
                            instrumental=False
                        )
                    
                    if songs and len(songs) > 0:
                        song = songs[0]
                        st.success(f"🎼 Şarkı ID: {song.id}")
                        
                        # Bekleme + ilerleme
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        max_wait = 180
                        start_time = time.time()
                        
                        while time.time() - start_time < max_wait:
                            # Şarkı durumunu kontrol et
                            song_data = client.songs.get(song.id)
                            
                            elapsed = int(time.time() - start_time)
                            progress = min(elapsed / max_wait, 0.95)
                            progress_bar.progress(progress)
                            
                            if song_data.audio_url:
                                progress_bar.progress(1.0)
                                status_text.success("✅ Şarkı hazır!")
                                
                                st.audio(song_data.audio_url, format="audio/mp3")
                                
                                st.download_button(
                                    label="⬇️ Şarkıyı İndir",
                                    data=client.songs.download(song.id),
                                    file_name=f"{song_title}.mp3",
                                    mime="audio/mp3"
                                )
                                
                                st.balloons()
                                break
                            
                            status_text.info(f"🎵 Üretiliyor... ({elapsed}s)")
                            time.sleep(3)
                        else:
                            st.warning("⏱️ Zaman aşımı - Şarkı henüz hazır değil")
                    else:
                        st.error("Şarkı oluşturulamadı")
                        
                except Exception as e:
                    st.error(f"Suno hatası: {e}")
                    st.info("💡 Sözleri manuel olarak suno.ai'de kullanabilirsiniz")
            else:
                st.error("Suno client başlatılamadı. Cookie'nizi kontrol edin.")
        else:
            st.warning("⚠️ Suno entegrasyonu için cookie gerekli!")
            st.info("📋 Şimdilik sözleri kopyalayıp suno.ai'de kullanabilirsiniz")
    
    elif btn_olustur:
        st.warning("Lütfen şarkı konusunu yazın!")
