import streamlit as st
import pandas as pd
import plotly.express as px
import os
import io
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="SSC CGL 2025 SSC-Rule Predictor", layout="wide")

# ---------------- DATA LOADING ---------------- #

@st.cache_data
def load_and_clean_data(file_name):
    if not os.path.exists(file_name):
        return None, None

    df = pd.read_csv(file_name, encoding='latin1', on_bad_lines='skip')
    df.columns = [str(c).strip() for c in df.columns]

    if 'Main Paper Marks' not in df.columns:
        df = pd.read_csv(file_name, skiprows=1, encoding='latin1')
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
    df.columns = [str(c).strip() for c in df.columns]

    key_col = 'Roll Number' if 'Roll Number' in df.columns else df.columns[0]

    df['Stat Marks'] = pd.to_numeric(df.get('Stat Marks', df.iloc[:, -1]), errors='coerce')

    return df[[key_col, 'Stat Marks']], key_col


# ---------------- FULL VACANCY LIST ---------------- #

def get_full_vacancy_list():
    return [
        ("L-7","CSS (DoPT) - ASO",273,104,52,185,68,682,True,False),
        ("L-7","MEA - ASO",44,13,0,33,10,100,True,False),
        ("L-7","CBIC - Inspector (Examiner)",68,18,24,13,14,137,True,False),
        ("L-7","CBIC - Inspector (Preventive Officer)",138,75,20,91,29,353,True,False),
        ("L-7","CBIC - Inspector (Central Excise)",611,175,82,269,169,1306,True,False),
        ("L-7","CBDT - IT Inspector",176,52,39,95,27,389,False,False),
        ("L-7","ED - Assistant Enforcement Officer",1,2,2,13,0,18,False,False),
        ("L-7","IB - ASO",100,24,19,39,15,197,False,False),
        ("L-7","Railways - ASO",23,4,4,14,3,48,False,False),
        ("L-7","EPFO - ASO",36,17,5,30,6,94,False,False),
        ("L-7","CBI - Sub Inspector",52,12,5,18,6,93,False,False),
        ("L-7","NIC - ASO",2,0,0,0,1,3,False,False),
        ("L-7","CAT - ASO",0,0,0,0,1,1,False,False),
        ("L-7","CBN - Inspector",1,1,0,1,1,4,False,False),
        ("L-7","ECI - ASO",0,0,0,5,1,6,False,False),
        ("L-7","MeitY - ASO",2,0,1,0,0,3,False,False),
        ("L-6","CBIC - Executive Assistant",89,24,12,40,18,183,True,False),
        ("L-6","CBDT - Office Superintendent",2766,1012,496,1822,657,6753,False,False),
        ("L-6","RGI - Statistical Investigator Gr. II",50,18,12,28,10,118,False,True),
        ("L-6","MoSPI - Junior Statistical Officer",124,47,15,36,27,249,False,True),
        ("L-6","ED - Assistant",0,0,0,3,0,3,False,False),
        ("L-6","TRAI - Assistant",2,1,0,0,0,3,False,False),
        ("L-6","Official Language - Assistant",4,0,0,1,0,5,False,False),
        ("L-6","MCA - Assistant",0,1,0,0,0,1,False,False),
        ("L-6","Mines - Assistant",11,2,2,3,4,22,True,False),
        ("L-6","Textiles - Assistant",1,0,0,0,0,1,False,False),
        ("L-6","Indian Coast Guard - Assistant",8,3,1,5,1,18,False,False),
        ("L-6","DFSS - Assistant",1,0,0,1,1,3,False,False),
        ("L-6","NCB - ASO",7,1,1,2,0,11,False,False),
        ("L-6","NCB - Sub-Inspector/JIO",10,3,4,8,5,30,False,False),
        ("L-6","NIA - Sub Inspector",6,2,1,3,2,14,False,False),
        ("L-6","MoSPI - Assistant",0,0,0,2,0,2,False,False),
        ("L-5","CGDA - Auditor",477,176,88,316,117,1174,False,False),
        ("L-5","C&AG - Accountant",86,31,17,28,18,180,False,False),
        ("L-5","Posts - Accountant",42,13,6,12,3,76,False,False),
        ("L-5","CGCA - Accountant",15,6,3,9,3,36,False,False),
        ("L-4","CBIC - Tax Assistant",256,136,82,203,94,771,True,False),
        ("L-4","CBDT - Tax Assistant",572,171,80,340,86,1249,False,False),
        ("L-4","MSME - UDC/SSA",25,4,5,16,5,55,False,False),
        ("L-4","Science & Tech - UDC/SSA",24,9,4,16,6,59,False,False),
        ("L-4","CBN - UDC/SSA",12,2,0,5,2,21,False,False),
        ("L-4","CBN - Sub-Inspector",11,2,0,6,0,19,False,False),
        ("L-4","Mines - UDC/SSA",13,2,3,4,4,26,False,False),
        ("L-4","DGDE - UDC/SSA",7,2,1,3,1,14,False,False),
        ("L-4","MeitY - UDC/SSA",5,1,1,2,1,10,False,False),
        ("L-4","Textiles - UDC/SSA",4,0,1,1,2,8,False,False),
        ("L-4","Water Resources - UDC/SSA",5,0,0,0,0,5,False,False),
        ("L-4","BRO - UDC/SSA",20,1,0,0,4,25,False,False),
        ("L-4","Agriculture - UDC/SSA",2,0,0,0,1,3,False,False),
        ("L-4","Health - UDC/SSA",1,0,0,0,0,1,False,False),
        ("L-4","Dept of Post - PA/SA",0,0,0,0,0,0,True,False)
    ]


