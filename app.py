import base64
import io
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import zipfile
import requests
import static_ffmpeg
import streamlit as st
import yt_dlp

try:
  static_ffmpeg.add_paths()
except Exception:
  pass

# yt-dlp auto-update check (runs once per session to keep cloud builds fast)
if "ytdlp_updated" not in st.session_state:
  try:
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "--upgrade", "yt-dlp"],
        capture_output=True,
        text=True,
    )
  except Exception:
    pass
  st.session_state["ytdlp_updated"] = True


def _get_secret(key: str, default: str = "") -> str:
  env_val = os.getenv(key, "")
  if env_val and env_val.strip():
    return env_val.strip()
  try:
    if key in st.secrets and str(st.secrets[key]).strip():
      return str(st.secrets[key]).strip()
  except Exception:
    pass
  return default


# Load YouTube cookies from Streamlit Secrets if configured
COOKIE_FILE_PATH = None
yt_cookies = _get_secret("YT_COOKIES", "")
if yt_cookies:
  try:
    with tempfile.NamedTemporaryFile(
        mode="w", delete=False, suffix=".txt", encoding="utf-8"
    ) as cf:
      cf.write(yt_cookies + "\n")
      COOKIE_FILE_PATH = cf.name
  except Exception:
    pass

# Global yt-dlp wrapper to attach cookies, JS runtime, and bypass cloud blocks
_OriginalYoutubeDL = yt_dlp.YoutubeDL


class CloudSafeYoutubeDL(_OriginalYoutubeDL):

  def __init__(self, params=None, *args, **kwargs):
    params = dict(params) if params else {}
    params.setdefault("geo_bypass", True)
    params.setdefault("nocheckcertificate", True)
    params.setdefault("retries", 5)
    params.setdefault("fragment_retries", 5)

    deno_exe = shutil.which("deno")
    deno_config = {"path": deno_exe} if deno_exe else {}
    params.setdefault("js_runtimes", {"deno": deno_config})
    params.setdefault("remote_components", ["ejs:github"])

    params.setdefault(
        "extractor_args",
        {"youtube": {"player_client": ["android", "ios", "web"]}},
    )
    params.setdefault(
        "http_headers",
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    if COOKIE_FILE_PATH and os.path.exists(COOKIE_FILE_PATH):
      params.setdefault("cookiefile", COOKIE_FILE_PATH)
    super().__init__(params, *args, **kwargs)


yt_dlp.YoutubeDL = CloudSafeYoutubeDL


def download_via_github_actions(
    video_url: str, media_format: str = "mp4", workflow_file: str = "download.yml"
):
  """Triggers GitHub Actions workflow and returns (filename, file_bytes) from artifact."""
  token = _get_secret("GITHUB_TOKEN", "")
  owner = _get_secret("GITHUB_OWNER", "maximusfanai")
  repo = _get_secret("GITHUB_REPO", "coco-media-tube")
  if not token:
    raise RuntimeError("GITHUB_TOKEN Streamlit Secrets-ah a la dah luh lo.")

  headers = {
      "Authorization": f"Bearer {token}",
      "Accept": "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
  }

  dispatch_url = (
      f"https://api.github.com/repos/{owner}/{repo}/actions/workflows/{workflow_file}/dispatches"
  )
  res = requests.post(
      dispatch_url,
      headers=headers,
      json={"ref": "main", "inputs": {"url": video_url, "format": media_format}},
      timeout=15,
  )
  res.raise_for_status()

  runs_url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs?per_page=5"
  time.sleep(4)
  run_id = None
  for _ in range(45):
    runs = requests.get(runs_url, headers=headers, timeout=15).json().get(
        "workflow_runs", []
    )
    if runs:
      latest = runs[0]
      run_id = latest["id"]
      if latest["status"] == "completed":
        if latest["conclusion"] != "success":
          raise RuntimeError(f"GitHub Actions failed: {latest['conclusion']}")
        break
    time.sleep(4)
  else:
    raise TimeoutError("GitHub Actions run a rei lutuk a, a hun a liam ta.")

  artifacts_url = (
      f"https://api.github.com/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts"
  )
  artifacts = requests.get(artifacts_url, headers=headers, timeout=15).json().get(
      "artifacts", []
  )
  if not artifacts:
    raise RuntimeError("Artifact hmuh a ni lo.")

  zip_res = requests.get(
      artifacts[0]["archive_download_url"], headers=headers, timeout=60
  )
  zip_res.raise_for_status()

  with zipfile.ZipFile(io.BytesIO(zip_res.content)) as zf:
    filename = zf.namelist()[0]
    return filename, zf.read(filename)


# Google OAuth 2.0 Config (loaded from Streamlit Secrets / .streamlit/secrets.toml)
GOOGLE_CLIENT_ID = _get_secret("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = _get_secret("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = _get_secret(
    "GOOGLE_REDIRECT_URI",
    _get_secret("REDIRECT_URI", "http://localhost:8501"),
).rstrip("/")

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


def build_google_auth_url():
  params = {
      "client_id": GOOGLE_CLIENT_ID,
      "redirect_uri": GOOGLE_REDIRECT_URI,
      "response_type": "code",
      "scope": "openid email profile",
      "access_type": "offline",
      "prompt": "select_account",
  }
  return (
      "https://accounts.google.com/o/oauth2/v2/auth?"
      + urllib.parse.urlencode(params)
  )


def exchange_google_code(auth_code: str):
  if not GOOGLE_CLIENT_SECRET:
    st.session_state["oauth_debug"] = (
        "GOOGLE_CLIENT_SECRET is empty. Add it in .streamlit/secrets.toml"
        " or Streamlit Cloud Secrets."
    )
    return None
  try:
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "code": auth_code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=15,
    )
  except Exception as exc:
    st.session_state["oauth_debug"] = f"Token request failed: {exc}"
    return None

  if token_resp.status_code != 200:
    st.session_state["oauth_debug"] = (
        f"Token error ({token_resp.status_code}): {token_resp.text}"
    )
    return None

  token_json = token_resp.json()
  access_token = token_json.get("access_token")
  if not access_token:
    st.session_state["oauth_debug"] = f"No access_token returned: {token_json}"
    return None

  try:
    user_resp = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=15,
    )
  except Exception as exc:
    st.session_state["oauth_debug"] = f"Userinfo request failed: {exc}"
    return None

  if user_resp.status_code != 200:
    st.session_state["oauth_debug"] = (
        f"Userinfo error ({user_resp.status_code}): {user_resp.text}"
    )
    return None

  st.session_state.pop("oauth_debug", None)
  return user_resp.json()


