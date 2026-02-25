import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="SSC CGL Real Predictor", layout="wide")

st.title("SSC CGL 2025 Real Allocation Predictor")

# =========================
# LOAD DATA FROM GITHUB
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

st.success(f"Loaded {len(df)} candidates from GitHub dataset")

# =========================
# USER INPUT ON MAIN PAGE
# =========================

st.subheader("Enter Your Marks")

col1, col2, col3, col4 = st.columns(4)

with col1:
    user_main = st.number_input("Main Paper Marks",0.0,390.0,310.0)

with col2:
    user_comp = st.number_input("Computer Marks",0.0,60.0,25.0)

with col3:
    user_cat = st.selectbox("Category",["UR","OBC","EWS","SC","ST"])

with col4:
    bonus_q = st.number_input("Expected Computer Bonus Questions",0,10,0)

bonus_marks = bonus_q * 3

st.info(f"Computer bonus applied: +{bonus_marks} marks")

# =========================
# APPLY BONUS
# =========================

df_sim = df.copy()

df_sim["Computer Marks"] += bonus_marks
user_comp += bonus_marks

# Insert user

user_row = pd.DataFrame({
"Name":["YOU"],
"Main Paper Marks":[user_main],
"Computer Marks":[user_comp],
"Category":[user_cat]
})

df_sim = pd.concat([df_sim,user_row],ignore_index=True)

# =========================
# FULL VACANCY LIST
# =========================

vacancies = [

("L7","Inspector Examiner",68,18,24,13,14),
("L7","Inspector Preventive Officer",138,75,20,91,29),
("L7","Assistant EPFO",36,17,5,30,6),
("L7","Inspector Central Excise",611,175,82,269,169),
("L7","Assistant Enforcement Officer",1,2,2,13,0),
("L7","ASO NIC",2,0,0,0,1),
("L7","ASO CAT",0,0,0,0,1),
("L7","Inspector Narcotics",1,1,0,1,1),
("L7","ASO MEA",44,13,0,33,10),
("L7","ASO Election Commission",0,0,0,5,1),
("L7","ASO MeitY",2,0,1,0,0),
("L7","ASO IB",100,24,19,39,15),
("L7","Sub Inspector CBI",52,12,5,18,6),
("L7","ASO Railways",23,4,4,14,3),
("L7","Income Tax Inspector",176,52,39,95,27),
("L7","ASO CSS",273,104,52,185,68),

("L6","Executive Assistant CBIC",89,24,12,40,18),
("L6","Assistant ED",0,0,0,3,0),
("L6","Statistical Investigator",50,18,12,28,10),
("L6","Assistant TRAI",2,1,0,0,0),
("L6","Assistant Official Language",4,0,0,1,0),
("L6","Assistant MCA",0,1,0,0,0),
("L6","Assistant Mines",11,2,2,3,4),
("L6","Assistant Textiles",1,0,0,0,0),
("L6","Assistant Coast Guard",8,3,1,5,1),
("L6","Junior Statistical Officer",124,47,15,36,27),
("L6","Assistant DFSS",1,0,0,1,1),
("L6","Assistant NCB",7,1,1,2,0),
("L6","Sub Inspector NCB",10,3,4,8,5),
("L6","Sub Inspector NIA",6,2,1,3,2),
("L6","Assistant MoSPI",0,0,0,2,0),
("L6","Office Superintendent CBDT",2766,1012,496,1822,657),

("L5","Accountant CAG",86,31,17,28,18),
("L5","Auditor CGDA",477,176,88,316,117),
("L5","Accountant Posts",42,13,6,12,3),
("L5","Accountant CGCA",15,6,3,9,3),

("L4","UDC MSME",25,4,5,16,5),
("L4","Tax Assistant CBIC",256,136,82,203,94),
("L4","UDC Science Tech",24,9,4,16,6),
("L4","UDC Narcotics",12,2,0,5,2),
("L4","Sub Inspector Narcotics",11,2,0,6,0),
("L4","UDC Mines",13,2,3,4,4),
("L4","UDC DGDE",7,2,1,3,1),
("L4","UDC MeitY",5,1,1,2,1),
("L4","UDC Textiles",4,0,1,1,2),
("L4","UDC Water Resources",5,0,0,0,0),
("L4","UDC BRO",20,1,0,0,4),
("L4","UDC Agriculture",2,0,0,0,1),
("L4","UDC Health",1,0,0,0,0),
("L4","Tax Assistant CBDT",572,171,80,340,86),

]

# =========================
# ALLOCATION ENGINE
# =========================

computer_cutoff={"UR":18,"OBC":15,"EWS":15,"SC":12,"ST":12}

df_sim = df_sim.sort_values("Main Paper Marks",ascending=False).reset_index(drop=True)

df_sim["Post"]=None
df_sim["Allotted Category"]=None

vac=[]

for v in vacancies:

    vac.append({
    "Post":v[1],
    "UR":v[2],
    "SC":v[3],
    "ST":v[4],
    "OBC":v[5],
    "EWS":v[6]
    })

for i,row in df_sim.iterrows():

    if row["Computer Marks"] < computer_cutoff[row["Category"]]:
        continue

    for post in vac:

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

# =========================
# RESULT DISPLAY
# =========================

st.subheader("Prediction Result")

c1,c2,c3=st.columns(3)

c1.metric("Predicted Rank",user["Rank"])
c2.metric("Predicted Post",user["Post"])
c3.metric("Allotted Category",user["Allotted Category"])

# Graph

fig=px.histogram(df_sim,x="Main Paper Marks",title="Marks Distribution")

st.plotly_chart(fig,use_container_width=True)

# Table

st.subheader("Top 500 Allocation- Level 7 post allocation not accurate CPT Cut off not considering")

st.dataframe(df_sim.head(500),use_container_width=True)


