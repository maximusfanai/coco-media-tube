import base64
import os
import runpy
import time
import streamlit as st

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


# Path setup
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = current_dir  # All app files are now in the repository root; no core/ folder.

# Logos path detection
logo_path = os.path.join(current_dir, "logo.png")
if not os.path.exists(logo_path):
  logo_path = os.path.join(current_dir, "1logo.png")
  if not os.path.exists(logo_path):
    logo_path = os.path.join(root_dir, "logo.png")
logo_b64 = get_image_base64(logo_path)

theme_img_path = os.path.join(current_dir, "theme.png")
if not os.path.exists(theme_img_path):
  theme_img_path = os.path.join(root_dir, "theme.png")
theme_img_b64 = get_image_base64(theme_img_path)

# Session state initialization
if "app_started" not in st.session_state:
  st.session_state["app_started"] = True
  st.session_state["show_login"] = False
  st.session_state["logged_in"] = False
  st.session_state["show_google_popup"] = False
  st.session_state["login_page_loaded_time"] = None
  st.session_state["popup_email"] = ""
  st.session_state["popup_pass"] = ""
else:
  if "show_login" not in st.session_state:
    st.session_state["show_login"] = True
  if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
  if "show_google_popup" not in st.session_state:
    st.session_state["show_google_popup"] = False
  if "popup_email" not in st.session_state:
    st.session_state["popup_email"] = ""
  if "popup_pass" not in st.session_state:
    st.session_state["popup_pass"] = ""

# --- ROUTING FOR DOWNLOADERS (Root folder routing) ---
query_params = st.query_params
page = query_params.get("page")

if page and page != "":
  if page == "facebook":
    fb_path = os.path.join(current_dir, "facebook.py")
    if os.path.exists(fb_path):
      runpy.run_path(fb_path, run_name="__main__")
      st.stop()
    else:
      st.error(f"File not found: {fb_path}")

  elif page == "youtube":
    yt_path = os.path.join(current_dir, "youtube.py")
    if os.path.exists(yt_path):
      runpy.run_path(yt_path, run_name="__main__")
      st.stop()
    else:
      st.error(f"File not found: {yt_path}")

  elif page == "instagram":
    ig_path = os.path.join(current_dir, "instagram.py")
    if os.path.exists(ig_path):
      runpy.run_path(ig_path, run_name="__main__")
      st.stop()
    else:
      st.error(f"File not found: {ig_path}")
  elif page == "home":
    st.session_state["show_login"] = True
    st.session_state["logged_in"] = False
    st.query_params.clear()
    st.rerun()


# --- 1. SPLASH SCREEN STAGE ---
if not st.session_state["show_login"]:
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
            object-fit: contain;
            display: block;
            margin: 0 auto;
            margin-top: -5vh;
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

  time.sleep(5.0)
  st.session_state["show_login"] = True
  st.session_state["login_page_loaded_time"] = time.time()
  st.rerun()

