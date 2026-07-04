import streamlit as st
import re

st.set_page_config(
    page_title="ReplaysText",
    layout="wide"
)

teams_tags = {}
formats = []
Output = []

def team_test(x):
    teams = []
    for key in teams_tags:
            team = re.search(rf'\b{key}\b', x)
            if team:
                teams.append((team.start(), team.group()))
    return [name for index, name in sorted(teams)]

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Replays TextBlock Generator:")

if "output" not in st.session_state:
    st.session_state.output = ""
if st.session_state.get('clear'):
    st.session_state['block'] = ''
    st.session_state.output = ""
if st.session_state.get('streamlit'):
    st.session_state['block'] = 'generate'


Block = st.text_area("Enter Replay Text Block Here...", value=st.session_state.get("links", ""), key="block", height=200)

col1, col2, _ = st.columns([1, 1])

with col1:
    if st.button("Generate", key='generate', use_container_width=True):
        for i in Block.splitlines():
            b = re.findall(r'^([^:]+):',i)
            if b:
                if b[0].strip() not in formats:
                    formats.append(b[0].strip())

        teams = []

        x = re.findall(r"^(.+?)\s*\(\d+\)\s+vs\s+\(\d+\)\s*(.+)$", Block, re.MULTILINE)
        for y in x:
            u1 = re.sub(r":[^:]+:", "", y[0])
            v1 = re.sub(r"[^a-zA-Z0-9\s]", "", u1).strip()
            if v1 not in teams:
                teams.append(v1)
            u2 = re.sub(r":[^:]+:", "", y[1])
            v2 = re.sub(r"[^a-zA-Z0-9\s]", "", u2).strip()
            if v2 not in teams:
                teams.append(v2)

        k = ""
        for t in teams:
            n = t.split()[:2]
            if len(n) == 1:
                k = t[:2].upper()
                j = f"[{k}]"
                if j not in teams_tags.values():
                    teams_tags[t] = j
                else:
                    k = k[0]
                    for x in t[1:]:
                        k += x.upper()
                        j = f"[{k}]"
                        if j not in teams_tags.values():
                            teams_tags[t] = j
                            break
                        else:
                            k = k[0]
                    else:
                        teams_tags.clear()
                        for t in teams:
                            n = t.split()
                            if len(n) == 1:
                                k = t[:3].upper()
                                j = f"[{k}]"
                                if j not in teams_tags.values():
                                    teams_tags[t] = j
                                else:
                                    k = k[0]
                                    for l, q in zip(t[1:], t[2:]):
                                        k += (l+q).upper()
                                        j = f"[{k}]"
                                        if j not in teams_tags.values():
                                            teams_tags[t] = j
                                            break
                                        else:
                                            k = k[0]
                                            k += (q+l).upper()
                                            j = f"[{k}]"
                                            if j not in teams_tags.values():
                                                teams_tags[t] = j
                                                break
                                            else:
                                                k = k[0] # I am really fucking sure 99.99% of English Words are not coming this far...
            elif len(n) == 2:
                k = n[0][0].upper()
                if teams_tags:
                    rl = len(next(iter(teams_tags.values())))
                    rll = rl - 2
                elif not teams_tags:
                    rll = 2
                if rll == 2:
                    for i in n[1]:
                        k += i.upper()
                        j = f"[{k}]"
                        if j not in teams_tags.values():
                            teams_tags[t] = j
                            break
                        else:
                            k = n[0][0].upper()
                else:
                    teams_tags.clear()
                    for t in teams:
                        n = t.split()[:2]
                        if len(n) == 1:
                            k = t[:2].upper()
                            j = f"[{k}]"
                            if j not in teams_tags.values():
                                teams_tags[t] = j
                            else:
                                k = k[0]
                                for x in t[1:]:
                                    k += x.upper()
                                    j = f"[{k}]"
                                    if j not in teams_tags.values():
                                        teams_tags[t] = j
                                        break
                                    else:
                                        k = k[0]
                                else:
                                    teams_tags.clear()
                                    for t in teams:
                                        n = t.split()
                                        if len(n) == 1:
                                            k = t[:3].upper()
                                            j = f"[{k}]"
                                            if j not in teams_tags.values():
                                                teams_tags[t] = j
                                            else:
                                                k = k[0]
                                                for l, q in zip(t[1:], t[2:]):
                                                    k += (l+q).upper()
                                                    j = f"[{k}]"
                                                    if j not in teams_tags.values():
                                                        teams_tags[t] = j
                                                        break
                                                    else:
                                                        k = k[0]
                                                        k += (q+l).upper()
                                                        j = f"[{k}]"
                                                        if j not in teams_tags.values():
                                                            teams_tags[t] = j
                                                            break
                                                        else:
                                                            k = k[0]
                        elif len(n) == 2:                  
                            k = n[0][0].upper()
                            for l, q in zip(n[1][0:], n[1][1:]):
                                k += (l+q).upper()
                                j = f"[{k}]"
                                if j not in teams_tags.values():
                                    teams_tags[t] = j
                                    break
                                else:
                                    k = n[0][0].upper()
                                    k += (q+l).upper()
                                    j = f"[{k}]"
                                    if j not in teams_tags.values():
                                        teams_tags[t] = j
                                        break
                                    else:
                                        k = n[0][0].upper()

        matchups = re.findall(r".+\(\d+\)\s+vs\s+\(\d+\).+(?:\n.+)*", Block)

        for key in formats:
            store2 = key
            Output.append(store2)
            for x in matchups:
                u = re.sub(r":[^:]+:", "", x)
                v = re.sub(r"[^a-zA-Z0-9\s]", "", u).strip()
                teams = team_test(v)
                if len(teams)==2:
                    t1 = teams_tags[teams[0]]
                    t2 = teams_tags[teams[1]]
                    f = re.findall(rf'(?i){re.escape(key)}:\s*(.*)', x)                    
                    for j in f:
                        store3 = f'{t1} {j.strip()} {t2}'
                        Output.append(store3)

            Output.append("")

        st.session_state.output = "\n".join(Output)

with col2:
    st.button('Clear', key='clear', use_container_width=True)

st.caption("ReplayStat Block:")
st.code(st.session_state.output, language=None, height=300)
