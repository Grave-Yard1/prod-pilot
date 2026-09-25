from app.services.recommendation import recommend


def test_strong_successful_match_recommends_slow():
    assert recommend(top_score=0.87, top_successful=True, safety=False) == "slow"


def test_weak_match_recommends_continue():
    assert recommend(top_score=0.47, top_successful=True, safety=False) == "continue"


def test_no_history_recommends_continue():
    assert recommend(top_score=None, top_successful=False, safety=False) == "continue"


def test_safety_code_recommends_stop_even_with_a_strong_match():
    assert recommend(top_score=0.95, top_successful=True, safety=True) == "stop"
