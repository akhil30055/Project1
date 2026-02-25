import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="SSC CGL 2025 Real SSC Rule Predictor", layout="wide")

# ---------------- DATA LOADING ---------------- #

@st.cache_data
def load_and_clean_data(file_name):

    if not os.path.exists(file_name):
        return None, None

    df = pd.read_csv(file_name, encoding='latin1', on_bad_lines='skip')
    df.columns = [str(c).strip() for c in df.columns]

    key_col = 'Roll Number' if 'Roll Number' in df.columns else df.columns[0]

    df['Main Paper Marks'] = pd.to_numeric(df['Main Paper Marks'], errors='coerce')
    df['Computer Marks'] = pd.to_numeric(df['Computer Marks'], errors='coerce')

    df = df.dropna(subset=['Main Paper Marks', 'Category', 'Computer Marks'])

    return df, key_col


@st.cache_data
def load_stat_data(file_name):

    if not os.path.exists(file_name):
        return None, None

    df = pd.read_csv(file_name, encoding='latin1', on_bad_lines='skip')

    key_col = 'Roll Number' if 'Roll Number' in df.columns else df.columns[0]

    df['Stat Marks'] = pd.to_numeric(df.get('Stat Marks', 0), errors='coerce')

    return df[[key_col, 'Stat Marks']], key_col


# ---------------- VACANCY ---------------- #

def get_full_vacancy_list():

    return [

        ("L-7","CSS ASO",273,104,52,185,68,682,True,False),
        ("L-7","MEA ASO",44,13,0,33,10,100,True,False),
        ("L-7","CBIC Inspector Examiner",68,18,24,13,14,137,True,False),
        ("L-7","CBIC Inspector Preventive",138,75,20,91,29,353,True,False),
        ("L-7","CBIC Inspector Excise",611,175,82,269,169,1306,True,False),
        ("L-7","CBDT Inspector",176,52,39,95,27,389,False,False),

        ("L-6","CBDT Office Superintendent",2766,1012,496,1822,657,6753,False,False),

        ("L-5","CGDA Auditor",477,176,88,316,117,1174,False,False),

        ("L-4","CBIC Tax Assistant",256,136,82,203,94,771,True,False),
        ("L-4","CBDT Tax Assistant",572,171,80,340,86,1249,False,False)

    ]


# ---------------- SSC REAL ENGINE ---------------- #

def ssc_real_allocation(df, posts_df):

    df = df.copy()
    posts = posts_df.copy()

    computer_cutoff = {"UR":18,"OBC":15,"EWS":15,"SC":12,"ST":12}

    df["Computer_Qualified"] = df["Computer Marks"] >= df["Category"].map(computer_cutoff)

    df = df.sort_values("Main Paper Marks", ascending=False).reset_index(drop=True)

    df["Allocated_Post"] = None
    df["Allocated_Category"] = None

    vacancy = posts.to_dict("index")

    for i, candidate in df.iterrows():

        if not candidate["Computer_Qualified"]:
            continue

        for p in vacancy:

            post = vacancy[p]

            if post["UR"] > 0:

                vacancy[p]["UR"] -= 1
                df.at[i,"Allocated_Post"] = post["Post"]
                df.at[i,"Allocated_Category"] = "UR"
                break

            cat = candidate["Category"]

            if cat in ["OBC","EWS","SC","ST"]:

                if post[cat] > 0:

                    vacancy[p][cat] -= 1
                    df.at[i,"Allocated_Post"] = post["Post"]
                    df.at[i,"Allocated_Category"] = cat
                    break

    cutoff_df = df[df["Allocated_Post"].notnull()]

    cutoff_df = cutoff_df.groupby(
        ["Allocated_Post","Allocated_Category"]
    )["Main Paper Marks"].min().reset_index()

    result = {}

    for _,row in cutoff_df.iterrows():

        post=row["Allocated_Post"]
        cat=row["Allocated_Category"]
        cutoff=row["Main Paper Marks"]

        if post not in result:
            result[post]={"Cutoff":{}}

        result[post]["Cutoff"][cat]=cutoff

    return result, df


# ---------------- PDF ---------------- #

def generate_pdf(df):

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)

    table = Table([df.columns.tolist()] + df.values.tolist())

    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.5,colors.black)
    ]))

    doc.build([table])

    buffer.seek(0)

    return buffer


# ---------------- UI ---------------- #

st.title("SSC CGL Real Allocation Predictor")

st.sidebar.header("Enter Your Marks")

u_marks = st.sidebar.number_input("Main Marks",0.0,390.0,310.0)
u_comp = st.sidebar.number_input("Computer Marks",0.0,60.0,25.0)
u_cat = st.sidebar.selectbox("Category",["UR","OBC","EWS","SC","ST"])

MAIN_FILE="CSV - SSC CGL Mains 2025 Marks List.xlsx - in.csv"

df_main,key=load_and_clean_data(MAIN_FILE)

if df_main is not None:

    df_main["Stat Marks"]=0

    posts=get_full_vacancy_list()

    posts_df=pd.DataFrame(posts,columns=[
        "Level","Post","UR","SC","ST","OBC","EWS",
        "Total","IsCPT","IsStat"
    ])

    # INSERT USER

    user_row={
        key:"USER",
        "Main Paper Marks":u_marks,
        "Computer Marks":u_comp,
        "Stat Marks":0,
        "Category":u_cat
    }

    df_with_user=pd.concat([df_main,pd.DataFrame([user_row])],ignore_index=True)

    result,allocated_df=ssc_real_allocation(df_with_user,posts_df)

    allocated_df=allocated_df.sort_values(
        "Main Paper Marks",ascending=False
    ).reset_index(drop=True)

    allocated_df["Rank"]=allocated_df.index+1

    user=allocated_df[allocated_df[key]=="USER"].iloc[0]

    st.subheader("Prediction Result")

    c1,c2,c3=st.columns(3)

    c1.metric("Predicted Rank",user["Rank"])

    qualified=allocated_df[
        allocated_df["Computer Marks"]>=
        allocated_df["Category"].map(
            {"UR":18,"OBC":15,"EWS":15,"SC":12,"ST":12}
        )
    ]

    qualified=qualified.reset_index(drop=True)

    qualified["CPT Rank"]=qualified.index+1

    if "USER" in qualified[key].values:

        cpt_rank=qualified[qualified[key]=="USER"]["CPT Rank"].values[0]

    else:

        cpt_rank="Not Qualified"

    c2.metric("CPT Rank",cpt_rank)

    post=user["Allocated_Post"]

    if post:

        c3.metric("Allocated Post",post)

        st.success(f"Category: {user['Allocated_Category']}")

    else:

        c3.metric("Allocated Post","Not Selected")

        st.error("Not selected")

    # Cutoff Table

    rows=[]

    for post,data in result.items():

        rows.append({
            "Post":post,
            "UR":data["Cutoff"].get("UR",""),
            "OBC":data["Cutoff"].get("OBC",""),
            "EWS":data["Cutoff"].get("EWS",""),
            "SC":data["Cutoff"].get("SC",""),
            "ST":data["Cutoff"].get("ST","")
        })

    cutoff_df=pd.DataFrame(rows)

    st.subheader("Cutoff Table")

    st.dataframe(cutoff_df,use_container_width=True)

    # Distribution Chart

    fig=px.histogram(df_main,x="Main Paper Marks")

    st.plotly_chart(fig,use_container_width=True)

    # PDF

    pdf=generate_pdf(cutoff_df)

    st.download_button(
        "Download Report",
        pdf,
        file_name="ssc_report.pdf"
    )

else:

    st.warning("Marks CSV not found")