else:
  # --- 2. LOGIN PAGE STAGE ---
  if not st.session_state["logged_in"]:
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@800;900&display=swap');

            html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], .main, .block-container {
                overflow: hidden !important;
                height: 100vh !important;
                max-height: 100vh !important;
                background: #06060e !important;
                color: white !important;
            }
            .main .block-container {
                padding-top: 20px !important;
                max-width: 440px;
                margin: auto;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            #MainMenu, footer, header {visibility: hidden;}
            .login-container {
                margin-top: 100px;
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

    if not st.session_state["show_google_popup"]:
      # Welcome screen
      st.markdown('<div class="login-container">', unsafe_allow_html=True)

      if theme_img_b64:
        st.markdown(
            f"<div style='text-align: center; margin-bottom: 0px;'><img"
            f" src='{theme_img_b64}' style='width: 110px; height: auto;' /></div>",
            unsafe_allow_html=True,
        )

      st.markdown(
          '<div class="login-title">CoCo Media Tube</div>',
          unsafe_allow_html=True,
      )

      delay_seconds = 2.0
      elapsed_time = (
          time.time() - st.session_state["login_page_loaded_time"]
          if st.session_state["login_page_loaded_time"]
          else 0
      )

      if elapsed_time < delay_seconds:
        time.sleep(delay_seconds - elapsed_time)
        st.rerun()
      else:
        col1, col2, col3 = st.columns([2.0, 4.0, 2.0])
        with col2:
          st.markdown(
              '<div class="welcome-btn-wrapper">', unsafe_allow_html=True
          )
          if st.button("Welcome", use_container_width=True, type="primary"):
            st.session_state["show_google_popup"] = True
            st.rerun()
          st.markdown("</div>", unsafe_allow_html=True)

      st.markdown("</div>", unsafe_allow_html=True)

    else:
      # Email & Password Form Screen
      if theme_img_b64:
        st.markdown(
            f"<div style='text-align: center; margin-bottom: 0px;'><img"
            f" src='{theme_img_b64}' style='width: 70px; height: auto;"
            f" border-radius: 12px;' /></div>",
            unsafe_allow_html=True,
        )

      st.markdown(
          '<div class="login-title" style="font-size: 26px;'
          ' margin-bottom: 10px;">CoCo Media Tube</div>',
          unsafe_allow_html=True,
      )

      st.text_input(
          "Email :",
          value=st.session_state["popup_email"],
          placeholder="you@youraddress.com",
          key="popup_email",
      )
      st.text_input(
          "Password :",
          value=st.session_state["popup_pass"],
          type="password",
          key="popup_pass",
      )

      col_l, col_m, col_r = st.columns([1.5, 3.0, 1.5])
      with col_m:
        if st.button("Login", use_container_width=True, key="submit_btn"):
          if st.session_state["popup_email"] and st.session_state["popup_pass"]:
            st.session_state["logged_in"] = True
            st.rerun()
          else:
            st.warning("Please enter your email and password.")

      st.markdown(
          "<p style='text-align: center; margin-top: 15px;'><a href='#'"
          " style='color: #4a90e2; text-decoration: none; font-size:"
          " 13px;'>If you forgot your password, recover it from your Google"
          " email</a></p>",
          unsafe_allow_html=True,
      )
      st.markdown(
          "<p style='text-align: center; color: #4a90e2; font-size:"
          " 13px;'>Hlimtak leh nuam tak in hun hmang rawh</p>",
          unsafe_allow_html=True,
      )

  else:
    # --- 3. MAIN PAGE ---
    st.markdown(
        """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@800;900&display=swap');

        html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stMainBlockContainer"], .main, .block-container {
            overflow: hidden !important;
            height: 100vh !important;
            max-height: 100vh !important;
            position: fixed !important;
            width: 100% !important;
            touch-action: none !important;
        }

        .stApp {
            background: #06060e;
            color: #ffffff;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .main .block-container {
            padding-top: 0.4rem !important;
            padding-bottom: 1rem !important;
            padding-left: 0.8rem !important;
            padding-right: 0.8rem !important;
            max-width: 440px;
            margin: auto;
        }
        
        .neon-header {
            text-align: center;
            padding: 2px 0 4px 0;
            margin-bottom: 2px;
        }
        
        .small-logo-img {
            width: 55px;
            height: auto;
            border-radius: 12px;
            margin-bottom: 2px;
            filter: drop-shadow(0 0 10px rgba(168, 85, 247, 0.75));
        }
        
        .logo-main-title {
            font-size: 34px;
            font-weight: 900;
            letter-spacing: 1px;
            background: linear-gradient(135deg, #00f2fe, #4facfe, #a855f7, #f43f5e);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-shadow: 0 0 15px rgba(168, 85, 247, 0.6);
            margin: -4px 0;
            line-height: 1;
        }
        
        .logo-sub-title {
            font-family: 'Orbitron', sans-serif;
            font-size: 16px;
            font-weight: 900;
            letter-spacing: 4px;
            background: linear-gradient(90deg, #00ff87, #10b981, #047857);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            filter: drop-shadow(0 0 8px rgba(0, 255, 135, 0.8));
            text-transform: uppercase;
            margin-top: 2px;
        }

        .platform-container {
            display: flex;
            gap: 10px;
            justify-content: space-between;
            margin-top: 10px;
            margin-bottom: 14px;
        }
        
        .platform-card {
            flex: 1;
            height: 95px;
            border-radius: 18px;
            padding: 10px 4px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            gap: 6px;
            text-align: center;
            color: white !important;
            text-decoration: none !important;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .platform-card:hover {
            transform: translateY(-2px);
        }
        
        .yt-card { 
            background: linear-gradient(145deg, #2b030a, #0d0205);
            border: 1.5px solid #ff0044;
            box-shadow: 0 0 14px rgba(255, 0, 68, 0.35);
        }
        .fb-card { 
            background: linear-gradient(145deg, #031833, #020814);
            border: 1.5px solid #0088ff;
            box-shadow: 0 0 14px rgba(0, 136, 255, 0.35);
        }
        .ig-card { 
            background: radial-gradient(circle at 30% 107%, rgba(253, 244, 151, 0.25) 0%, rgba(253, 89, 73, 0.25) 45%, rgba(214, 36, 159, 0.25) 60%, rgba(40, 90, 235, 0.25) 90%), linear-gradient(145deg, #2a032b, #0d020e);
            border: 1.5px solid #d6249f;
            box-shadow: 0 0 14px rgba(214, 36, 159, 0.5);
        }

        .card-title {
            font-weight: 800;
            font-size: 15px;
            letter-spacing: 0.3px;
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

        #MainMenu, footer, header {visibility: hidden;}
    </style>
    """,
        unsafe_allow_html=True,
    )

    theme_display = (
        f"<img src='{theme_img_b64}' class='small-logo-img' />"
        if theme_img_b64
        else ""
    )

    st.markdown(
        f"""
    <div class='neon-header'>
        {theme_display}
        <div class='logo-main-title'>CoCo</div>
        <div class='logo-sub-title'>MEDIA TUBE</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div class='platform-container'>
        <a href='?page=youtube' target='_self' class='platform-card yt-card'>
            <svg width="34" height="34" viewBox="0 0 24 24" fill="#FF0000">
                <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
            </svg>
            <div class='card-title'>YouTube</div>
        </a>
        <a href='?page=facebook' target='_self' class='platform-card fb-card'>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="#1877F2">
                <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
            </svg>
            <div class='card-title'>Facebook</div>
        </a>
        <a href='?page=instagram' target='_self' class='platform-card ig-card'>
            <svg width="32" height="32" viewBox="0 0 24 24">
                <radialGradient id="rg" r="150%" cx="30%" cy="107%">
                    <stop stop-color="#fdf497" offset="0%" />
                    <stop stop-color="#fdf497" offset="5%" />
                    <stop stop-color="#fd5949" offset="45%" />
                    <stop stop-color="#d6249f" offset="60%" />
                    <stop stop-color="#285AEB" offset="90%" />
                </radialGradient>
                <path fill="url(#rg)" d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
        </svg>
        <div class='card-title'>Instagram</div>
    </a>
</div>
""",
    unsafe_allow_html=True,
)