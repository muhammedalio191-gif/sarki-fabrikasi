import streamlit as st
import google.generativeai as genai
import os
import time
import requests
from dotenv import load_dotenv

# 1. Sayfa Ayarları
st.set_page_config(page_title="SongAI - Kişiye Özel Müzik", page_icon="🎵", layout="wide")

# 2. API Anahtarları Kontrolü
api_key = st.secrets.get("GEMINI_API_KEY") or (load_dotenv() or os.getenv("GEMINI_API_KEY"))
suno_cookie = st.secrets.get("SUNO_COOKIE") or os.getenv("SUNO_COOKIE")

try:
    if not api_key:
        st.error("⚠️ Gemini API Anahtarı Bulunamadı!")
        st.stop()
    
    if not suno_cookie:
        st.warning("⚠️ Suno Cookie bulunamadı. Manuel olarak Streamlit secrets'a ekleyin.")
        st.info("Cookie nasıl alınır: Suno.ai'ye giriş yap → F12 → Application → Cookies → '__client' değerini kopyala")
        
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

# --- SUNO API FONKSİYONLARI ---
class SunoAPI:
    def __init__(self, cookie):
        self.base_url = "https://studio-api.suno.ai"
        self.cookie = cookie
        self.headers = {
            "Cookie": f"__client={cookie}",
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }
    
    def create_song(self, prompt, style="Turkish Pop", title="My Song"):
        """Suno'da şarkı oluşturur"""
        url = f"{self.base_url}/api/generate/v2/"
        payload = {
            "gpt_description_prompt": prompt,
            "mv": "chirp-v3-5",
            "prompt": "",
            "make_instrumental": False,
            "title": title
        }
        
        try:
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return data[0].get("id"), data
            return None, None
        except Exception as e:
            st.error(f"Suno API Hatası: {e}")
            return None, None
    
    def get_song_status(self, song_id):
        """Şarkının durumunu kontrol eder"""
        url = f"{self.base_url}/api/feed/?ids={song_id}"
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                song = data[0]
                status = song.get("status")
                audio_url = song.get("audio_url")
                return status, audio_url
            return None, None
        except Exception as e:
            return None, None
    
    def wait_for_song(self, song_id, max_wait=120):
        """Şarkının tamamlanmasını bekler"""
        start_time = time.time()
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        while time.time() - start_time < max_wait:
            status, audio_url = self.get_song_status(song_id)
            
            elapsed = int(time.time() - start_time)
            progress = min(elapsed / max_wait, 0.95)
            progress_bar.progress(progress)
            
            if status == "complete" and audio_url:
                progress_bar.progress(1.0)
                status_text.success("✅ Şarkı hazır!")
                return audio_url
            elif status == "error":
                status_text.error("❌ Üretim hatası")
                return None
            
            status_text.info(f"🎵 Üretiliyor... ({elapsed}s) - Durum: {status or 'Bekliyor'}")
            time.sleep(3)
        
        status_text.warning("⏱️ Zaman aşımı - Şarkı henüz hazır değil")
        return None

# --- ARAYÜZ ---
st.title("🎵 SongAI: Hayalindeki Şarkıyı Yarat")
st.markdown(f"**Yapay Zeka Motoru: {aktif_model} ile çalışıyor.**")

with st.sidebar:
    st.header("📢 Menü")
    st.info("💡 İletişim: info@songai.com")
    
    with st.expander("⚙️ Suno Ayarları"):
        if suno_cookie:
            st.success("✅ Suno bağlantısı aktif")
        else:
            cookie_input = st.text_input("Suno Cookie (__client)", type="password")
            if cookie_input:
                suno_cookie = cookie_input

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🎹 Tasarım Stüdyosu")
    konu = st.text_area("Şarkı kime/neye özel olsun?", "İstanbul'da aşk...", height=100)
    tur = st.selectbox("Müzik Tarzı", ["Turkish Pop", "Rap", "Rock", "Deep House"])
    vokal = st.selectbox("Vokal", ["Erkek", "Kadın", "Düet"])
    baslik = st.text_input("Şarkı Başlığı (opsiyonel)", "")
    btn_olustur = st.button("✨ Şarkıyı Üret", use_container_width=True)

with col2:
    st.subheader("🎧 Sonuç")
    if btn_olustur and konu:
        with st.spinner("🤖 Gemini sözleri yazıyor..."):
            # 1. Gemini Sözleri Yazıyor
            prompt_sozler = f"""Write a {tur} song in Turkish about: {konu}
            
Vocal: {vokal}
Style: {tur}

Requirements:
- Write complete lyrics with verses, chorus, and bridge
- Make it emotional and fitting for {tur} style
- Use natural Turkish language
- Include song structure markers like [Verse], [Chorus], [Bridge]

Output only the lyrics in Turkish."""

            res = model.generate_content(prompt_sozler)
            sozler = res.text
            
            st.success("✅ Sözler Hazır!")
            with st.expander("📝 Sözleri Gör"):
                st.code(sozler, language="text")
            
            # 2. SUNO ENTEGRASYONU
            if suno_cookie:
                st.divider()
                st.info("🎵 Suno AI ile müzik üretiliyor...")
                
                suno = SunoAPI(suno_cookie)
                
                # Suno için prompt hazırla
                suno_prompt = f"{tur} song in Turkish. {vokal} vocals. Theme: {konu}"
                song_title = baslik or f"{tur} - {konu[:30]}"
                
                # Şarkı oluştur
                song_id, raw_data = suno.create_song(
                    prompt=suno_prompt,
                    style=tur,
                    title=song_title
                )
                
                if song_id:
                    st.success(f"🎼 Şarkı ID: {song_id}")
                    
                    # Şarkının hazır olmasını bekle
                    audio_url = suno.wait_for_song(song_id, max_wait=180)
                    
                    if audio_url:
                        st.success("🎉 Şarkın hazır!")
                        st.audio(audio_url, format="audio/mp3")
                        
                        st.download_button(
                            label="⬇️ Şarkıyı İndir",
                            data=requests.get(audio_url).content,
                            file_name=f"{song_title}.mp3",
                            mime="audio/mp3"
                        )
                        
                        st.balloons()
                    else:
                        st.error("Şarkı üretilemedi. Lütfen tekrar deneyin.")
                        st.info("💡 Alternatif: Sözleri kopyalayıp suno.ai'de manuel oluşturabilirsiniz.")
                else:
                    st.error("Suno bağlantısı başarısız. Cookie'nizi kontrol edin.")
            else:
                st.warning("⚠️ Suno entegrasyonu için cookie gerekli!")
                st.info("👉 Şimdilik sözleri kopyalayıp suno.ai'de manuel kullanabilirsiniz.")
                
                if st.button("📋 Sözleri Kopyala"):
                    st.code(sozler)
    
    elif btn_olustur:
        st.warning("Lütfen şarkı konusunu yazın!")
