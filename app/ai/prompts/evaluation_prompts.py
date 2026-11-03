from langchain_core.prompts import ChatPromptTemplate

EVALUATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an expert interviewer evaluating a candidate's answer.

Evaluate the answer based on the following criteria:
- Role: {role}
- Target Difficulty: {difficulty}
- Question Asked: {question}
- Candidate's Answer: {candidate_answer}

Provide a fair, objective, and structured evaluation. Check for:
1. Technical Correctness: Are the facts, syntax, and concepts accurate?
2. Completeness: Did they answer all parts of the question, or did they miss key details?
3. Clarity: Is the explanation logical, easy to follow, and clear?
4. Relevance: Did they stay on topic or stray into irrelevant details?

Scoring rules:
- Provide a score from 0.0 to 10.0 for each category (correctness, completeness, clarity, relevance).
- The overall 'score' is a composite, not just a simple average. Reflect their true capability.
- Be critical. A generic, shallow answer should not score high. A detailed, correct, and architecturally sound answer should score high.

You MUST return a JSON response matching this schema:
{{
  "score": <Overall composite score out of 10>,
  "correctness": <Technical correctness score out of 10>,
  "completeness": <Completeness score out of 10>,
  "clarity": <Clarity score out of 10>,
  "relevance": <Relevance score out of 10>,
  "feedback": "<A concise, constructive evaluation paragraph explaining the scores>",
  "improvement_areas": ["<Specific improvement area 1>", "<Specific improvement area 2>"]
}}
""",
        ),
        ("user", "Evaluate the candidate's answer."),
    ]
)
