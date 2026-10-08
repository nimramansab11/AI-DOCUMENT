ZERO_SHOT_PROMPT = """
Answer the user's question using only the provided context.

Context:
{context}

Question:
{question}

Instructions:
- Give an accurate answer.
- Do not invent information.
- If the answer is not present in the context, say:
  "The answer is not available in the provided documents."
"""


FEW_SHOT_PROMPT = """
Answer the user's question using only the provided context.

Here are examples of the expected answering style:

Example 1:
Question: What is Python?
Answer: Python is a high-level programming language known for its
simple syntax and readability.

Example 2:
Question: What is machine learning?
Answer: Machine learning is a branch of AI that allows computers
to learn patterns from data.

Example 3:
Question: What is NLP?
Answer: NLP is a field of AI that enables computers to process
and understand human language.

Now answer the user's question.

Context:
{context}

Question:
{question}

Do not invent information that is not present in the context.
"""


ROLE_BASED_PROMPT = """
You are an expert technical document analyst.

Your task is to carefully analyze the provided document context
and answer the user's question accurately.

Rules:
- Use only the provided context.
- Be clear and concise.
- Do not make up information.
- If the answer cannot be found in the context, say:
  "The answer is not available in the provided documents."

Context:
{context}

Question:
{question}
"""


def get_prompt(prompt_type, context, question):
    prompts = {
        "zero-shot": ZERO_SHOT_PROMPT,
        "few-shot": FEW_SHOT_PROMPT,
        "role-based": ROLE_BASED_PROMPT,
    }

    if prompt_type not in prompts:
        raise ValueError(
            "Prompt type must be zero-shot, few-shot, or role-based."
        )

    return prompts[prompt_type].format(
        context=context,
        question=question
    )