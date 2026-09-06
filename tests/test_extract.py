from app.extract import (
    build_karte_draft,
    extract_allergy_mentions,
    extract_medications,
    extract_symptoms,
    guess_chief_complaint,
)


def test_extract_symptoms_detects_known_keyword():

    text = (
        "昨日から冷たいものがしみるんです。"
        "あと噛むと痛いです。"
    )

    symptoms = extract_symptoms(text)

    normalized_names = {
        s.normalized
        for s in symptoms
    }

    assert (
        "冷水痛（冷たいものがしみる）"
        in normalized_names
    )

    assert (
        "咬合痛（噛むと痛い）"
        in normalized_names
    )


def test_extract_medications_detects_known_keyword():

    text = (
        "今ワーファリンを飲んでいます。"
        "あとロキソニンも持ってます。"
    )

    meds = extract_medications(text)

    categories = {
        m.category
        for m in meds
    }

    assert (
        "抗血栓薬（血をサラサラにする薬）"
        in categories
    )

    assert (
        "鎮痛剤"
        in categories
    )


def test_extract_allergy_mentions():

    text = (
        "以前ペニシリンでアレルギーが"
        "出たことがあります。"
    )

    mentions = extract_allergy_mentions(text)

    assert len(mentions) >= 1


def test_guess_chief_complaint_returns_something_reasonable():

    text = (
        "先生、奥歯が痛いです。"
        "特に冷たいものを飲むとしみます。"
    )

    complaint = guess_chief_complaint(text)

    assert complaint is not None
    assert "痛い" in complaint


def test_build_karte_draft_full_pipeline():

    text = (
        "右下の奥歯が噛むと痛いです。"
        "ワーファリンを飲んでいます。"
        "アレルギーは特にありません。"
    )

    draft = build_karte_draft(text)

    assert draft.raw_transcript == text

    assert draft.needs_manual_review is True

    assert len(draft.symptoms) >= 1

    assert len(draft.current_medications) >= 1
