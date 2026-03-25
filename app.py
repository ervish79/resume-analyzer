import streamlit as st
from utils import extract_text, calculate_score, skill_analysis, generate_pdf_report
from roles import roles
import matplotlib.pyplot as plt
from database import add_user, get_user, save_result, get_history, get_all_users, get_admin_stats
from io import BytesIO

# =========================
# APP CONFIGURATION
# =========================
st.set_page_config(page_title="AI Resume Analyzer", layout="wide")


st.markdown("""
<style>
.stMetric {
    background-color: #1e293b;
    padding: 15px;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# =========================
# ADMIN CREDENTIALS
# =========================
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# =========================
# SESSION STATE INITIALIZATION
# =========================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =========================
# AUTHENTICATION PAGE
# =========================
def auth_page():
    st.markdown("## Login / Signup")

    tab1, tab2 = st.tabs(["Login", "Signup"])

    # LOGIN
    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            # Admin login
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.session_state.username = "admin"
                st.session_state.is_admin = True
                st.rerun()

            # Normal user login
            elif get_user(username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.is_admin = False
                st.rerun()
            else:
                st.error("Invalid credentials")

    # SIGNUP
    with tab2:
        new_user = st.text_input("New Username")
        new_pass = st.text_input("New Password", type="password")

        if st.button("Signup"):
            if new_user and new_pass:
                if add_user(new_user, new_pass):
                    st.success("Account created. Please login.")
                else:
                    st.warning("User already exists")
            else:
                st.error("Please fill all fields")

# =========================
# BLOCK ACCESS IF NOT LOGGED IN
# =========================
if not st.session_state.logged_in:
    auth_page()
    st.stop()

# =========================
# ADMIN DASHBOARD
# =========================
if st.session_state.is_admin:
    st.title("Admin Dashboard")

    # Show users
    st.subheader("Registered Users")
    users_list = get_all_users()
    for user in users_list:
        st.write(user[0])

    # Admin stats
    total_resumes, avg_score = get_admin_stats()
    # Score distribution graph
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM history")
    scores = [row[0] for row in cursor.fetchall()]

    if scores:
        fig, ax = plt.subplots()
        ax.hist(scores)
        ax.set_title("All Users Score Distribution")
        st.pyplot(fig)

    st.metric("Total Resumes Analyzed", total_resumes)
    st.metric("Average Score", round(avg_score, 2) if avg_score else 0)

    # Logout
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.is_admin = False
        st.rerun()

    st.stop()

# =========================
# MAIN HEADER
# =========================
col1, col2 = st.columns([8, 2])

with col1:
    st.title("Smart AI Resume Analyzer")

with col2:
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

st.write(f"Welcome, {st.session_state.username}")

# App description
st.markdown("""
AI-powered Resume Screening System  
Upload your resume and get instant feedback, ranking, and job match score
""")

# Role selection
role = st.selectbox("Select Job Role", list(roles.keys()))

# =========================
# SINGLE RESUME ANALYSIS
# =========================
st.markdown("---")
st.header("Resume Analysis")

uploaded_file = st.file_uploader("Upload Resume (PDF)", type="pdf")

if uploaded_file:
    resume_text = extract_text(uploaded_file)
    skills = roles[role]

    # Debug view
    if st.checkbox("Show Extracted Text"):
        st.write(resume_text[:1000])

    # Score calculation
    score = calculate_score(resume_text, skills)
    found, missing = skill_analysis(resume_text, skills)

    # Save result (only if valid)
    if score > 0:
        save_result(st.session_state.username, role, score, found, missing)

    # Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{score}/100")
    col2.metric("Skills Found", len(found))
    col3.metric("Missing Skills", len(missing))

    st.progress(int(score))

    # Skills display
    st.subheader("Matching Skills")
    st.success(", ".join(found) if found else "None")

    st.subheader("Missing Skills")
    st.error(", ".join(missing) if missing else "None")

    # Resume improvement tips
    st.markdown("### Resume Tips")

    if "projects" not in resume_text:
        st.write("Add projects section to improve impact")

    if "experience" not in resume_text:
        st.write("Include work experience")

    if len(resume_text.split()) < 300:
        st.write("Increase resume content length")

    # Suggestions
    st.markdown("### Suggestions to Improve Resume")
    if missing:
        for skill in missing:
            st.write(f"Add skill: {skill}")
    else:
        st.success("Your resume is well optimized")

    # Skill breakdown
    st.markdown("### Skill Match Breakdown")
    for skill in skills:
        pct = 100 if skill in found else 0
        st.progress(pct)
        st.write(f"{skill} ({'Matched' if skill in found else 'Missing'})")

    # Pie chart
    fig, ax = plt.subplots()
    ax.pie([len(found), len(missing)], labels=["Found", "Missing"], autopct='%1.1f%%')
    st.pyplot(fig)

    # PDF download
    if st.button("Download Report"):
        pdf_buffer = BytesIO()
        generate_pdf_report(pdf_buffer, score, found, missing)
        st.download_button("Download PDF", pdf_buffer, file_name="report.pdf", mime="application/pdf")

# =========================
# MULTIPLE RESUME RANKING
# =========================
st.markdown("---")
st.header("Resume Ranking")

uploaded_files = st.file_uploader(
    "Upload Multiple Resumes",
    type="pdf",
    accept_multiple_files=True
)

if uploaded_files:
    results = []

    for file in uploaded_files:
        text = extract_text(file)
        score = calculate_score(text, roles[role])
        found, missing = skill_analysis(text, roles[role])

        if score > 0:
            save_result(st.session_state.username, role, score, found, missing)

        results.append((file.name, score))

    results.sort(key=lambda x: x[1], reverse=True)

    for i, (name, score) in enumerate(results, start=1):
        st.write(f"{i}. {name} -> {score}/100")

    # Bar chart
    names = [r[0] for r in results]
    scores = [r[1] for r in results]

    fig, ax = plt.subplots()
    ax.barh(names, scores)
    ax.set_xlabel("Score")
    ax.set_title("Resume Ranking")
    ax.invert_yaxis()
    st.pyplot(fig)



# =========================
# USER HISTORY DASHBOARD
# =========================
st.markdown("---")
st.header("Your Analysis History")

history = get_history(st.session_state.username)

if history:
    for role, score, found, missing in history:
        st.write(f"Role: {role} | Score: {score}")

    # Score graph
    scores = [row[1] for row in history]
    attempts = list(range(1, len(scores)+1))

    fig, ax = plt.subplots()
    ax.plot(attempts, scores)
    ax.set_xlabel("Attempts")
    ax.set_ylabel("Score")
    ax.set_title("Score Improvement")
    st.pyplot(fig)

else:
    st.write("No history yet")

# =========================
# JOB DESCRIPTION MATCHING
# =========================
st.markdown("---")
st.header("Job Description Matching")

job_desc = st.text_area("Paste Job Description")

if uploaded_file and job_desc:
    jd_score = calculate_score(resume_text + " " + job_desc, roles[role])

    st.progress(int(jd_score))
    st.write(f"Match Score: {jd_score}/100")

    if jd_score > 0:
        save_result(st.session_state.username, f"{role} (JD Match)", jd_score, [], [])
