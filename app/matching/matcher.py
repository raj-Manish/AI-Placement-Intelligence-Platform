"""
Company Matcher module for AI Placement Intelligence Platform:
Evaluates benchmark target companies against a student profile, computes deterministic
match scores, and produces fully explainable reasoning breakdowns.
"""

import os
import csv
from typing import List, Dict, Any, Optional
from app.matching.profile import StudentProfile
from app.matching.scoring import (
    calculate_skill_score,
    calculate_role_score,
    calculate_salary_score,
    calculate_hiring_history_score,
    compute_final_score
)
from app.database.connection import get_session_factory
from app.database.models import Company


def load_all_companies() -> List[Dict[str, Any]]:
    """
    Loads benchmark companies from PostgreSQL database if available;
    transparently falls back to data/companies.csv if the database is not initialized.
    """
    companies = []

    # 1. Try loading from database
    try:
        SessionFactory = get_session_factory()
        with SessionFactory() as session:
            db_companies = session.query(Company).all()
            if db_companies:
                for c in db_companies:
                    companies.append({
                        "company_name": c.company_name,
                        "role": c.role,
                        "required_skills": c.required_skills,
                        "min_salary": float(c.min_salary),
                        "max_salary": float(c.max_salary),
                        "hiring_history": c.hiring_history
                    })
                return companies
    except Exception:
        # Fallback to CSV if DB is not running or accessible
        pass

    # 2. Fallback to data/companies.csv
    csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "companies.csv")
    csv_path = os.path.abspath(csv_path)

    if os.path.exists(csv_path):
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                companies.append({
                    "company_name": row["company_name"].strip(),
                    "role": row["role"].strip(),
                    "required_skills": row["required_skills"].strip(),
                    "min_salary": float(row["min_salary"]),
                    "max_salary": float(row["max_salary"]),
                    "hiring_history": row["hiring_history"].strip()
                })

    return companies


def match_companies(
    profile: StudentProfile,
    top_n: int = 10,
    min_score: float = 0.0
) -> List[Dict[str, Any]]:
    """
    Scores all target firms against the candidate profile and returns
    a ranked list with detailed explainable score breakdowns.

    Args:
        profile (StudentProfile): Validated candidate profile.
        top_n (int): Number of top shortlisted firms to return.
        min_score (float): Optional minimum match score threshold.

    Returns:
        List[Dict[str, Any]]: Ranked companies with scores, breakdowns, and explanations.
    """
    all_companies = load_all_companies()
    if not all_companies:
        return []

    ranked_results: List[Dict[str, Any]] = []

    for comp in all_companies:
        # 1. Individual component scores
        skill_score, matched_skills, missing_skills = calculate_skill_score(
            student_skills=profile.skills,
            required_skills_str=comp["required_skills"]
        )

        role_score, role_explanation = calculate_role_score(
            preferred_roles=profile.preferred_roles,
            company_role=comp["role"]
        )

        salary_score, salary_explanation = calculate_salary_score(
            expected_salary=profile.expected_salary,
            min_salary=comp["min_salary"],
            max_salary=comp["max_salary"]
        )

        hiring_score, hiring_explanation = calculate_hiring_history_score(
            hiring_history=comp["hiring_history"]
        )

        # 2. Weighted total score
        total_score = compute_final_score(
            skill_score=skill_score,
            role_score=role_score,
            salary_score=salary_score,
            hiring_score=hiring_score
        )

        if total_score < min_score:
            continue

        # 3. Formulate transparent explanations ("Why this score?")
        reasons = [
            f"Skills: Matched {len(matched_skills)} of {len(matched_skills) + len(missing_skills)} required technologies ({skill_score}%)",
            f"Role: {role_explanation} ({role_score}%)",
            f"Salary: {salary_explanation} ({salary_score}%)",
            f"Hiring Track Record: {hiring_explanation} ({hiring_score}%)"
        ]

        result_entry = {
            "company_name": comp["company_name"],
            "role": comp["role"],
            "match_score": total_score,
            "salary_range": f"{comp['min_salary']} - {comp['max_salary']} LPA",
            "required_skills": comp["required_skills"],
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "breakdown": {
                "skill_score": skill_score,
                "role_score": role_score,
                "salary_score": salary_score,
                "hiring_score": hiring_score
            },
            "reasons": reasons
        }

        ranked_results.append(result_entry)

    # Sort descending by final match score
    ranked_results.sort(key=lambda x: x["match_score"], reverse=True)

    return ranked_results[:top_n]
