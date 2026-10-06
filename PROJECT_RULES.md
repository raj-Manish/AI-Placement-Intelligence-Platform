# PROJECT RULES: AI Placement Intelligence Platform

## Core Constraints
1. **No Docker / No Microservices**: Run directly with standard Python and PostgreSQL to keep deployment and interview explanations straightforward.
2. **No Over-Engineering**: Readable, modular Python over complex design patterns or clever abstractions.
3. **No Fake Implementations**: Use real PDF chunking, real embeddings, real PostgreSQL vector similarity search, and real LLM generation.
4. **Source-Backed Answers**: The RAG pipeline must always cite page numbers from the uploaded JD.
5. **Anti-Hallucination**: If information is absent from the JD, the system must clearly output:
   *"I could not find this information in the uploaded job description."*
6. **Deterministic Matching Engine**: Module 2 uses explainable mathematical scoring (skill, role, salary, hiring history) — never an LLM for the core match calculation.
7. **Demo Data Transparency**: Company hiring data is benchmark demo data (30-50 realistic records) and explicitly identified as such.
8. **Interview Explainability First**: Every component must have clear answers to "Why this technology?", "How does it work?", and "What are the limitations?".
