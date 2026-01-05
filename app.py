import streamlit as st
import google.generativeai as genai
import os
import time
from dotenv import load_dotenv

# 1. Sayfa Ayarları
st.set_page_config(page_title="SongAI - Kişiye Özel Müzik", page_icon="🎵", layout="wide")

# 2. API Anahtarı
api_key = st.secrets["GEMINI_API_KEY"] if "GEMINI_API_KEY" in st.secrets else (load_dotenv() or os.getenv("GEMINI_API_KEY"))

try:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")
except:
    st.error("⚠️ Sistem Bakımda (API Key Hatası)")
    st.stop()

# --- REKLAM ALANLARI (HTML) ---
google_ads_html = """
<div style="background-color:#f0f0f0; padding:20px; text-align:center; border:1px dashed #ccc; margin-bottom:10px;">
    <p style="color:#888; font-size:12px;">REKLAM ALANI (Google Ads)</p>
    <h4>Buraya Müzik Ekipmanı Reklamı Gelecek</h4>
</div>
"""

# --- ARAYÜZ ---
st.title("🎵 SongAI: Hayalindeki Şarkıyı Yarat")
st.markdown("**Sadece Nakaratı Dinle, Beğenirsen Satın Al!**")
st.markdown("---")

# Yan Menü: Reklam ve İletişim
with st.sidebar:
    st.header("📢 Sponsorlar")
    st.markdown(google_ads_html, unsafe_allow_html=True)
    st.markdown(google_ads_html, unsafe_allow_html=True)
    st.info("💡 Kurumsal Jingle ve Marka Müzikleri için bizimle iletişime geçin.")

col1, col2 = st.columns([1, 1.5])

with col1:
    st.subheader("🎹 Stüdyo Paneli")
    konu = st.text_area("Şarkı kime/neye özel olsun?", "Sevgilim Ayşe için romantik bir doğum günü şarkısı...", height=100)
    tur = st.selectbox("Müzik Tarzı", ["Turkish Pop", "Slow & Damar", "Rap & Drill", "Anatolian Rock", "Deep House", "K-Pop", "Lo-Fi"])
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
                
                # SİMÜLASYON: Gerçek Suno entegrasyonu için GoAPI gereklidir.
                # Şimdilik kullanıcıya sistemin çalıştığını hissettiriyoruz.
                time.sleep(3) 
                
                st.success("✅ Demo Hazırlandı!")
                
                # 2. Demo Oynatıcı (Buraya örnek bir ses dosyası koyuyoruz, gerçek sistemde API'den gelen link olacak)
                # Buraya gerçek bir 15 saniyelik MP3 URL'si koyarsan o çalar.
                st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3", start_time=0, end_time=15)
                st.caption("⚠️ Şu an sadece 15 saniyelik önizleme (Demo) dinliyorsunuz.")
                
                # 3. Sözleri Göster (Blur efektli - Merak uyandırmak için)
                with st.expander("📜 Şarkı Sözlerini Gör"):
                    st.code(sozler)

                st.markdown("---")
                
                # 4. ÖDEME DUVARI (PAYWALL) 🚧
                st.error("🔒 Şarkının Tamamına Erişmek İçin Kilidi Açın")
                
                # WHATSAPP SİPARİŞ LİNKİ
                # Mesajı otomatik oluşturuyoruz
                wp_mesaj = f"Merhaba, SongAI üzerinden bir şarkı tasarladım. Konu: {konu}, Tarz: {tur}. Tamamını satın almak istiyorum."
                wp_link = f"https://wa.me/905510236145?text={wp_mesaj.replace(' ', '%20')}"
                
                c_pay1, c_pay2 = st.columns(2)
                with c_pay1:
                     st.link_button("🔓 KİLİDİ AÇ (50 TL)", wp_link, use_container_width=True, type="primary")
                with c_pay2:
                     st.caption("Butona bastığınızda WhatsApp üzerinden IBAN iletilecek ve şarkının tamamı size gönderilecektir.")

                # Reklam
                st.markdown(google_ads_html, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Hata: {e}")
                
    elif not btn_olustur:
        st.info("👈 Soldan tasarımını yap, ücretsiz demonu hemen dinle!")
        # Boşken de reklam gösterelim, para kaçmasın
        st.markdown(google_ads_html, unsafe_allow_html=True)
