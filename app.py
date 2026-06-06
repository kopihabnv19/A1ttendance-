import streamlit as st
import pandas as pd
import google.generativeai as genai
import plotly.express as px

# ====================================================
# GEMINI API KEY
# =====================================================

GEMINI_API_KEY = "AQ.Ab8RN6LQrFd_0N58CYHXte3FtDRCS64FMwRGXu5aq5iFLxFslg"

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Attendance Management System",
    page_icon="🎓",
    layout="wide"
)

# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>

.stApp{
    background-color:#eef7ff;
}

.title{
    text-align:center;
    color:#003366;
    font-weight:bold;
}

h1,h2,h3,h4,h5,h6{
    color:#003366 !important;
}

p, div, span, label{
    color:#000000 !important;
}

[data-testid="stMetric"]{
    background:#ffffff;
    padding:15px;
    border-radius:10px;
    border:1px solid #d9e6f2;
}

[data-testid="stDataFrame"]{
    background:#ffffff;
}

.report-box{
    background:#ffffff;
    color:#000000 !important;
    padding:25px;
    border-radius:15px;
    border:1px solid #d9d9d9;
    box-shadow:0px 2px 10px rgba(0,0,0,0.08);
    line-height:1.8;
    font-size:16px;
    white-space:pre-wrap;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown(
    "<h1 class='title'>🎓 AI Attendance Management System</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<center><h4>Smart Attendance Analytics using Gemini AI</h4></center>",
    unsafe_allow_html=True
)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.header("📌 How to Use")

    st.markdown("""
1. Upload Attendance File

2. AI calculates attendance

3. Detects risk students

4. Generates smart reports

5. Faculty receives recommendations

6. AI suggests intervention plans
""")

# =====================================================
# FILE UPLOAD
# =====================================================

uploaded_file = st.file_uploader(
    "📂 Upload Attendance Sheet",
    type=["csv", "xlsx"]
)

# =====================================================
# LOAD FILE
# =====================================================

def load_file(file):

    try:

        if file.name.endswith(".csv"):
            return pd.read_csv(file)

        return pd.read_excel(file)

    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

# =====================================================
# ATTENDANCE CALCULATION
# =====================================================

def calculate_attendance(df):

    total_classes = (
        df.groupby("Student Name")
        .size()
    )

    present_classes = (
        df[df["Status"].astype(str).str.strip().str.lower() == "present"]
        .groupby("Student Name")
        .size()
    )

    result = pd.DataFrame({
        "Total Classes": total_classes,
        "Present Classes": present_classes
    }).fillna(0)

    result["Attendance %"] = (
        result["Present Classes"]
        / result["Total Classes"]
    ) * 100

    result.reset_index(inplace=True)

    return result.round(2)

# =====================================================
# GEMINI ANALYSIS
# =====================================================

def ai_analysis(summary):

    prompt = f"""
You are an AI Attendance Analyst.

Analyze the attendance data and generate:

1. Executive Summary
2. Attendance Overview
3. Students Below 75%
4. Students Below 60%
5. Attendance Risk Classification
6. Possible Causes of Low Attendance
7. Student Engagement Insights
8. Faculty Recommendations
9. Parent Communication Suggestions
10. Smart Intervention Plan
11. Attendance Improvement Strategies
12. Motivational Quote

Attendance Data:

{summary}

Return a professional report.
"""

    try:

        model = genai.GenerativeModel(
            "gemini-2.5-flash"
        )

        response = model.generate_content(prompt)

        if hasattr(response, "text"):
            return response.text

        return str(response)

    except Exception as e:
        return f"AI Error: {str(e)}"

# =====================================================
# MAIN APP
# =====================================================

if uploaded_file:

    df = load_file(uploaded_file)

    if df is not None:

        required_columns = ["Student Name", "Status"]

        missing = [
            col for col in required_columns
            if col not in df.columns
        ]

        if missing:

            st.error(
                f"Missing required columns: {', '.join(missing)}"
            )

        else:

            st.success(
                "✅ Attendance File Uploaded Successfully"
            )

            st.subheader("📋 Raw Attendance Data")

            st.dataframe(
                df,
                use_container_width=True
            )

            attendance_summary = calculate_attendance(df)

            st.subheader("📊 Attendance Summary")

            st.dataframe(
                attendance_summary,
                use_container_width=True
            )

            total_students = len(attendance_summary)

            avg_attendance = (
                attendance_summary["Attendance %"]
                .mean()
            )

            low_students = len(
                attendance_summary[
                    attendance_summary["Attendance %"] < 75
                ]
            )

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Students",
                total_students
            )

            c2.metric(
                "Average Attendance",
                f"{avg_attendance:.2f}%"
            )

            c3.metric(
                "Low Attendance",
                low_students
            )

            st.subheader("⚠️ At-Risk Students")

            risk_students = attendance_summary[
                attendance_summary["Attendance %"] < 75
            ]

            if len(risk_students) > 0:

                st.dataframe(
                    risk_students,
                    use_container_width=True
                )

            else:

                st.success(
                    "No students are currently at risk."
                )

            st.subheader(
                "📈 Attendance Visualization"
            )

            fig = px.bar(
                attendance_summary,
                x="Student Name",
                y="Attendance %",
                title="Attendance Percentage by Student"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.subheader(
                "🤖 AI Attendance Intelligence Report"
            )

            with st.spinner(
                "Analyzing attendance using Gemini AI..."
            ):

                report = ai_analysis(
                    attendance_summary.to_string(
                        index=False
                    )
                )

            st.markdown(
                f"""
<div class="report-box">
{report}
</div>
                """,
                unsafe_allow_html=True
            )

            st.success(
                "🎉 Attendance Analysis Completed"
            )

            st.balloons()

else:

    st.info(
        "📂 Upload a CSV or Excel attendance sheet to begin."
    )
