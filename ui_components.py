﻿# ui_components.py
import streamlit as st
import time
import os

def load_css():
    """Load CSS styles"""
    css_file = "style.css"
    if os.path.exists(css_file):
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback CSS if file doesn't exist
        fallback_css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        :root {
            --primary-purple: #9B6DD6;
            --light-purple: #B794E6;
            --lilac-bg: #F3E8FF;
            --lilac-light: #F8F2FF;
            --dark-purple: #2B1B4C;
            --chat-user-bg: #E7D4F9;
            --chat-bot-bg: #FFFFFF;
            --border-purple: #D4B5F7;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            color: var(--dark-purple);
        }
        
        .stApp {
            background: linear-gradient(135deg, #F3E8FF 0%, #FFFFFF 100%) !important;
            min-height: 100vh;
        }
        
        .main > div {
            background: transparent !important;
        }
        
        section[data-testid="stSidebar"] {
            background: rgba(248, 242, 255, 0.8) !important;
            backdrop-filter: blur(10px);
            border-right: 1px solid var(--border-purple);
        }
        
        section[data-testid="stSidebar"] > div {
            background: transparent !important;
        }
        
        .prezlab-logo {
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            font-size: 28px;
            color: var(--dark-purple);
            margin: 0;
            padding: 0;
        }
        
        .point {
            color: var(--primary-purple);
        }
        
        .scribble-bottom {
            display: block;
            height: 4px;
            background-color: var(--light-purple);
            border-radius: 2px;
            margin: 10px 0 20px 0;
            width: 100px;
        }
        
        .scribble-highlight {
            position: relative;
            display: inline-block;
        }
        
        .scribble-highlight::after {
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 6px;
            background-color: rgba(155, 109, 214, 0.3);
            border-radius: 3px;
            z-index: -1;
        }
        
        .chat-messages-container {
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            height: 500px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        
        .chat-message-wrapper {
            display: flex;
            width: 100%;
            margin-bottom: 8px;
        }
        
        .chat-message-user {
            justify-content: flex-end;
        }
        
        .chat-message-bot {
            justify-content: flex-start;
        }
        
        .chat-bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            font-size: 15px;
            line-height: 1.5;
            word-wrap: break-word;
            position: relative;
        }
        
        .user-bubble {
            background-color: var(--primary-purple);
            color: white;
            border-bottom-right-radius: 4px;
            margin-right: 10px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
        }
        
        .bot-bubble {
            background-color: white;
            color: var(--dark-purple);
            border: 1px solid rgba(212, 181, 247, 0.3);
            border-bottom-left-radius: 4px;
            margin-left: 10px;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
        }
        
        .download-button-container {
            display: flex;
            justify-content: flex-start;
            margin-left: 10px;
            margin-top: 8px;
            margin-bottom: 12px;
        }
        
        .welcome-box {
            text-align: center;
            padding: 40px;
            background: rgba(255, 255, 255, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            margin-top: 20px;
            box-shadow: 0 4px 12px rgba(155, 109, 214, 0.1);
            border: 1px solid rgba(212, 181, 247, 0.3);
        }
        
        .welcome-title {
            color: var(--dark-purple);
            font-weight: 600;
            font-size: 24px;
            margin-bottom: 16px;
        }
        
        .welcome-text {
            color: #666;
            margin-bottom: 24px;
            font-size: 16px;
        }
        
        /* Simple scribble image as a CSS background */
        .simple-scribble {
            height: 8px;
            width: 120px;
            margin: 24px auto;
            background-color: var(--light-purple);
            border-radius: 4px;
            position: relative;
        }
        
        .simple-scribble::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 70%;
            height: 100%;
            background-color: var(--primary-purple);
            border-radius: 4px;
        }
        
        /* Login container styling - simplified without white box */
        .login-container {
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
        }
        
        /* Beautiful gradient background for login page */
        .login-gradient {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(135deg, #F3E8FF 0%, #E7D4F9 50%, #F8F2FF 100%);
            z-index: -1;
        }
        
        /* Floating animation for decorative elements */
        @keyframes float {
            0% {
                transform: translateY(0px);
            }
        
            50% {
                transform: translateY(-10px);
            }
        
            100% {
                transform: translateY(0px);
            }
        }
        
        /* Subtle glow effect */
        @keyframes glow {
            0% {
                box-shadow: 0 8px 32px rgba(155, 109, 214, 0.1);
            }
        
            50% {
                box-shadow: 0 8px 40px rgba(155, 109, 214, 0.2);
            }
        
            100% {
                box-shadow: 0 8px 32px rgba(155, 109, 214, 0.1);
            }
        }
        
        /* Glass morphism card effect */
        .glass-card {
            background: rgba(255, 255, 255, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(183, 148, 230, 0.3);
            border-radius: 16px;
            animation: glow 3s ease-in-out infinite;
        }
        
        /* Download button styling */
        div[data-testid="stDownloadButton"] > button {
            background-color: var(--primary-purple) !important;
            color: white !important;
            border: none !important;
            padding: 0.5rem 2rem !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            margin-top: 0.5rem !important;
            transition: all 0.2s ease !important;
        }
        
        div[data-testid="stDownloadButton"] > button:hover {
            background-color: var(--light-purple) !important;
            transform: translateY(-1px) !important;
        }
        
        /* Progress bar styling */
        .stProgress > div > div > div > div {
            background-color: var(--primary-purple) !important;
        }
        
        /* Success messages */
        .stSuccess {
            background-color: rgba(155, 109, 214, 0.1) !important;
            border: 1px solid var(--light-purple) !important;
            border-radius: 8px !important;
            color: var(--dark-purple) !important;
        }
        
        /* Error messages */
        .stError {
            background-color: rgba(255, 107, 107, 0.1) !important;
            border: 1px solid #FF6B6B !important;
            border-radius: 8px !important;
        }
        
        /* Info messages */
        .stInfo {
            background-color: rgba(155, 109, 214, 0.08) !important;
            border: 1px solid var(--border-purple) !important;
            border-radius: 8px !important;
            color: var(--dark-purple) !important;
        }
        
        /* Text input styling */
        .stTextInput > div > div > input {
            background-color: white !important;
            border: 1px solid var(--border-purple) !important;
            border-radius: 8px !important;
            padding: 0.75rem !important;
            color: var(--dark-purple) !important;
            transition: border-color 0.2s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-purple) !important;
            box-shadow: 0 0 0 2px rgba(155, 109, 214, 0.2) !important;
        }
        
        /* Checkbox styling */
        .stCheckbox label {
            color: var(--dark-purple) !important;
        }
        
        /* Markdown text */
        .stMarkdown {
            color: var(--dark-purple);
        }
        
        /* Code blocks */
        .stCodeBlock {
            background-color: rgba(155, 109, 214, 0.05) !important;
            border: 1px solid var(--border-purple) !important;
            border-radius: 8px !important;
        }
        
        /* Scrollbar styling */
        ::-webkit-scrollbar {
            width: 8px;
            height: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--lilac-light);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--light-purple);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--primary-purple);
        }
        
        /* Chat input area enhancement */
        .stChatInputContainer {
            background-color: white;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 -2px 8px rgba(155, 109, 214, 0.1);
            border: 1px solid var(--border-purple);
        }
        
        /* Make expanders more subtle */
        .streamlit-expander {
            border: 1px solid var(--border-purple) !important;
            border-radius: 8px !important;
            background-color: white !important;
        }
        
        /* Enhanced input styling for login page */
        .stTextInput > div > div > input {
            background-color: rgba(255, 255, 255, 0.9) !important;
            border: 2px solid rgba(183, 148, 230, 0.3) !important;
            border-radius: 10px !important;
            padding: 0.75rem 1rem !important;
            font-size: 1rem !important;
            transition: all 0.3s ease !important;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: var(--primary-purple) !important;
            box-shadow: 0 0 0 3px rgba(155, 109, 214, 0.1) !important;
            background-color: white !important;
        }
        
        .stTextInput > div > div > input::placeholder {
            color: #999 !important;
        }
        
        /* Form container glass effect */
        [data-testid="stForm"] {
            background: rgba(255, 255, 255, 0.6);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            border: 1px solid rgba(183, 148, 230, 0.3);
            border-radius: 16px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(155, 109, 214, 0.1);
        }
        </style>
        """
        st.markdown(fallback_css, unsafe_allow_html=True)

def render_header():
    """Render the Prezlab header"""
    st.markdown(
        """
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <div class="prezlab-logo">prezlab<span class="point">.</span></div>
            <div style="margin-left: 15px; font-size: 20px; color: var(--dark-purple);">Employee Chatbot</div>
        </div>
        <div class="scribble-bottom"></div>
        """, 
        unsafe_allow_html=True
    )

def render_login_form(login_callback, saved_credentials=None):
    """
    Render the login form
    
    Args:
        login_callback: Function to call when login is submitted
        saved_credentials: Optional saved credentials dict
    """
    # Add prezlab logo at the top left
    st.markdown("""
    <div style="position: fixed; top: 2rem; left: 2rem; z-index: 1000;">
        <div class="prezlab-logo" style="font-size: 28px;">
            prezlab<span class="point">.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Add welcome message
    st.markdown("""
    <div style="text-align: center; margin-top: 4rem; margin-bottom: 3rem;">
        <h2 style="color: var(--dark-purple); font-weight: 600; margin-bottom: 0.5rem;">Welcome to PrezBot</h2>
        <p style="color: #666; font-size: 1.1rem;">How can I help you?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create three columns for centering
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        # Login form in a glass card
        with st.container():
            with st.form("login_form", clear_on_submit=False):
                # Pre-fill username if available
                default_username = saved_credentials['username'] if saved_credentials else ""
                username = st.text_input("Email", 
                                       value=default_username,
                                       placeholder="your.email@prezlab.com",
                                       label_visibility="collapsed")
                
                st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)
                
                # Pre-fill password if available (hidden)
                default_password = saved_credentials['password'] if saved_credentials else ""
                password = st.text_input("Password", 
                                       value=default_password,
                                       type="password", 
                                       placeholder="Enter your password",
                                       label_visibility="collapsed")
                
                st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
                
                # Remember me checkbox with custom styling
                remember_me = st.checkbox("Remember me", 
                                        value=bool(saved_credentials),
                                        help="Save your credentials for faster login next time")
                
                st.markdown("<div style='margin-bottom: 1.5rem;'></div>", unsafe_allow_html=True)
                
                submitted = st.form_submit_button("Sign In", use_container_width=True)
                
                if submitted:
                    if username and password:
                        login_callback(username, password, remember_me)
                    else:
                        st.error("Please enter both email and password")
            
            # Show if credentials are saved
            if saved_credentials:
                st.info("🔐 Saved credentials found")
                
                # Auto-login if not already attempted
                if 'auto_login_attempted' not in st.session_state:
                    st.session_state.auto_login_attempted = True
                    time.sleep(0.5)  # Small delay for UI
                    login_callback(saved_credentials['username'], saved_credentials['password'], remember_me=True)
            
            # Show forget credentials option if credentials are saved
            if saved_credentials:
                st.markdown("<div style='text-align: center; margin-top: 1rem;'>", unsafe_allow_html=True)
                if st.button("Forget saved credentials", key="forget_btn", use_container_width=True):
                    # This should trigger a callback to clear credentials
                    st.session_state.clear_credentials = True
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)
        
        # Add decorative bottom element
        st.markdown("""
        <div style="margin-top: 3rem; text-align: center;">
            <div style="display: inline-flex; align-items: center; gap: 8px; color: #999; font-size: 0.875rem;">
                <div style="width: 20px; height: 1px; background-color: rgba(155, 109, 214, 0.3);"></div>
                <span>Powered by</span>
                <div style="width: 20px; height: 1px; background-color: rgba(155, 109, 214, 0.3);"></div>
            </div>
            <div style="margin-top: 0.5rem; display: flex; justify-content: center; gap: 1rem; opacity: 0.7;">
                <span style="color: #666; font-size: 0.875rem;">OpenAI</span>
                <span style="color: #666;">•</span>
                <span style="color: #666; font-size: 0.875rem;">Odoo</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Brief app description
    st.markdown(
        """
        <div style="text-align: center; margin-top: 2rem;">
            <p style="font-size: 16px; color: #666;">
                Chat with AI about your employee data. Turn raw data into 
                <span class="scribble-highlight">clear insights</span>.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

def render_sidebar(username, is_manual_search_mode, logout_callback):
    """
    Render the sidebar content
    
    Args:
        username: Current user's username
        is_manual_search_mode: Boolean for manual search mode
        logout_callback: Function to call when logout is clicked
    """
    with st.sidebar:
        st.markdown(
            f"""
            <h3 style="color: var(--dark-purple); font-weight: 600;">Welcome!</h3>
            <p style="color: #666; font-size: 0.9rem;">Logged in as: {username}</p>
            <div class="scribble-bottom"></div>
            """, 
            unsafe_allow_html=True
        )
        
        # OpenAI API key status
        st.success("✅ OpenAI API key is set!")
        
        # Odoo connection status
        st.success("✅ Connected to Odoo")
        
        # Debug toggle
        show_debug = st.checkbox(
            "Show Debug Info", 
            value=st.session_state.get('show_debug', False),
            key='debug_toggle'
        )
        
        # Update session state when checkbox changes
        if show_debug != st.session_state.get('show_debug', False):
            st.session_state.show_debug = show_debug
            st.rerun()
        
        # Add manual search toggle
        st.markdown("---")
        manual_mode = st.checkbox(
            "Manual Search Mode", 
            value=is_manual_search_mode,
            help="Enable to search for other employees instead of viewing your own data",
            key='manual_mode_toggle'
        )
        
        # Update session state when checkbox changes
        if manual_mode != st.session_state.get('manual_search_mode', False):
            st.session_state.manual_search_mode = manual_mode
            st.rerun()
        
        # Show available templates
        st.markdown("---")
        st.markdown(
            """
            <h4 style="color: var(--dark-purple); font-weight: 500;">Available Templates</h4>
            """, 
            unsafe_allow_html=True
        )
        st.markdown("""
        📄 **Employment Letters**
        - Standard (English)
        - Arabic version
        - Embassy/visa letters
        - Experience certificates
        
        Just ask the chatbot to generate any of these!
        """)
        
        # Logout button
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            logout_callback()

def render_chat_message(message, message_type="user"):
    """
    Render a single chat message in WhatsApp-like style
    
    Args:
        message: Message content
        message_type: "user" or "bot"
    """
    if message_type == "user":
        # User messages on the right
        st.markdown(f"""
        <div class="chat-message-wrapper chat-message-user">
            <div class="chat-bubble user-bubble">
                {message}
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Bot messages on the left
        st.markdown(f"""
        <div class="chat-message-wrapper chat-message-bot">
            <div class="chat-bubble bot-bubble">
                {message}
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_empty_state(is_manual_mode):
    """
    Render the empty state when no employee data is loaded
    
    Args:
        is_manual_mode: Boolean indicating if in manual search mode
    """
    if is_manual_mode:
        st.markdown("""
        <div class="welcome-box">
            <div class="welcome-title">Ready to turn data into insights</div>
            <div class="welcome-text">Enter a name and click 'Search' to start exploring employee data.</div>
            <div class="simple-scribble"></div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="welcome-box">
            <div class="welcome-title">Loading your data...</div>
            <div class="welcome-text">Your employee information will load automatically.</div>
            <div class="simple-scribble"></div>
        </div>
        """, unsafe_allow_html=True)


def render_search_result(found, name):
    """
    Display search result
    
    Args:
        found: Boolean indicating if employee was found
        name: Name of the employee searched
    """
    if found:
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
            <div style="background-color: var(--primary-purple); width: 8px; height: 8px; border-radius: 50%; margin-right: 8px;"></div>
            <span style="color: var(--dark-purple); font-weight: 600;">Found:</span> {name}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display: flex; align-items: center;">
            <div style="background-color: #FF6B6B; width: 8px; height: 8px; border-radius: 50%; margin-right: 8px;"></div>
            <span style="color: var(--dark-purple); font-weight: 600;">Not found:</span> {name}
        </div>
        """, unsafe_allow_html=True)