import os
import threading
import time
import static_ffmpeg
import streamlit as st
import streamlit.components.v1 as components
import yt_dlp

# Streamlit secrets atanga cookie text siam chawpna
if "YOUTUBE_COOKIES" in st.secrets:
    with open("youtube_cookies.txt", "w") as f:
        f.write(st.secrets["YOUTUBE_COOKIES"])

try:
  static_ffmpeg.add_paths()
except Exception:
  pass

st.set_page_config(
    page_title="YouTube Video Downloader",
    page_icon="▶",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# Session States Initialization
if "downloaded_file" not in st.session_state:
  st.session_state.downloaded_file = None
if "downloaded_mime" not in st.session_state:
  st.session_state.downloaded_mime = "video/mp4"
if "is_audio" not in st.session_state:
  st.session_state.is_audio = False
if "is_downloading" not in st.session_state:
  st.session_state.is_downloading = False
if "progress_val" not in st.session_state:
  st.session_state.progress_val = 0
if "show_ad" not in st.session_state:
  st.session_state.show_ad = False
if "ad_timer" not in st.session_state:
  st.session_state.ad_timer = 25

st.markdown(
    """
<style>
#MainMenu, footer, header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #04060d !important;
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
.yt-icon { background: #ff0000; color: #ffffff; padding: 4px 10px; border-radius: 8px; font-size: 16px; font-weight: 700; box-shadow: 0 0 12px rgba(255, 0, 0, 0.75); display: flex; align-items: center; justify-content: center; }
.title-white { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; line-height: 1; }
.title-row { display: flex; gap: 6px; margin-top: 4px; align-items: flex-start; }
.title-dark { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; line-height: 1; }
.title-red { font-size: 20px; font-weight: 800; color: #ff2236; letter-spacing: -0.5px; line-height: 1; }
.subtitle-text { font-size: 11px; color: #838d9d; margin-top: 4px; font-weight: 500; }

.top-right-container { display: flex; flex-direction: column; align-items: flex-end; margin-top: 2px; }
.action-icons-row { display: flex; gap: 10px; margin-bottom: 4px; }
.icon-btn-style { 
    background: #090e1c; 
    border: 1.5px solid rgba(255, 0, 30, 0.5); 
    border-radius: 8px; 
    width: 32px; 
    height: 32px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    cursor: pointer; 
    text-decoration: none !important;
    box-shadow: 0 0 8px rgba(255, 0, 30, 0.4);
    transition: all 0.2s ease;
}
.icon-btn-style:hover { border-color: #ff001e; background: #141c2e; }

.graphic-link-container { display: flex; flex-direction: column; align-items: center; }
.graphic-link { text-decoration: none !important; border-bottom: none !important; display: flex; flex-direction: column; align-items: center; }
.watch-on-yt-text { font-size: 10px; font-weight: 800; color: #ffffff; margin-bottom: 4px; letter-spacing: 0.5px; text-align: center; }
.graphic-glow { position: relative; width: 96px; height: 70px; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, rgba(139,0,0,0.3) 0%, rgba(4,6,13,0) 75%); }
.video-player-card { width: 84px; height: 48px; background: #090e1c; border: 1.5px solid #8b0000; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(139, 0, 0, 0.6); position: relative; }
.vp-screen { width: 68px; height: 24px; background: #141c2e; border-radius: 4px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
.vp-play-icon { color: #ff001e; font-size: 18px; }
.vp-label { font-size: 9px; font-weight: 700; color: #ffffff; margin-top: 1px; }
.dl-badge-card { position: absolute; bottom: -4px; right: -4px; background: #ff001e; color: #ffffff; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; font-size: 9px; border: 1.5px solid #04060d; }

.url-input-label { font-size: 12px; font-weight: 600; color: #ffffff; margin-bottom: 4px; margin-top: 8px; display: flex; align-items: center; gap: 5px; }

div[data-baseweb="input"] { background: #090e1c !important; border: 1.5px solid rgba(255, 255, 255, 0.25) !important; border-radius: 12px !important; color: white !important; }
div[data-baseweb="input"] input { color: white !important; }
div[data-testid="stTextInput"] div[data-baseweb="input"] ~ div { display: none !important; }

div[data-testid="stRadio"], 
div[data-testid="stRadio"] > div {
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] { 
    display: grid !important; 
    grid-template-columns: repeat(4, 1fr) !important;
    gap: 4px !important; 
    width: 100% !important; 
}

div[data-testid="stRadio"] div[role="radiogroup"] > div {
    width: 100% !important;
    min-width: 0 !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label {
    background-color: #090e1c !important; 
    border: 1.5px solid rgba(255, 255, 255, 0.4) !important; 
    border-radius: 8px !important; 
    padding: 6px 2px !important;
    height: 38px !important; 
    min-height: 38px !important;
    cursor: pointer !important; 
    display: flex !important; 
    flex-direction: row !important; 
    align-items: center !important; 
    justify-content: center !important;
    width: 100% !important; 
    min-width: 0 !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    border-color: #ff001e !important; 
    background-color: #3b0a11 !important; 
    box-shadow: 0 0 12px rgba(255, 0, 30, 0.5) !important; 
}

div[data-testid="stRadio"] label > div:first-child { 
    display: none !important; 
}

div[data-testid="stRadio"] label > div {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label p { 
    font-size: 11px !important; 
    font-weight: 600 !important; 
    color: #ffffff !important; 
    text-align: center !important; 
    margin: 0 !important; 
    padding: 0 !important;
    line-height: 1 !important; 
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    width: 100% !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) p {
    color: #ffffff !important;
    font-weight: 800 !important;
    text-shadow: 0 0 6px rgba(255, 255, 255, 0.8) !important;
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
    border: 1.5px solid rgba(139, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    box-shadow: 0 0 10px rgba(100, 0, 0, 0.6), inset 0 0 6px rgba(100, 0, 0, 0.4);
    background: radial-gradient(circle, rgba(15, 4, 4, 0.9) 0%, rgba(6, 2, 2, 0.99) 100%);
}
.neon-ring {
    width: 66px;
    height: 66px;
    border-radius: 50%;
    background: conic-gradient(#ff1e38 0deg, #ff1e38 var(--deg), #4a0005 var(--deg), #4a0005 360deg);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 10px rgba(255, 0, 30, 0.5), 0 0 10px rgba(139, 0, 0, 0.6);
    position: relative;
}
.neon-ring-inner {
    width: 54px;
    height: 54px;
    background-color: #050202;
    border-radius: 50%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(255, 30, 56, 0.2);
}
.neon-center-video-box {
    width: 22px;
    height: 15px;
    background: #0f0505;
    border: 1px solid #8b0000;
    border-radius: 3px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 4px rgba(139, 0, 0, 0.7);
    position: relative;
    margin-bottom: 1px;
}
.neon-inner-screen {
    width: 16px;
    height: 9px;
    background: #1a0808;
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}
.neon-play-arrow {
    color: #ff1e38;
    font-size: 6px;
    filter: drop-shadow(0 0 1px #ff1e38);
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
    background: rgba(15, 8, 8, 0.95);
    border: 2px solid #ff001e;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 20px 0;
    box-shadow: 0 0 20px rgba(255, 0, 30, 0.4);
    width: 100%;
    box-sizing: border-box;
}
.ad-title {
    font-size: 18px;
    font-weight: 800;
    color: #ff001e;
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

div[data-testid="stButton"] button {
    background: rgba(8, 20, 38, 0.45) !important;
    border: 1.5px solid rgba(0, 235, 255, 0.85) !important;
    border-radius: 8px !important;
    color: #33f3ff !important;
    font-weight: 700 !important;
    box-shadow: 0 0 16px rgba(0, 235, 255, 0.45), inset 0 0 10px rgba(0, 235, 255, 0.25) !important;
    backdrop-filter: blur(6px) !important;
    padding: 6px 14px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    width: 100% !important;
    max-width: 100% !important;
    transition: all 0.2s ease-in-out !important;
    box-sizing: border-box !important;
}

div[data-testid="stDownloadButton"] button {
    background: rgba(10, 30, 50, 0.65) !important;
    border: 1.5px solid #00d8ff !important;
    color: #00d8ff !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 16px rgba(0, 216, 255, 0.5), inset 0 0 10px rgba(0, 216, 255, 0.2) !important;
    backdrop-filter: blur(6px) !important;
    padding: 6px 14px !important;
    margin-left: auto !important;
    margin-right: auto !important;
    width: 100% !important;
    max-width: 100% !important;
    transition: all 0.2s ease-in-out !important;
    box-sizing: border-box !important;
}

div[data-testid="stVideo"] { max-width: 320px !important; margin: 0 auto !important; }
div[data-testid="stVideo"] video { max-height: 380px !important; object-fit: contain !important; width: 100% !important; }

@media screen and (max-width: 768px) {
    .main .block-container, [data-testid="stMainBlockContainer"] {
        padding: 8px 6px 100px 6px !important;
    }
}
</style>

<div class="header-box">
    <div>
        <div class="brand-row">
            <span class="yt-icon">▶</span>
            <span class="title-white">YouTube</span>
        </div>
        <div class="title-row">
            <span class="title-dark">Video</span>
            <span class="title-red">Downloader</span>
        </div>
        <div class="subtitle-text">Save your favorite videos<br>anywhere, anywhere!</div>
    </div>
    <div class="top-right-container">
        <div class="action-icons-row" style="gap: 10px;">
            <form action="" method="get" style="margin: 0; display: inline-flex;">
                <input type="hidden" name="page" value="home">
                <button type="submit" class="icon-btn-style" title="Home / Reset" style="background: #090e1c; padding: 0; cursor: pointer;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#ffffff" viewBox="0 0 24 24"><path d="M12 3l10 9h-3v9h-6v-6h-2v6h-6v-9h-3z"/></svg>
                </button>
            </form>
        </div>
        <div class="graphic-link-container">
            <a href="https://www.youtube.com" target="_blank" class="graphic-link" title="Open YouTube">
                <div class="watch-on-yt-text">WATCH ON YOUtube</div>
                <div class="graphic-glow">
                    <div class="video-player-card">
                        <div class="vp-screen"><span class="vp-play-icon">▶</span></div>
                        <div class="vp-label">YouTube</div>
                        <div class="dl-badge-card">↓</div>
                    </div>
                </div>
            </a>
        </div>
    </div>
</div>
<div class="url-input-label"><span style="color: #ff001e;">▶</span> Youtube Link Paste</div>
""",
    unsafe_allow_html=True,
)

url = st.text_input(
    "YouTube URL Link",
    placeholder="🔗 Paste YouTube link here...",
    label_visibility="collapsed",
)

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
                if (tracker) {
                    tracker.setValue('');
                }
                input.dispatchEvent(new Event('input', { bubbles: true }));
                input.dispatchEvent(new Event('change', { bubbles: true }));
                input.blur();
            };

            input.addEventListener('paste', () => {
                setTimeout(forceStreamlitUpdate, 100);
            });

            input.addEventListener('input', () => {
                if (input.value && input.value.trim().length > 3) {
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

st.markdown(
    '<div class="section-label"><span style="color: #ff001e;">▶</span> Choose'
    " Format :</div>",
    unsafe_allow_html=True,
)
selected_format = st.radio(
    "Choose Format",
    ["MP4 (video)", "Mp3 (audio)", "MKV (video)", "WebM (video)"],
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown(
    '<div class="section-label"><span style="color: #ff001e;">▶</span> Select'
    " Quality :</div>",
    unsafe_allow_html=True,
)
selected_quality = st.radio(
    "Choose Quality",
    ["Data Saver", "SD", "HD", "Best Quality"],
    index=3,
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

if not st.session_state.downloaded_file:
  if url and url.strip() != "":
    if not st.session_state.is_downloading and not st.session_state.show_ad:
      if st.button(
          "Download Now ↓",
          key="main_download_btn",
          type="primary",
          use_container_width=True,
      ):
        st.session_state.show_ad = True
        st.session_state.ad_timer = 25
        st.rerun()

  if st.session_state.show_ad:
    ad_placeholder = st.empty()

    while st.session_state.ad_timer > 0:
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
                        <div class="ad-timer">{st.session_state.ad_timer}s</div>
                        <div style="font-size: 10px; color: #838d9d; margin-top: 5px;">Advertisement is playing (non-skippable)</div>
                    </div>
                    """,
            unsafe_allow_html=True,
        )

      time.sleep(1)
      st.session_state.ad_timer -= 1

    ad_placeholder.empty()
    st.session_state.show_ad = False
    st.session_state.is_downloading = True
    st.session_state.progress_val = 1
    st.rerun()

  if st.session_state.is_downloading:
    progress_placeholder = st.empty()

    try:
      target_url = url.strip()
      if "&list=" in target_url:
        target_url = target_url.split("&list=")[0]
      elif "?list=" in target_url:
        target_url = target_url.split("?list=")[0]

      fmt_upper = selected_format.upper()
      qual_upper = selected_quality.upper()

      is_direct_link = target_url.startswith("http://") or target_url.startswith("https://")
      is_yt_link = "youtube.com" in target_url or "youtu.be" in target_url or "shorts" in target_url
      is_shorts = "shorts" in target_url

      if "MP3" in fmt_upper:
        ydl_format = "bestaudio/best"
        mime_type = "audio/mpeg"
        target_ext = "mp3"
      else:
        if is_direct_link and not is_yt_link:
          ydl_format = "best/best"
          target_ext = os.path.splitext(target_url.split("?")[0])[1].replace(".", "")
          if not target_ext or len(target_ext) > 5:
            target_ext = "mp4"
          mime_type = f"video/{target_ext}" if target_ext in ["mp4", "webm", "mkv"] else "video/mp4"
        else:
          if "DATA SAVER" in qual_upper:
            ydl_format = "best[height<=360]/best"
          elif "SD" in qual_upper:
            ydl_format = "best[height<=480]/best"
          elif "HD" in qual_upper:
            ydl_format = "best[height<=720]/best"
          else:
            ydl_format = "best/best"

          if "MKV" in fmt_upper:
            mime_type = "video/x-matroska"
            target_ext = "mkv"
          elif "WEBM" in fmt_upper:
            mime_type = "video/webm"
            target_ext = "webm"
          else:
            mime_type = "video/mp4"
            target_ext = "mp4"

      quality_tag = "Audio" if "MP3" in fmt_upper else selected_quality
      
      base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      outtmpl_str = os.path.join(base_dir, f"%(title)s_{quality_tag}.%(ext)s")

      download_completed = [False]
      download_error = [None]
      download_result = [None]
      extracted_info = [None]

      cookies_file_path = "youtube_cookies.txt" if os.path.exists("youtube_cookies.txt") else None

      ydl_opts = {
          "format": ydl_format,
          "outtmpl": outtmpl_str,
          "quiet": True,
          "noplaylist": True,
          "cookiefile": cookies_file_path,
          "extractor_args": {
              "youtube": {
                  "player_client": ["web_embedded", "web_safari", "mweb", "tv"],
              }
          },
          "http_headers": {
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:144.0) Gecko/20100101 Firefox/144.0",
              "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
              "Accept-Language": "en-US,en;q=0.5",
          }
      }
      
      if ydl_opts.get("cookiefile") is None:
          del ydl_opts["cookiefile"]

      if "MP3" in fmt_upper:
        ydl_opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]
      else:
        ydl_opts["merge_output_format"] = target_ext
        if "MKV" in fmt_upper:
          ydl_opts["postprocessor_args"] = {
              "Merger": ["-c:v", "copy", "-c:a", "aac", "-ac", "2"]
          }
        elif "WEBM" in fmt_upper:
          ydl_opts["postprocessor_args"] = {
              "Merger": ["-c:v", "copy", "-c:a", "opus"]
          }
        else:
          ydl_opts["postprocessor_args"] = {
              "Merger": ["-c:v", "copy", "-c:a", "aac", "-ac", "2"]
          }

      def run_dl():
        try:
          with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(target_url, download=True)
            extracted_info[0] = info
            filename = ydl.prepare_filename(info)
            base, _ = os.path.splitext(filename)
            expected_file = f"{base}.{target_ext}"
            if os.path.exists(expected_file):
              filename = expected_file
            download_result[0] = filename
            download_completed[0] = True
        except Exception as e:
          download_error[0] = e
          download_completed[0] = True

      t = threading.Thread(target=run_dl)
      t.start()

      current_p = st.session_state.progress_val
      if current_p < 1:
        current_p = 1

      while not download_completed[0]:
        if current_p < 92:
          current_p += 1
          st.session_state.progress_val = current_p

        deg = int((current_p / 100) * 360)
        with progress_placeholder.container():
          st.markdown(
              f"""
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
                                    <div class="neon-percent-text">{current_p}%</div>
                                </div>
                            </div>
                        </div>
                        <div class="loading-title">Downloading... ({current_p}%)</div>
                        <div class="loading-subtitle">Please do not close the app</div>
                    </div>
                    """,
              unsafe_allow_html=True,
          )

        time.sleep(0.08)

      t.join()

      if download_error[0]:
        st.session_state.is_downloading = False
        st.error(f"Dik lo a awm tlat: {download_error[0]}")
      else:
        while current_p < 100:
          current_p += 1
          st.session_state.progress_val = current_p
          deg = int((current_p / 100) * 360)
          with progress_placeholder.container():
            st.markdown(
                f"""
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
                                        <div class="neon-percent-text">{current_p}%</div>
                                    </div>
                                </div>
                            </div>
                            <div class="loading-title">Finalizing...</div>
                            <div class="loading-subtitle">Almost done, please wait</div>
                        </div>
                        """,
                unsafe_allow_html=True,
            )
          time.sleep(0.06)

        progress_placeholder.empty()

        st.session_state.downloaded_file = download_result[0]
        st.session_state.downloaded_mime = mime_type
        st.session_state.is_audio = "MP3" in fmt_upper
        st.session_state.is_downloading = False

        if extracted_info[0]:
          vid_title = extracted_info[0].get("title", "YouTube Video")
          file_path = download_result[0]
          file_size_mb = 0.0
          if os.path.exists(file_path):
            file_size_mb = round(
                os.path.getsize(file_path) / (1024 * 1024), 1
            )

          if "downloads" not in st.session_state:
            st.session_state.downloads = []

          st.session_state.downloads.insert(
              0,
              {
                  "title": vid_title,
                  "platform": "YouTube/Web",
                  "size": f"{file_size_mb} MB",
                  "quality": selected_quality,
                  "color": "#FF0000",
              },
          )

        st.rerun()

    except Exception as e:
      st.session_state.is_downloading = False
      st.error(f"Dik lo a awm tlat: {e}")

if st.session_state.downloaded_file and os.path.exists(
    st.session_state.downloaded_file
):
  st.markdown(
      '<div class="section-label"><span style="color: #ff001e;">▶</span>'
      " Downloaded Media Preview :</div>",
      unsafe_allow_html=True,
  )

  if st.button(
      "🔄 Download Another Video",
      use_container_width=True,
      key="download_another_btn",
  ):
    st.session_state.downloaded_file = None
    st.rerun()

  if st.session_state.is_audio:
    st.audio(st.session_state.downloaded_file)
  else:
    st.video(st.session_state.downloaded_file)

  with open(st.session_state.downloaded_file, "rb") as file:
    st.download_button(
        label="Save Folder",
        data=file,
        file_name=os.path.basename(st.session_state.downloaded_file),
        mime=st.session_state.downloaded_mime,
        use_container_width=True,
    )