# ---------------- SSC REAL ENGINE ---------------- #

def ssc_real_allocation(df_final, posts_df):

    def run_allocation(df, posts, force_qualified=False):

        df = df.copy()
        posts = posts.copy()

        cpt_cutoff = {"UR": 27, "OBC": 24, "EWS": 24, "SC": 21, "ST": 21}
        computer_cutoff = {"UR": 18, "OBC": 15, "EWS": 15, "SC": 12, "ST": 12}

        if force_qualified:
            df["CPT_Qualified"] = True
            df["Computer_Qualified"] = True
        else:
            df["CPT_Qualified"] = (
                df["Computer Marks"] >= df["Category"].map(cpt_cutoff)
            )
            df["Computer_Qualified"] = (
                df["Computer Marks"] >= df["Category"].map(computer_cutoff)
            )

        df = df.sort_values("Main Paper Marks", ascending=False).reset_index(drop=True)

        df["Allocated_Post"] = None
        df["Allocated_Category"] = None

        vacancy = posts.to_dict("index")

        col_post = df.columns.get_loc("Allocated_Post")
        col_cat = df.columns.get_loc("Allocated_Category")

        for idx, candidate in enumerate(df.itertuples(index=False)):

            if not candidate.Computer_Qualified:
                continue

            for p_idx in vacancy:
                post = vacancy[p_idx]

                if post["IsCPT"] and not candidate.CPT_Qualified:
                    continue

                if post["IsStat"] and getattr(candidate, "Stat Marks", 0) <= 0:
                    continue

                if post["UR"] > 0:
                    post["UR"] -= 1
                    df.iat[idx, col_post] = post["Post"]
                    df.iat[idx, col_cat] = "UR"
                    break

                if candidate.Category in ["OBC", "EWS", "SC", "ST"]:
                    if post[candidate.Category] > 0:
                        post[candidate.Category] -= 1
                        df.iat[idx, col_post] = post["Post"]
                        df.iat[idx, col_cat] = candidate.Category
                        break

        allocated = df[df["Allocated_Post"].notnull()]

        cutoff_df = (
            allocated
            .groupby(["Allocated_Post", "Allocated_Category"])["Main Paper Marks"]
            .min()
            .reset_index()
        )

        result = {}

        for _, row in cutoff_df.iterrows():
            post = row["Allocated_Post"]
            cat = row["Allocated_Category"]
            cutoff = row["Main Paper Marks"]

            if post not in result:
                result[post] = {"Cutoff": {}}

            result[post]["Cutoff"][cat] = cutoff

        return result, df

    real_cutoff, real_df = run_allocation(df_final, posts_df, False)
    predicted_cutoff, _ = run_allocation(df_final, posts_df, True)

    return {
        "Real_Cutoff": real_cutoff,
        "Predicted_Cutoff": predicted_cutoff
    }, real_df


# ---------------- PDF ---------------- #

