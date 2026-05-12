import os
from anthropic import Anthropic

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

_HR_CONTACT = "Jane Smith at hr@abcwidgets.fake or (555) 867-5309"

_SYSTEM_TEMPLATE = """\
You are an HR assistant for ABC Widgets. Answer employee questions strictly using the HR document excerpts provided below.

Rules:
1. Only answer questions about ABC Widgets HR policies using the provided context.
2. Respond in {language}.
3. If the question is unrelated to HR (e.g., general knowledge, coding, current events, personal advice), politely decline and redirect the employee to ask HR-related questions.
4. If the answer is not present in the context, say so plainly and direct the employee to contact {hr_contact}.
5. Reference sources using [N] notation where N matches the numbered context entries below.
6. Never fabricate information.

Context:
{context}"""


def build_system_prompt(chunks: list[dict], language: str) -> str:
    language_name = "English" if language == "en" else "Spanish"
    context_parts = [
        f"[{i}] {c['source_file']}, p.{c['page_number']}:\n{c['text']}"
        for i, c in enumerate(chunks, 1)
    ]
    context = "\n\n".join(context_parts) if context_parts else "(No relevant context found.)"
    return _SYSTEM_TEMPLATE.format(
        language=language_name,
        hr_contact=_HR_CONTACT,
        context=context,
    )


def chat(
    message: str,
    chunks: list[dict],
    language: str,
    history: list[dict],
) -> str:
    system_prompt = build_system_prompt(chunks, language)
    messages = history + [{"role": "user", "content": message}]
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text
