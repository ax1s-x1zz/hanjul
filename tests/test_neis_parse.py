from datetime import date

from core import neis


def test_parse_rows_success():
    payload = {
        "hisTimetable": [
            {"head": [{"list_total_count": 1}]},
            {
                "row": [
                    {"PERIO": "1", "ITRT_CNTNT": "미적분Ⅰ", "CLRM_NM": "5"},
                    {"PERIO": "2", "ITRT_CNTNT": "영어Ⅱ", "CLRM_NM": "5"},
                ]
            },
        ]
    }
    rows = neis.parse_rows(payload, "hisTimetable")
    assert len(rows) == 2
    assert rows[0]["ITRT_CNTNT"] == "미적분Ⅰ"


def test_parse_rows_error_payload():
    payload = {"RESULT": {"CODE": "INFO-200", "MESSAGE": "해당하는 데이터가 없습니다."}}
    assert neis.parse_rows(payload, "hisTimetable") == []


def test_subject_normalization_and_events():
    assert neis.normalize_subject("수학Ⅱ") == "수학2"
    assert neis.normalize_subject("미적분Ⅰ") == "미적분1"
    assert neis.is_event_subject("숙박형 현장체험학습") is True
    assert neis.is_event_subject("미적분Ⅰ") is False


def test_find_exams_excludes_holidays():
    events = [
        {"date": "20261214", "event": "2학기 기말고사", "holiday": ""},
        {"date": "20261119", "event": "재량휴업일(대학수학능력시험일)", "holiday": "휴업일"},
    ]
    exams = neis.find_exams(events)
    assert len(exams) == 1
    assert exams[0]["event"] == "2학기 기말고사"


def test_next_exam():
    events = [
        {"date": "20261214", "event": "2학기 기말고사", "holiday": ""},
        {"date": "20261220", "event": "모의고사", "holiday": ""},
    ]
    exam = neis.next_exam(events, date(2026, 11, 7))
    assert exam["event"] == "2학기 기말고사"

    assert neis.next_exam(events, date(2027, 1, 1)) is None


def test_demo_exam_shape():
    exam = neis.demo_exam()
    assert exam["is_demo"] is True
    assert len(exam["date"]) == 8
