"""
Scoring module for AI Placement Intelligence Platform:
Implements deterministic, explainable mathematical formulas for matching student profiles
against company hiring requirements.

Formula:
Match Score = (0.50 * skill_score) + (0.20 * role_score) + (0.15 * salary_score) + (0.15 * hiring_score)
"""

from typing import List, Dict, Any, Tuple, Set, Optional


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


# Canonical Branch aliases for campus eligibility checking
BRANCH_ALIASES = {
    "computer science": {"cse", "cs", "computer science", "comp sci"},
    "cse": {"cse", "cs", "computer science", "comp sci"},
    "cs": {"cse", "cs", "computer science", "comp sci"},
    "information technology": {"it", "information technology", "infotech"},
    "it": {"it", "information technology", "infotech"},
    "electronics & communication": {"ece", "electronics", "electronics & communication", "electronics and communication", "etc"},
    "electronics": {"ece", "electronics", "electronics & communication", "electronics and communication"},
    "ece": {"ece", "electronics", "electronics & communication", "electronics and communication"},
    "electrical engineering": {"ee", "eee", "electrical", "electrical engineering"},
    "electrical": {"ee", "eee", "electrical", "electrical engineering"},
    "ee": {"ee", "eee", "electrical", "electrical engineering"},
    "mechanical engineering": {"me", "mech", "mechanical", "mechanical engineering"},
    "mechanical": {"me", "mech", "mechanical", "mechanical engineering"},
    "me": {"me", "mech", "mechanical", "mechanical engineering"},
    "civil engineering": {"ce", "civil", "civil engineering"},
    "civil": {"ce", "civil", "civil engineering"},
    "ce": {"ce", "civil", "civil engineering"},
    "data science / ai": {"ds", "data science", "ai", "artificial intelligence", "data science / ai"},
    "mathematics": {"math", "mathematics", "mnc", "mathematics and computing"}
}


def parse_hiring_history_details(hiring_history: str) -> Tuple[str, List[str], Optional[float]]:
    """
    Parses structured hiring history into:
    (base_description, eligible_branches, min_cpi)

    Example:
    'Tier-1 Campus Hiring (High Volume) | Eligible: CSE, IT, ECE | Min CPI: 7.0'
    -> ('Tier-1 Campus Hiring (High Volume)', ['cse', 'it', 'ece'], 7.0)
    """
    if not hiring_history:
        return "Standard campus recruitment track record", [], None

    parts = [p.strip() for p in hiring_history.split("|")]
    base_desc = parts[0] if parts else hiring_history

    eligible_branches: List[str] = []
    min_cpi: Optional[float] = None

    for part in parts[1:]:
        p_lower = part.lower()
        if p_lower.startswith("eligible:"):
            branches_str = part.split(":", 1)[1].strip()
            if "all" in branches_str.lower():
                eligible_branches = ["all"]
            else:
                eligible_branches = [b.strip().lower() for b in branches_str.split(",") if b.strip()]
        elif p_lower.startswith("min cpi:"):
            try:
                cpi_str = part.split(":", 1)[1].strip().replace("+", "")
                min_cpi = float(cpi_str)
            except ValueError:
                pass

    return base_desc, eligible_branches, min_cpi


def is_branch_eligible(candidate_branch: str, eligible_branches: List[str]) -> bool:
    """Checks if candidate branch is accepted by company campus criteria."""
    if not eligible_branches or "all" in eligible_branches:
        return True

    c_lower = (candidate_branch or "").strip().lower()
    c_aliases = BRANCH_ALIASES.get(c_lower, {c_lower})

    for elig in eligible_branches:
        elig_clean = elig.strip().lower()
        if elig_clean in c_aliases or any(a in elig_clean or elig_clean in a for a in c_aliases):
            return True

    return False


def calculate_hiring_history_score(
    hiring_history: str,
    candidate_cpi: Optional[float] = None,
    candidate_branch: Optional[str] = None
) -> Tuple[float, str]:
    """
    Assigns an objective score based on historical hiring consistency, volume,
    academic branch eligibility, and minimum CPI cutoffs.

    Returns:
        Tuple[float, str]: (score 0-100, hiring_explanation)
    """
    base_desc, eligible_branches, min_cpi = parse_hiring_history_details(hiring_history)
    text = (base_desc or hiring_history or "").lower()

    # 1. Base Score from campus track record / volume
    if "high volume" in text or "mass" in text:
        base_score = 95.0
        track_desc = "High volume campus hiring record"
    elif "tier-1" in text or "active" in text or "regular" in text:
        base_score = 90.0
        track_desc = "Consistent annual campus hiring track record"
    elif "selective" in text or "competitive" in text:
        base_score = 75.0
        track_desc = "Selective hiring bar with rigorous assessment"
    elif "off-campus" in text:
        base_score = 70.0
        track_desc = "Active off-campus and lateral hiring"
    else:
        base_score = 75.0
        track_desc = "Standard campus recruitment track record"

    score = base_score
    notes = [track_desc]

    # 2. Branch Eligibility Check
    if candidate_branch and eligible_branches and "all" not in eligible_branches:
        if is_branch_eligible(candidate_branch, eligible_branches):
            notes.append(f"Branch eligible ({candidate_branch})")
        else:
            score -= 30.0
            elig_disp = ", ".join(b.upper() for b in eligible_branches)
            notes.append(f"Branch mismatch (Candidate: {candidate_branch}, Target: {elig_disp})")

    # 3. CPI Cutoff Check
    if candidate_cpi is not None and min_cpi is not None:
        if candidate_cpi >= min_cpi:
            notes.append(f"CPI {candidate_cpi:.1f} meets cutoff ({min_cpi:.1f})")
        else:
            deficit = min_cpi - candidate_cpi
            cpi_penalty = min(35.0, deficit * 20.0)
            score -= cpi_penalty
            notes.append(f"CPI {candidate_cpi:.1f} below cutoff of {min_cpi:.1f}")

    final_score = round(max(0.0, min(100.0, score)), 1)
    explanation = " | ".join(notes)
    return final_score, explanation


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
