SYSTEM_INSTRUCTION = """You are an expert article summarizer.

Summarize the provided article faithfully.

Rules:
- Preserve the original meaning.
- Do not invent facts.
- Do not add information that is not supported by the article.
- Focus on the most important ideas, claims, findings, and conclusions.
- Remove repetition and unnecessary details.
- Use clear, neutral language.
- Do not mention that you are an AI.
- Do not discuss your hidden reasoning."""

STYLE_INSTRUCTIONS: dict[str, str] = {
    "brief": "Create a concise summary in about 5 bullet points.",
    "standard": (
        "Create a structured summary with:\n"
        "1. Overview\n"
        "2. Key Points\n"
        "3. Conclusion\n\n"
        "Keep it concise but informative."
    ),
    "detailed": (
        "Create a detailed summary with:\n"
        "1. Main topic\n"
        "2. Key arguments or findings\n"
        "3. Important facts\n"
        "4. Supporting details\n"
        "5. Conclusion\n\n"
        "Retain important nuance while avoiding unnecessary repetition."
    ),
}


def build_prompts(text: str, style: str) -> tuple[str, str]:
    style_instruction = STYLE_INSTRUCTIONS.get(style, STYLE_INSTRUCTIONS["standard"])
    user_prompt = f"{style_instruction}\n\nArticle:\n{text}"
    return SYSTEM_INSTRUCTION, user_prompt
