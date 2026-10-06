"""
Test script for Phase 6: Student Profile Module
Verifies:
1. Parsing of comma-separated skills and roles.
2. Serialization to dictionary.
3. Defensive validation for missing/empty skills, negative salary, and negative experience.
"""

import os
import sys

# Ensure root workspace is on python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.matching.profile import (
    StudentProfile,
    ProfileValidationError,
    validate_profile_inputs
)


def run_tests():
    print("=" * 65)
    print("PHASE 6 TEST: Student Profile Parsing & Defensive Validation")
    print("=" * 65)

    # TEST 1: Valid Profile Creation
    print("\n[Test 1] Parsing Valid Student Profile...")
    profile = StudentProfile.from_form_inputs(
        name="Rahul Sharma",
        skills_raw="C++, Python, SQL, React, Node.js, MongoDB",
        roles_raw="Software Engineer, Backend Developer",
        expected_salary_raw="14.5",
        experience_raw="0.0"
    )
    print(f" -> Created Profile: {profile}")
    assert profile.name == "Rahul Sharma"
    assert len(profile.skills) == 6
    assert "C++" in profile.skills
    assert "Python" in profile.skills
    assert profile.expected_salary == 14.5
    assert profile.experience == 0.0

    profile_dict = profile.to_dict()
    assert "skills" in profile_dict
    assert "preferred_roles" in profile_dict
    print(" -> Serialization dictionary verified.")
    print(" -> Test 1 PASSED: Valid profile creation verified.")

    # TEST 2: Defensive Validation - Empty Skills
    print("\n[Test 2] Defensive Validation: Empty Skills...")
    try:
        StudentProfile.from_form_inputs(
            name="Test",
            skills_raw="   ",
            roles_raw="SDE",
            expected_salary_raw=12,
            experience_raw=0
        )
        print(" -> FAILED: Expected ProfileValidationError was not raised.")
    except ProfileValidationError as e:
        print(f" -> Correctly caught ProfileValidationError: '{e}'")
        print(" -> Test 2 PASSED: Empty skills guard verified.")

    # TEST 3: Defensive Validation - Negative / Invalid Salary
    print("\n[Test 3] Defensive Validation: Negative Salary...")
    try:
        StudentProfile.from_form_inputs(
            name="Test",
            skills_raw="Python, SQL",
            roles_raw="SDE",
            expected_salary_raw="-5",
            experience_raw=0
        )
        print(" -> FAILED: Expected ProfileValidationError was not raised.")
    except ProfileValidationError as e:
        print(f" -> Correctly caught ProfileValidationError: '{e}'")
        print(" -> Test 3 PASSED: Negative salary guard verified.")

    # TEST 4: Defensive Validation - Negative Experience
    print("\n[Test 4] Defensive Validation: Negative Experience...")
    try:
        StudentProfile.from_form_inputs(
            name="Test",
            skills_raw="Python, SQL",
            roles_raw="SDE",
            expected_salary_raw=12,
            experience_raw="-1"
        )
        print(" -> FAILED: Expected ProfileValidationError was not raised.")
    except ProfileValidationError as e:
        print(f" -> Correctly caught ProfileValidationError: '{e}'")
        print(" -> Test 4 PASSED: Negative experience guard verified.")

    # TEST 5: Lightweight Validation Helper
    print("\n[Test 5] Validating validate_profile_inputs Helper...")
    is_valid, err = validate_profile_inputs("Python, C++", "SDE", 12, 0)
    assert is_valid is True
    assert err is None

    is_invalid, err_msg = validate_profile_inputs("", "SDE", 12, 0)
    assert is_invalid is False
    assert err_msg is not None
    print(f" -> Returned user error message: '{err_msg}'")
    print(" -> Test 5 PASSED: Validation helper verified.")

    print("\n" + "=" * 65)
    print("ALL PHASE 6 STUDENT PROFILE TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 65)


if __name__ == "__main__":
    run_tests()
