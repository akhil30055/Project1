import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SSC CGL Real Predictor", layout="wide")

st.title("SSC CGL 2025 Real Allocation + CPT Cutoff Predictor")

# =========================
# LOAD DATA
# =========================

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/akhil30055/Cglscoresheets/refs/heads/main/cgl-data.json"
    df = pd.read_json(url)
    df["Main Paper Marks"] = pd.to_numeric(df["Main Paper Marks"], errors="coerce")
    df["Computer Marks"] = pd.to_numeric(df["Computer Marks"], errors="coerce")
    df = df.dropna(subset=["Main Paper Marks","Computer Marks","Category"])
    return df

df = load_data()

st.success(f"Loaded {len(df)} candidates")

# =========================
# USER INPUT
# =========================

st.subheader("Enter Your Marks")

col1,col2,col3,col4 = st.columns(4)

with col1:
    user_main = st.number_input("Main Marks",0.0,390.0,310.0)

with col2:
    user_comp = st.number_input("Computer Marks",0.0,60.0,25.0)

with col3:
    user_cat = st.selectbox("Category",["UR","OBC","EWS","SC","ST"])

with col4:
    bonus_q = st.number_input("Expected Computer Bonus Questions",0,10,0)

bonus_marks = bonus_q * 3
st.info(f"Computer bonus applied: +{bonus_marks} marks")

# ST Data Warning
if df["Category"].value_counts().get(user_cat,0) < 500:
    st.warning(f"{user_cat} students data is lesser so prediction may show some errors.")

# =========================
# APPLY BONUS
# =========================

df_sim = df.copy()
df_sim["Computer Marks"] += bonus_marks
user_comp += bonus_marks

user_row = pd.DataFrame({
"Name":["YOU"],
"Main Paper Marks":[user_main],
"Computer Marks":[user_comp],
"Category":[user_cat]
})

df_sim = pd.concat([df_sim,user_row],ignore_index=True)

# =========================
# COMPUTER QUALIFICATION
# =========================

comp_cutoff = {"UR":18,"OBC":15,"EWS":15,"SC":12,"ST":12}

df_sim["Comp_Qualified"] = df_sim.apply(
    lambda x: x["Computer Marks"] >= comp_cutoff[x["Category"]],
    axis=1
)

# =========================
# CPT POSTS VACANCY (Level 7 + CPT Level 6)
# =========================

cpt_posts = {

"CSS ASO":{"UR":273,"SC":104,"ST":52,"OBC":185,"EWS":68},
"Income Tax Inspector":{"UR":176,"SC":52,"ST":39,"OBC":95,"EWS":27},
"Inspector Central Excise":{"UR":611,"SC":175,"ST":82,"OBC":269,"EWS":169},
"Inspector Preventive Officer":{"UR":138,"SC":75,"ST":20,"OBC":91,"EWS":29},
"Inspector Examiner":{"UR":68,"SC":18,"ST":24,"OBC":13,"EWS":14}

}

# =========================
# CPT CUTOFF ENGINE
# =========================

st.subheader("CPT Post Cutoff Simulation")

df_cpt = df_sim[df_sim["Comp_Qualified"]==True].copy()
df_cpt = df_cpt.sort_values("Main Paper Marks",ascending=False)

cutoff_result = {}

for post,vacancy in cpt_posts.items():

    vacancy_copy = vacancy.copy()
    selected = []

    for _,row in df_cpt.iterrows():

        cat = row["Category"]

        if vacancy_copy["UR"]>0:
            vacancy_copy["UR"]-=1
            selected.append(row)

        elif vacancy_copy[cat]>0:
            vacancy_copy[cat]-=1
            selected.append(row)

        if sum(vacancy_copy.values())==0:
            break

    if len(selected)>0:
        selected_df = pd.DataFrame(selected)
        cutoff = selected_df.groupby("Category")["Main Paper Marks"].min().to_dict()
        cutoff_result[post]=cutoff

# Display Cutoff Table

cutoff_table = []

for post,data in cutoff_result.items():
    row = {"Post":post}
    for cat in ["UR","OBC","EWS","SC","ST"]:
        row[cat] = data.get(cat,"-")
    cutoff_table.append(row)

cutoff_df = pd.DataFrame(cutoff_table)

st.dataframe(cutoff_df,use_container_width=True)

# =========================
# USER RANK
# =========================

df_sim = df_sim.sort_values("Main Paper Marks",ascending=False).reset_index(drop=True)
df_sim["Rank"]=df_sim.index+1

user = df_sim[df_sim["Name"]=="YOU"].iloc[0]

st.subheader("Your Position")

c1,c2 = st.columns(2)

c1.metric("Predicted Rank",user["Rank"])
c2.metric("Computer Qualified","Yes" if user["Comp_Qualified"] else "No")

# =========================
# DISTRIBUTION GRAPH
# =========================

fig = px.histogram(df_sim,x="Main Paper Marks",title="Marks Distribution")
st.plotly_chart(fig,use_container_width=True)

# =========================
# TABLE
# =========================

st.subheader("Top 500 Candidates")
st.dataframe(df_sim.head(500),use_container_width=True)