def generate_pdf(result_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    data = [result_df.columns.tolist()] + result_df.values.tolist()
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer


# ---------------- APP UI ---------------- #

st.title("🏆 SSC CGL 2025 Real SSC Rule Predictor")

st.sidebar.header("Your Profile")

u_marks = st.sidebar.number_input("Main Paper Marks", 0.0, 390.0, 310.0)
u_stat = st.sidebar.number_input("Statistics Marks", 0.0, 200.0, 0.0)
u_cat = st.sidebar.selectbox("Category", ["UR", "OBC", "EWS", "SC", "ST"])
u_comp = st.sidebar.number_input("Computer Marks", 0.0, 60.0, 25.0)

MAIN_FILE = "CSV - SSC CGL Mains 2025 Marks List.xlsx - in.csv"
STAT_FILE = "CSV - SSC CGL Mains 2025 Statistics Paper Marks List (1).csv"

df_main, main_key = load_and_clean_data(MAIN_FILE)
df_stat, stat_key = load_stat_data(STAT_FILE)

if df_main is not None:

    if df_stat is not None:
        df_final = pd.merge(
            df_main, df_stat,
            left_on=main_key,
            right_on=stat_key,
            how='left'
        ).fillna(0)
    else:
        df_final = df_main.copy()
        df_final["Stat Marks"] = 0

    posts = get_full_vacancy_list()

    posts_df = pd.DataFrame(posts, columns=[
        "Level", "Post", "UR", "SC", "ST", "OBC", "EWS",
        "Total", "IsCPT", "IsStat"
    ])

    result, final_df = ssc_real_allocation(df_final, posts_df)

    vacancy_result = result["Real_Cutoff"]

    # Rank
    rank = final_df[final_df["Main Paper Marks"] >= u_marks].shape[0] + 1
    total = len(final_df)
    percentile = (1 - rank / total) * 100

    c1, c2, c3 = st.columns(3)
    c1.metric("Predicted Rank", f"#{rank}")
    c2.metric("Percentile", f"{percentile:.2f}%")
    c3.metric("Total Candidates", total)

    # Post-wise Cutoff
    display = []

    for post, info in vacancy_result.items():
        cutoff = info["Cutoff"].get(u_cat, 0)

        if cutoff > 0 and u_marks >= cutoff:
            chance = "⭐ HIGH"
        else:
            chance = "📉 LOW"

        display.append({
            "Post": post,
            "Final SSC Cutoff": cutoff,
            "Your Status": chance
        })

    result_df = pd.DataFrame(display)

    st.subheader("📊 SSC Final Cutoff (Simulated)")
    st.dataframe(result_df, use_container_width=True)

    # ---------------- TABLE FORMAT CUT-OFF DISPLAY ---------------- #

def cutoff_dict_to_table(cutoff_dict, title):
    rows = []

    for post, data in cutoff_dict.items():
        cutoffs = data.get("Cutoff", {})

        row = {
            "Post": post,
            "UR": cutoffs.get("UR", ""),
            "OBC": cutoffs.get("OBC", ""),
            "EWS": cutoffs.get("EWS", ""),
            "SC": cutoffs.get("SC", ""),
            "ST": cutoffs.get("ST", "")
        }

        rows.append(row)

    df_table = pd.DataFrame(rows)

    st.subheader(title)
    st.dataframe(
        df_table.sort_values("Post"),
        use_container_width=True
    )


# Show Real Cutoff Table
cutoff_dict_to_table(result["Real_Cutoff"], "📊 Real SSC Cutoffs")

# Show Predicted Cutoff Table
cutoff_dict_to_table(result["Predicted_Cutoff"], "📈 Predicted Cutoffs (All Qualified)")

    # Predicted Allotment
predicted_post = result_df[
        result_df["Your Status"] == "⭐ HIGH"
    ]["Post"].head(1)

if not predicted_post.empty:
    st.success(f"🎯 Predicted Allotted Post: {predicted_post.values[0]}")
else:
    st.error("No Allotment Based on Current Score")


# Chart
fig = px.histogram(df_final, x="Main Paper Marks", title="Score Distribution")
st.plotly_chart(fig, use_container_width=True)


# PDF
if df_main is not None and not df_main.empty:

    pdf = generate_pdf(result_df)

    st.download_button(
        "⬇️ Download Full SSC Report",
        data=pdf,
        file_name="SSC_CGL_SSC_Rule_Report.pdf",
        mime="application/pdf"
    )

else:
    st.warning("⚠️ CSV files not found.")











