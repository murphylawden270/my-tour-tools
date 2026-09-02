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

if "replays" not in st.session_state:
    st.session_state.replays = ""

if "lock" not in st.session_state:
    st.session_state.lock = threading.Lock()

if "final_bbcode" not in st.session_state:
    st.session_state.final_bbcode = ""

if "table" not in st.session_state:
    st.session_state.table = []

if "no_tera" not in st.session_state:
    st.session_state.no_tera = 0

if "tera" not in st.session_state:
    st.session_state.tera = {}

if "sorted_tera" not in st.session_state:
    st.session_state.sorted_tera = {}

if "processed_replay" not in st.session_state:
    st.session_state.processed_replay = 0

if "time" not in st.session_state:
    st.session_state.time = 0

if "invalid_urls" not in st.session_state:
    st.session_state.invalid_urls = []

def fetch_tera(replay):
    if replay.strip() == "":
        return 
    if not replay.startswith("https://replay"):
        return
    if "gen9" not in replay:
        return
    retry = 0
    while retry != 3:
        try:
            a = requests.get(replay + ".log")
            a.raise_for_status()
            break
        except:
            retry += 1
    else:
        return
    if "|rule|Terastal Clause: You cannot Terastallize" in a.text:
        return
    b = re.findall(r'(\|-terastallize\|.*: .*)', a.text)
    if len(b) == 1:
        with st.session_state.lock:
            st.session_state.no_tera += 1
    elif len(b) == 0:
        with st.session_state.lock:
            st.session_state.no_tera += 2

    for i in b:
        c = a.text.split(i)
        d = re.findall(r'\|-terastallize\|(.*): (.*)', i)
        e = d[0][1].split("|")
        for j in reversed(c[0].splitlines()):
            if re.match(rf'\|(?:switch|drag)\|{d[0][0].strip()}: {re.escape(e[0].strip())}\|([^,|]+)(?:,[^|]*)?\|', j):
                f = re.findall(rf'\|(?:switch|drag)\|{d[0][0].strip()}: {re.escape(e[0].strip())}\|([^,|]+)(?:,[^|]*)?\|', j)
                with st.session_state.lock:
                    if f[0].strip() not in st.session_state.tera:
                        st.session_state.tera[f[0].strip()] = []
                    st.session_state.tera[f[0].strip()].append(e[1].strip())
                break

st.session_state.replays = st.text_area("Enter Replay URL Here...", height=200)

if st.button("Fetch"):
    if st.session_state.replays.strip():
        st.session_state.no_tera = 0
        st.session_state.tera = {}
        st.session_state.table = []
        st.session_state.invalid_urls = []
        st.session_state.processed_replay = 0

    with ThreadPoolExecutor(max_workers=50) as executor:
        list(executor.map(fetch_tera, st.session_state.replays.splitlines()))

    header = '''[TABLE width="100%"]
[TR][TD width="33.3333%"]Pokemon[/TD][TD width="10%"]Count[/TD][TD width="33.3333%"]Type[/TD][/TR]'''
    st.session_state.table.append(header)

    st.session_state.sorted_tera = {keys : values for keys, values in sorted(st.session_state.tera.items(), key = lambda item: len(item[1]), reverse=True)}

    for x, y in st.session_state.sorted_tera.items():
        counts = collections.Counter(y)
        sorted_counts = dict(counts.most_common())
        types = ""
        for l, m in sorted_counts.items():
            types += f"{l} ({m}), "
        types = types[:-2]
        row = f'''[TR][TD width="33.3333%"]:{x}:{x}[/TD][TD width="10%"]{len(y)}[/TD][TD width="33.3333%"]{types}[/TD][/TR]'''
        st.session_state.table.append(row)

    closer = f'''[TR][TD width="33.3333%"]No Tera[/TD][TD width="10%"]{st.session_state.no_tera}[/TD][TD width="33.3333%"][/TD][/TR]
[/TABLE]'''
    st.session_state.table.append(closer)

    st.session_state.final_bbcode = "\n".join(st.session_state.table)

    st.caption("BB Code:")
    st.code(st.session_state.final_bbcode, language=None, height=300)
