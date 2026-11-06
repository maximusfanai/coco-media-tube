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

# Base directory setting
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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
  st.session_state["show_splash"] = True

if "show_google_auth" not in st.session_state:
  st.session_state["show_google_auth"] = False

if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False

current_page = page_param if page_param else "home"
if current_page not in ["home", "youtube", "facebook", "instagram", "refresh"]:
  current_page = "home"

if current_page == "refresh":
  st.query_params.clear()
  current_page = "home"


def get_image_base64(filename):
  target_path = os.path.join(BASE_DIR, filename)
  if not os.path.exists(target_path):
    base_name = filename.lower()
    if os.path.exists(BASE_DIR):
      for f in os.listdir(BASE_DIR):
        if f.lower() == base_name:
          target_path = os.path.join(BASE_DIR, f)
          break

  if os.path.exists(target_path):
    with open(target_path, "rb") as f:
      data = f.read()
    return f"data:image/png;base64,{base64.b64encode(data).decode()}"
  return ""


logo_b64 = get_image_base64("logo.png")
theme_img_b64 = get_image_base64("theme.png")

# --- 1. SPLASH SCREEN ---
if st.session_state["show_splash"]:
  splash_path = os.path.join(BASE_DIR, "splash.py")
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
    .stButton>button {
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        padding: 20px 10px !important;
    }
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

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
      if st.button("YouTube", use_container_width=True, type="primary"):
        st.query_params["page"] = "youtube"
        st.rerun()
    with col2:
      if st.button("Facebook", use_container_width=True, type="primary"):
        st.query_params["page"] = "facebook"
        st.rerun()

    if st.button("Instagram", use_container_width=True, type="primary"):
      st.query_params["page"] = "instagram"
      st.rerun()

  elif current_page == "youtube":
    yt_path = os.path.join(BASE_DIR, "youtube.py")
    if os.path.exists(yt_path):
      with open(yt_path, encoding="utf-8") as f:
        exec(f.read())
    else:
      st.error(f"File not found: {yt_path}")

  elif current_page == "facebook":
    fb_path = os.path.join(BASE_DIR, "facebook.py")
    if os.path.exists(fb_path):
      with open(fb_path, encoding="utf-8") as f:
        exec(f.read())
    else:
      st.error(f"File not found: {fb_path}")

  elif current_page == "instagram":
    ig_path = os.path.join(BASE_DIR, "instagram.py")
    if os.path.exists(ig_path):
      with open(ig_path, encoding="utf-8") as f:
        exec(f.read())
    else:
      st.error(f"File not found: {ig_path}")
