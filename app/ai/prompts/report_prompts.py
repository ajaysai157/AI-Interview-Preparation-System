from langchain_core.prompts import ChatPromptTemplate

REPORT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a principal evaluator preparing a final interview performance report.

Review the candidate's complete interview history:
- Role: {role}
- Experience Level: {experience_level}
- Interview History: {history}

Analyze the history to synthesize overall performance metrics:
1. Overall Score: Aggregate candidate's performance across all questions (scale 0-100).
2. Strengths: Identify 2-4 key capabilities or concepts they demonstrated well.
3. Weaknesses: Identify 2-4 primary gaps or development areas.
4. Topic-wise Performance: Categorize questions by topic and assign a percentage performance (0-100) for each topic.
5. Recommendations: Provide specific, actionable steps (e.g. books, topics, design patterns) to improve.
6. Summary: Provide a high-level summary paragraph.

You MUST return a JSON response matching this schema:
{{
  "overall_score": <Aggregate overall score out of 100>,
  "strengths": ["<Strength 1>", "<Strength 2>"],
  "weaknesses": ["<Weakness 1>", "<Weakness 2>"],
  "topic_performance": {{
     "<Topic A>": <Score out of 100>,
     "<Topic B>": <Score out of 100>
  }},
  "recommendations": ["<Recommendation 1>", "<Recommendation 2>"],
  "interview_summary": "<Descriptive paragraph summarizing overall performance>"
}}
""",
        ),
        ("user", "Generate the final performance report."),
    ]
)
