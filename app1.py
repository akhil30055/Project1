import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SSC CGL Predictor", layout="wide")

st.title("SSC CGL 2025 Smart Allocation Predictor")

# ---------------- LOAD DATA ---------------- #

@st.cache_data
def load_data():
    url="https://raw.githubusercontent.com/akhil30055/Cglscoresheets/refs/heads/main/cgl-data.json"
    df=pd.read_json(url)

    df["Main Paper Marks"]=pd.to_numeric(df["Main Paper Marks"],errors="coerce")
    df["Computer Marks"]=pd.to_numeric(df["Computer Marks"],errors="coerce")

    df=df.dropna(subset=["Main Paper Marks","Computer Marks","Category"])

    return df

df=load_data()

st.success(f"Loaded {len(df)} candidates")

# ---------------- USER INPUT ---------------- #

st.subheader("Enter Your Marks")

c1,c2,c3,c4=st.columns(4)

with c1:
    user_main=st.number_input("Main Marks",0.0,390.0,310.0)

with c2:
    user_comp=st.number_input("Computer Marks",0.0,60.0,25.0)

with c3:
    user_cat=st.selectbox("Category",["UR","OBC","EWS","SC","ST"])

with c4:
    bonus_q=st.number_input("Expected Computer Bonus Questions",0,10,0)

bonus_marks=bonus_q*3

# ---------------- CPT CUT OFF ---------------- #

st.subheader("Expected CPT Cutoff")

c1,c2,c3,c4,c5=st.columns(5)

cpt_cutoff={
"UR":c1.number_input("UR",0,60,27),
"OBC":c2.number_input("OBC",0,60,24),
"EWS":c3.number_input("EWS",0,60,24),
"SC":c4.number_input("SC",0,60,21),
"ST":c5.number_input("ST",0,60,21)
}

# ---------------- DEST ---------------- #

typing_error=st.number_input("Expected DEST Typing Error %",0.0,20.0,3.0)

dest_pass = typing_error <= (5 if user_cat=="UR" else 7)

# ---------------- APPLY BONUS ---------------- #

df_sim=df.copy()

df_sim["Computer Marks"]+=bonus_marks
user_comp+=bonus_marks

user_row=pd.DataFrame({
"Name":["YOU"],
"Main Paper Marks":[user_main],
"Computer Marks":[user_comp],
"Category":[user_cat]
})

df_sim=pd.concat([df_sim,user_row],ignore_index=True)

# ---------------- POST STRUCTURE ---------------- #

posts=[

("L7","ASO CSS",398,147,74,265,98,"CPT"),
("L7","Income Tax Inspector",188,55,37,102,30,"NONE"),
("L7","Inspector Examiner",68,18,24,13,14,"CPT"),
("L7","Inspector Preventive Officer",138,75,20,91,29,"CPT"),
("L7","Assistant Enforcement Officer",1,2,2,13,0,"NONE"),
("L7","ASO MEA",46,17,6,30,11,"CPT"),
("L7","ASO IB",100,24,19,39,15,"NONE"),
("L7","Inspector Central Excise",611,175,82,269,169,"CPT"),
("L7","Sub Inspector CBI",52,12,5,18,6,"NONE"),

("L6","Executive Assistant CBIC",89,24,12,40,18,"CPT"),
("L6","Section Head DGFT",22,10,5,15,5,"CPT"),
("L6","Assistant Commerce",2,0,0,0,0,"CPT"),
("L6","Office Superintendent CBDT",2709,983,498,1791,645,"NONE"),

("L5","Auditor CGDA",477,176,88,316,117,"NONE"),
("L5","Accountant CAG",86,31,17,28,18,"NONE"),

("L4","Tax Assistant CBDT",617,162,78,347,90,"DEST"),
("L4","Tax Assistant CBIC",256,136,82,203,94,"DEST")
]

computer_cutoff={"UR":18,"OBC":15,"EWS":15,"SC":12,"ST":12}

# ---------------- ALLOCATION FUNCTION ---------------- #

def run_allocation(df_base,cpt_cut):

    df_alloc=df_base.copy()
    df_alloc=df_alloc.sort_values("Main Paper Marks",ascending=False).reset_index(drop=True)

    df_alloc["Post"]=None
    df_alloc["Allotted Category"]=None

    vacancies=[]

    for p in posts:
        vacancies.append({
        "Level":p[0],
        "Post":p[1],
        "UR":p[2],
        "SC":p[3],
        "ST":p[4],
        "OBC":p[5],
        "EWS":p[6],
        "Test":p[7]
        })

    for i,row in df_alloc.iterrows():

        if row["Computer Marks"] < computer_cutoff[row["Category"]]:
            continue

        for post in vacancies:

            if post["Test"]=="CPT":
                if row["Computer Marks"] < cpt_cut[row["Category"]]:
                    continue

            if post["Test"]=="DEST":
                if not dest_pass:
                    continue

            if post["UR"]>0:
                post["UR"]-=1
                df_alloc.at[i,"Post"]=post["Post"]
                df_alloc.at[i,"Allotted Category"]="UR"
                break

            cat=row["Category"]

            if post[cat]>0:
                post[cat]-=1
                df_alloc.at[i,"Post"]=post["Post"]
                df_alloc.at[i,"Allotted Category"]=cat
                break

    df_alloc["Rank"]=df_alloc.index+1

    return df_alloc


# ---------------- THREE SCENARIOS ---------------- #

real_df = run_allocation(df_sim,cpt_cutoff)

opt_cpt={k:v-2 for k,v in cpt_cutoff.items()}
optimistic_df = run_allocation(df_sim,opt_cpt)

worst_cpt={k:v+2 for k,v in cpt_cutoff.items()}
worst_df = run_allocation(df_sim,worst_cpt)

# ---------------- USER RESULT ---------------- #

user=real_df[real_df["Name"]=="YOU"].iloc[0]

st.subheader("Prediction")

c1,c2,c3=st.columns(3)

c1.metric("Predicted Rank",user["Rank"])
c2.metric("Predicted Post",user["Post"])
c3.metric("Allotted Category",user["Allotted Category"])

# ---------------- CUT OFF CALCULATION ---------------- #

def cutoff_table(df):

    rows=[]

    for post in df["Post"].dropna().unique():

        for cat in ["UR","OBC","EWS","SC","ST"]:

            subset=df[(df["Post"]==post) & (df["Allotted Category"]==cat)]

            cutoff=subset["Main Paper Marks"].min() if len(subset)>0 else None

            rows.append({
            "Post":post,
            "Category":cat,
            "Cutoff":cutoff
            })

    return pd.DataFrame(rows)

opt_cut=cutoff_table(optimistic_df)
real_cut=cutoff_table(real_df)
worst_cut=cutoff_table(worst_df)

st.subheader("Expected Post Wise Cutoff")

tabs=st.tabs(["Optimistic","Realistic","Worst Case"])

with tabs[0]:
    st.dataframe(opt_cut)

with tabs[1]:
    st.dataframe(real_cut)

with tabs[2]:
    st.dataframe(worst_cut)

# ---------------- CHART ---------------- #

fig=px.histogram(real_df,x="Main Paper Marks")

st.plotly_chart(fig,use_container_width=True)

st.dataframe(real_df.head(500))
