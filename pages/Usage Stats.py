import streamlit as st

import re
import time

import tempfile
from pathlib import Path
from github import Github, Auth
import random
from datetime import datetime

from concurrent.futures import ThreadPoolExecutor
import itertools

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

import requests

st.set_page_config(
    page_title="Usage Stats",
    layout="wide"
)

if "replays" not in st.session_state:
    st.session_state.replays = {}

if "smogon_name" not in st.session_state:
    st.session_state.smogon_name = ""

if "tournament_name" not in st.session_state:
    st.session_state.tournament_name = ""

if "additional_usage" not in st.session_state:
    st.session_state.additional_usage = []

if "round_name" not in st.session_state:
    st.session_state.round_name = ""

if "optin" not in st.session_state:
    st.session_state.optin = True

if "spoiler" not in st.session_state:
    st.session_state.spoiler = False

if "foldername" not in st.session_state:
    st.session_state.foldername = ""

if "folder" not in st.session_state:
    st.session_state.folder = None

if "ftime" not in st.session_state:
    st.session_state.ftime = "" 

if "a" not in st.session_state:
    st.session_state.a = "" 

if "all_bbcode" not in st.session_state:
    st.session_state.all_bbcode = {}

if "filedesc" not in st.session_state:
    st.session_state.filedesc = {}

if "ip" not in st.session_state:
    st.session_state.ip = ""

if "send" not in st.session_state:
    st.session_state.send = ""

if "start" not in st.session_state:
    st.session_state.start = None

if "colorrl" not in st.session_state:
    st.session_state.colorrl = 0

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
st.caption("Usage logs can be found [here](https://github.com/LapplandO7/team-tour-stats-uploads).")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

lappland = st.secrets['lappland']
discord = st.secrets['discord']
authorization = st.secrets['authorization']

@st.dialog("Format Name")
def name_dialog():
    name = st.text_input("Enter Your Format Name:")
    if st.button("Confirm"):
        if name:
            if name in st.session_state.replays:
                st.error("Format name already exists! Please choose another format name.")
            else:
                st.session_state.replays[name] = []
                st.rerun()

def checkreplay(i):
    i = i.strip()
    if i.startswith("https://replay.pokemonshowdown.com/"):
        return i

with st.expander("Prerequisites:", expanded=True):
    set1, set2 = st.columns(([1,1]), gap="small", border=True)
    with set1:
        st.text("Just remember, I know everytime YOU use this.", help="Your IP address is sent to me through Discord everytime a folder gets uploaded to the GitHub repository. This allows to stop someone from intentionally spamming. If you are uncomforatable to use this tool knowing about this, don't use this tool or feel me to reach out. Every website you visit knows you IP address.")
        st.session_state.smogon_name = st.text_input("Smogon Name *:", help="This field is mandatory. Please use your actual Smogon name, it's necessary for proper logging, but I can't really verify this so I am trusting you.", width=500)
        st.session_state.tournament_name = st.text_input("Project Name *:", help="This field is mandatory. Enter the full name of the project like NDPL VII or ORAS OU Tournament-Based Tiering.", width=500)
        st.session_state.round_name = st.text_input("Round Name (for Tournaments ONLY):", help="Enter the full round name like Week 1 or Round One. Useful for you if you are making tournament stats.", width=500)
    with set2:
        st.text("Additional Settings:")
        makepost = st.checkbox("Make it a Post", value=True, help="Output akin to [tournament usage stats](https://www.smogon.com/forums/threads/oraspl-vi-replays-and-usage-stats.3785250/post-11060712) with colors added for up to 15 format name and a title.")
        if makepost:
            st.session_state.optin = True
        else:
            st.session_state.optin = False
        st.text("Usage Type:")        
        spoiler = st.checkbox("Spoiler")
        if spoiler:
            st.session_state.spoiler = True
        else:
            st.session_state.spoiler = False
        st.text("Additional Usage:")
        st.session_state.additional_usage = [] 
        movesandteammates = st.checkbox("Moves and Teammates", value=True)
        if movesandteammates and "Moves and Teammates" not in st.session_state.additional_usage:
            st.session_state.additional_usage.append("Moves and Teammates")
        combos = st.checkbox("Combos", value=True)
        if combos and "Combos" not in st.session_state.additional_usage:
            st.session_state.additional_usage.append("Combos")
        leads = st.checkbox("Leads", value=True)
        if leads and "Leads" not in st.session_state.additional_usage:
            st.session_state.additional_usage.append("Leads")

