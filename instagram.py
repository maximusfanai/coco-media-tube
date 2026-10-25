import os
import tempfile
import threading
import time
import streamlit as st
import streamlit.components.v1 as components
import yt_dlp


def show_instagram_page():
  # Session state setup
  if "quality" not in st.session_state:
    st.session_state["quality"] = "1080P"
  if "format" not in st.session_state:
    st.session_state["format"] = "MP4"
  if "downloaded_bytes" not in st.session_state:
    st.session_state["downloaded_bytes"] = None
  if "download_title" not in st.session_state:
    st.session_state["download_title"] = ""
  if "download_ext" not in st.session_state:
    st.session_state["download_ext"] = "MP4"
  if "mime_type" not in st.session_state:
    st.session_state["mime_type"] = ""
  if "show_ad" not in st.session_state:
    st.session_state["show_ad"] = False
  if "ad_timer" not in st.session_state:
    st.session_state["ad_timer"] = 30

  st.markdown(
      """
<style>
#MainMenu, footer, header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #0c0914 !important;
    color: #ffffff !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    margin: 0 !important;
    padding: 0 !important;
}

.main .block-container, [data-testid="stMainBlockContainer"] {
    max-width: 480px !important; width: 100% !important; margin: 0 auto !important; padding: 12px 10px 130px 10px !important;
}

.header-box { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; margin-top: 2px; }
.brand-row { display: flex; align-items: center; gap: 8px; }
.yt-icon { background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fdf497 5%, #fd5949 45%, #d6249f 60%, #285AEB 90%); color: #ffffff; padding: 5px; border-radius: 8px; box-shadow: 0 0 12px rgba(214, 36, 159, 0.75); display: flex; align-items: center; justify-content: center; }
.title-white { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; line-height: 1; }
.title-row { display: flex; gap: 6px; margin-top: 4px; align-items: flex-start; }
.title-dark { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; line-height: 1; }
.title-red { 
    font-size: 20px; 
    font-weight: 800; 
    background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fdf497 5%, #fd5949 45%, #d6249f 60%, #285AEB 90%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.5px; 
    line-height: 1; 
}
.subtitle-text { font-size: 11px; color: #838d9d; margin-top: 4px; font-weight: 500; }

.top-right-container { display: flex; flex-direction: column; align-items: flex-end; margin-top: 2px; }
.action-icons-row { display: flex; gap: 10px; margin-bottom: 4px; }
.icon-btn-style { 
    background: #120d1c; 
    border: 1.5px solid rgba(214, 36, 159, 0.5); 
    border-radius: 8px; 
    width: 32px; 
    height: 32px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    cursor: pointer; 
    text-decoration: none !important;
    box-shadow: 0 0 8px rgba(214, 36, 159, 0.4);
    transition: all 0.2s ease;
}
.icon-btn-style:hover { border-color: #d6249f; background: #1e142e; }

.graphic-link-container { display: flex; flex-direction: column; align-items: center; }
.graphic-link { text-decoration: none !important; border-bottom: none !important; display: flex; flex-direction: column; align-items: center; }

.watch-on-yt-text { 
    font-size: 13px !important; 
    font-weight: 800; 
    background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fd5949 45%, #d6249f 60%, #285AEB 90%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 3px; 
    letter-spacing: 0.3px; 
    text-align: center; 
}
.watch-on-white {
    color: #ffffff !important;
    -webkit-text-fill-color: #ffffff !important;
}

.graphic-glow { position: relative; width: 90px; height: 62px; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, rgba(214,36,159,0.3) 0%, rgba(12,9,20,0) 75%); }
.video-player-card { width: 78px; height: 42px; background: #120d1c; border: 1.5px solid #d6249f; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(214, 36, 159, 0.6); position: relative; }
.vp-screen { width: 62px; height: 21px; background: #1e142e; border-radius: 4px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
.vp-play-icon { display: flex; align-items: center; justify-content: center; }

.vp-label { font-size: 10px !important; font-weight: 700; color: #ffffff; margin-top: 1px; }

.dl-badge-card { position: absolute; bottom: -4px; right: -4px; background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fd5949 45%, #d6249f 60%, #285AEB 90%); color: #ffffff; border-radius: 50%; width: 16px; height: 16px; display: flex; align-items: center; justify-content: center; font-size: 8px; border: 1.5px solid #0c0914; }

.url-input-label { font-size: 12px; font-weight: 600; color: #ffffff; margin-bottom: 4px; margin-top: 8px; display: flex; align-items: center; gap: 5px; }

div[data-baseweb="input"] { background: #120d1c !important; border: 1.5px solid rgba(214, 36, 159, 0.4) !important; border-radius: 12px !important; color: white !important; }
div[data-baseweb="input"] input { color: white !important; }
div[data-testid="stTextInput"] div[data-baseweb="input"] ~ div { display: none !important; }

div[data-testid="stWidgetLabel"] { display: none !important; }

div[data-testid="stRadio"], 
div[data-testid="stRadio"] > div {
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] { 
    display: flex !important; 
    flex-direction: row !important;
    flex-wrap: nowrap !important; 
    gap: 7px !important; 
    width: 100% !important; 
    justify-content: space-between !important;
    align-items: stretch !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] > div {
    flex: 1 1 0% !important; 
    width: 100% !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: #120d1c !important; 
    border: 1.5px solid rgba(214, 36, 159, 0.4) !important; 
    border-radius: 8px !important; 
    padding: 6px 2px !important;
    height: 38px !important; 
    min-height: 38px !important;
    cursor: pointer !important; 
    display: flex !important; 
    flex-direction: row !important; 
    align-items: center !important; 
    justify-content: center !important;
    flex: 1 1 0% !important; 
    width: 100% !important; 
    margin: 0 !important;
    box-sizing: border-box !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    border: 1.5px solid transparent !important;
    background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fd5949 45%, #d6249f 60%, #285AEB 90%) border-box !important;
    box-shadow: 0 0 14px rgba(214, 36, 159, 0.7), 0 0 6px rgba(253, 89, 73, 0.6) !important;
}

div[data-testid="stRadio"] label > div:first-child { 
    display: none !important; 
}

div[data-testid="stRadio"] div[role="radiogroup"] label p { 
    font-size: 10px !important; 
    font-weight: 600 !important; 
    color: #ffffff !important; 
    text-align: center !important; 
    margin: 0 !important; 
    padding: 0 !important;
    line-height: 1 !important; 
    white-space: nowrap !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 800 !important;
    text-shadow: 0 0 6px rgba(253, 244, 151, 0.8) !important;
}

.section-label { font-size: 12px; font-weight: 700; color: #ffffff; margin-bottom: 4px; margin-top: 10px; display: flex; align-items: center; gap: 5px; }

.neon-loader-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: 8px 0;
}
.outer-orbit-ring {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    border: 1.5px solid rgba(214, 36, 159, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    box-shadow: 0 0 10px rgba(214, 36, 159, 0.6), inset 0 0 6px rgba(214, 36, 159, 0.4);
    background: radial-gradient(circle, rgba(20, 10, 30, 0.9) 0%, rgba(8, 4, 12, 0.99) 100%);
}
.neon-ring {
    width: 66px;
    height: 66px;
    border-radius: 50%;
    background: conic-gradient(#d6249f 0deg, #d6249f var(--deg), #30104a var(--deg), #30104a 360deg);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 10px rgba(214, 36, 159, 0.5);
    position: relative;
}
.neon-ring-inner {
    width: 54px;
    height: 54px;
    background-color: #0c0512;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(214, 36, 159, 0.2);
}
.neon-center-video-box {
    width: 22px;
    height: 15px;
    background: #1e0a2b;
    border: 1px solid #d6249f;
    border-radius: 3px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 4px rgba(214, 36, 159, 0.7);
    position: relative;
    margin-bottom: 1px;
}
.neon-inner-screen {
    width: 16px;
    height: 9px;
    background: #36114d;
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}
.neon-play-arrow {
    color: #fdf497;
    font-size: 6px;
    filter: drop-shadow(0 0 1px #fdf497);
}
.neon-dot-badge {
    position: absolute;
    bottom: 1px;
    right: 1px;
    width: 3px;
    height: 3px;
    background: #ffffff;
    border-radius: 50%;
    box-shadow: 0 0 1px #ffffff;
}
.neon-percent-text {
    font-size: 11px;
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.5px;
}
.loading-title {
    font-size: 11px;
    font-weight: 700;
    color: #ffffff;
    margin-top: 6px;
    text-align: center;
    letter-spacing: -0.3px;
}
.loading-subtitle {
    font-size: 9px;
    color: #838d9d;
    margin-top: 1px;
    text-align: center;
}

.ad-box {
    background: rgba(20, 10, 30, 0.95);
    border: 2px solid #d6249f;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 20px 0;
    box-shadow: 0 0 20px rgba(214, 36, 159, 0.4);
    width: 100%;
    box-sizing: border-box;
}
.ad-title {
    font-size: 18px;
    font-weight: 800;
    background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fd5949 45%, #d6249f 60%, #285AEB 90%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.ad-desc {
    font-size: 12px;
    color: #cccccc;
    margin-bottom: 15px;
}
.ad-timer {
    font-size: 24px;
    font-weight: 900;
    color: #ffffff;
    margin: 10px 0;
}

div[data-testid="stButton"] {
    display: flex !important;
    justify-content: center !important;
}
div[data-testid="stButton"] button {
    background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fd5949 45%, #d6249f 60%, #285AEB 90%) !important;
    border: 1.5px solid rgba(253, 244, 151, 0.8) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    box-shadow: 0 0 16px rgba(214, 36, 159, 0.45), inset 0 0 10px rgba(253, 244, 151, 0.25) !important;
    backdrop-filter: blur(6px) !important;
    padding: 10px 14px !important;
    margin: 4px auto !important;
    width: 100% !important;
    max-width: 240px !important;
    transition: all 0.2s ease-in-out !important;
}

div[data-testid="stDownloadButton"] {
    display: flex !important;
    justify-content: center !important;
}
div[data-testid="stDownloadButton"] button {
    background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fd5949 45%, #d6249f 60%, #285AEB 90%) !important;
    border: 1.5px solid #fdf497 !important;
    color: #ffffff !important;
    font-weight: 800 !important;
    border-radius: 12px !important;
    box-shadow: 0 0 16px rgba(214, 36, 159, 0.5), inset 0 0 10px rgba(253, 244, 151, 0.2) !important;
    backdrop-filter: blur(6px) !important;
    padding: 10px 14px !important;
    margin: 4px auto !important;
    width: 100% !important;
    max-width: 240px !important;
    transition: all 0.2s ease-in-out !important;
}

div[data-testid="stVideo"] { 
    max-width: 100% !important; 
    width: 100% !important; 
    margin: 10px auto !important; 
}
div[data-testid="stVideo"] video { 
    max-height: 540px !important; 
    object-fit: contain !important; 
    border-radius: 12px !important; 
    width: 100% !important; 
    background-color: #000000 !important;
}
</style>

<div class="header-box">
    <div>
        <div class="brand-row">
            <span class="yt-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#ffffff" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
            </span>
            <span class="title-white">Instagram</span>
        </div>
        <div class="title-row">
            <span class="title-dark">Video</span>
            <span class="title-red">Downloader</span>
        </div>
        <div class="subtitle-text">Save your favorite reels & videos<br>anywhere, anytime!</div>
    </div>
    <div class="top-right-container">
        <div class="action-icons-row" style="gap: 10px;">
            <!-- Home Button -->
            <form action="" method="get" style="margin: 0; display: inline-flex;">
                <input type="hidden" name="page" value="home">
                <button type="submit" class="icon-btn-style" title="Home / Reset" style="background: #120d1c; padding: 0; cursor: pointer;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#ffffff" viewBox="0 0 24 24"><path d="M12 3l10 9h-3v9h-6v-6h-2v6h-6v-9h-3z"/></svg>
                </button>
            </form>
        </div>
        <div class="graphic-link-container">
            <a href="https://www.instagram.com" target="_blank" class="graphic-link" title="Open Instagram">
                <div class="watch-on-yt-text"><span class="watch-on-white">Watch on </span>INSTAgram</div>
                <div class="graphic-glow">
                    <div class="video-player-card">
                        <div class="vp-screen">
                            <span class="vp-play-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" fill="#d6249f" viewBox="0 0 24 24"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/></svg>
                            </span>
                        </div>
                        <div class="vp-label">Instagram</div>
                        <div class="dl-badge-card">↓</div>
                    </div>
                </div>
            </a>
        </div>
    </div>
</div>
<div class="url-input-label"><span style="background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fd5949 45%, #d6249f 60%, #285AEB 90%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">▶</span> Instagram Link Paste</div>
""",
      unsafe_allow_html=True,
  )

  # Input Link
  ig_url = st.text_input(
      "Instagram URL Link",
      placeholder="🔗 Paste Instagram URL or HTTP link here...",
      label_visibility="collapsed",
  )

  # JavaScript observer for instant paste detection
  components.html(
      """
    <script>
    const parentDoc = window.parent.document;
    function attachInstantPasteListener() {
        const input = parentDoc.querySelector('div[data-testid="stTextInput"] input');
        if (input && !input.hasAttribute('data-instant-paste-listener')) {
            input.setAttribute('data-instant-paste-listener', 'true');
            const forceStreamlitUpdate = () => {
                const tracker = input._valueTracker;
                if (tracker) { tracker.setValue(''); }
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.blur();
            };
            input.addEventListener('paste', () => { setTimeout(forceStreamlitUpdate, 100); });
            input.addEventListener('input', () => {
                if (input.value && input.value.trim().length > 5) {
                    setTimeout(forceStreamlitUpdate, 250);
                }
            });
        }
    }
    setInterval(attachInstantPasteListener, 250);
    </script>
    """,
      height=0,
      width=0,
  )

  # Choose Format First
  st.markdown(
      '<div class="section-label"><span style="background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fd5949 45%, #d6249f 60%, #285AEB 90%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">▶</span> Choose Format :</div>',
      unsafe_allow_html=True,
  )
  selected_format = st.radio(
      "Choose Format",
      ["MP4 (video)", "Mp3 (audio)", "MKV (video)", "WebM (video)"],
      horizontal=True,
      label_visibility="collapsed",
  )

  # Select Quality Second
  st.markdown(
      '<div class="section-label"><span style="background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fd5949 45%, #d6249f 60%, #285AEB 90%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">▶</span> Select Quality :</div>',
      unsafe_allow_html=True,
  )
  selected_quality = st.radio(
      "Choose Quality",
      ["144P", "240P", "360P", "480P", "720P", "1080P"],
      index=5,
      horizontal=True,
      label_visibility="collapsed",
  )

  st.markdown("<br>", unsafe_allow_html=True)

  # Download Action & Handler
  if st.session_state["downloaded_bytes"] is None:
    if ig_url and ig_url.strip():
      if not st.session_state.get(
          "is_downloading", False
      ) and not st.session_state["show_ad"]:
        if st.button(
            "Download Now ↓",
            key="main_download_btn_ig",
            type="primary",
            use_container_width=True,
        ):
          st.session_state["show_ad"] = True
          st.session_state["ad_timer"] = 30
          st.rerun()

    if st.session_state["show_ad"]:
      ad_placeholder = st.empty()
      while st.session_state["ad_timer"] > 0:
        with ad_placeholder.container():
          st.markdown(
              f"""
              <div class="ad-box">
                  <div class="ad-title">SPONSORED ADVERTISEMENT</div>
                  <div class="ad-desc">Please wait while your download link is being prepared...</div>
              </div>
              """,
              unsafe_allow_html=True,
          )

          st.components.v1.html(
              """
              <div style="margin: 0 auto; width: 100%; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); border-radius: 6px; border: 1px dashed rgba(255,255,255,0.15); padding: 10px;">
                  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
                  <ins class="adsbygoogle"
                       style="display:block; width:100%;"
                       data-ad-client="ca-pub-XXXXXXXXXXXXXXXX"
                       data-ad-slot="1234567890"
                       data-ad-format="auto"
                       data-full-width-responsive="true"></ins>
                  <script>
                       (adsbygoogle = window.adsbygoogle || []).push({});
                  </script>
              </div>
              """,
              height=100,
          )

          st.markdown(
              f"""
              <div class="ad-box" style="margin-top: 0; border-top: none; border-top-left-radius: 0; border-top-right-radius: 0; padding-top: 0;">
                  <div class="ad-timer">{st.session_state["ad_timer"]}s</div>
                  <div style="font-size: 10px; color: #838d9d; margin-top: 5px;">Advertisement is playing (non-skippable)</div>
              </div>
              """,
              unsafe_allow_html=True,
          )

        time.sleep(1)
        st.session_state["ad_timer"] -= 1

      ad_placeholder.empty()
      st.session_state["show_ad"] = False
      st.session_state["is_downloading"] = True
      st.rerun()

    if st.session_state.get("is_downloading", False):
      target_link = ig_url.strip()
      is_direct_link = target_link.startswith(
          "http://"
      ) or target_link.startswith("https://")

      if not is_direct_link:
        raw_url = target_link.split("?")[0]
        if "/reels/audio/" in raw_url:
          clean_url = raw_url.replace("/reels/audio/", "/reel/")
        else:
          clean_url = raw_url
      else:
        clean_url = target_link

      progress_area = st.empty()

      def render_loader(pct=0, title="Downloading Media..."):
        deg = int((pct / 100) * 360)
        html_code = f"""
              <div class="neon-loader-container">
                  <div class="outer-orbit-ring">
                      <div class="neon-ring" style="--deg: {deg}deg;">
                          <div class="neon-ring-inner">
                              <div class="neon-center-video-box">
                                  <div class="neon-inner-screen">
                                      <div class="neon-play-arrow">▶</div>
                                  </div>
                                  <div class="neon-dot-badge"></div>
                              </div>
                              <div class="neon-percent-text">{pct}%</div>
                          </div>
                      </div>
                  </div>
                  <div class="loading-title">{title} ({pct}%)</div>
                  <div class="loading-subtitle">Please do not close the app</div>
              </div>
              """
        progress_area.markdown(html_code, unsafe_allow_html=True)

      with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "outtmpl": os.path.join(tmpdir, "media_file.%(ext)s"),
            "quiet": True,
            "no_warnings": True,
        }
        fmt_upper = selected_format.upper()
        res = selected_quality.replace("P", "").strip()

        if (
            is_direct_link
            and "instagram.com" not in clean_url
            and "fbcdn.net" not in clean_url
        ):
          ydl_opts.update({
              "format": "best/best",
          })
          parsed_ext = os.path.splitext(clean_url.split("?")[0])[1]
          target_ext = (
              parsed_ext if parsed_ext and len(parsed_ext) <= 5 else ".mp4"
          )
        else:
          if "MP3" in fmt_upper:
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
            target_ext = ".mp3"
          else:
            ydl_opts["format"] = f"best[height<={res}]/best"
            if "WEBM" in fmt_upper:
              ydl_opts["merge_output_format"] = "webm"
              target_ext = ".webm"
            elif "MKV" in fmt_upper:
              ydl_opts["merge_output_format"] = "mkv"
              target_ext = ".mkv"
            else:
              ydl_opts["merge_output_format"] = "mp4"
              target_ext = ".mp4"

        result = {"info": None, "error": None}

        def download_worker():
          try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
              result["info"] = ydl.extract_info(clean_url, download=True)
          except Exception as e:
            result["error"] = e

        thread = threading.Thread(target=download_worker)
        thread.start()

        current_pct = 1
        while thread.is_alive():
          render_loader(current_pct, "Downloading Media...")
          time.sleep(0.06)
          if current_pct < 94:
            current_pct += 1

        thread.join()

        if result["error"]:
          progress_area.empty()
          st.session_state["is_downloading"] = False
          st.error(f"Download error: {result['error']}")
        else:
          for p in range(current_pct, 101):
            render_loader(p, "Processing Media...")
            time.sleep(0.015)

          title = (
              result["info"].get("title", "Instagram_Media")
              if result["info"]
              else "Instagram_Media"
          )
          downloaded_files = os.listdir(tmpdir)
          if downloaded_files:
            file_path = os.path.join(tmpdir, downloaded_files[0])
            with open(file_path, "rb") as f:
              file_bytes = f.read()

            st.session_state["downloaded_bytes"] = file_bytes
            st.session_state["download_title"] = title
            st.session_state["download_ext"] = target_ext.replace(".", "")
            st.session_state["mime_type"] = (
                "audio/mpeg"
                if target_ext == ".mp3"
                else f"video/{target_ext[1:]}"
            )

            # Calculate actual file size in MB
            file_size_mb = f"{len(file_bytes) / (1024 * 1024):.1f} MB"

            if "downloads" not in st.session_state:
              st.session_state.downloads = []

            new_download_item = {
                "title": title[:25] + "..." if len(title) > 25 else title,
                "platform": "Instagram",
                "size": file_size_mb,
                "quality": selected_quality,
                "color": "#e000ff",
                "icon": "📷",
            }
            st.session_state.downloads.insert(0, new_download_item)

            progress_area.empty()
            st.session_state["is_downloading"] = False
            st.rerun()
          else:
            progress_area.empty()
            st.session_state["is_downloading"] = False
            st.error("File download chhuak zo lo.")

  # Preview & Save Section
  if st.session_state["downloaded_bytes"] is not None:
    st.markdown(
        '<div class="section-label"><span style="background: radial-gradient(circle at 30% 107%, #fdf497 0%, #fd5949 45%, #d6249f 60%, #285AEB 90%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">▶</span> Downloaded Media Preview :</div>',
        unsafe_allow_html=True,
    )
    if st.button(
        "🔄 Download Another Media",
        use_container_width=True,
        key="download_another_btn_ig",
    ):
      st.session_state["downloaded_bytes"] = None
      st.rerun()

    if st.session_state["download_ext"] == "mp3":
      st.audio(st.session_state["downloaded_bytes"])
    else:
      st.video(st.session_state["downloaded_bytes"])

    st.download_button(
        label="💾 Save File to Device",
        data=st.session_state["downloaded_bytes"],
        file_name=(
            f"{st.session_state['download_title'][:20]}.{st.session_state['download_ext']}"
        ),
        mime=st.session_state["mime_type"],
        use_container_width=True,
    )


if __name__ == "__main__":
  show_instagram_page()