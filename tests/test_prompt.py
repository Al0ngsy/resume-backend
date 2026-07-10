from src.prompt import build_system_prompt, count_tokens_approx


def test_prompt_contains_resume():
    """Prompt includes text from resume.md."""
    prompt = build_system_prompt()
    assert "Le Quoc Anh Tran" in prompt
    assert "Backend Software Engineer" in prompt


def test_prompt_contains_qa():
    """Prompt includes Q&A pairs."""
    prompt = build_system_prompt()
    assert "Common Q&A" in prompt
    assert "Q:" in prompt
    assert "A:" in prompt


def test_prompt_has_safety_preamble():
    """Prompt starts with safety instructions."""
    prompt = build_system_prompt()
    assert "You are an AI assistant representing" in prompt
    assert "Guidelines:" in prompt


def test_token_count_positive():
    """count_tokens_approx returns a positive number."""
    result = count_tokens_approx("hello world")
    assert result > 0


def test_prompt_not_empty():
    """build_system_prompt returns a non-empty string."""
    prompt = build_system_prompt()
    assert len(prompt) > 0
