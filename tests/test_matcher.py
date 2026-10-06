"""
Test script for Phase 7: Deterministic Company Matching Engine
Verifies:
1. Mathematical skill scoring and synonym awareness.
2. Role matching and synonym clusters.
3. Salary elasticity and bracket bounds.
4. Hiring history weighting.
5. Composite formula calculation.
6. Multi-firm shortlisting with full explainability breakdowns.
"""

import os
import sys

# Ensure root workspace is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.matching.profile import StudentProfile
from app.matching.scoring import (
    calculate_skill_score,
    calculate_role_score,
    calculate_salary_score,
    calculate_hiring_history_score,
    compute_final_score
)
from app.matching.matcher import match_companies


def run_tests():
    print("=" * 65)
    print("PHASE 7 TEST: Deterministic Matching Engine & Scoring")
    print("=" * 65)

    # TEST 1: Skill Score & Synonym Awareness
    print("\n[Test 1] Testing Skill Scoring & Synonyms...")
    student_skills = ["C++", "Python", "SQL"]
    required_str = "cpp, Python, SQL"
    score, matched, missing = calculate_skill_score(student_skills, required_str)
    print(f" -> Score: {score}%, Matched: {matched}, Missing: {missing}")
    assert score == 100.0, f"Expected 100.0% with synonym matching, got {score}"
    assert len(missing) == 0

    partial_req = "Python, SQL, Go, Kubernetes"
    score_p, matched_p, missing_p = calculate_skill_score(student_skills, partial_req)
    print(f" -> Partial match score: {score_p}%, Matched: {matched_p}, Missing: {missing_p}")
    assert score_p == 50.0, f"Expected 50.0% for 2/4 skills, got {score_p}"
    print(" -> Test 1 PASSED: Skill score and synonyms verified.")

    # TEST 2: Role Score & Alignment
    print("\n[Test 2] Testing Role Scoring...")
    score_exact, _ = calculate_role_score(["Backend Developer"], "Backend Developer")
    assert score_exact == 100.0
    score_syn, _ = calculate_role_score(["Backend"], "Software Development Engineer")
    assert score_syn > 60.0
    score_mismatch, _ = calculate_role_score(["Frontend"], "Data Scientist")
    assert score_mismatch <= 35.0
    print(f" -> Exact: {score_exact}%, Related: {score_syn}%, Mismatch: {score_mismatch}%")
    print(" -> Test 2 PASSED: Role scoring verified.")

    # TEST 3: Salary Score Elasticity
    print("\n[Test 3] Testing Salary Bracket Elasticity...")
    # Case A: Inside range
    score_in, exp_in = calculate_salary_score(expected_salary=15.0, min_salary=12.0, max_salary=24.0)
    assert score_in == 100.0
    # Case B: Below min
    score_below, exp_below = calculate_salary_score(expected_salary=10.0, min_salary=14.0, max_salary=28.0)
    assert score_below == 90.0
    # Case C: Exceeds max budget
    score_above, exp_above = calculate_salary_score(expected_salary=25.0, min_salary=8.0, max_salary=16.0)
    assert score_above < 100.0
    print(f" -> Within bracket: {score_in}%, Below min: {score_below}%, Exceeds max: {score_above}%")
    print(" -> Test 3 PASSED: Salary scoring verified.")

    # TEST 4: Hiring History Score
    print("\n[Test 4] Testing Hiring History Score...")
    score_high, _ = calculate_hiring_history_score("High Volume Campus Tech Hiring")
    assert score_high == 95.0
    score_sel, _ = calculate_hiring_history_score("Selective SDE-1 Hiring")
    assert score_sel == 75.0
    print(f" -> High Volume: {score_high}%, Selective: {score_sel}%")
    print(" -> Test 4 PASSED: Hiring history scoring verified.")

    # TEST 5: Composite Weighted Formula
    print("\n[Test 5] Testing Composite Formula Math...")
    # 0.50*100 + 0.20*100 + 0.15*100 + 0.15*100 = 100.0
    assert compute_final_score(100, 100, 100, 100) == 100.0
    # 0.50*50 + 0.20*80 + 0.15*90 + 0.15*70 = 25 + 16 + 13.5 + 10.5 = 65.0
    comp_score = compute_final_score(50, 80, 90, 70)
    assert comp_score == 65.0, f"Expected 65.0, got {comp_score}"
    print(f" -> Composite score calculation: {comp_score}%")
    print(" -> Test 5 PASSED: Composite formula verified.")

    # TEST 6: Multi-Company Shortlisting & Full Breakdown
    print("\n[Test 6] Testing End-to-End Company Shortlisting...")
    profile = StudentProfile.from_form_inputs(
        name="Test Student",
        skills_raw="Java, Spring Boot, MySQL, Kafka",
        roles_raw="Backend Engineer",
        expected_salary_raw=12.0,
        experience_raw=0.0
    )
    shortlist = match_companies(profile=profile, top_n=5)
    print(f" -> Shortlisted {len(shortlist)} companies.")
    assert len(shortlist) > 0, "No companies shortlisted!"

    top_pick = shortlist[0]
    print(f"\n[Rank 1 Company]: {top_pick['company_name']} - Role: {top_pick['role']}")
    print(f" -> Total Match Score: {top_pick['match_score']}%")
    print(f" -> Score Breakdown: {top_pick['breakdown']}")
    print(f" -> Matched Skills: {top_pick['matched_skills']}")
    print(f" -> Missing Skills: {top_pick['missing_skills']}")
    print(f" -> Explainability Reasons:")
    for r in top_pick["reasons"]:
        print(f"    * {r}")

    assert "skill_score" in top_pick["breakdown"]
    assert "role_score" in top_pick["breakdown"]
    assert "salary_score" in top_pick["breakdown"]
    assert "hiring_score" in top_pick["breakdown"]
    assert len(top_pick["reasons"]) == 4

    print("\n -> Test 6 PASSED: Transparent, explainable matching verified.")

    print("\n" + "=" * 65)
    print("ALL PHASE 7 MATCHING ENGINE TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
