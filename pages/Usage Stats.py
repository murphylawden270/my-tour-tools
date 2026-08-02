import streamlit as st
import re

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

st.set_page_config(
    page_title="Usage Stats",
    layout="wide"
)

if "project" not in st.session_state:
    st.session_state.project = {}

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
options.add_argument("--disable-gpu")

bbcode = []

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

if st.button("Add Format", icon="➕"):
    name_dialog()

for f, formats in enumerate(st.session_state.project):
    with st.container(border=True):
        st.text(formats)
        links = st.text_area("Enter Replay URLs Here...", key=f"text_area_{f}", height=100)
        st.session_state.project[formats] = links

if st.button("Generate"):
    if not st.session_state.project:
        st.error("No formats available! Please add a format first.")
    else:
        for key, values in st.session_state.project.items():
            replay = "\n".join(values)
            driver = webdriver.Chrome(options=options)
            driver.get('https://replaystats-eo.herokuapp.com/')

            Replay_urls = driver.find_element(By.NAME, "replay_urls")
            Replay_urls.send_keys(values)
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

final = "\n".join(bbcode)

if final:
    st.caption("BB Code:")
    st.code(final, language=None, height=300)
