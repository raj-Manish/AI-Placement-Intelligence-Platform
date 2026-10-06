"""
Question Answering (QA) module for AI Placement Intelligence Platform:
Connects retrieved JD context chunks with Google Gemini LLM using a strictly grounded,
anti-hallucination prompt. Generates source-backed answers with exact page citations.
"""

import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

from app.rag.retriever import retrieve_context, format_context_for_prompt, RetrievalError

load_dotenv()

NOT_FOUND_MESSAGE = "I could not find this information in the uploaded job description."


class QAError(Exception):
    """Custom exception raised when QA generation fails."""
    pass


def get_llm_client() -> ChatGoogleGenerativeAI:
    """
    Initializes and returns the Gemini Chat client.
    Temperature is set to 0.0 for deterministic, factual, zero-hallucination outputs.
    """
    api_key = os.getenv("GOOGLE_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        raise QAError(
            "GOOGLE_API_KEY is not configured in your .env file.\n"
            "Please obtain a free API key from https://aistudio.google.com/ and add it to .env:\n"
            "GOOGLE_API_KEY=AIzaSy..."
        )

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-3.8-flash",
            temperature=0.0,
            google_api_key=api_key,
            max_output_tokens=1024
        )
        return llm
    except Exception as e:
        raise QAError(f"Failed to initialize Gemini LLM client: {str(e)}")


def build_system_prompt(student_profile: Optional[Dict[str, Any]] = None) -> str:
    """
    Constructs the grounded system instructions for the LLM.
    Strictly forbids hallucination and instructs fallback if data is missing from JD.
    """
    base_prompt = (
        "You are the Placement Copilot on the AI Placement Intelligence Platform.\n"
        "Your role is to analyze company Job Descriptions (JDs) and provide factual, "
        "concise, and source-grounded guidance to students.\n\n"
        "CRITICAL RULES YOU MUST STRICTLY FOLLOW:\n"
        "1. Answer ONLY using the facts present in the provided Job Description Context excerpts.\n"
        "2. If the user's question asks for information not present in the context, you MUST output:\n"
        f"   \"{NOT_FOUND_MESSAGE}\"\n"
        "3. Do NOT make up qualifications, salaries, interview questions, or benefits that are not explicitly stated.\n"
        "4. When referring to facts, mention the specific page numbers referenced in the excerpts.\n"
        "5. Be professional, structured, and use bullet points where helpful.\n"
    )

    if student_profile:
        base_prompt += (
            "\nADDITIONAL INSTRUCTION FOR PERSONALIZED PROFILE MATCHING:\n"
            "You are also provided with the Candidate's Profile.\n"
            "When analyzing how the candidate matches the JD:\n"
            "- Clearly distinguish between: (1) what is required by the JD, "
            "(2) what the student has in their profile, and (3) your objective assessment.\n"
            "- Point out matching skills, missing skills, and prioritized areas of improvement.\n"
        )

    return base_prompt


def extract_unique_sources(chunks: List[Dict[str, Any]]) -> List[str]:
    """
    Extracts deduplicated, formatted source citations from retrieved chunks.
    Example: ['Amazon_SDE_JD.pdf — Page 2', 'Amazon_SDE_JD.pdf — Page 3']
    """
    seen = set()
    sources = []
    for chunk in chunks:
        filename = chunk.get("source_filename", "Document.pdf")
        page = chunk.get("page_number", 1)
        citation = f"{filename} — Page {page}"
        if citation not in seen:
            seen.add(citation)
            sources.append(citation)
    return sources


def ask_copilot(
    question: str,
    company_name: Optional[str] = None,
    student_profile: Optional[Dict[str, Any]] = None,
    top_k: int = 4
) -> Dict[str, Any]:
    """
    Main RAG entry point:
    1. Retrieves top-k chunks from pgvector.
    2. Builds grounded prompt with context excerpts and optional student profile.
    3. Invokes Gemini LLM.
    4. Extracts source citations.

    Args:
        question (str): Student's query.
        company_name (Optional[str]): Optional company name filter.
        student_profile (Optional[Dict]): Optional candidate profile dictionary.
        top_k (int): Number of chunks to retrieve.

    Returns:
        Dict[str, Any]: {
            "question": str,
            "answer": str,
            "sources": List[str],
            "chunks": List[Dict],
            "found": bool
        }
    """
    if not question or not question.strip():
        return {
            "question": "",
            "answer": "Please provide a valid question.",
            "sources": [],
            "chunks": [],
            "found": False
        }

    # 1. Retrieve relevant chunks
    try:
        chunks = retrieve_context(
            query=question.strip(),
            top_k=top_k,
            company_name=company_name
        )
    except RetrievalError as e:
        raise QAError(f"Retrieval error: {str(e)}")

    # 2. If no chunks found at all, return immediate honest fallback
    if not chunks:
        return {
            "question": question,
            "answer": NOT_FOUND_MESSAGE,
            "sources": [],
            "chunks": [],
            "found": False
        }

    # 3. Format context
    context_text = format_context_for_prompt(chunks)

    user_message_parts = [
        "--- RETRIEVED JOB DESCRIPTION CONTEXT ---",
        context_text,
        ""
    ]

    if student_profile:
        user_message_parts.extend([
            "--- CANDIDATE STUDENT PROFILE ---",
            f"Name: {student_profile.get('name', 'Student')}",
            f"Skills: {student_profile.get('skills', 'None specified')}",
            f"Preferred Roles: {student_profile.get('preferred_roles', 'None specified')}",
            f"Expected Salary: {student_profile.get('expected_salary', 'None specified')} LPA",
            f"Experience: {student_profile.get('experience', 0)} years",
            ""
        ])

    user_message_parts.extend([
        "--- CANDIDATE QUESTION ---",
        question.strip()
    ])

    user_content = "\n".join(user_message_parts)

    # 4. Generate response via LLM
    llm = get_llm_client()
    system_prompt = build_system_prompt(student_profile)

    try:
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_content)
        ]
        response = llm.invoke(messages)
        answer_text = response.content.strip()

        # Check if LLM determined data was absent
        is_found = NOT_FOUND_MESSAGE.lower() not in answer_text.lower()
        sources = extract_unique_sources(chunks) if is_found else []

        return {
            "question": question,
            "answer": answer_text,
            "sources": sources,
            "chunks": chunks,
            "found": is_found
        }

    except Exception as e:
        raise QAError(f"LLM generation failed: {str(e)}")


def analyze_candidate_fit(
    student_profile: Dict[str, Any],
    company_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience method for Module 1.1 Personalized Fit Analysis:
    Prompts the LLM to perform an objective fit assessment, identify matching/missing skills,
    and generate a customized interview preparation roadmap.
    """
    fit_question = (
        "Please analyze how well my student profile matches this job description:\n"
        "1. Direct Skill Matches: Which skills in my profile are required or preferred by the JD?\n"
        "2. Missing Skills / Gaps: What technologies or requirements from the JD are missing in my profile?\n"
        "3. High-Priority Topics: What sections or requirements from the JD are most critical for me?\n"
        "4. Actionable Preparation Plan: What should I focus on studying to crack the interview for this specific role?"
    )

    return ask_copilot(
        question=fit_question,
        company_name=company_name,
        student_profile=student_profile,
        top_k=5
    )
