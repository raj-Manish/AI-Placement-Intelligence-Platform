"""
Streamlit Web Application: AI Placement Intelligence Platform
Integrates:
1. Module 1: Placement Copilot (PDF Ingestion, pgvector similarity search, grounded Gemini QA, page sources)
2. Module 1.1: Personalized Profile Analysis (Candidate skills gap, priority topics, preparation plan)
3. Module 2: Deterministic Company Matching Engine (Skill, role, salary, hiring history scoring)
"""

import os
import sys
from dotenv import load_dotenv

# Ensure fresh environment variables are loaded on each Streamlit rerun
load_dotenv(override=True)

import streamlit as st

# Ensure root workspace is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.database.connection import test_connection
from app.rag.loader import load_pdf, PDFLoadError
from app.rag.splitter import split_documents
from app.rag.vector_store import store_document_chunks, get_all_documents, VectorStoreError
from app.rag.qa import ask_copilot, analyze_candidate_fit, NOT_FOUND_MESSAGE, QAError
from app.matching.profile import StudentProfile, ProfileValidationError
from app.matching.matcher import match_companies

# Set page configuration
st.set_page_config(
    page_title="AI Placement Intelligence Platform",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initializes persistent session state variables."""
    if "student_profile" not in st.session_state:
        st.session_state.student_profile = StudentProfile(
            name="Rahul Sharma",
            skills=["C++", "Python", "SQL", "React", "Node.js"],
            preferred_roles=["Software Engineer", "Backend Developer"],
            expected_salary=14.0,
            experience=0.0
        )
    if "last_analysis" not in st.session_state:
        st.session_state.last_analysis = None
    if "match_results" not in st.session_state:
        st.session_state.match_results = None
    if "uploaded_filename" not in st.session_state:
        st.session_state.uploaded_filename = "Amazon_SDE_JD.pdf"


initialize_session_state()

# ---------------------------------------------------------
# SIDEBAR: System Status & Candidate Profile Configuration
# ---------------------------------------------------------
with st.sidebar:
    st.title("🎓 Placement Platform")
    st.caption("AI Placement Intelligence & Shortlisting")
    st.markdown("---")

    # 1. System Health Status
    st.subheader("System Status")
    db_status = test_connection()
    if db_status["connected"]:
        st.success("🟢 PostgreSQL Connected")
        if db_status["pgvector_enabled"]:
            st.caption("✓ pgvector extension active")
        else:
            st.warning("⚠️ pgvector extension missing")
    else:
        st.error("🔴 PostgreSQL Disconnected")
        st.caption("Using offline CSV fallback for matching engine")

    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if api_key and api_key != "your_gemini_api_key_here":
        st.success("🟢 Gemini API Key Set")
    else:
        st.warning("⚠️ GOOGLE_API_KEY missing in .env")

    st.markdown("---")

    # 2. Candidate Profile Form
    st.subheader("Candidate Profile")
    p_name = st.text_input("Name", value=st.session_state.student_profile.name)
    p_skills = st.text_area(
        "Technical Skills (comma-separated)",
        value=", ".join(st.session_state.student_profile.skills),
        help="Example: C++, Python, SQL, React, Node.js"
    )
    p_roles = st.text_input(
        "Preferred Roles (comma-separated)",
        value=", ".join(st.session_state.student_profile.preferred_roles),
        help="Example: Software Engineer, Backend Developer"
    )
    col_sal, col_exp = st.columns(2)
    with col_sal:
        p_salary = st.number_input(
            "Expected CTC (LPA)",
            min_value=1.0,
            max_value=150.0,
            value=float(st.session_state.student_profile.expected_salary),
            step=0.5
        )
    with col_exp:
        p_exp = st.number_input(
            "Experience (Years)",
            min_value=0.0,
            max_value=20.0,
            value=float(st.session_state.student_profile.experience),
            step=0.5
        )

    if st.button("💾 Save Profile", use_container_width=True):
        try:
            profile = StudentProfile.from_form_inputs(
                name=p_name,
                skills_raw=p_skills,
                roles_raw=p_roles,
                expected_salary_raw=p_salary,
                experience_raw=p_exp
            )
            st.session_state.student_profile = profile
            st.success("Profile updated successfully!")
        except ProfileValidationError as e:
            st.error(str(e))

# ---------------------------------------------------------
# MAIN DASHBOARD TABS
# ---------------------------------------------------------
tab_rag, tab_matching, tab_upload = st.tabs([
    "🤖 Placement Copilot (RAG)",
    "🎯 Company Matching Engine",
    "📄 Ingest Job Descriptions"
])

# =========================================================
# TAB 1: PLACEMENT COPILOT (MODULE 1 & 1.1)
# =========================================================
with tab_rag:
    st.header("🤖 Placement Copilot")
    st.markdown(
        "Ask questions about the uploaded Job Description. Every answer is strictly grounded "
        "in the document text and cited with page numbers."
    )

    # Active JD Selector
    col_sel1, col_sel2 = st.columns([3, 1])
    with col_sel1:
        st.info(f"**Active Job Description:** `{st.session_state.uploaded_filename}`")
    with col_sel2:
        if st.button("🔄 Reload Documents"):
            st.rerun()

    st.markdown("---")

    # Personalized Analysis Quick Action (Module 1.1)
    st.subheader("1. Personalized Profile Fit Analysis")
    st.caption("Compares your profile directly against the active JD requirements.")

    if st.button("🔍 Analyze My Profile Against This JD", type="primary"):
        with st.spinner("Analyzing profile against JD requirements..."):
            try:
                fit_result = analyze_candidate_fit(
                    student_profile=st.session_state.student_profile.to_dict(),
                    company_name=None
                )
                st.session_state.last_analysis = fit_result
            except Exception as e:
                st.error(f"Analysis failed: {str(e)}")

    if st.session_state.last_analysis:
        res = st.session_state.last_analysis
        st.markdown("### 📋 Analysis Report")
        st.markdown(res["answer"])

        if res.get("sources"):
            st.markdown("#### 📚 Referenced Sources:")
            for s in res["sources"]:
                st.markdown(f"- 📄 `{s}`")

    st.markdown("---")

    # Interactive Q&A Form
    st.subheader("2. Ask a Specific Question")
    preset_questions = [
        "Select a sample question or type your own...",
        "What are the required programming languages?",
        "What databases and cloud platforms are mentioned?",
        "What is the expected salary package and compensation?",
        "What are the important interview topics?",
        "What is the expected experience level?",
        "Does this company sponsor international work visas?"  # Test question for "Not Found"
    ]

    selected_preset = st.selectbox("Quick Questions:", preset_questions)
    user_query = st.text_input(
        "Enter your question:",
        value="" if selected_preset == preset_questions[0] else selected_preset
    )

    if st.button("🚀 Ask Copilot"):
        if not user_query.strip():
            st.warning("Please type a question before submitting.")
        else:
            with st.spinner("Searching JD and generating grounded answer..."):
                try:
                    qa_result = ask_copilot(
                        question=user_query,
                        student_profile=st.session_state.student_profile.to_dict(),
                        top_k=4
                    )

                    st.markdown("### Answer:")
                    st.write(qa_result["answer"])

                    # Display Sources
                    if qa_result.get("sources"):
                        st.markdown("### Sources:")
                        for s in qa_result["sources"]:
                            st.markdown(f"- 📄 **{s}**")
                    else:
                        if not qa_result["found"]:
                            st.info("ℹ️ No source citations provided because the information was absent from the document.")

                    # Inspect Retrieved Chunks
                    if qa_result.get("chunks"):
                        with st.expander("🔍 Inspect Retrieved Context Chunks (Top-K)"):
                            for i, ch in enumerate(qa_result["chunks"], 1):
                                st.markdown(f"**Chunk {i}** | File: `{ch.get('source_filename')}` | Page: `{ch.get('page_number')}` | Similarity: `{ch.get('similarity_score', 'N/A')}`")
                                st.text(ch.get("chunk_text"))
                                st.markdown("---")

                except Exception as e:
                    st.error(f"Error answering question: {str(e)}")

# =========================================================
# TAB 2: COMPANY MATCHING ENGINE (MODULE 2)
# =========================================================
with tab_matching:
    st.header("🎯 Company Matching Engine")
    st.markdown(
        "A **deterministic, rule-based matching engine** that shortlists target firms based on your "
        "skills, role preferences, expected CTC, and historical hiring patterns.  \n"
        "*Formula: 50% Skill Match + 20% Role Match + 15% Salary Match + 15% Hiring History.*"
    )

    col_btn, col_k = st.columns([3, 1])
    with col_btn:
        find_btn = st.button("🚀 Find Best Matching Companies", type="primary", use_container_width=True)
    with col_k:
        top_k_firms = st.selectbox("Shortlist Top:", [5, 10, 15, 20], index=1)

    if find_btn or st.session_state.match_results is not None:
        if find_btn:
            with st.spinner("Evaluating candidate profile against benchmark companies..."):
                st.session_state.match_results = match_companies(
                    profile=st.session_state.student_profile,
                    top_n=top_k_firms
                )

        results = st.session_state.match_results
        if not results:
            st.warning("No companies matched the criteria. Please broaden your skills or roles.")
        else:
            st.success(f"Successfully evaluated benchmark dataset! Showing Top {len(results)} matches:")

            for i, comp in enumerate(results, 1):
                score = comp["match_score"]
                color = "green" if score >= 80 else ("orange" if score >= 60 else "red")

                with st.expander(f"**#{i} {comp['company_name']}** — Role: `{comp['role']}` | **Match Score: :{color}[{score}%]**", expanded=(i <= 3)):
                    c_col1, c_col2 = st.columns([1, 1])

                    with c_col1:
                        st.markdown("#### 📊 Score Breakdown:")
                        bd = comp["breakdown"]
                        st.progress(bd["skill_score"] / 100.0, text=f"Skills Match (50%): {bd['skill_score']}%")
                        st.progress(bd["role_score"] / 100.0, text=f"Role Match (20%): {bd['role_score']}%")
                        st.progress(bd["salary_score"] / 100.0, text=f"Salary Range Match (15%): {bd['salary_score']}%")
                        st.progress(bd["hiring_score"] / 100.0, text=f"Hiring History (15%): {bd['hiring_score']}%")

                    with c_col2:
                        st.markdown("#### 💡 Detailed Reasoning:")
                        for reason in comp["reasons"]:
                            st.markdown(f"- {reason}")

                        st.markdown(f"**Salary Bracket:** `{comp['salary_range']}`")

                    # Skill comparison tags
                    st.markdown("---")
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        matched = comp.get("matched_skills", [])
                        st.markdown(f"**✅ Matched Skills ({len(matched)}):**")
                        if matched:
                            st.write(", ".join([f"`{s}`" for s in matched]))
                        else:
                            st.caption("No direct skills matched.")

                    with col_m2:
                        missing = comp.get("missing_skills", [])
                        st.markdown(f"**⚠️ Missing Skills ({len(missing)}):**")
                        if missing:
                            st.write(", ".join([f"`{s}`" for s in missing]))
                        else:
                            st.caption("No missing skills! 100% skill match.")

    st.caption("ℹ️ Benchmark dataset contains 40 curated hiring records across Tech, Fintech, and SaaS.")

# =========================================================
# TAB 3: INGEST JOB DESCRIPTIONS (INGESTION PIPELINE)
# =========================================================
with tab_upload:
    st.header("📄 Ingest Job Description (PDF)")
    st.markdown(
        "Upload a company Job Description PDF to chunk, embed, and store in PostgreSQL + pgvector."
    )

    upload_col1, upload_col2 = st.columns([1, 1])

    with upload_col1:
        st.subheader("Upload Custom JD")
        uploaded_file = st.file_uploader("Select PDF File", type=["pdf"])
        comp_name_input = st.text_input("Company Name (e.g., Google, Amazon)", value="Amazon")

        if st.button("📥 Ingest and Store Chunks", type="primary"):
            if not uploaded_file:
                st.warning("Please choose a PDF file first.")
            else:
                # Save to uploads directory
                uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))
                os.makedirs(uploads_dir, exist_ok=True)
                save_path = os.path.join(uploads_dir, uploaded_file.name)

                with open(save_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                with st.spinner("Extracting pages, chunking text, and embedding into pgvector..."):
                    try:
                        pages = load_pdf(save_path)
                        chunks = split_documents(pages, chunk_size=900, chunk_overlap=120)
                        doc_id = store_document_chunks(
                            filename=uploaded_file.name,
                            company_name=comp_name_input,
                            chunks=chunks
                        )
                        st.session_state.uploaded_filename = uploaded_file.name
                        st.success(
                            f"Successfully ingested '{uploaded_file.name}'! "
                            f"Created {len(chunks)} chunks across {len(pages)} pages (Document ID: {doc_id})."
                        )
                    except (PDFLoadError, VectorStoreError) as e:
                        st.error(f"Ingestion Error: {str(e)}")
                    except Exception as e:
                        st.error(f"Unexpected Error: {str(e)}")

    with upload_col2:
        st.subheader("Use Pre-built Sample JD")
        st.markdown(
            "Quickly test with our verified 3-page **Amazon SDE-1 Job Description** without uploading a new file."
        )
        sample_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_jds", "Amazon_SDE_JD.pdf"))

        if os.path.exists(sample_path):
            if st.button("🚀 Ingest Sample Amazon SDE JD"):
                with st.spinner("Processing sample Amazon SDE JD..."):
                    try:
                        pages = load_pdf(sample_path)
                        chunks = split_documents(pages, chunk_size=900, chunk_overlap=120)
                        doc_id = store_document_chunks(
                            filename="Amazon_SDE_JD.pdf",
                            company_name="Amazon",
                            chunks=chunks
                        )
                        st.session_state.uploaded_filename = "Amazon_SDE_JD.pdf"
                        st.success(f"Sample JD ingested! {len(chunks)} chunks stored in pgvector.")
                    except Exception as e:
                        st.error(f"Sample Ingestion Failed: {str(e)}")
        else:
            st.info("Sample JD not found in data/sample_jds/.")

    st.markdown("---")
    st.subheader("Stored Documents in Vector Database")
    docs = get_all_documents()
    if docs:
        st.dataframe(docs, use_container_width=True)
    else:
        st.caption("No documents currently stored in the database. Ingest a JD to begin.")