if st.button("Add Format", icon="➕"):
    name_dialog()

for f, formats in enumerate(st.session_state.replays):
    with st.expander(formats, expanded=True):
        smol1, smol2 = st.columns([18,1], gap="small", border=True)
        with  smol1:
            links = st.text_area("Enter Replay URLs Here...", key=f"text_area_{f}", height=100)
            actuallinks = []
            with ThreadPoolExecutor(max_workers=50) as executor:
                result = list(executor.map(checkreplay, links.splitlines()))
                if result:
                    actuallinks.append(result[0])
            if "\n".join(actuallinks) != "":
                st.session_state.replays[formats] = "\n".join(actuallinks)
        with smol2:
            if st.button("❌", key=f"delete_{f}"):
                del st.session_state.replays[formats]
                if formats in st.session_state.all_bbcode:
                    del st.session_state.all_bbcode[formats]
                st.rerun()

color = ["#9370db","#008080","#ffa500","#e25041","#1abc9c","#f37934","#fac51c","#2969b0","#7c706b","#a61c00","#ff00ff","#134f5c","#534042","#9d66bd","#ffff00"]
def usages(key, values, foldernameft):
    rl = len(values.splitlines())
    l = 1
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
    filedesc = {}
    textarea = driver.find_elements(By.CSS_SELECTOR, "textarea.rawtext.results")
    for i in textarea:
        usage.append(i.get_attribute("value"))

    driver.quit()
    for i, j in enumerate(usage):
        if i == 0:
            if "Leads" in usage[3] and ".00%" in usage[3]:
                if spoilerft == False:
                    b = j.replace("[CODE]", f'''{aft}
[CODE]''')
                    main.append(b)
                else:
                    b = j.replace("[CODE]", f'''{aft}
[SPOILER="Usage"]
[CODE]''')
                    if "[LIST]" in b:
                        c = b.replace("[/LIST]", '''[/LIST]
[/SPOILER]''')
                    else:
                        c = b.replace("[/CODE]", '''[/CODE]
[/SPOILER]''')
                    main.append(c)
            else:
                if f"[URL='https://raw.githubusercontent.com/LapplandO7/team-tour-stats-uploads/refs/heads/main/{foldernameft}/lds']Leads[/URL]" in aft:
                    b = aft.replace(f" | [URL='https://raw.githubusercontent.com/LapplandO7/team-tour-stats-uploads/refs/heads/main/{foldernameft}/lds']Leads[/URL]","")
                if spoilerft == False:
                    c = j.replace("[CODE]", f'''{b}
[CODE]''')
                    main.append(c)
                else:
                    c = j.replace("[CODE]", f'''{b}
[SPOILER="Usage"]
[CODE]''')
                    if "[LIST]" in b:
                        d = c.replace("[/LIST]", '''[/LIST]
[/SPOILER]''')
                    else:
                        d = c.replace("[/CODE]", '''[/CODE]
[/SPOILER]''')
                    main.append(d)

        k = re.sub(r'\[IMG\](.*?)\[\/IMG\]|\[B\](.*?)\[\/B\]|\[\/?CODE\]', "", j)
        k = k.strip()

        truename = key

        if i == 0:
            usg = "Usage"
            addusg = "usg"
        elif i == 1:
            usg = "Moves and Teammates"
            addusg = "mat"
        elif i == 2:
            usg = "Combos"
            addusg = "cmb"
        elif i == 3:
            usg = "Leads"
            addusg = "lds"

        if roundft != "":
            file = f"{tourft.lower().replace(" ","")}-{roundft.lower().replace(" ","")}-{truename.lower().replace(" ","")}-{addusg}.txt"
            desc = f"This is {usg} for {truename} in {roundft.upper()} of {tourft.upper().strip()}."
        else:
            file = f"{tourft.lower().replace(" ","")}-{truename.lower().replace(" ","")}-{addusg}.txt"
            desc = f"This is {usg} for {truename} of {tourft.upper().strip()}."
        filedesc[file] = desc
        filepath = foldernameft/file
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            f.write(k)
        if i != 0:
            url.append(file)

    if optinft == True:
        if colorrl <= len(color):
            Final = main[0].replace("-*.png",".png").replace("???", f"[B][COLOR={color[colorrl]}][SIZE=6]{key}[/SIZE][/COLOR][/B]").replace("mats", f"{url[0]}").replace("cmbs", f"{url[1]}").replace("lds", f"{url[2]}")
            colorrl += 1
        else:
            Final = main[0].replace("-*.png",".png").replace("???", f"{key}").replace("mats", f"{url[0]}").replace("cmbs", f"{url[1]}").replace("lds", f"{url[2]}")
    else:
        Final = main[0].replace("-*.png",".png").replace("???", f"{key}").replace("mats", f"{url[0]}").replace("cmbs", f"{url[1]}").replace("lds", f"{url[2]}")

    return key, Final, filedesc, rl, 1

