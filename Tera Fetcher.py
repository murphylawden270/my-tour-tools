import streamlit as st
import requests
import re
import collections
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

st.set_page_config(
    page_title="Tera Fetcher",
    layout="wide"
)

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Tera Fetcher Tool For Usage Stats:")
