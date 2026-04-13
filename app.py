import streamlit as st
import os
import io
import base64
import json
from datetime import datetime
from PIL import Image

# Setup Streamlit page config
st.set_page_config(page_title="Agro-AI - Farming Assistant", page_icon="🌱", layout="wide")

# ================= DATABASE SETUP =================
DB_USERS = "users.json"
DB_LOGS = "logs.json"

def init_db():
    if not os.path.exists(DB_USERS):
        with open(DB_USERS, "w") as f:
            json.dump({
                "admin": {"password": "admin", "role": "admin", "reset_required": False},
                "farmer": {"password": "farmer", "role": "farmer", "reset_required": False}
            }, f)
    if not os.path.exists(DB_LOGS):
        with open(DB_LOGS, "w") as f:
            json.dump([], f)

def load_users():
    with open(DB_USERS, "r") as f:
        return json.load(f)

def save_users(users):
    with open(DB_USERS, "w") as f:
        json.dump(users, f, indent=4)

def log_login(username, status):
    if not os.path.exists(DB_LOGS):
        logs = []
    else:
        with open(DB_LOGS, "r") as f:
            logs = json.load(f)
    logs.append({
        "username": username,
        "timestamp": datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
        "status": status
    })
    with open(DB_LOGS, "w") as f:
        json.dump(logs, f, indent=4)

def get_logs():
    if not os.path.exists(DB_LOGS):
        return []
    with open(DB_LOGS, "r") as f:
        return json.load(f)

# Initialize JSON file databases locally
init_db()

# ================= LOGIN SYSTEM =================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["username"] = None
    st.session_state["reset_required"] = False

if not st.session_state["logged_in"]:
    st.markdown("<h1 style='text-align: center;'>Welcome to Agro-AI 🌾</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #555;'>Please log in to access the system.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                users = load_users()
                if username in users and users[username]["password"] == password:
                    log_login(username, "Success")
                    st.session_state["logged_in"] = True
                    st.session_state["role"] = users[username]["role"]
                    st.session_state["username"] = username
                    st.session_state["reset_required"] = users[username].get("reset_required", False)
                    st.rerun()
                else:
                    log_login(username, "Failed")
                    st.error("Invalid credentials. Please contact an Admin if you lost your password.")
    st.stop()  # Halt execution until logged in

# ================= PASSWORD RESET SYSTEM =================
if st.session_state.get("reset_required"):
    st.markdown("<h1 style='text-align: center;'>🔒 Update Your Password</h1>", unsafe_allow_html=True)
    st.warning("The system administrator has granted you access to reset your password. Please choose a new secure password to continue.")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("reset_password_form"):
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm New Password", type="password")
            submit_reset = st.form_submit_button("Update Password & Continue", use_container_width=True)
            
            if submit_reset:
                if new_password and new_password == confirm_password:
                    users = load_users()
                    users[st.session_state["username"]]["password"] = new_password
                    users[st.session_state["username"]]["reset_required"] = False
                    save_users(users)
                    
                    st.session_state["reset_required"] = False
                    st.success("Password updated successfully! Welcome to Agro-AI.")
                    st.rerun()
                else:
                    st.error("Passwords do not match or are empty.")
    st.stop() # Block app access until password is changed

# ================= MAIN APPLICATION =================
st.sidebar.title("🌱 Agro-AI")
st.sidebar.markdown(f"**User:** `{st.session_state['username']}`\n\n**Role:** `{st.session_state['role'].capitalize()}`")

if st.sidebar.button("Logout", use_container_width=True):
    st.session_state["logged_in"] = False
    st.session_state["role"] = None
    st.session_state["username"] = None
    st.rerun()

st.title("🌱 Agro-AI - AI-Powered Farming Assistant")

# Grab API Key securely
try:
    api_key = st.secrets["GROQ_API_KEY"]
except Exception:
    api_key = os.getenv("GROQ_API_KEY") 

if not api_key:
    st.error("Server Misconfiguration: Groq API Key is not set on the server. The application cannot function without this key securely stored in environment variables.")
    st.stop()

from groq import Groq
client = Groq(api_key=api_key)

# Language Selector Sidebar
st.sidebar.header("Translation Settings")
languages = {
    "English": "en",
    "Hindi": "hi",
    "Gujarati": "gu",
    "Marathi": "mr",
    "Tamil": "ta",
    "Telugu": "te",
    "Bengali": "bn"
}
selected_language_name = st.sidebar.selectbox("Display Language / भाषा", list(languages.keys()))

# ---- LLM HELPER FUNCTIONS ----

# Process Groq Audio to Text Transcriptions
def transcribe_audio(audio_data):
    if not audio_data:
        return None
    try:
        transcription = client.audio.transcriptions.create(
          file=("audio.wav", audio_data.read()),
          model="whisper-large-v3", # Groq's high speed Whisper model
          response_format="json"
        )
        return transcription.text
    except Exception as e:
        st.error(f"Voice Transcription Error: {e}")
        return None

def translate_text(text, target_language_name):
    if target_language_name == "English" or not text:
        return text
    translate_prompt = f'Translate the following text accurately to {target_language_name}. Return ONLY the translated text, nothing else.\n\n"{text}"'
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": translate_prompt}]
    )
    return response.choices[0].message.content

