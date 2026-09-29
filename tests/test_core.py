from gapd.search_space import PeptideSpace
from gapd.evaluators.toy import ToyEvaluator


def test_space_and_mutation():
    space = PeptideSpace("ACD", 3)
    assert space.mutate("AAA", 1, "C") == "ACA"


def test_toy_is_deterministic():
    a = ToyEvaluator(5).evaluate(["AAAA"])["AAAA"]
    b = ToyEvaluator(5).evaluate(["AAAA"])["AAAA"]
    assert a == b
