import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io

st.set_page_config(layout="wide")

# ---------------- LOAD DATA ---------------- #

@st.cache_data
def load_data(file):

    df = pd.read_csv(file, encoding="latin1", on_bad_lines="skip")

    df["Main Paper Marks"] = pd.to_numeric(df["Main Paper Marks"], errors="coerce")
    df["Computer Marks"] = pd.to_numeric(df["Computer Marks"], errors="coerce")

    df = df.dropna(subset=["Main Paper Marks","Computer Marks","Category"])

    return df


# ---------------- FULL OFFICIAL VACANCY ---------------- #

def get_all_vacancies():

    return [

("L7","Inspector Examiner",68,18,24,13,14),
("L7","Inspector Preventive",138,75,20,91,29),
("L7","EPFO ASO",36,17,5,30,6),
("L7","Inspector Excise",611,175,82,269,169),
("L7","AEO ED",1,2,2,13,0),
("L7","NIC ASO",2,0,0,0,1),
("L7","CAT ASO",0,0,0,0,1),
("L7","CBN Inspector",1,1,0,1,1),
("L7","MEA ASO",44,13,0,33,10),
("L7","ECI ASO",0,0,0,5,1),
("L7","Meity ASO",2,0,1,0,0),
("L7","IB ASO",100,24,19,39,15),
("L7","CBI SI",52,12,5,18,6),
("L7","Railway ASO",23,4,4,14,3),
("L7","Income Tax Inspector",176,52,39,95,27),
("L7","CSS ASO",273,104,52,185,68),

("L6","Executive Assistant",89,24,12,40,18),
("L6","Assistant ED",0,0,0,3,0),
("L6","Stat Investigator",50,18,12,28,10),
("L6","Assistant TRAI",2,1,0,0,0),
("L6","Assistant Language",4,0,0,1,0),
("L6","Assistant MCA",0,1,0,0,0),
("L6","Assistant Mines",11,2,2,3,4),
("L6","Assistant Textiles",1,0,0,0,0),
("L6","Assistant Coast Guard",8,3,1,5,1),
("L6","JSO",124,47,15,36,27),
("L6","Assistant DFSS",1,0,0,1,1),
("L6","ASO NCB",7,1,1,2,0),
("L6","SI NCB",10,3,4,8,5),
("L6","SI NIA",6,2,1,3,2),
("L6","Assistant MOSPI",0,0,0,2,0),
("L6","Office Superintendent",2766,1012,496,1822,657),

("L5","Accountant CAG",86,31,17,28,18),
("L5","Auditor CGDA",477,176,88,316,117),
("L5","Accountant Post",42,13,6,12,3),
("L5","Accountant CGCA",15,6,3,9,3),

("L4","UDC MSME",25,4,5,16,5),
("L4","Tax Assistant CBIC",256,136,82,203,94),
("L4","UDC Science",24,9,4,16,6),
("L4","UDC Narcotics",12,2,0,5,2),
("L4","SI Narcotics",11,2,0,6,0),
("L4","UDC Mines",13,2,3,4,4),
("L4","UDC DGDE",7,2,1,3,1),
("L4","UDC Meity",5,1,1,2,1),
("L4","UDC Textiles",4,0,1,1,2),
("L4","UDC Water",5,0,0,0,0),
("L4","UDC BRO",20,1,0,0,4),
("L4","UDC Agriculture",2,0,0,0,1),
("L4","UDC Health",1,0,0,0,0),
("L4","Tax Assistant CBDT",572,171,80,340,86),

    ]


# ---------------- REAL SSC ENGINE ---------------- #

def allocate(df, vacancies):

    computer_cut = {"UR":18,"OBC":15,"EWS":15,"SC":12,"ST":12}

    df = df.sort_values("Main Paper Marks", ascending=False).reset_index(drop=True)

    df["Post"]=None
    df["Allotted_Category"]=None

    vacancy_dict=[]

    for v in vacancies:

        level,post,ur,sc,st,obc,ews=v

        vacancy_dict.append({
            "Level":level,
            "Post":post,
            "UR":ur,
            "OBC":obc,
            "EWS":ews,
            "SC":sc,
            "ST":st
        })

    for i,row in df.iterrows():

        if row["Computer Marks"] < computer_cut[row["Category"]]:
            continue

        for post in vacancy_dict:

            if post["UR"]>0:

                post["UR"]-=1
                df.at[i,"Post"]=post["Post"]
                df.at[i,"Allotted_Category"]="UR"
                break

            cat=row["Category"]

            if post[cat]>0:

                post[cat]-=1
                df.at[i,"Post"]=post["Post"]
                df.at[i,"Allotted_Category"]=cat
                break

    return df


# ---------------- STREAMLIT ---------------- #

st.title("SSC CGL Real Predictor with Bonus Simulation")

file="marks.csv"

df=load_data(file)

bonus_q=st.sidebar.number_input("Expected Computer Bonus Questions",0,10,0)

bonus_marks=bonus_q*3

df["Computer Marks"]=df["Computer Marks"]+bonus_marks

user_marks=st.sidebar.number_input("Your Main Marks",0,390,310)
user_comp=st.sidebar.number_input("Your Computer Marks",0,60,25)+bonus_marks
user_cat=st.sidebar.selectbox("Category",["UR","OBC","EWS","SC","ST"])

user=pd.DataFrame({
"Main Paper Marks":[user_marks],
"Computer Marks":[user_comp],
"Category":[user_cat]
})

df_full=pd.concat([df,user],ignore_index=True)

vacancies=get_all_vacancies()

allocated=allocate(df_full,vacancies)

allocated["Rank"]=allocated.index+1

user_result=allocated.iloc[-1]

st.metric("Predicted Rank",user_result["Rank"])
st.metric("Predicted Post",user_result["Post"])

fig=px.histogram(allocated,x="Main Paper Marks")

st.plotly_chart(fig,use_container_width=True)

st.dataframe(allocated.head(500))
