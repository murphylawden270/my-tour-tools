import time

start = time.time()

import streamlit as st
import re

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from concurrent.futures import ThreadPoolExecutor

st.set_page_config(
    page_title="Usage Stats",
    layout="wide"
)

if "project" not in st.session_state:
    st.session_state.project = {}

if "all_bbcode" not in st.session_state:
    st.session_state.all_bbcode = {}

if "final" not in st.session_state:
    st.session_state.final = []

if "processed_replays" not in st.session_state:
    st.session_state.processed_replays = 0

if "processed_formats" not in st.session_state:
    st.session_state.processed_formats = 0

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1.4rem;
            padding-bottom: 1rem;
        }
    """,
    unsafe_allow_html=True,
)

st.title("Usage Stats Generator:")
st.caption("This application uses [eo.herokuapp](https://replaystats-eo.herokuapp.com/) as a base. HUGE S/O to [Eo Ut Mortus](http://www.smogon.com/forums/members/eo-ut-mortus.9718/) for this awesome tool.")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

@st.dialog("Format Name")
def name_dialog():
    name = st.text_input("Enter Your Format Name:")
    if st.button("Confirm"):
        if name:
            if name in st.session_state.project:
                st.error("Format name already exists! Please choose another format name.")
            else:
                st.session_state.project[name] = []
                st.rerun()

def replay(key, values):
    if not values or values.strip() == "":
        return key, [], 0
    rl = len(values.splitlines())
    bbcode = []
    driver = webdriver.Chrome(options=options)
    driver.get('https://replaystats-eo.herokuapp.com/')

    Replay_urls = driver.find_element(By.NAME, "replay_urls")
    driver.execute_script("arguments[0].value = arguments[1];", Replay_urls, values)
    driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", Replay_urls)
    Submit = driver.find_element(By.NAME, "link_submit")
    Submit.click()

    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.rawtext.results")))

    main = []
    usage = []
    url = []
    TextArea = driver.find_elements(By.CSS_SELECTOR, "textarea.rawtext.results")
    for i in TextArea:
            usage.append(i.get_attribute("value"))
        
    for i, j in enumerate(usage):
            if i == 0:
                if "Leads" in usage[3] and "1" in usage[3]:
                    a = j.replace("[CODE]", '''[URL='1']Moves and Teammates[/URL] | [URL='2']Combos[/url] | [URL='3']Leads[/URL]
[CODE]''')
                    main.append(a)

                else:
                    a = j.replace("[CODE]", '''[URL='1']Moves and Teammates[/URL] | [URL='2']Combos[/url]
[CODE]''')
                    main.append(a)

            elif i >= 1:
                k = re.sub(r'\[IMG\](.*?)\[\/IMG\]|\[B\](.*?)\[\/B\]|\[\/?CODE\]', "", j)
                k = k.strip()

                driver.get('https://pokepast.es/')
                
                wait.until(EC.presence_of_element_located((By.NAME, "paste")))
                Paste = driver.find_element(By.NAME, "paste")
                driver.execute_script("arguments[0].value = arguments[1];", Paste, k)
                driver.execute_script("arguments[0].dispatchEvent(new Event('input', { bubbles: true }));", Paste)

                Submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value='Submit Paste!']")))
                Submit.click()

                wait.until(EC.presence_of_element_located((By.TAG_NAME, "pre")))

                url.append(driver.current_url)

    driver.quit()

    Final = main[0].replace("-*.png",".png").replace("???", f"{key}").replace("'1'", f"'{url[0]}'").replace("'2'", f"'{url[1]}'").replace("'3'", f"'{url[2]}'")
    bbcode.append(Final)
    bbcode.append("")

    return key, bbcode, rl

if st.button("Add Format", icon="➕"):
    name_dialog()

for f, formats in enumerate(st.session_state.project):
    with st.container(border=True):
        smol1, smol2, smol3 = st.columns([1,8,1], gap="small")
        with smol1:
            st.text(formats)
        with smol3:
            if st.button("❌", key=f"delete_{f}"):
                del st.session_state.project[formats]
                if formats in st.session_state.all_bbcode:
                    del st.session_state.all_bbcode[formats]
                st.rerun()
        links = st.text_area("Enter Replay URLs Here...", key=f"text_area_{f}", height=100)
        st.session_state.project[formats] = links    

col1, col2, col3 = st.columns([1,1,5], gap="small")
with col1:
    if st.button("Generate", use_container_width=True):
        st.session_state.processed_replays = 0
        st.session_state.processed_formats = 0
        if not st.session_state.project:
            st.error("No formats available! Please add a format first.")
        else:
            with ThreadPoolExecutor(max_workers=4) as executor:
                output = list(executor.map(replay, st.session_state.project.keys(), st.session_state.project.values()))

            for key, bbcode, rl in output:
                st.session_state.processed_replays += rl
                st.session_state.processed_formats += 1
                st.session_state.all_bbcode[key] = bbcode

with col2:
    if st.button("Clear All", use_container_width=True):
        st.session_state.project.clear()
        st.session_state.all_bbcode.clear()
        st.session_state.final.clear()
        st.session_state.processed_replays = 0
        st.session_state.processed_formats = 0
        st.rerun()

for i in st.session_state.project.keys():
    if i in st.session_state.all_bbcode:
        st.session_state.final.append("\n".join(st.session_state.all_bbcode[i]))

if st.session_state.final:
    done = "\n".join(st.session_state.final)
    if done == "":
        st.error("No replays found! Please enter a replay.")
    elif done != "":
        st.caption(f"Processed {st.session_state.processed_formats} formats and {st.session_state.processed_replays} replays.")
        end = time.time()
        st.caption(f"Time taken: {end - start} seconds.")
        st.caption("BB Code:")
        st.code(done, language=None, height=300)
