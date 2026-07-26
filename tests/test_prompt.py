from src.prompt import build_system_prompt, count_tokens_approx


def test_prompt_contains_resume():
    """Prompt includes text from resume.md."""
    prompt = build_system_prompt()
    assert "Le Quoc Anh Tran" in prompt
    assert "Backend Software Engineer" in prompt


def test_prompt_contains_qa():
    """Without rag_context the prompt has no Q&A section; with it, context is appended."""
    prompt = build_system_prompt()
    # No file-read Q&A anymore — that comes via rag_context
    assert "Common Q&A" not in prompt

    rag_prompt = build_system_prompt(
        "Q: What frameworks do you use?\nA: NestJS and TypeScript.\n"
    )
    assert "Relevant Background Information" in rag_prompt
    assert "NestJS and TypeScript" in rag_prompt


def test_prompt_has_safety_preamble():
    """Prompt starts with safety instructions."""
    prompt = build_system_prompt()
    assert "You are an AI assistant that represents" in prompt
    assert "Guidelines:" in prompt


def test_token_count_positive():
    """count_tokens_approx returns a positive number."""
    result = count_tokens_approx("hello world")
    assert result > 0


def test_prompt_not_empty():
    """build_system_prompt returns a non-empty string."""
    prompt = build_system_prompt()
    assert len(prompt) > 0
