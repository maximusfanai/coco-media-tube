import os
import threading
import time
import static_ffmpeg
import streamlit as st
import streamlit.components.v1 as components
import yt_dlp

COOKIE_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "youtube_cookies.txt",
)

try:
  cookies_secret = st.secrets.get("YOUTUBE_COOKIES", "")
except Exception:
  cookies_secret = ""

if isinstance(cookies_secret, str) and cookies_secret.strip():
  with open(COOKIE_FILE, "w", encoding="utf-8", newline="") as cookie_file:
    cookie_file.write(cookies_secret.strip() + "\n")

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

query_params = st.query_params
if query_params.get("page") == "home":
  st.session_state.downloaded_file = None
  st.session_state.url_input = ""
  st.session_state.is_downloading = False
  st.query_params.clear()
  st.rerun()

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
if "url_input" not in st.session_state:
  st.session_state.url_input = ""

st.markdown(
    """
<style>
#MainMenu, footer, header, [data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }
html, body, .stApp, [data-testid="stAppViewContainer"] {
    background-color: #04060d !important; color: #ffffff !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    margin: 0 !important; padding: 0 !important;
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
    background: #090e1c; border: 1.5px solid rgba(255, 0, 30, 0.5); border-radius: 8px; 
    width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; 
    cursor: pointer; text-decoration: none !important; box-shadow: 0 0 8px rgba(255, 0, 30, 0.4);
}
.section-label { font-size: 12px; font-weight: 700; color: #ffffff; margin-bottom: 4px; margin-top: 10px; display: flex; align-items: center; gap: 5px; }
.neon-loader-container { display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 8px 0; }
.outer-orbit-ring {
    width: 80px; height: 80px; border-radius: 50%; border: 1.5px solid rgba(139, 0, 0, 0.5);
    display: flex; align-items: center; justify-content: center; position: relative;
    background: radial-gradient(circle, rgba(15, 4, 4, 0.9) 0%, rgba(6, 2, 2, 0.99) 100%);
}
.neon-ring {
    width: 66px; height: 66px; border-radius: 50%;
    background: conic-gradient(#ff1e38 0deg, #ff1e38 var(--deg), #4a0005 var(--deg), #4a0005 360deg);
    display: flex; align-items: center; justify-content: center; position: relative;
}
.neon-ring-inner {
    width: 54px; height: 54px; background-color: #050202; border-radius: 50%;
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    border: 1px solid rgba(255, 30, 56, 0.2);
}
.neon-percent-text { font-size: 11px; font-weight: 800; color: #ffffff; }
.loading-title { font-size: 11px; font-weight: 700; color: #ffffff; margin-top: 6px; text-align: center; }
.loading-subtitle { font-size: 9px; color: #838d9d; margin-top: 1px; text-align: center; }
div[data-testid="stButton"] button, div[data-testid="stDownloadButton"] button {
    background: rgba(8, 20, 38, 0.45) !important; border: 1.5px solid rgba(0, 235, 255, 0.85) !important;
    border-radius: 8px !important; color: #33f3ff !important; font-weight: 700 !important; width: 100% !important;
}
</style>
<div class="header-box">
    <div>
        <div class="brand-row"><span class="yt-icon">▶</span><span class="title-white">YouTube</span></div>
        <div class="title-row"><span class="title-dark">Video</span><span class="title-red">Downloader</span></div>
        <div class="subtitle-text">Save your favorite videos<br>anywhere, anywhere!</div>
    </div>
</div>
<div class="url-input-label"><span style="color: #ff001e;">▶</span> Youtube Link Paste</div>
""",
    unsafe_allow_html=True,
)

url = st.text_input(
    "YouTube URL Link",
    value=st.session_state.url_input,
    placeholder="🔗 Paste YouTube link here...",
    label_visibility="collapsed",
    key="url_input_field",
)

if url != st.session_state.url_input:
  st.session_state.url_input = url

detected_format_index = 0
if url and ".mkv" in url.lower():
  detected_format_index = 2
elif url and ".webm" in url.lower():
  detected_format_index = 3

selected_format = st.radio(
    "Choose Format",
    ["MP4 (video)", "Mp3 (audio)", "MKV (video)", "WebM (video)"],
    index=detected_format_index,
    horizontal=True,
    label_visibility="collapsed",
)

st.markdown("<br>", unsafe_allow_html=True)

if not st.session_state.downloaded_file:
  if url and url.strip() != "":
    if not st.session_state.is_downloading:
      if st.button(
          "Download Now ↓",
          key="main_download_btn",
          type="primary",
          use_container_width=True,
      ):
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

      if "MP3" in fmt_upper:
        ydl_format = "bestaudio/best"
        mime_type = "audio/mpeg"
        target_ext = "mp3"
      elif "MKV" in fmt_upper:
        ydl_format = "best/bestvideo+bestaudio/best"
        mime_type = "video/x-matroska"
        target_ext = "mkv"
      elif "WEBM" in fmt_upper:
        ydl_format = "best/bestvideo+bestaudio/best"
        mime_type = "video/webm"
        target_ext = "webm"
      else:
        ydl_format = "best[ext=mp4]/best"
        mime_type = "video/mp4"
        target_ext = "mp4"

      quality_tag = "Audio" if "MP3" in fmt_upper else "Best"
      base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

      if "MP3" in fmt_upper:
        music_dir = os.path.join(os.path.expanduser("~"), "Music")
        if not os.path.exists(music_dir):
          try:
            os.makedirs(music_dir, exist_ok=True)
          except Exception:
            music_dir = base_dir
        outtmpl_str = os.path.join(music_dir, f"%(title)s.%(ext)s")
      else:
        outtmpl_str = os.path.join(base_dir, f"%(title)s_{quality_tag}.%(ext)s")

      download_completed = [False]
      download_error = [None]
      download_result = [None]
      extracted_info = [None]

      cookies_file_path = COOKIE_FILE if os.path.isfile(COOKIE_FILE) else None

      ydl_opts = {
          "format": ydl_format,
          "outtmpl": outtmpl_str,
          "quiet": True,
          "noplaylist": True,
          "retries": 5,
          "fragment_retries": 5,
          "socket_timeout": 30,
          "extractor_args": {
              "youtube": {
                  "player_client": ["android", "ios", "web"]
              }
          },
          "http_headers": {
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
              "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
              "Accept-Language": "en-US,en;q=0.5",
          },
      }

      if cookies_file_path:
        ydl_opts["cookiefile"] = cookies_file_path

      if "MP3" in fmt_upper:
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            },
            {"key": "FFmpegMetadata"},
        ]
      else:
        ydl_opts["merge_output_format"] = target_ext

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
        st.error(f"Dik lo a awm tlat: {str(download_error[0])}")
      else:
        progress_placeholder.empty()
        st.session_state.downloaded_file = download_result[0]
        st.session_state.downloaded_mime = mime_type
        st.session_state.is_audio = "MP3" in fmt_upper
        st.session_state.is_downloading = False
        st.session_state.url_input = ""
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
    st.session_state.url_input = ""
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
