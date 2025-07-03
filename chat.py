# chat.py
import streamlit as st
from openai_helper import generate_ai_response
from ui_components import render_chat_message

class ChatManager:
    def __init__(self):
        self._initialize_session_state()
    
    def _initialize_session_state(self):
        """Initialize chat-related session state variables"""
        if 'messages' not in st.session_state:
            st.session_state.messages = []
        if 'template_bytes' not in st.session_state:
            st.session_state.template_bytes = None
        if 'template_filename' not in st.session_state:
            st.session_state.template_filename = None
    
    def add_message(self, role, content):
        """Add a message to the chat history"""
        st.session_state.messages.append({"role": role, "content": content})
    
    def clear_history(self):
        """Clear chat history and any associated documents"""
        st.session_state.messages = []
        st.session_state.template_bytes = None
        st.session_state.template_filename = None

        # ─────────────────── UI / CHAT RENDERING ───────────────────
    def display_chat_interface(self, employee_data):
        """
        Draws the conversation using Streamlit's chat API
        while the CSS from StyleManager turns them into bubbles.
        """
        import streamlit as st
        from style_manager import StyleManager
        from openai_helper import generate_ai_response

        # 1️⃣  inject CSS once per page
        StyleManager().load_css()

        # 3️⃣  history
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                if msg["role"] == "user":
                    st.markdown(f'<div class="user-bubble"><span>{msg["content"]}</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="bot-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

        st.markdown("<div style='margin-bottom:20px;'></div>", unsafe_allow_html=True)

        # 4️⃣  input
        if prompt := st.chat_input(
            f"Ask a question about {employee_data['name']} or request a document"
        ):
            # user bubble
            self.add_message("user", prompt)
            with st.chat_message("user"):
                st.markdown(f'<div class="user-bubble"><span>{prompt}</span></div>', unsafe_allow_html=True)

            # bot bubble
            with st.chat_message("assistant"):
                with st.spinner("Thinking…"):
                    reply = generate_ai_response(prompt, employee_data)
                st.markdown(f'<div class="bot-bubble">{reply}</div>', unsafe_allow_html=True)
            self.add_message("assistant", reply)

