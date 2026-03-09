import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="CGL Allocation Study Tool", layout="wide")

st.title("CGL Allocation Study Simulator")

st.info(
"This tool is created for study and analytical purposes only. "
"It is not affiliated with any government organisation."
)

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

# ---------------- USER MARK INPUT ---------------- #

st.subheader("Enter Your Marks")

col1,col2,col3,col4=st.columns(4)

with col1:
    user_main=st.number_input("Main Marks",0.0,390.0,310.0)

with col2:
    user_comp=st.number_input("Computer Marks",0.0,60.0,25.0)

with col3:
    user_cat=st.selectbox("Category",["UR","OBC","EWS","SC","ST"])

with col4:
    bonus_q=st.number_input("Expected Computer Bonus Questions",0,10,0)

bonus_marks=bonus_q*3

# ---------------- CPT INPUT ---------------- #

st.subheader("Expected CPT Cutoff")

c1,c2,c3,c4,c5=st.columns(5)

cpt_cutoff={
"UR":c1.number_input("UR",0,60,27),
"OBC":c2.number_input("OBC",0,60,24),
"EWS":c3.number_input("EWS",0,60,24),
"SC":c4.number_input("SC",0,60,21),
"ST":c5.number_input("ST",0,60,21)
}

# ---------------- DEST INPUT ---------------- #

typing_error=st.number_input("Expected DEST Typing Error %",0.0,20.0,3.0)

dest_pass = typing_error <= (5 if user_cat=="UR" else 7)

# ---------------- POSTS ---------------- #

posts=[

"ASO CSS",
"Income Tax Inspector",
"Inspector Examiner",
"Inspector Preventive Officer",
"Assistant Enforcement Officer",
"ASO MEA",
"ASO IB",
"Inspector Central Excise",
"Sub Inspector CBI",
"Executive Assistant CBIC",
"Section Head DGFT",
"Office Superintendent CBDT",
"Auditor CGDA",
"Accountant CAG",
"Tax Assistant CBDT",
"Tax Assistant CBIC"
]

# ---------------- POST PREFERENCE INPUT ---------------- #

st.subheader("Choose Your Post Preference Order")

pref=st.multiselect(
"Arrange posts in your preference order (top = most preferred)",
posts,
default=posts
)

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

# ---------------- VACANCY ---------------- #

vacancy={

"ASO CSS":{"UR":398,"OBC":265,"EWS":98,"SC":147,"ST":74},
"Income Tax Inspector":{"UR":188,"OBC":102,"EWS":30,"SC":55,"ST":37},
"Inspector Examiner":{"UR":68,"OBC":13,"EWS":14,"SC":18,"ST":24},
"Inspector Preventive Officer":{"UR":138,"OBC":91,"EWS":29,"SC":75,"ST":20},
"Assistant Enforcement Officer":{"UR":1,"OBC":13,"EWS":0,"SC":2,"ST":2},
"ASO MEA":{"UR":46,"OBC":30,"EWS":11,"SC":17,"ST":6},
"ASO IB":{"UR":100,"OBC":39,"EWS":15,"SC":24,"ST":19},
"Inspector Central Excise":{"UR":611,"OBC":269,"EWS":169,"SC":175,"ST":82},
"Sub Inspector CBI":{"UR":52,"OBC":18,"EWS":6,"SC":12,"ST":5},
"Executive Assistant CBIC":{"UR":89,"OBC":40,"EWS":18,"SC":24,"ST":12},
"Section Head DGFT":{"UR":22,"OBC":15,"EWS":5,"SC":10,"ST":5},
"Office Superintendent CBDT":{"UR":2709,"OBC":1791,"EWS":645,"SC":983,"ST":498},
"Auditor CGDA":{"UR":477,"OBC":316,"EWS":117,"SC":176,"ST":88},
"Accountant CAG":{"UR":86,"OBC":28,"EWS":18,"SC":31,"ST":17},
"Tax Assistant CBDT":{"UR":617,"OBC":347,"EWS":90,"SC":162,"ST":78},
"Tax Assistant CBIC":{"UR":256,"OBC":203,"EWS":94,"SC":136,"ST":82}

}

# ---------------- ALLOCATION ENGINE ---------------- #

computer_cutoff={"UR":18,"OBC":15,"EWS":15,"SC":12,"ST":12}

df_sim=df_sim.sort_values("Main Paper Marks",ascending=False).reset_index(drop=True)

df_sim["Post"]=None
df_sim["Allotted Category"]=None

for i,row in df_sim.iterrows():

    if row["Computer Marks"]<computer_cutoff[row["Category"]]:
        continue

    for p in pref:

        if vacancy[p]["UR"]>0:
            vacancy[p]["UR"]-=1
            df_sim.at[i,"Post"]=p
            df_sim.at[i,"Allotted Category"]="UR"
            break

        cat=row["Category"]

        if vacancy[p][cat]>0:
            vacancy[p][cat]-=1
            df_sim.at[i,"Post"]=p
            df_sim.at[i,"Allotted Category"]=cat
            break

df_sim["Rank"]=df_sim.index+1

# ---------------- USER RESULT ---------------- #

user=df_sim[df_sim["Name"]=="YOU"].iloc[0]

st.subheader("Prediction Result")

c1,c2,c3=st.columns(3)

c1.metric("Predicted Rank",user["Rank"])
c2.metric("Predicted Post",user["Post"])
c3.metric("Category",user["Allotted Category"])

# ---------------- CUT OFF TABLE ---------------- #

st.subheader("Expected Post Wise Cutoff")

cutoff_rows=[]

for p in posts:

    for cat in ["UR","OBC","EWS","SC","ST"]:

        subset=df_sim[(df_sim["Post"]==p)&(df_sim["Allotted Category"]==cat)]

        cutoff=subset["Main Paper Marks"].min() if len(subset)>0 else None

        cutoff_rows.append({
        "Post":p,
        "Category":cat,
        "Cutoff":cutoff
        })

cut_df=pd.DataFrame(cutoff_rows)

st.dataframe(cut_df)

# ---------------- DISTRIBUTION CHART ---------------- #

fig=px.histogram(df_sim,x="Main Paper Marks")

st.plotly_chart(fig,use_container_width=True)

st.dataframe(df_sim.head(500))