myname = st.secrets['myname']
myrealname = st.secrets['myrealname']
mylap = st.secrets['mylap']
ips = st.secrets['ips']
allowed = True
addname = True
notmyname = True
notmyrealname = True
notmylap = True
tourname = True
exists = True
col1, col2, col3 = st.columns([1,1,5], gap="small")
with col1:
    if st.button("Compile", use_container_width=True):
        st.session_state.ip = st.context.ip_address
        if st.session_state.ip in ips:
            allowed = False
        elif st.session_state.smogon_name == "":
            addname = False
        elif st.session_state.smogon_name.lower().replace(" ","") in myname:
            notmyname = False
        elif st.session_state.smogon_name.lower().replace(" ","") in myrealname:
            notmyrealname = False
        elif st.session_state.smogon_name.lower().replace(" ","") in mylap:
            notmylap = False
        elif st.session_state.tournament_name == "":
            tourname = False
        elif not st.session_state.replays:
            exists = False
        else:
            st.session_state.processed_replays = 0
            st.session_state.processed_formats = 0
            st.session_state.all_bbcode = {}
            st.session_state.start = time.time()
            spoilerft = st.session_state.spoiler
            tourft = st.session_state.tournament_name
            roundft = st.session_state.round_name
            with tempfile.TemporaryDirectory() as td:
                st.session_state.ftime = datetime.now().strftime("%Y%m%d-%H%M%S")
                if st.session_state.round_name != "":
                    st.session_state.foldername = f"{st.session_state.tournament_name.lower().replace(" ","")}-{st.session_state.round_name.lower().replace(" ","")}-{st.session_state.smogon_name.lower().replace(" ","")}-{st.session_state.ftime}"
                else:
                    st.session_state.foldername = f"{st.session_state.tournament_name.lower().replace(" ","")}-{st.session_state.smogon_name.lower().replace(" ","")}-{st.session_state.ftime}"
                st.session_state.folder = Path(td)/st.session_state.foldername
                st.session_state.folder.mkdir(parents=True, exist_ok=True)
                st.session_state.a = ""
                for z in st.session_state.additional_usage:
                    if z == "Moves and Teammates":
                        st.session_state.a += f"[URL='https://raw.githubusercontent.com/LapplandO7/team-tour-stats-uploads/refs/heads/main/{st.session_state.foldername}/mats']{z}[/URL]"
                    elif z == "Combos":
                        st.session_state.a += f"[URL='https://raw.githubusercontent.com/LapplandO7/team-tour-stats-uploads/refs/heads/main/{st.session_state.foldername}/cmbs']{z}[/URL]"
                    elif z == "Leads":
                        st.session_state.a += f"[URL='https://raw.githubusercontent.com/LapplandO7/team-tour-stats-uploads/refs/heads/main/{st.session_state.foldername}/lds']{z}[/URL]"
                    st.session_state.a += " | "
                st.session_state.a = st.session_state.a[:-3]
                aft = st.session_state.a
                optinft = st.session_state.optin
                colorrlft = st.session_state.colorrl
                with ThreadPoolExecutor(max_workers=4) as executor:
                    output = list(executor.map(usages, st.session_state.replays.keys(), st.session_state.replays.values(), itertools.repeat(st.session_state.folder)))
                st.session_state.filedesc = {}
                for key, Final, filedesc, rl, l in output:
                    st.session_state.processed_replays += rl
                    st.session_state.processed_formats += 1
                    st.session_state.filedesc.update(filedesc)
                    st.session_state.all_bbcode[key] = Final
                    colorrl += l

                send = Github(auth=Auth.Token(lappland)).get_repo(f"LapplandO7/team-tour-stats-uploads")

                for i in st.session_state.folder.iterdir():
                    content = i.read_text(encoding="utf-8")

                    path = f"{st.session_state.foldername}/{i.name}"
                    
                    send.create_file(
                        path=path,
                        message=f"{st.session_state.filedesc[i.name]}",
                        content=content,
                        branch="main"
                    )
                    delay = random.uniform(0, 3.0)
                    time.sleep(delay)
                st.session_state.send = f"{st.session_state.ip} created <https://github.com/LapplandO7/team-tour-stats-uploads/tree/main/{st.session_state.foldername}>."
                murphy = {
                    "content" : st.session_state.send
                }
                headers = {
                    "Authorization" : authorization
                }
                res = requests.post(discord, murphy, headers=headers)

