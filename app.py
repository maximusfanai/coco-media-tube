import base64
import os
import time
import static_ffmpeg
import streamlit as st
import streamlit.components.v1 as components
import yt_dlp

try:
  static_ffmpeg.add_paths()
except Exception:
  pass

st.set_page_config(
    page_title="CoCo Media Tube",
    page_icon="📥",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def scan_media_file(file_path):
  """Triggers Android Media Scanner so downloaded files appear in music/video players instantly."""
  try:
    if os.path.exists(file_path):
      os.system(
          f"am broadcast -a android.intent.action.MEDIA_SCANNER_SCAN_FILE -d"
          f" file://{file_path}"
      )
  except Exception:
    pass


# Query params check
query_params = st.query_params
page_param = query_params.get("page", None)
if isinstance(page_param, list):
  page_param = page_param[0] if page_param else None

# Session States Initialization
if "show_splash" not in st.session_state:
  # App a tir a hawn anih chuan splash a rawn lang ang, link/button atanga lut anih chuan a skip ang
  st.session_state["show_splash"] = False if page_param else True

if "show_google_auth" not in st.session_state:
  st.session_state["show_google_auth"] = False

if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = True if page_param else False

current_page = page_param if page_param else "home"
if current_page not in ["home", "youtube", "facebook", "instagram", "refresh"]:
  current_page = "home"

if current_page == "refresh":
  st.query_params.clear()
  current_page = "home"


def get_image_base64(file_path):
  if os.path.exists(file_path):
    with open(file_path, "rb") as f:
      data = f.read()
    return f"data:image/png;base64,{base64.b64encode(data).decode()}"
  return ""


logo_path = r"E:\video_downloader\logo.png"
logo_b64 = get_image_base64(logo_path)

theme_img_path = r"E:\video_downloader\theme.png"
theme_img_b64 = get_image_base64(theme_img_path)

# --- 1. SPLASH SCREEN ---
if st.session_state["show_splash"]:
  splash_path = r"E:\video_downloader\splash.py"
  if os.path.exists(splash_path):
    with open(splash_path, encoding="utf-8") as f:
      exec(f.read())
  else:
    st.markdown(
        f"""
        <style>
            .stApp {{ background: #06060e !important; overflow: hidden !important; }}
            .splash-container {{
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                display: flex; align-items: center; justify-content: center;
                background: #06060e; z-index: 99999;
            }}
            .splash-logo-img {{
                width: 100vw; height: 100vh; object-fit: cover; object-position: center; display: block;
            }}
        </style>
        <div class="splash-container">
            {"<img src='" + logo_b64 + "' class='splash-logo-img' />" if logo_b64 else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )
    time.sleep(3.5)
    st.session_state["show_splash"] = False
    st.rerun()

# --- 2. WELCOME & GOOGLE AUTH SCREEN ---
elif not st.session_state["logged_in"]:
  st.markdown(
      """
    <style>
        html, body, .stApp { background: #06060e !important; color: white !important; }
        #MainMenu, footer, header {visibility: hidden;}
        .login-title {
            text-align: center; margin-top: 12px; margin-bottom: 15px; font-size: 32px; font-weight: bold;
            background: linear-gradient(135deg, #ff007f, #ff8c00, #00f2fe, #a855f7);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .google-logo { font-size: 24px; font-weight: 800; margin-bottom: 5px; text-align: center; }
        .g-blue { color: #4285F4; }
        .g-red { color: #EA4335; }
        .g-yellow { color: #FBBC05; }
        .g-green { color: #34A853; }
    </style>
    """,
      unsafe_allow_html=True,
  )

  if not st.session_state["show_google_auth"]:
    if theme_img_b64:
      st.markdown(
          f"<div style='text-align: center; margin-top: 80px;"
          f" margin-bottom: 0px;'><img src='{theme_img_b64}' style='width:"
          " 100px; height: auto;' /></div>",
          unsafe_allow_html=True,
      )
    st.markdown(
        '<div class="login-title">CoCo Media Tube</div>', unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([2.0, 4.0, 2.0])
    with col2:
      if st.button("Welcome", use_container_width=True, type="primary"):
        st.session_state["show_google_auth"] = True
        st.rerun()
  else:
    if theme_img_b64:
      st.markdown(
          f"<div style='text-align: center; margin-top: 20px;"
          f" margin-bottom: 0px;'><img src='{theme_img_b64}' style='width:"
          " 70px; height: auto;' /></div>",
          unsafe_allow_html=True,
      )
    st.markdown(
        '<div class="login-title">CoCo Media Tube</div>', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="google-logo"><span class="g-blue">G</span><span'
        ' class="g-red">o</span><span class="g-yellow">o</span><span'
        ' class="g-blue">g</span><span class="g-green">l</span><span'
        ' class="g-red">e</span></div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
      email_input = st.text_input(
          "Email or phone", placeholder="Enter your Gmail..."
      )
      pass_input = st.text_input(
          "Password", type="password", placeholder="Enter password..."
      )

      st.markdown("<br>", unsafe_allow_html=True)
      if st.button(
          "Sign in with Google", use_container_width=True, type="primary"
      ):
        if email_input.strip() != "" and pass_input.strip() != "":
          st.session_state["logged_in"] = True
          st.success("Google Authentication Successful!")
          time.sleep(1)
          st.rerun()
        else:
          st.warning("Please enter both email and password.")

      if st.button("Back", use_container_width=True):
        st.session_state["show_google_auth"] = False
        st.rerun()

# --- 3. HOMEPAGE & ROUTER ---
else:
  st.markdown(
      """
    <style>
    #MainMenu, footer, header, [data-testid="stHeader"] { display: none !important; }
    html, body, .stApp { background-color: #06060e !important; color: #ffffff !important; }
    .home-title {
        text-align: center; margin-top: 2px; margin-bottom: 10px; font-size: 24px; font-weight: bold;
        background: linear-gradient(135deg, #ff007f, #ff8c00, #00f2fe, #a855f7);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .platforms-grid { display: flex; flex-direction: column; gap: 8px; width: 100%; margin-top: 30px; }
    .platforms-row { display: flex; gap: 8px; width: 100%; }
    .platform-card {
        flex: 1; padding: 16px 6px; text-align: center; color: #ffffff !important;
        text-decoration: none !important; display: flex; flex-direction: column;
        align-items: center; justify-content: center; gap: 4px; border-radius: 12px; border: 2px solid transparent;
    }
    .platform-card.youtube { background: rgba(25, 4, 4, 0.95); border-color: rgba(180, 20, 20, 0.8); }
    .platform-card.facebook { background: rgba(4, 15, 35, 0.95); border-color: rgba(13, 71, 161, 0.9); }
    .platform-card.instagram { background: linear-gradient(135deg, rgba(240, 148, 51, 0.25), rgba(220, 39, 67, 0.25)); border-color: #dc2743; }
    .platform-card span { color: #ffffff !important; font-weight: 700; font-size: 14px; }
    </style>
    """,
      unsafe_allow_html=True,
  )

  if current_page == "home":
    st.markdown("<br>", unsafe_allow_html=True)
    if theme_img_b64:
      st.markdown(
          f"<div style='text-align: center;'><img src='{theme_img_b64}'"
          " style='width: 50px;'/></div>",
          unsafe_allow_html=True,
      )
    st.markdown(
        '<div class="home-title">CoCo Media Tube</div>', unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="platforms-grid">
            <div class="platforms-row">
                <a href="/?page=youtube" class="platform-card youtube">
                    <svg height="22" viewBox="0 0 24 24" width="22" xmlns="http://www.w3.org/2000/svg"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" fill="#FF0000"/></svg>
                    <span>YouTube</span>
                </a>
                <a href="/?page=facebook" class="platform-card facebook">
                    <svg height="22" viewBox="0 0 24 24" width="22" xmlns="http://www.w3.org/2000/svg"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" fill="#1877F2"/></svg>
                    <span>Facebook</span>
                </a>
            </div>
            <div class="platforms-row">
                <a href="/?page=instagram" class="platform-card instagram" style="width: 100%;">
                    <svg height="22" viewBox="0 0 24 24" width="22" xmlns="http://www.w3.org/2000/svg"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z" fill="#E1306C"/></svg>
                    <span>Instagram</span>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

  elif current_page == "youtube":
    yt_path = r"E:\video_downloader\youtube.py"
    if os.path.exists(yt_path):
      with open(yt_path, encoding="utf-8") as f:
        exec(f.read())
    else:
      st.error(f"File not found: {yt_path}")

  elif current_page == "facebook":
    fb_path = r"E:\video_downloader\facebook.py"
    if os.path.exists(fb_path):
      with open(fb_path, encoding="utf-8") as f:
        exec(f.read())
    else:
      st.error(f"File not found: {fb_path}")

  elif current_page == "instagram":
    ig_path = r"E:\video_downloader\instagram.py"
    if os.path.exists(ig_path):
      with open(ig_path, encoding="utf-8") as f:
        exec(f.read())
    else:
      st.error(f"File not found: {ig_path}")
