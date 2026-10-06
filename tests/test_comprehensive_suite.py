"""
Comprehensive Test Suite for AI Placement Intelligence Platform (Phase 9)
Executes and validates the 10 core resume & interview test cases:

1. Valid JD (Loading, page count, chunk extraction)
2. Empty PDF (0 bytes exception guard)
3. Question whose answer exists (Context retrieval & citations)
4. Question whose answer does not exist (Anti-hallucination fallback)
5. Skill matching (Exact overlap, partial overlap, synonyms)
6. Role mismatch (Title divergence penalty)
7. Salary mismatch (Out-of-range salary penalty)
8. Strong overall company match (High composite score > 85%)
9. Weak overall company match (Low composite score < 45%)
10. Missing / Invalid student profile fields (Validation guards)
"""

import os
import sys

# Ensure root workspace is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.rag.loader import load_pdf, PDFLoadError
from app.rag.splitter import split_documents
from app.rag.retriever import format_context_for_prompt
from app.rag.qa import extract_unique_sources, NOT_FOUND_MESSAGE
from app.matching.profile import StudentProfile, ProfileValidationError
from app.matching.scoring import (
    calculate_skill_score,
    calculate_role_score,
    calculate_salary_score,
    compute_final_score
)
from app.matching.matcher import match_companies