# Query params check
query_params = st.query_params
auth_code_param = query_params.get("code", None)
if isinstance(auth_code_param, list):
  auth_code_param = auth_code_param[0] if auth_code_param else None

page_param = query_params.get("page", None)
if isinstance(page_param, list):
  page_param = page_param[0] if page_param else None

# Session States Initialization
if "show_splash" not in st.session_state:
  st.session_state["show_splash"] = (
      False if (page_param or auth_code_param) else True
  )

if "show_google_auth" not in st.session_state:
  st.session_state["show_google_auth"] = False

if "logged_in" not in st.session_state:
  st.session_state["logged_in"] = True if page_param else False

if "google_user" not in st.session_state:
  st.session_state["google_user"] = None

if auth_code_param and not st.session_state["logged_in"]:
  user_info = exchange_google_code(auth_code_param)
  st.query_params.clear()
  if user_info:
    st.session_state["google_user"] = user_info
    st.session_state["logged_in"] = True
    st.session_state["show_splash"] = False
    st.rerun()
  else:
    st.session_state["show_google_auth"] = True
    st.session_state["show_splash"] = False
    st.error(
        "Google sign-in failed. Check GOOGLE_CLIENT_SECRET and redirect URI."
    )
    if st.session_state.get("oauth_debug"):
      st.code(st.session_state["oauth_debug"])

current_page = page_param if page_param else "home"
if current_page not in [
    "home",
    "youtube",
    "facebook",
    "instagram",
    "refresh",
]:
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


logo_b64 = get_image_base64("logo.png")
theme_img_b64 = get_image_base64("theme.png")

# --- 1. SPLASH SCREEN ---
if st.session_state["show_splash"]:
  splash_path = "splash.py"
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
        .google-logo { font-size: 24px; font-weight: 800; margin-bottom: 12px; text-align: center; }
        .g-blue { color: #4285F4; }
        .g-red { color: #EA4335; }
        .g-yellow { color: #FBBC05; }
        .g-green { color: #34A853; }
        .oauth-btn {
            display: block; text-align: center; width: 100%; padding: 10px 14px;
            border-radius: 8px; background: #1a73e8; color: #ffffff !important;
            font-weight: 700; text-decoration: none !important; margin-bottom: 10px;
        }
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
      if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.warning("Secrets-ah GOOGLE_CLIENT_ID leh GOOGLE_CLIENT_SECRET dah lut rawh.")
      else:
        google_auth_url = build_google_auth_url()
        st.markdown(
            f'<a href="{google_auth_url}" target="_blank" rel="noopener noreferrer" class="oauth-btn">Sign in with Google</a>',
            unsafe_allow_html=True,
        )

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
    yt_path = "youtube.py"
    if os.path.exists(yt_path):
      with open(yt_path, encoding="utf-8") as f:
        exec(f.read())
    else:
      st.error(f"File not found: {yt_path}")

  elif current_page == "facebook":
    fb_path = "facebook.py"
    if os.path.exists(fb_path):
      with open(fb_path, encoding="utf-8") as f:
        exec(f.read())
    else:
      st.error(f"File not found: {fb_path}")

  elif current_page == "instagram":
    ig_path = "instagram.py"
    if os.path.exists(ig_path):
      with open(ig_path, encoding="utf-8") as f:
        exec(f.read())
    else:
      st.error(f"File not found: {ig_path}")