with col2:
    if st.button("Clear All", use_container_width=True):
        st.session_state.replays.clear()
        st.rerun()

if allowed == False:
    st.error("Access Denied!")
if addname == False:
    st.error("Please enter your Smogon name in the Prerequisites first.")
if notmyname == False:
    st.error("You are not Murphy Lawden! I don't even use this tool, well I do, but the python version of it. Anyways, use a different name.")
if notmyrealname == False:
    st.error("DUDE! WHY ARE YOU USING MY REAL NAME??? Use a different name.")
if notmylap == False:
    st.error("HEYYYY! THAT'S MY WAIFU! Use a different name.")
if tourname == False:
    st.error("Please add a project name in the Prerequisites first.")
if exists == False:
    st.error("No formats or replays available! Please add a format and replays first.")

st.session_state.final = []
if st.session_state.optin == True:
    st.session_state.final.append(f"[B][COLOR=rgb(160, 32, 240)][SIZE=7]{st.session_state.round_name.capitalize()} Usage[/SIZE][/COLOR][/B]")
    st.session_state.final.append("")
if st.session_state.all_bbcode:
    for i in st.session_state.replays.keys():
        if i in st.session_state.all_bbcode:
            st.session_state.final.append(st.session_state.all_bbcode[i])
            st.session_state.final.append("")

    if st.session_state.final:
        done = "\n".join(st.session_state.final)
        st.caption(f"Processed {st.session_state.processed_formats} formats and {st.session_state.processed_replays} replays.")
        if "start" in st.session_state and st.session_state.start is not None:
            if "complete" not in st.session_state:
                st.session_state.complete = time.time() - st.session_state.start
            st.caption(f"Time taken: {st.session_state.complete} seconds.")
        st.caption("BB Code:")
        st.code(done, language=None, height=300)
