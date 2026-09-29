from gapd.search_space import PeptideSpace
from gapd.policies import RandomSearchPolicy, SimpleGeneticPolicy


def exercise(policy):
    batch = policy.propose(4)
    assert len(batch) == len(set(batch)) == 4
    for idx, sequence in enumerate(batch):
        policy.update(sequence, float(idx))
    later = policy.propose(4)
    assert set(batch).isdisjoint(later)


def test_random_policy():
    exercise(RandomSearchPolicy(PeptideSpace("ACD", 3), seed=1))


def test_simple_genetic_policy():
    exercise(SimpleGeneticPolicy(PeptideSpace("ACD", 3), seed=1, mutation_rate=0.3))
