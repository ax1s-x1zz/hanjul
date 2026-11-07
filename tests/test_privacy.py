from core import privacy


def test_phone_email_url_and_long_digits_are_masked():
    text = "010-1234-5678 test@example.com https://a.com 123456"
    clean = privacy.strip_pii(text)
    assert "010-1234-5678" not in clean
    assert "test@example.com" not in clean
    assert "https://a.com" not in clean
    assert "123456" not in clean


def test_school_and_teacher_are_masked():
    text = "진성고등학교 김철수 선생님 수업"
    clean = privacy.strip_pii(text, school_name="진성고등학교")
    assert "진성고등학교" not in clean
    assert "김철수" not in clean
    assert "○○고" in clean


def test_profanity_guard():
    assert privacy.contains_profanity("씨발 진짜")
    assert not privacy.contains_profanity("미적분 문제풀이")


def test_sanitize_reports_change():
    clean, changed = privacy.sanitize_for_public("010-1234-5678 오늘 배움")
    assert changed is True
    assert "010-1234-5678" not in clean

    clean2, changed2 = privacy.sanitize_for_public("오늘 배움")
    assert changed2 is False


def test_k_anonymity():
    assert privacy.k_anonymized(5) is True
    assert privacy.k_anonymized(4) is False
