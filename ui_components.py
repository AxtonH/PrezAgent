# ui_components.py
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
        # Fallback CSS if file doesn't exist (no chat bubble or chat alignment CSS)
        fallback_css = """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        :root {
            --primary-purple: #9B6DD6;
            --light-purple: #B794E6;
            --lilac-bg: #F3E8FF;
            --lilac-light: #F8F2FF;
            --dark-purple: #2B1B4C;
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
        /* (All chat bubble, chat-message, chat-messages-container, user-bubble, bot-bubble, and related chat CSS removed) */
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