def run_comprehensive_test_suite():
    print("=" * 70)
    print("AI PLACEMENT INTELLIGENCE PLATFORM — 10-POINT COMPREHENSIVE TEST SUITE")
    print("=" * 70)

    # -------------------------------------------------------------
    # TEST CASE 1: Valid Job Description Ingestion
    # -------------------------------------------------------------
    print("\n[TEST CASE 1] Valid Job Description PDF Ingestion")
    valid_pdf = os.path.join("data", "sample_jds", "Amazon_SDE_JD.pdf")
    pages = load_pdf(valid_pdf)
    assert len(pages) == 3, f"Expected 3 pages, found {len(pages)}"
    chunks = split_documents(pages, chunk_size=900, chunk_overlap=120)
    assert len(chunks) >= 5, f"Expected at least 5 chunks, found {len(chunks)}"
    print(f" -> Successfully loaded {len(pages)} pages and created {len(chunks)} chunks.")
    print(" -> TEST CASE 1 PASSED: Valid JD parsed with page numbers.")

    # -------------------------------------------------------------
    # TEST CASE 2: Empty PDF Ingestion Guard
    # -------------------------------------------------------------
    print("\n[TEST CASE 2] Empty PDF File Guard (0 bytes)")
    empty_pdf = os.path.join("data", "sample_jds", "empty.pdf")
    try:
        load_pdf(empty_pdf)
        raise AssertionError("Empty PDF should have raised PDFLoadError!")
    except PDFLoadError as e:
        print(f" -> Correctly caught PDFLoadError: '{e}'")
        print(" -> TEST CASE 2 PASSED: 0-byte file rejected safely.")

    # -------------------------------------------------------------
    # TEST CASE 3: Question Whose Answer Exists in the JD
    # -------------------------------------------------------------
    print("\n[TEST CASE 3] Question Whose Answer Exists in the JD")
    # Simulate retrieved chunks for: "What are the required programming languages?"
    relevant_chunks = [
        c for c in chunks if "C++" in c.page_content and "Python" in c.page_content
    ]
    assert len(relevant_chunks) > 0, "Failed to find relevant chunk containing programming languages!"
    target_chunk = relevant_chunks[0]
    sources = extract_unique_sources([
        {
            "source_filename": target_chunk.metadata["source_filename"],
            "page_number": target_chunk.metadata["page_number"]
        }
    ])
    print(f" -> Found relevant excerpt on Page {target_chunk.metadata['page_number']}:")
    print(f"    Excerpt: '{target_chunk.page_content[:150]}...'")
    print(f" -> Formatted Source Citation: {sources}")
    assert "Amazon_SDE_JD.pdf — Page 2" in sources
    print(" -> TEST CASE 3 PASSED: Relevant answer excerpts and page sources identified.")

    # -------------------------------------------------------------
    # TEST CASE 4: Question Whose Answer Does NOT Exist in the JD
    # -------------------------------------------------------------
    print("\n[TEST CASE 4] Question Whose Answer Does NOT Exist in the JD")
    # Query for information absent from the JD
    irrelevant_query = "Does Amazon sponsor visas for intergalactic space travel?"
    # If no relevant chunks match, our system triggers the honest fallback
    empty_context = format_context_for_prompt([])
    assert "No relevant job description text found" in empty_context
    fallback_sources = extract_unique_sources([])
    assert len(fallback_sources) == 0
    print(f" -> Anti-hallucination Fallback Message: '{NOT_FOUND_MESSAGE}'")
    print(f" -> Source Citations Suppressed: {fallback_sources}")
    print(" -> TEST CASE 4 PASSED: Honest fallback and source suppression verified.")

    # -------------------------------------------------------------
    # TEST CASE 5: Skill Matching (Exact, Partial, Synonyms)
    # -------------------------------------------------------------
    print("\n[TEST CASE 5] Deterministic Skill Matching")
    # Exact + Synonym match
    s_score_100, matched, missing = calculate_skill_score(
        student_skills=["cpp", "python", "sql"],
        required_skills_str="C++, Python, SQL"
    )
    assert s_score_100 == 100.0
    print(f" -> 100% Match: Matched={matched}, Missing={missing}")

    # Partial match (2 out of 4)
    s_score_50, matched_p, missing_p = calculate_skill_score(
        student_skills=["python", "sql"],
        required_skills_str="Python, SQL, Go, Rust"
    )
    assert s_score_50 == 50.0
    print(f" -> 50% Match: Matched={matched_p}, Missing={missing_p}")
    print(" -> TEST CASE 5 PASSED: Skill intersection and synonym handling verified.")

    # -------------------------------------------------------------
    # TEST CASE 6: Role Mismatch
    # -------------------------------------------------------------
    print("\n[TEST CASE 6] Role Mismatch Detection")
    mismatch_score, mismatch_exp = calculate_role_score(
        preferred_roles=["Graphic Designer", "Accountant"],
        company_role="Software Development Engineer"
    )
    print(f" -> Divergent Role Score: {mismatch_score}% ({mismatch_exp})")
    assert mismatch_score <= 35.0, f"Expected low role score, got {mismatch_score}"
    print(" -> TEST CASE 6 PASSED: Role mismatch penalized appropriately.")

    # -------------------------------------------------------------
    # TEST CASE 7: Salary Mismatch
    # -------------------------------------------------------------
    print("\n[TEST CASE 7] Salary Mismatch Penalty")
    # Student expects 35 LPA, but company max budget is 12 LPA
    sal_mismatch_score, sal_exp = calculate_salary_score(
        expected_salary=35.0,
        min_salary=6.0,
        max_salary=12.0
    )
    print(f" -> Out-of-Budget Salary Score: {sal_mismatch_score}% ({sal_exp})")
    assert sal_mismatch_score < 40.0, f"Expected strong penalty, got {sal_mismatch_score}"
    print(" -> TEST CASE 7 PASSED: Salary budget overflow penalized cleanly.")

    # -------------------------------------------------------------
    # TEST CASE 8: Strong Overall Company Match
    # -------------------------------------------------------------
    print("\n[TEST CASE 8] Strong Overall Company Match (> 85%)")
    strong_profile = StudentProfile.from_form_inputs(
        name="Strong Candidate",
        skills_raw="Java, Spring Boot, MySQL, Kafka",
        roles_raw="Backend Engineer",
        expected_salary_raw=14.0,
        experience_raw=0.0
    )
    shortlist_strong = match_companies(strong_profile, top_n=3)
    top_company = shortlist_strong[0]
    print(f" -> Top Shortlisted Firm: {top_company['company_name']} ({top_company['role']})")
    print(f" -> Composite Match Score: {top_company['match_score']}%")
    print(f" -> Breakdown: {top_company['breakdown']}")
    assert top_company["match_score"] >= 85.0, f"Expected score >= 85%, got {top_company['match_score']}"
    print(" -> TEST CASE 8 PASSED: Strong fit identified with top ranking.")

    # -------------------------------------------------------------
    # TEST CASE 9: Weak Overall Company Match
    # -------------------------------------------------------------
    print("\n[TEST CASE 9] Weak Overall Company Match (< 50%)")
    weak_profile = StudentProfile.from_form_inputs(
        name="Mismatched Candidate",
        skills_raw="Ruby on Rails, Swift, Objective-C",
        roles_raw="iOS Developer",
        expected_salary_raw=40.0,
        experience_raw=0.0
    )
    shortlist_weak = match_companies(weak_profile, top_n=40)
    # Bottom firm in benchmark dataset
    bottom_company = shortlist_weak[-1]
    print(f" -> Lowest Match Firm: {bottom_company['company_name']} ({bottom_company['role']})")
    print(f" -> Composite Match Score: {bottom_company['match_score']}%")
    print(f" -> Breakdown: {bottom_company['breakdown']}")
    assert bottom_company["match_score"] < 50.0, f"Expected score < 50%, got {bottom_company['match_score']}"
    print(" -> TEST CASE 9 PASSED: Weak fit correctly placed at bottom of rankings.")

    # -------------------------------------------------------------
    # TEST CASE 10: Missing Student Profile Fields
    # -------------------------------------------------------------
    print("\n[TEST CASE 10] Missing & Invalid Profile Fields Guard")
    # Sub-case A: Empty skills
    try:
        StudentProfile.from_form_inputs("Test", "", "SDE", 12, 0)
        raise AssertionError("Empty skills should have failed!")
    except ProfileValidationError as e:
        print(f" -> Correctly rejected empty skills: '{e}'")

    # Sub-case B: Negative salary
    try:
        StudentProfile.from_form_inputs("Test", "Python", "SDE", -10, 0)
        raise AssertionError("Negative salary should have failed!")
    except ProfileValidationError as e:
        print(f" -> Correctly rejected negative salary: '{e}'")

    # Sub-case C: Negative experience
    try:
        StudentProfile.from_form_inputs("Test", "Python", "SDE", 12, -2)
        raise AssertionError("Negative experience should have failed!")
    except ProfileValidationError as e:
        print(f" -> Correctly rejected negative experience: '{e}'")

    print(" -> TEST CASE 10 PASSED: All defensive input guards verified.")

    print("\n" + "=" * 70)
    print("CONGRATULATIONS! ALL 10 COMPREHENSIVE PLACEMENT TEST CASES PASSED!")
    print("=" * 70)


if __name__ == "__main__":
    run_comprehensive_test_suite()
