"""
Scoring module for AI Placement Intelligence Platform:
Implements deterministic, explainable mathematical formulas for matching student profiles
against company hiring requirements.

Formula:
Match Score = (0.50 * skill_score) + (0.20 * role_score) + (0.15 * salary_score) + (0.15 * hiring_score)
"""

from typing import List, Dict, Any, Tuple, Set


# Common tech synonyms for fair matching
SKILL_SYNONYMS = {
    "cpp": "c++",
    "golang": "go",
    "postgres": "postgresql",
    "node": "node.js",
    "nodejs": "node.js",
    "reactjs": "react",
    "react.js": "react",
    "dsa": "data structures",
    "algotithms": "algorithms",
    "oop": "object oriented programming",
    "oops": "object oriented programming",
    "amazon web services": "aws",
    "google cloud platform": "gcp"
}

ROLE_SYNONYMS = {
    "sde": {"software development engineer", "software engineer", "sde-1", "sde", "developer", "backend", "programmer"},
    "software engineer": {"sde", "software development engineer", "software engineer", "programmer", "developer", "backend"},
    "backend": {"backend engineer", "backend developer", "software engineer", "software development engineer", "sde", "developer"},
    "backend developer": {"backend engineer", "backend developer", "software engineer", "software development engineer", "sde"},
    "full stack": {"full stack developer", "fullstack engineer", "software engineer", "software development engineer", "sde"}
}


def normalize_skill(skill: str) -> str:
    """Normalizes skill strings for case-insensitive and alias-aware comparison."""
    cleaned = skill.strip().lower()
    return SKILL_SYNONYMS.get(cleaned, cleaned)


def calculate_skill_score(student_skills: List[str], required_skills_str: str) -> Tuple[float, List[str], List[str]]:
    """
    Computes skill match score as the percentage of company required skills
    possessed by the student.

    Returns:
        Tuple[float, List[str], List[str]]: (score 0-100, matched_skills, missing_skills)
    """
    if not required_skills_str or not required_skills_str.strip():
        return 100.0, [], []

    raw_required = [s.strip() for s in required_skills_str.split(",") if s.strip()]
    if not raw_required:
        return 100.0, [], []

    student_normalized: Set[str] = {normalize_skill(s) for s in student_skills}

    matched: List[str] = []
    missing: List[str] = []

    for req in raw_required:
        norm_req = normalize_skill(req)
        # Check direct or substring inclusion
        if norm_req in student_normalized or any(norm_req in s or s in norm_req for s in student_normalized):
            matched.append(req)
        else:
            missing.append(req)

    score = (len(matched) / len(raw_required)) * 100.0
    return round(score, 1), matched, missing


def calculate_role_score(preferred_roles: List[str], company_role: str) -> Tuple[float, str]:
    """
    Computes role match score based on title compatibility and synonyms.

    Returns:
        Tuple[float, str]: (score 0-100, role_match_explanation)
    """
    if not preferred_roles or not company_role:
        return 50.0, "Role preference unstated"

    comp_role_lower = company_role.strip().lower()
    student_roles_lower = [r.strip().lower() for r in preferred_roles]

    # Exact or substring match
    for s_role in student_roles_lower:
        if s_role == comp_role_lower or s_role in comp_role_lower or comp_role_lower in s_role:
            return 100.0, f"Direct role alignment ({company_role})"

    # Check synonym cluster (bidirectional)
    for s_role in student_roles_lower:
        synonyms = ROLE_SYNONYMS.get(s_role, set())
        if any(syn in comp_role_lower or comp_role_lower in syn for syn in synonyms):
            return 85.0, f"Strong role overlap ({company_role})"

    # Partial / general tech alignment (shared engineering keyword)
    general_tech = ["software", "engineer", "developer", "analyst", "programmer"]
    if any(any(w in s_role and w in comp_role_lower for w in general_tech) for s_role in student_roles_lower):
        return 65.0, f"Related engineering role ({company_role})"

    return 30.0, f"Role mismatch (Target: {company_role})"


def calculate_salary_score(expected_salary: float, min_salary: float, max_salary: float) -> Tuple[float, str]:
    """
    Computes salary match score based on company CTC bracket.

    Returns:
        Tuple[float, str]: (score 0-100, salary_explanation)
    """
    if min_salary <= expected_salary <= max_salary:
        return 100.0, f"Expected {expected_salary} LPA is well within company bracket ({min_salary}-{max_salary} LPA)"

    if expected_salary < min_salary:
        # Candidate expectations are easily met by company
        return 90.0, f"Expected {expected_salary} LPA is below company offer range ({min_salary}-{max_salary} LPA)"

    # Candidate expects more than company's maximum offer
    excess = expected_salary - max_salary
    # Penalty decays by 15% for every 2 LPA above max
    penalty = (excess / max_salary) * 100.0
    score = max(0.0, 100.0 - penalty)
    return round(score, 1), f"Expected {expected_salary} LPA exceeds maximum budget of {max_salary} LPA"


def calculate_hiring_history_score(hiring_history: str) -> Tuple[float, str]:
    """
    Assigns an objective score based on historical hiring consistency and volume.

    Returns:
        Tuple[float, str]: (score 0-100, hiring_explanation)
    """
    text = (hiring_history or "").lower()

    if "high volume" in text or "mass" in text:
        return 95.0, "High volume campus hiring record"
    if "tier-1" in text or "active" in text or "regular" in text:
        return 90.0, "Consistent annual campus hiring track record"
    if "selective" in text or "competitive" in text:
        return 75.0, "Selective hiring bar with rigorous assessment"
    if "off-campus" in text:
        return 70.0, "Active off-campus and lateral hiring"

    return 75.0, "Standard campus recruitment track record"


def compute_final_score(
    skill_score: float,
    role_score: float,
    salary_score: float,
    hiring_score: float,
    weights: Dict[str, float] = None
) -> float:
    """
    Calculates weighted composite match score.
    Default weights: Skills 50%, Role 20%, Salary 15%, Hiring History 15%.
    """
    if weights is None:
        weights = {
            "skill": 0.50,
            "role": 0.20,
            "salary": 0.15,
            "hiring": 0.15
        }

    total = (
        (weights["skill"] * skill_score) +
        (weights["role"] * role_score) +
        (weights["salary"] * salary_score) +
        (weights["hiring"] * hiring_score)
    )
    return round(min(100.0, max(0.0, total)), 1)
