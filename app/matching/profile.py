"""
Student Profile module for AI Placement Intelligence Platform:
Defines the candidate profile data structures, input validation, and normalization.
Supports skill parsing and provides structured context for both RAG analysis and the matching engine.
"""

from typing import List, Dict, Any, Optional, Tuple


class ProfileValidationError(Exception):
    """Custom exception raised when student profile validation fails."""
    pass


class StudentProfile:
    """
    Represents a student's placement profile.
    Attributes:
        name (str): Candidate's name.
        skills (List[str]): Cleaned list of technical skills.
        preferred_roles (List[str]): Cleaned list of target roles (e.g. ['SDE', 'Backend Engineer']).
        expected_salary (float): Expected CTC in LPA (Lakhs Per Annum).
        experience (float): Years of professional experience (e.g. 0 for freshers).
    """

    def __init__(
        self,
        name: str = "Student",
        skills: Optional[List[str]] = None,
        preferred_roles: Optional[List[str]] = None,
        expected_salary: float = 12.0,
        experience: float = 0.0
    ):
        self.name = name.strip() if name else "Student"
        self.skills = skills or []
        self.preferred_roles = preferred_roles or []
        self.expected_salary = float(expected_salary)
        self.experience = float(experience)

    @classmethod
    def from_form_inputs(
        cls,
        name: str,
        skills_raw: str,
        roles_raw: str,
        expected_salary_raw: Any,
        experience_raw: Any = 0.0
    ) -> "StudentProfile":
        """
        Factory method to parse and validate raw string inputs from the UI.
        Handles comma-separated skills and roles.
        """
        # 1. Parse and normalize skills
        if not skills_raw or not skills_raw.strip():
            raise ProfileValidationError("Please provide at least one technical skill.")

        raw_skill_list = [s.strip() for s in skills_raw.replace("\n", ",").split(",") if s.strip()]
        if not raw_skill_list:
            raise ProfileValidationError("Skills cannot be empty. Please enter your technical skills.")

        # 2. Parse and normalize preferred roles
        if not roles_raw or not roles_raw.strip():
            raise ProfileValidationError("Please specify at least one preferred role (e.g., SDE, Backend Developer).")

        raw_role_list = [r.strip() for r in roles_raw.replace("\n", ",").split(",") if r.strip()]
        if not raw_role_list:
            raise ProfileValidationError("Preferred roles cannot be empty.")

        # 3. Validate salary
        try:
            salary = float(expected_salary_raw)
            if salary <= 0:
                raise ProfileValidationError("Expected salary must be greater than 0 LPA.")
            if salary > 200:
                raise ProfileValidationError("Expected salary appears unrealistic (> 200 LPA).")
        except (ValueError, TypeError):
            raise ProfileValidationError("Expected salary must be a valid number (e.g. 12 or 14.5).")

        # 4. Validate experience
        try:
            exp = float(experience_raw)
            if exp < 0:
                raise ProfileValidationError("Experience cannot be negative.")
            if exp > 40:
                raise ProfileValidationError("Experience years appears unrealistic (> 40 years).")
        except (ValueError, TypeError):
            raise ProfileValidationError("Experience must be a valid number (e.g. 0 for freshers).")

        return cls(
            name=name or "Candidate",
            skills=raw_skill_list,
            preferred_roles=raw_role_list,
            expected_salary=salary,
            experience=exp
        )

    def to_dict(self) -> Dict[str, Any]:
        """Serializes the profile to a dictionary for LLM context and matching."""
        return {
            "name": self.name,
            "skills": ", ".join(self.skills),
            "skills_list": self.skills,
            "preferred_roles": ", ".join(self.preferred_roles),
            "preferred_roles_list": self.preferred_roles,
            "expected_salary": self.expected_salary,
            "experience": self.experience
        }

    def __repr__(self) -> str:
        return (
            f"<StudentProfile(name='{self.name}', skills={len(self.skills)}, "
            f"salary={self.expected_salary} LPA, exp={self.experience}y)>"
        )


def validate_profile_inputs(
    skills_text: str,
    roles_text: str,
    salary: Any,
    experience: Any
) -> Tuple[bool, Optional[str]]:
    """
    Lightweight validator returning a success boolean and a user-friendly error message.
    """
    try:
        StudentProfile.from_form_inputs(
            name="Check",
            skills_raw=skills_text,
            roles_raw=roles_text,
            expected_salary_raw=salary,
            experience_raw=experience
        )
        return True, None
    except ProfileValidationError as e:
        return False, str(e)
