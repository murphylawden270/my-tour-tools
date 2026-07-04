import streamlit as st
import random
import re

st.set_page_config(
    page_title="Schedule Maker",
    layout="wide"
)

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

st.title("Schedule Maker For Team Tournaments:")

if "output" not in st.session_state:
    st.session_state.output = ""

warn = []

teams = st.text_area("Enter Team Names Here (e.g. :Groudon-Primal: Desolation Groudons :Groudon-Primal:)", value=st.session_state.get("links", ""), key="links", height=200)

if st.button("Generate Schedule"):
    team_icon_pair = {}

    teams_with_icons = []
    for line in teams.split("\n"):
        clean = line.strip()
        if clean:
            teams_with_icons.append(clean)

    if len(teams_with_icons)%2 !=0:
        teams_with_icons.append("Bye")
        team_icon_pair["Bye"] = ""     

    teams = []
    for i in teams_with_icons:
        if re.search(r':([^:]+):', i, re.IGNORECASE):
            removed_icon = re.findall(r':[\w-]+:', i, re.IGNORECASE)         
            if len(removed_icon) == 1:
                icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                team_icon_pair[icon_removed_team.strip()] = removed_icon[0]
                teams.append(icon_removed_team.strip())                        
            elif removed_icon[0].lower() != removed_icon[1].lower():
                icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                team_icon_pair[icon_removed_team.strip()] = ""
                teams.append(icon_removed_team.strip())
                warn.append(f'**WARNING!** Team icon {removed_icon[0]} and {removed_icon[1]} do not match!\nNo icon was printed for {icon_removed_team.strip()}.')
            elif removed_icon[0].lower() == removed_icon[1].lower() and len(removed_icon) == 2:
                icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                team_icon_pair[icon_removed_team.strip()] = removed_icon[0]
                teams.append(icon_removed_team.strip())
            elif removed_icon[0].lower() == removed_icon[1].lower() and len(removed_icon) >= 3:
                icon_removed_team = re.sub(r':[\w-]+:', '', i, flags=re.IGNORECASE)
                team_icon_pair[icon_removed_team.strip()] = removed_icon[0]
                teams.append(icon_removed_team.strip())
                warn.append(f'**WARNING!** More than two icons detected in {icon_removed_team.strip()}!\nHowever, the first two icons were the same. Therefore, they were used.')        
        else:
            team_icon_pair[i.strip()] = ""
            teams.append(i.strip()) 

    pair = []
    matchup = []
    matchups = []
    reply = []

    for j in range(0,len(teams)-1):
        for l in range(len(teams)//2):
            pair.append(teams[l])
            pair.append(teams[len(teams)-l-1])
            random.shuffle(pair)
            matchup.append(pair)
            random.shuffle(matchup)
            pair = []
        matchups.append(matchup)
        matchup = []
        move = teams[len(teams)-1]
        for i in range(len(teams)-1,0,-1):
            teams[i] = teams[i-1]
        teams[i] = move

    for week, i in enumerate(matchups, start=1):
        zaweek = f'Week {week}'
        reply.append(zaweek)
        for j in i:
            zamatchup = f'{team_icon_pair[j[0]]}{j[0]} vs {j[1]}{team_icon_pair[j[1]]}'
            reply.append(zamatchup)
        reply.append("")

    st.session_state.output = "\n".join(reply)

if warn:
    st.code("\n".join(warn))

st.caption("Schedules:")
st.code(st.session_state.output, language=None, height=300)
