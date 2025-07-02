# style_manager.py
import streamlit as st
import os

class StyleManager:
    def __init__(self, css_file="style.css"):
        self.css_file = css_file
    
    def load_css(self):
        """
        Final bubble layout:
        • Orange-icon user → right, white bubble
        • Yellow-icon bot  → left, light-purple bubble
        • Icons now perfectly centred vertically beside the bubble
        """
        import streamlit as st, os, textwrap

        # keep your own stylesheet first
        if os.path.exists(self.css_file):
            with open(self.css_file) as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

        st.markdown(
            textwrap.dedent(
                """
                <style>
                /* hide Streamlit chrome */
                #MainMenu, footer {visibility:hidden;}

                /* chat container */
                div[data-testid="stChatMessageContainer"]{
                    display:flex;flex-direction:column;gap:14px;
                }

                /* ───────── VERTICAL-ALIGN FIX ───────── */
                /* every message row is flex & centred */
                div[data-testid="stChatMessage"]{
                    display:flex !important;          /* override Streamlit default */
                    align-items:center !important;    /* center avatar + bubble   */
                    gap:12px;                         /* nice breathing room      */
                }

                /* USER (odd) – bubble right, avatar right */
                div[data-testid="stChatMessage"]:nth-child(odd){
                    flex-direction:row-reverse;
                }
                div[data-testid="stChatMessage"]:nth-child(odd) > div:nth-child(2){
                    background:#FFFFFF;color:#2B1B4C;
                    border:1px solid #E5E5E5;border-radius:18px 18px 4px 18px;
                    padding:12px 16px;max-width:75%;text-align:left;
                    box-shadow:0 1px 2px rgba(0,0,0,.06);
                }

                /* BOT (even) – bubble left, avatar left */
                div[data-testid="stChatMessage"]:nth-child(even){
                    flex-direction:row;
                }
                div[data-testid="stChatMessage"]:nth-child(even) > div:nth-child(2){
                    background:#E6D4FF;color:#2B1B4C;
                    border-radius:18px 18px 18px 4px;
                    padding:12px 16px;max-width:75%;text-align:left;
                    box-shadow:0 1px 2px rgba(0,0,0,.04);
                }

                /* tidy list indentation */
                div[data-testid="stChatMessage"] ul,
                div[data-testid="stChatMessage"] ol{
                    margin:0 0 0 1.25em;
                }
                </style>
                """
            ),
            unsafe_allow_html=True,
        )

    def _load_fallback_css(self):
        """Load fallback CSS if file doesn't exist"""
        fallback_css = """
        <style>
        /* Your fallback CSS here */
        </style>
        """
        st.markdown(fallback_css, unsafe_allow_html=True)