def generate_chat_response(full_messages, model="llama-3.3-70b-versatile"):
    filtered_messages = [{"role": msg["role"], "content": msg["content"]} for msg in full_messages]
    response = client.chat.completions.create(model=model, messages=filtered_messages)
    return response.choices[0].message.content

# Initializing temporary UI Chats
if "crop_chat" not in st.session_state: st.session_state.crop_chat = []
if "market_chat" not in st.session_state: st.session_state.market_chat = []
if "scheme_chat" not in st.session_state: st.session_state.scheme_chat = []

# Prepare tabs
tabs_list = ["🍃 Crop Health Diagnosis", "📈 Market Price Insights", "🏛️ Government Schemes"]
if st.session_state["role"] == "admin":
    tabs_list.append("🛡️ Admin Dashboard")

tabs = st.tabs(tabs_list)

# ----------- FEATURE 1: CROP HEALTH DIAGNOSIS -----------
with tabs[0]:
    st.header("Crop Health Diagnosis")
    
    for msg in st.session_state.crop_chat:
        with st.chat_message(msg["role"]):
            if isinstance(msg["content"], str):
                st.markdown(msg["content"])
            else:
                st.markdown("*(Image Uploaded and Analyzed)*")
    
    if len(st.session_state.crop_chat) == 0:
        st.write("Upload a photo of your crop to begin your diagnostic session.")
        uploaded_file = st.file_uploader("Upload Crop Image...", type=["jpg", "jpeg", "png"])
        
        query = st.text_input("Your query about the crop:", "What disease does this crop have and how can I treat it?", key="crop_initial_query")
        crop_audio = st.audio_input("🎤 Or record your question via Voice", key="crop_audio_init")
        
        if st.button("Diagnose Crop", type="primary"):
            # Determine priority (Audio preferred if both filled)
            actual_query = transcribe_audio(crop_audio) if crop_audio else query
            
            if uploaded_file is not None and actual_query:
                with st.spinner("Analyzing image and query..."):
                    try:
                        img = Image.open(uploaded_file)
                        buffered = io.BytesIO()
                        if img.mode != "RGB":
                            img = img.convert("RGB")
                        img.save(buffered, format="JPEG")
                        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
                        
                        full_prompt = f"You are an expert in diagnosing crop diseases.\nAnalyze the provided image and answer: {actual_query}\nProvide a clear and actionable diagnosis."
                        system_msg = {
                            "role": "user",
                            "content": [{"type": "text", "text": full_prompt}, {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_str}"}}]
                        }
                        
                        response = client.chat.completions.create(model="meta-llama/llama-4-scout-17b-16e-instruct", messages=[system_msg])
                        output_text = response.choices[0].message.content
                        translated = translate_text(output_text, selected_language_name)
                        
                        st.session_state.crop_chat.append(system_msg)
                        st.session_state.crop_chat.append({"role": "assistant", "content": translated})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please upload an image and provide a text or voice query.")
    else:
        st.info("Ask follow-up questions regarding the diagnosis below.")
        
        follow_up = st.text_input("Type your Follow-up:", key="crop_follow_up")
        crop_audio_follow = st.audio_input("🎤 Or record Follow-up via Voice", key="crop_audio_follow")
        send_btn = st.button("Send Follow-up", key="crop_send", use_container_width=True, type="primary")
            
        if send_btn:
            actual_follow_up = transcribe_audio(crop_audio_follow) if crop_audio_follow else follow_up
            if actual_follow_up:
                with st.spinner("Generating answer..."):
                    st.session_state.crop_chat.append({"role": "user", "content": f"User's Question: {actual_follow_up}"})
                    try:
                        response_text = generate_chat_response(st.session_state.crop_chat, model="meta-llama/llama-4-scout-17b-16e-instruct")
                        translated = translate_text(response_text, selected_language_name)
                        st.session_state.crop_chat.append({"role": "assistant", "content": translated})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please type a message or record audio before sending.")
        
        if st.button("🗑️ Start New Diagnosis"):
            st.session_state.crop_chat = []
            st.rerun()

# ----------- FEATURE 2: MARKET PRICE INSIGHTS -----------
with tabs[1]:
    st.header("Market Price Insights")
    
    for msg in st.session_state.market_chat:
        role = msg["role"]
        display_text = msg.get("display", msg["content"])
        with st.chat_message(role):
            st.markdown(display_text)
            
    if len(st.session_state.market_chat) == 0:
        st.write("Get recent Market price trends and expert insights.")
        col1, col2 = st.columns(2)
        with col1:
            crop = st.text_input("Crop Name:")
        with col2:
            location = st.text_input("Location (District/State):")
        
        market_audio = st.audio_input("🎤 Or simply say your crop and location out loud", key="market_audio_init")
        
        if st.button("Get Initial Insights", type="primary"):
            # Use transcription directly as the prompt if audio provided
            transcribed = transcribe_audio(market_audio)
            actual_prompt = ""
            display_prompt = ""
            
            if transcribed:
                actual_prompt = f"You are an expert agricultural market analyst. A farmer spoke the following: '{transcribed}'. \nPlease identify their crop and location, and provide a realistic estimate of typical historical price trends, harvesting season market behavior, and general advice for this region. Since real-time streaming API data is unavailable, use your extensive knowledge base to provide typical price ranges."
                display_prompt = f"🎤 **Voice Query:** {transcribed}"
            elif crop and location:
                actual_prompt = f"You are an expert agricultural market analyst. A farmer is asking for recent market price trends for {crop} in {location}.\nPlease provide a realistic estimate of typical historical price trends, harvesting season market behavior, and general advice for a farmer selling this crop in this region to maximize their profits. Since real-time streaming API data is unavailable, use your extensive knowledge base to provide expert guidance and typical price ranges."
                display_prompt = f"**Query:** Provide market insights for **{crop}** in **{location}**."
            
            if actual_prompt:
                with st.spinner("Generating market insights..."):
                    try:
                        response_text = generate_chat_response([{"role": "user", "content": actual_prompt}])
                        translated = translate_text(response_text, selected_language_name)
                        
                        st.session_state.market_chat.append({"role": "user", "content": actual_prompt, "display": display_prompt})
                        st.session_state.market_chat.append({"role": "assistant", "content": translated})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please enter crop/location or record an audio message.")
    else:
        st.info("Ask follow-up questions about these market insights.")
        
        follow_up = st.text_input("Type your Follow-up:", key="market_follow_up")
        market_audio_follow = st.audio_input("🎤 Or record Follow-up via Voice", key="market_audio_follow")
        send_btn = st.button("Send Follow-up", key="market_send", use_container_width=True, type="primary")
            
        if send_btn:
            actual_follow_up = transcribe_audio(market_audio_follow) if market_audio_follow else follow_up
            if actual_follow_up:
                with st.spinner("Thinking..."):
                    st.session_state.market_chat.append({"role": "user", "content": actual_follow_up, "display": ("🎤 " if market_audio_follow else "") + actual_follow_up})
                    try:
                        response_text = generate_chat_response(st.session_state.market_chat)
                        translated = translate_text(response_text, selected_language_name)
                        st.session_state.market_chat.append({"role": "assistant", "content": translated})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                st.warning("Please type or speak a question first.")
        
        if st.button("🗑️ Start New Market Inquiry"):
            st.session_state.market_chat = []
            st.rerun()

# ----------- FEATURE 3: GOVERNMENT SCHEME SUMMARIZER -----------
with tabs[2]:
    st.header("Government Scheme Information")
    
    for msg in st.session_state.scheme_chat:
        role = msg["role"]
        display_text = msg.get("display", msg["content"]) 
        with st.chat_message(role):
            st.markdown(display_text)
            
    if len(st.session_state.scheme_chat) == 0:
         st.write("Ask questions about government agricultural schemes.")
         scheme_name = st.text_input("Scheme Name (e.g., PM-KISAN, Fasal Bima Yojana):")
         scheme_query = st.text_input("Your specific query:", "What are the eligibility criteria and benefits?")
         scheme_audio = st.audio_input("🎤 Or record your question regarding a scheme", key="scheme_audio_init")
         
         if st.button("Get Scheme Summary", type="primary"):
             transcribed = transcribe_audio(scheme_audio)
             actual_prompt = ""
             display_prompt = ""
             
             if transcribed:
                  actual_prompt = f"You are an expert in Indian government agricultural schemes. A farmer asked the following via voice: '{transcribed}'. \nProvide a concise and easy-to-understand summary of the scheme they are inquiring about, including key benefits and eligibility criteria."
                  display_prompt = f"🎤 **Voice Query:** {transcribed}"
             elif scheme_name and scheme_query:
                  actual_prompt = f"You are an expert in Indian government agricultural schemes. You will provide a simplified summary of the scheme based on the user's query.\nScheme Name: {scheme_name}\nQuery: {scheme_query}\nProvide a concise and easy-to-understand summary of the scheme, including key benefits and eligibility criteria, tailored to the farmer's query."
                  display_prompt = f"**Query:** {scheme_query} (Regarding **{scheme_name}**)"
             
             if actual_prompt:
                 with st.spinner("Summarizing..."):
                     try:
                         response_text = generate_chat_response([{"role": "user", "content": actual_prompt}])
                         translated = translate_text(response_text, selected_language_name)
                         
                         st.session_state.scheme_chat.append({"role": "user", "content": actual_prompt, "display": display_prompt})
                         st.session_state.scheme_chat.append({"role": "assistant", "content": translated})
                         st.rerun()
                     except Exception as e:
                         st.error(f"Error: {e}")
             else:
                 st.warning("Please enter a scheme name and query, or record a voice message.")
    else:
        st.info("Ask follow-up questions about this scheme.")
        
        follow_up = st.text_input("Type your Follow-up:", key="scheme_follow_up")
        scheme_audio_follow = st.audio_input("🎤 Or record Follow-up via Voice", key="scheme_audio_follow")
        send_btn = st.button("Send Follow-up", key="scheme_send", use_container_width=True, type="primary")
            
        if send_btn:
            actual_follow_up = transcribe_audio(scheme_audio_follow) if scheme_audio_follow else follow_up
            if actual_follow_up:
                with st.spinner("Thinking..."):
                    st.session_state.scheme_chat.append({"role": "user", "content": actual_follow_up, "display": ("🎤 " if scheme_audio_follow else "") + actual_follow_up})
                    try:
                        response_text = generate_chat_response(st.session_state.scheme_chat)
                        translated = translate_text(response_text, selected_language_name)
                        st.session_state.scheme_chat.append({"role": "assistant", "content": translated})
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            else:
                 st.warning("Please type or speak a question first.")
                        
        if st.button("🗑️ Start New Scheme Inquiry"):
            st.session_state.scheme_chat = []
            st.rerun()

# ----------- FEATURE 4: ADMIN DASHBOARD (ADMIN ONLY) -----------
if st.session_state["role"] == "admin":
    with tabs[3]:
        st.header("Admin Controls & Logs")
        
        st.subheader("Manage User Passwords")
        st.write("If a user has lost their password, securely grant them a one-time access token to change their password upon their next login.")
        
        users = load_users()
        farmers = [u for u, data in users.items() if data["role"] == "farmer"]
        
        col1, col2 = st.columns(2)
        with col1:
            selected_farmer = st.selectbox("Select User's Account:", farmers)
            if st.button("Grant Password Reset Access", type="primary"):
                users[selected_farmer]["reset_required"] = True
                save_users(users)
                st.success(f"Granted password reset permission to `{selected_farmer}` successfully! When they try to login, they will be forced to change their password securely.")
        
        st.divider()
        st.subheader("System Login Logs")
        st.write("Track all successful and failed authentication attempts recorded globally across the platform.")
        logs = get_logs()
        if logs:
             # Reverse logs to show newest at the top
            st.dataframe(logs[::-1], use_container_width=True)
        else:
            st.info("No logs generated yet.")
