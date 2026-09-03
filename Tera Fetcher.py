import streamlit as st
import requests
import re
import collections
import time
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

if "complete" not in st.session_state:
    st.session_state.complete = 0

if "invalid_urls" not in st.session_state:
    st.session_state.invalid_urls = []

if "send" not in st.session_state:
    st.session_state.send = ""

if "warn" not in st.session_state:
    st.session_state.warn = False

def fetch_tera(replay):
    tera = {}
    no_tera = 0
    if replay.strip() == "":
        return "", None
    if not replay.startswith("https://replay"):
        return "", None
    if "gen9" not in replay:
        return replay, None
    retry = 0
    while retry != 3:
        try:
            a = requests.get(replay + ".log")
            a.raise_for_status()
            break
        except:
            retry += 1
    else:
        return replay, None
    if "|rule|Terastal Clause: You cannot Terastallize" in a.text:
        return replay, None
    lock = threading.Lock()
    b = re.findall(r'(\|-terastallize\|.*: .*)', a.text)
    if len(b) == 1:
        with lock:
            no_tera += 1
    elif len(b) == 0:
        with lock:
            no_tera += 2

    for i in b:
        c = a.text.split(i)
        d = re.findall(r'\|-terastallize\|(.*): (.*)', i)
        e = d[0][1].split("|")
        for j in reversed(c[0].splitlines()):
            if re.match(rf'\|(?:switch|drag)\|{d[0][0].strip()}: {re.escape(e[0].strip())}\|([^,|]+)(?:,[^|]*)?\|', j):
                f = re.findall(rf'\|(?:switch|drag)\|{d[0][0].strip()}: {re.escape(e[0].strip())}\|([^,|]+)(?:,[^|]*)?\|', j)
                with lock:
                    if f[0].strip() not in tera:
                        tera[f[0].strip()] = []
                    tera[f[0].strip()].append(e[1].strip())
                break

    return tera, no_tera

def clear():
    st.session_state.replays = ""
    st.session_state.final_bbcode = ""
    st.session_state.table = []
    st.session_state.no_tera = 0
    st.session_state.tera = {}
    st.session_state.sorted_tera = {}
    st.session_state.processed_replay = 0
    st.session_state.invalid_urls = []
    st.session_state.send = ""
    st.session_state.warn = False
    st.session_state.time = 0
    st.session_state.complete = 0

st.text_area("**Enter Gen 9 Replay URL Here...**", key="replays", height=200)

col1, col2, _ = st.columns([1, 1, 6], gap="small")
with col1:
    if st.button("Fetch", use_container_width=True):
        st.session_state.no_tera = 0
        st.session_state.tera = {}
        st.session_state.table = []
        st.session_state.invalid_urls = []
        st.session_state.send = ""
        st.session_state.processed_replay = 0
        st.session_state.warn = False
        st.session_state.time = 0
        st.session_state.complete = 0

        st.session_state.time = time.time()
        with ThreadPoolExecutor(max_workers=50) as executor:
            output = list(executor.map(fetch_tera, st.session_state.replays.splitlines()))

            for o, p in output:
                if o is None:
                    continue
                if p is None:
                    if o != "":
                        if o not in st.session_state.invalid_urls: 
                            st.session_state.invalid_urls.append(o)
                    continue
                for key, value in o.items():
                    if key not in st.session_state.tera:
                        st.session_state.tera[key] = []
                    for i in value:
                        st.session_state.tera[key].append(i)
                st.session_state.no_tera += p
                st.session_state.processed_replay += 1

        if st.session_state.tera == {} and st.session_state.no_tera == 0:
            st.session_state.warn = True
        else:
            st.session_state.table = []
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

with col2:
    st.button("Clear", on_click=clear, use_container_width=True)

if st.session_state.warn == True:
    st.warning("No Replays Found! Please Enter Atleast One Valid Gen 9 Link!")

if st.session_state.processed_replay != 0:
    st.caption(f"Processed {st.session_state.processed_replay} replays.")
    st.session_state.complete = time.time()
    st.caption(f"Time taken: {st.session_state.complete - st.session_state.time} seconds.")
st.caption("BB Code:")
st.code(st.session_state.final_bbcode, language=None, height=300)

if st.session_state.invalid_urls != []:
    st.session_state.send = ""
    for d in st.session_state.invalid_urls:
        st.session_state.send += f"- {d}\n\n"
    st.warning(f'''Invalid Replays Found: \n\n
{st.session_state.send}''')
