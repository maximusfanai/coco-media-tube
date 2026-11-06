import base64
import os
import time
import streamlit as st
import streamlit.components.v1 as components

# Page Config
st.set_page_config(
    page_title="CoCo Media Tube",
    page_icon="🎬",
    layout="centered",
    initial_sidebar_state="collapsed",
)


# Function to encode local image to Base64
def get_image_base64(file_path):
  if os.path.exists(file_path):
    with open(file_path, "rb") as f:
      data = f.read()
    return f"data:image/png;base64,{base64.b64encode(data).decode()}"
  return ""


# Paths
logo_path = r"E:\video_downloader\logo.png"
logo_b64 = get_image_base64(logo_path)

theme_img_path = r"E:\video_downloader\theme.png"
theme_img_b64 = get_image_base64(theme_img_path)

# Session state initialization
if "show_splash" not in st.session_state:
  st.session_state["show_splash"] = True

if "show_login" not in st.session_state:
  st.session_state["show_login"] = False

if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = False

if "show_google_auth" not in st.session_state:
  st.session_state["show_google_auth"] = False

if "login_page_loaded_time" not in st.session_state:
  st.session_state["login_page_loaded_time"] = None

# --- 1. SPLASH SCREEN ---
if st.session_state["show_splash"]:
  st.markdown(
      f"""
    <style>
        .stApp {{
            background: #06060e !important;
            overflow: hidden !important;
        }}
        html, body, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], .main, .block-container {{
            background-color: #06060e !important;
            margin: 0 !important;
            padding: 0 !important;
            width: 100vw !important;
            height: 100vh !important;
            overflow: hidden !important;
        }}
        .main .block-container {{
            padding: 0 !important;
            max-width: 100% !important;
            height: 100vh !important;
            display: flex !important;
            align-items: flex-start !important;
            justify-content: center !important;
            overflow: hidden !important;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}
        .splash-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            display: flex;
            align-items: flex-start;
            justify-content: center;
            background: #06060e;
            margin: 0;
            padding: 0;
            animation: fadeIn 3.0s ease-in-out;
            overflow: hidden !important;
        }}
        .splash-logo-img {{
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            object-position: top center;
            display: block;
            margin: 0;
            padding: 0;
        }}
        #MainMenu, footer, header {{visibility: hidden;}}
    </style>

    <div class="splash-container">
        {"<img src='" + logo_b64 + "' class='splash-logo-img' />" if logo_b64 else ""}
    </div>
    """,
      unsafe_allow_html=True,
  )

  components.html(
      """
        <script>
            setTimeout(function() {
                window.parent.document.querySelector('iframe').contentWindow.location.reload();
            }, 6000);
        </script>
        """,
      height=0,
      width=0,
  )

  time.sleep(6.0)
  st.session_state["show_splash"] = False
  st.session_state["login_page_loaded_time"] = time.time()
  st.rerun()

# --- 2. GOOGLE AUTH LOGIN SCREEN ---
elif st.session_state["show_google_auth"]:
  st.markdown(
      """
        <style>
            html, body, .stApp {
                background: #06060e !important;
                color: white !important;
                overflow: hidden !important;
                height: 100vh !important;
                max-height: 100vh !important;
            }
            [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], .main, .block-container {
                overflow: hidden !important;
                height: 100vh !important;
                max-height: 100vh !important;
            }
            #MainMenu, footer, header {visibility: hidden;}
            .google-logo {
                font-size: 24px;
                font-weight: 800;
                margin-bottom: 5px;
                letter-spacing: -1px;
                text-align: center;
            }
            .g-blue { color: #4285F4; }
            .g-red { color: #EA4335; }
            .g-yellow { color: #FBBC05; }
            .g-green { color: #34A853; }
            .login-title {
                text-align: center;
                margin-top: 5px;
                margin-bottom: 5px;
                font-size: 26px;
                font-weight: bold;
                background: linear-gradient(135deg, #ff007f, #ff8c00, #00f2fe, #a855f7);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
        </style>
        """,
      unsafe_allow_html=True,
  )

  if theme_img_b64:
    st.markdown(
        f"<div style='text-align: center; margin-top: 0px; margin-bottom:"
        f" 0px;'><img src='{theme_img_b64}' style='width: 70px; height:"
        " auto;' /></div>",
        unsafe_allow_html=True,
    )

  st.markdown(
      '<div class="login-title">CoCo Media Tube</div>', unsafe_allow_html=True
  )

  st.markdown(
      """
        <div class="google-logo" style="margin-top: 0px; margin-bottom: 5px;">
            <span class="g-blue">G</span><span class="g-red">o</span><span class="g-yellow">o</span><span class="g-blue">g</span><span class="g-green">l</span><span class="g-red">e</span>
        </div>
        """,
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
    if st.button("Sign in with Google", use_container_width=True, type="primary"):
      if email_input.strip() != "" and pass_input.strip() != "":
        st.session_state["logged_in"] = True
        st.success("Google Authentication Successful!")
        time.sleep(1)
        st.rerun()
      else:
        st.warning("Please enter both email and password to continue.")

    if st.button("Back", use_container_width=True):
      st.session_state["show_google_auth"] = False
      st.rerun()

# --- 3. WELCOME SCREEN ---
else:
  st.markdown(
      """
        <style>
            html, body, .stApp {
                background: #06060e !important;
                color: white !important;
                overflow: hidden !important;
                height: 100vh !important;
                max-height: 100vh !important;
            }
            [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], .main, .block-container {
                overflow: hidden !important;
                height: 100vh !important;
                max-height: 100vh !important;
                padding-top: 5px !important;
            }
            #MainMenu, footer, header {visibility: hidden;}
            .login-container {
                margin-top: 180px;
                text-align: center;
                width: 100%;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .login-title {
                text-align: center;
                margin-top: 12px;
                margin-bottom: 15px;
                font-size: 32px;
                font-weight: bold;
                background: linear-gradient(135deg, #ff007f, #ff8c00, #00f2fe, #a855f7);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }
            @keyframes popUp {
                0% { opacity: 0; transform: scale(0.8); }
                100% { opacity: 1; transform: scale(1); }
            }
            .welcome-btn-wrapper {
                animation: popUp 0.5s ease-out forwards;
                width: 100%;
            }
            .stButton>button {
                background: linear-gradient(45deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D, #F56040, #F77737, #FCAF45, #FFDC80, #1877F2) !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                font-weight: bold !important;
                transition: transform 0.2s;
            }
            .stButton>button:hover {
                transform: scale(1.05);
                color: white !important;
            }
        </style>
        """,
      unsafe_allow_html=True,
  )

  delay_seconds = 1.0
  elapsed_time = (
      time.time() - st.session_state["login_page_loaded_time"]
      if st.session_state["login_page_loaded_time"]
      else 0
  )

  if elapsed_time < delay_seconds:
    time.sleep(delay_seconds - elapsed_time)
    st.rerun()
  else:
    if theme_img_b64:
      st.markdown(
          f"<div style='text-align: center; margin-top: 100px;"
          f" margin-bottom: 0px;'><img src='{theme_img_b64}' style='width:"
          " 110px; height: auto;' /></div>",
          unsafe_allow_html=True,
      )

    st.markdown(
        '<div class="login-title">CoCo Media Tube</div>', unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns([2.0, 4.0, 2.0])
    with col2:
      st.markdown('<div class="welcome-btn-wrapper">', unsafe_allow_html=True)
      if st.button("Welcome", use_container_width=True, type="primary"):
        st.session_state["show_google_auth"] = True
        st.rerun()
      st.markdown("</div>", unsafe_allow_html=True)