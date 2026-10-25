import base64
import os
import threading
import time
import imageio_ffmpeg
import streamlit as st
import streamlit.components.v1 as components
import yt_dlp

# Page Config
st.set_page_config(
    page_title="Facebook Media Downloader",
    page_icon="🌐",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Mobile MIME Type helper function
def get_mime_type(file_path):
  if file_path.endswith(".mp3"):
    return "audio/mpeg"
  elif file_path.endswith(".webm"):
    return "video/webm"
  elif file_path.endswith(".mkv"):
    return "video/x-matroska"
  elif file_path.endswith(".mp4"):
    return "video/mp4"
  return "application/octet-stream"


# Session States Initialization
if "fb_link" not in st.session_state:
  st.session_state.fb_link = ""
if "current_file" not in st.session_state:
  st.session_state.current_file = None
if "is_downloading" not in st.session_state:
  st.session_state.is_downloading = False
if "progress_val" not in st.session_state:
  st.session_state.progress_val = 0
if "show_ad" not in st.session_state:
  st.session_state.show_ad = False
if "ad_timer" not in st.session_state:
  st.session_state.ad_timer = 30

# Custom CSS matching exact UI Design (Fixed video distortion/landscape issue)
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
.yt-icon { background: linear-gradient(45deg, #1877f2, #0051cc); color: #ffffff; padding: 5px; border-radius: 8px; box-shadow: 0 0 12px rgba(24, 119, 242, 0.75); display: flex; align-items: center; justify-content: center; }
.title-white { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; line-height: 1; }
.title-row { display: flex; gap: 6px; margin-top: 4px; align-items: flex-start; }
.title-dark { font-size: 26px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; line-height: 1; }
.title-red { font-size: 20px; font-weight: 800; color: #1877f2; letter-spacing: -0.5px; line-height: 1; }
.subtitle-text { font-size: 11px; color: #838d9d; margin-top: 4px; font-weight: 500; }

.top-right-container { display: flex; flex-direction: column; align-items: flex-end; margin-top: 2px; }
.action-icons-row { display: flex; gap: 10px; margin-bottom: 4px; }
.icon-btn-style { 
    background: #090e1c; 
    border: 1.5px solid rgba(24, 119, 242, 0.5); 
    border-radius: 8px; 
    width: 32px; 
    height: 32px; 
    display: flex; 
    align-items: center; 
    justify-content: center; 
    cursor: pointer; 
    text-decoration: none !important;
    box-shadow: 0 0 8px rgba(24, 119, 242, 0.4);
    transition: all 0.2s ease;
}
.icon-btn-style:hover { border-color: #1877f2; background: #141c2e; }

.graphic-link-container { display: flex; flex-direction: column; align-items: center; }
.graphic-link { text-decoration: none !important; border-bottom: none !important; display: flex; flex-direction: column; align-items: center; }

.watch-on-yt-text { font-size: 12px !important; font-weight: 800; color: #ffffff; margin-bottom: 5px; letter-spacing: 0.5px; text-align: center; }

.graphic-glow { position: relative; width: 96px; height: 70px; display: flex; align-items: center; justify-content: center; background: radial-gradient(circle, rgba(24,119,242,0.3) 0%, rgba(4,6,13,0) 75%); }
.video-player-card { width: 84px; height: 48px; background: #090e1c; border: 1.5px solid #1877f2; border-radius: 8px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 0 10px rgba(24, 119, 242, 0.6); position: relative; }
.vp-screen { width: 68px; height: 24px; background: #141c2e; border-radius: 4px; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }
.vp-play-icon { display: flex; align-items: center; justify-content: center; }

.vp-label { font-size: 11px !important; font-weight: 700; color: #ffffff; margin-top: 1px; }

.dl-badge-card { position: absolute; bottom: -4px; right: -4px; background: #1877f2; color: #ffffff; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; font-size: 9px; border: 1.5px solid #04060d; }

.url-input-label { font-size: 12px; font-weight: 600; color: #ffffff; margin-bottom: 4px; margin-top: 8px; display: flex; align-items: center; gap: 5px; }

div[data-baseweb="input"] { background: #090e1c !important; border: 1.5px solid rgba(255, 255, 255, 0.25) !important; border-radius: 12px !important; color: white !important; }
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
    flex: 1 1 0% !important; 
    width: 100% !important; 
    margin: 0 !important;
    box-sizing: border-box !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
    border-color: #1877f2 !important; 
    background-color: #0c2142 !important; 
    box-shadow: 0 0 12px rgba(24, 119, 242, 0.5) !important; 
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
    border: 1.5px solid rgba(24, 119, 242, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    box-shadow: 0 0 10px rgba(24, 119, 242, 0.6), inset 0 0 6px rgba(24, 119, 242, 0.4);
    background: radial-gradient(circle, rgba(15, 4, 4, 0.9) 0%, rgba(6, 2, 2, 0.99) 100%);
}
.neon-ring {
    width: 66px;
    height: 66px;
    border-radius: 50%;
    background: conic-gradient(#1877f2 0deg, #1877f2 var(--deg), #002d6b var(--deg), #002d6b 360deg);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 10px rgba(24, 119, 242, 0.5);
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
    border: 1px solid rgba(24, 119, 242, 0.2);
}
.neon-center-video-box {
    width: 22px;
    height: 15px;
    background: #050d1a;
    border: 1px solid #1877f2;
    border-radius: 3px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 0 4px rgba(24, 119, 242, 0.7);
    position: relative;
    margin-bottom: 1px;
}
.neon-inner-screen {
    width: 16px;
    height: 9px;
    background: #081830;
    border-radius: 2px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
}
.neon-play-arrow {
    color: #1877f2;
    font-size: 6px;
    filter: drop-shadow(0 0 1px #1877f2);
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
    border: 2px solid #1877f2;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    margin: 20px 0;
    box-shadow: 0 0 20px rgba(24, 119, 242, 0.4);
    width: 100%;
    box-sizing: border-box;
}
.ad-title {
    font-size: 18px;
    font-weight: 800;
    color: #1877f2;
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
    padding: 10px 14px !important;
    margin: 0 !important;
    width: 100% !important;
    transition: all 0.2s ease-in-out !important;
}

div[data-testid="stDownloadButton"] button {
    background: rgba(10, 30, 50, 0.65) !important;
    border: 1.5px solid #00d8ff !important;
    color: #00d8ff !important;
    font-weight: 700 !important;
    border-radius: 8px !important;
    box-shadow: 0 0 16px rgba(0, 216, 255, 0.5), inset 0 0 10px rgba(0, 216, 255, 0.2) !important;
    backdrop-filter: blur(6px) !important;
    padding: 10px 14px !important;
    margin: 0 !important;
    width: 100% !important;
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
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" fill="#ffffff" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
            </span>
            <span class="title-white">Facebook</span>
        </div>
        <div class="title-row">
            <span class="title-dark">Video</span>
            <span class="title-red">Downloader</span>
        </div>
        <div class="subtitle-text">Save your favorite videos & reels<br>anywhere, anytime!</div>
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
            <a href="https://www.facebook.com" target="_blank" class="graphic-link" title="Open Facebook">
                <div class="watch-on-yt-text">Watch on FACEbook</div>
                <div class="graphic-glow">
                    <div class="video-player-card">
                        <div class="vp-screen">
                            <span class="vp-play-icon">
                                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="#1877f2" viewBox="0 0 24 24"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
                            </span>
                        </div>
                        <div class="vp-label">Facebook</div>
                        <div class="dl-badge-card">↓</div>
                    </div>
                </div>
            </a>
        </div>
    </div>
</div>
<div class="url-input-label"><span style="color: #1877f2;">▶</span> Facebook Link Paste</div>
""",
    unsafe_allow_html=True,
)

# Input Link
fb_url = st.text_input(
    "Facebook URL Link",
    placeholder="🔗 Paste Facebook link here...",
    label_visibility="collapsed",
)
st.session_state.fb_link = fb_url

# JavaScript observer: Forces React & Streamlit to rerun instantly on paste
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
    '<div class="section-label"><span style="color: #1877f2;">▶</span> Choose Format :</div>',
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
    '<div class="section-label"><span style="color: #1877f2;">▶</span> Select Quality :</div>',
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

# Main Download Controller - Threaded smooth loader execution
if not st.session_state.current_file:
  if not st.session_state.is_downloading and not st.session_state.show_ad:
    if fb_url and fb_url.strip():
      if st.button(
          "Download Now ↓",
          key="main_download_btn",
          type="primary",
          use_container_width=True,
      ):
        st.session_state.show_ad = True
        st.session_state.ad_timer = 30
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
      save_dir = "downloads"
      os.makedirs(save_dir, exist_ok=True)

      ffmpeg_exe_path = imageio_ffmpeg.get_ffmpeg_exe()

      ydl_opts = {
          "outtmpl": f"{save_dir}/%(title).30s_%(id)s.%(ext)s",
          "restrictfilenames": True,
          "windowsfilenames": True,
          "quiet": True,
          "no_warnings": True,
          "no_color": True,
          "nocheckcertificate": True,
          "ffmpeg_location": ffmpeg_exe_path,
          "http_headers": {
              "User-Agent": (
                  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
              ),
          },
      }

      fmt_upper = selected_format.upper()
      res = selected_quality.replace("P", "").strip()
      res_num = int(res)

      target_link = fb_url.strip()
      is_direct_link = target_link.startswith(
          "http://"
      ) or target_link.startswith("https://")
      if (
          is_direct_link
          and "facebook.com" not in target_link
          and "fb.watch" not in target_link
      ):
        ydl_opts.update({
            "format": "best/best",
        })
        target_ext = os.path.splitext(target_link.split("?")[0])[1]
        if not target_ext or len(target_ext) > 5:
          target_ext = ".mp4"
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
          if res_num <= 360:
            format_str = f"best[height<={res}]/worst"
          elif res_num <= 720:
            format_str = f"best[height<={res}]/best[height<=480]/worst"
          else:
            format_str = f"best[height<={res}]/best"

          ydl_opts.update({
              "format": format_str,
              "format_sort": [f"res:{res}"],
          })

          if "WEBM" in fmt_upper:
            ydl_opts.update({
                "merge_output_format": "webm",
            })
            target_ext = ".webm"
          elif "MKV" in fmt_upper:
            ydl_opts.update({
                "merge_output_format": "mkv",
                "postprocessor_args": {
                    "Merger": ["-c:v", "copy", "-c:a", "aac", "-ac", "2"]
                },
            })
            target_ext = ".mkv"
          else:
            ydl_opts.update({
                "merge_output_format": "mp4",
                "postprocessor_args": {
                    "Merger": ["-c:v", "copy", "-c:a", "aac", "-ac", "2"]
                },
            })
            target_ext = ".mp4"

      download_completed = [False]
      download_error = [None]
      download_result = [None]

      def run_dl(url_to_download):
        try:
          with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_to_download, download=True)
            prep_filename = ydl.prepare_filename(info)

            base_name = os.path.splitext(prep_filename)[0]
            expected_file = base_name + target_ext

            if os.path.exists(expected_file):
              filename = expected_file
            elif os.path.exists(prep_filename):
              filename = prep_filename
            else:
              files = [
                  os.path.join(save_dir, f)
                  for f in os.listdir(save_dir)
                  if not f.endswith(".part")
              ]
              filename = files[0] if files else expected_file

            download_result[0] = filename
            download_completed[0] = True
        except Exception as e:
          if "WEBM" in fmt_upper or "MKV" in fmt_upper:
            try:
              fb_opts = ydl_opts.copy()
              fb_opts["merge_output_format"] = "mp4"
              fb_opts["postprocessor_args"] = {
                  "Merger": ["-c:v", "copy", "-c:a", "aac", "-ac", "2"]
              }
              with yt_dlp.YoutubeDL(fb_opts) as ydl_fb:
                info = ydl_fb.extract_info(url_to_download, download=True)
                prep_filename = ydl_fb.prepare_filename(info)
                files = [
                    os.path.join(save_dir, f)
                    for f in os.listdir(save_dir)
                    if not f.endswith(".part")
                ]
                download_result[0] = (
                    prep_filename
                    if os.path.exists(prep_filename)
                    else (files[0] if files else prep_filename)
                )
                download_completed[0] = True
                return
            except Exception as inner_e:
              download_error[0] = str(inner_e)
              download_completed[0] = True
              return
          download_error[0] = str(e)
          download_completed[0] = True

      t = threading.Thread(target=run_dl, args=(target_link,))
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
        st.error(f"Download error: {download_error[0]}")
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

        st.session_state.current_file = download_result[0]
        st.session_state.is_downloading = False
        st.rerun()

    except Exception as e:
      st.session_state.is_downloading = False
      st.error(f"Download error: {e}")

# Downloaded Media Preview Section
if st.session_state.current_file and os.path.exists(
    st.session_state.current_file
):
  st.markdown(
      '<div class="section-label"><span style="color: #1877f2;">▶</span> Downloaded Media Preview :</div>',
      unsafe_allow_html=True,
  )

  if st.button(
      "🔄 Download Another Media",
      use_container_width=True,
      key="download_another_btn",
  ):
    st.session_state.current_file = None
    st.rerun()

  result = st.session_state.current_file
  if result.endswith(".mp3"):
    st.audio(result)
  else:
    st.video(result)

  mime_type = get_mime_type(result)
  with open(result, "rb") as file_data:
    st.download_button(
        label="💾 Save File to Device",
        data=file_data.read(),
        file_name=os.path.basename(result),
        mime=mime_type,
        use_container_width=True,
    )  