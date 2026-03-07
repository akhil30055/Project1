import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SSC CGL 2025 Predictor", layout="wide")

st.title("SSC CGL 2025 Final Vacancy Predictor")

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

st.subheader("Enter Your Details")

c1,c2,c3,c4=st.columns(4)

with c1:
    user_main=st.number_input("Main Marks",0.0,390.0,310.0)

with c2:
    user_comp=st.number_input("Computer Marks",0.0,60.0,25.0)

with c3:
    user_cat=st.selectbox("Category",["UR","OBC","EWS","SC","ST"])

with c4:
    bonus_q=st.number_input("Computer Bonus Questions",0,10,0)

bonus_marks=bonus_q*3

# ---------------- CPT CUTOFF INPUT ---------------- #

st.subheader("Expected CPT Cutoff")

c1,c2,c3,c4,c5=st.columns(5)

with c1:
    cpt_ur=st.number_input("UR CPT Cutoff",0,60,27)

with c2:
    cpt_obc=st.number_input("OBC CPT Cutoff",0,60,24)

with c3:
    cpt_ews=st.number_input("EWS CPT Cutoff",0,60,24)

with c4:
    cpt_sc=st.number_input("SC CPT Cutoff",0,60,21)

with c5:
    cpt_st=st.number_input("ST CPT Cutoff",0,60,21)

cpt_cutoff={
"UR":cpt_ur,
"OBC":cpt_obc,
"EWS":cpt_ews,
"SC":cpt_sc,
"ST":cpt_st
}

# ---------------- DEST INPUT ---------------- #

st.subheader("DEST Typing Error")

typing_error=st.number_input("Expected Typing Error %",0.0,20.0,3.0)

if user_cat=="UR":
    dest_pass=typing_error<=5
else:
    dest_pass=typing_error<=7

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

# ---------------- FINAL VACANCIES ---------------- #

vacancies=[

("Inspector Examiner",68,18,24,13,14,"CPT"),
("Inspector Preventive Officer",138,75,20,91,29,"CPT"),
("Inspector Central Excise",611,175,82,269,169,"CPT"),
("ASO MEA",46,17,6,30,11,"CPT"),
("ASO CSS",398,147,74,265,98,"CPT"),
("ASO AFHQ",81,22,9,27,15,"CPT"),
("Executive Assistant CBIC",89,24,12,40,18,"CPT"),
("Assistant TRAI",9,2,0,0,0,"CPT"),
("Assistant Mines",11,2,2,3,4,"CPT"),
("Section Head DGFT",22,10,5,15,5,"CPT"),
("Assistant Commerce",2,0,0,0,0,"CPT"),

("Tax Assistant CBIC",256,136,82,203,94,"DEST"),
("UDC Narcotics",12,2,0,5,2,"DEST"),
("UDC MeitY",5,1,1,2,1,"DEST"),
("Tax Assistant CBDT",617,162,78,347,90,"DEST"),

("Income Tax Inspector",188,55,37,102,30,"NONE"),
("Sub Inspector CBI",52,12,5,18,6,"NONE"),
("Inspector Narcotics",1,1,0,1,1,"NONE"),
("ASO IB",100,24,19,39,15,"NONE"),
("ASO Railways",23,4,4,14,3,"NONE"),
("Assistant EPFO",36,17,5,30,6,"NONE"),
("Assistant Enforcement Officer",1,2,2,13,0,"NONE"),
("Office Superintendent CBDT",2709,983,498,1791,645,"NONE"),

("Auditor CGDA",477,176,88,316,117,"NONE"),
("Accountant CAG",86,31,17,28,18,"NONE"),
("Accountant Posts",42,13,6,12,3,"NONE"),
("Accountant CGCA",15,6,3,9,3,"NONE"),

]

# ---------------- ALLOCATION ENGINE ---------------- #

computer_cutoff={"UR":18,"OBC":15,"EWS":15,"SC":12,"ST":12}

df_sim=df_sim.sort_values("Main Paper Marks",ascending=False).reset_index(drop=True)

df_sim["Post"]=None
df_sim["Allotted Category"]=None

vac=[]

for v in vacancies:

    vac.append({
    "Post":v[0],
    "UR":v[1],
    "SC":v[2],
    "ST":v[3],
    "OBC":v[4],
    "EWS":v[5],
    "Test":v[6]
    })

for i,row in df_sim.iterrows():

    if row["Computer Marks"]<computer_cutoff[row["Category"]]:
        continue

    for post in vac:

        # CPT posts
        if post["Test"]=="CPT":
            if row["Computer Marks"]<cpt_cutoff[row["Category"]]:
                continue

        # DEST posts
        if post["Test"]=="DEST":
            if not dest_pass:
                continue

        if post["UR"]>0:

            post["UR"]-=1
            df_sim.at[i,"Post"]=post["Post"]
            df_sim.at[i,"Allotted Category"]="UR"
            break

        cat=row["Category"]

        if post[cat]>0:

            post[cat]-=1
            df_sim.at[i,"Post"]=post["Post"]
            df_sim.at[i,"Allotted Category"]=cat
            break

df_sim["Rank"]=df_sim.index+1

user=df_sim[df_sim["Name"]=="YOU"].iloc[0]

# ---------------- RESULT ---------------- #

st.subheader("Prediction")

c1,c2,c3=st.columns(3)

c1.metric("Predicted Rank",user["Rank"])
c2.metric("Predicted Post",user["Post"])
c3.metric("Category",user["Allotted Category"])

fig=px.histogram(df_sim,x="Main Paper Marks")
st.plotly_chart(fig,use_container_width=True)

st.dataframe(df_sim.head(500))
