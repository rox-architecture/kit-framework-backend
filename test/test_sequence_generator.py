from cee.sequence_generator import SequenceGenerator


def test_plan_contains_dependencies_instead_of_generation_barriers() -> None:
    """The execution plan expresses dependencies without level barriers."""
    graph = {
        "nodes": [{"id": node_id} for node_id in ["root", "slow", "fast", "child"]],
        "edges": [
            {"source": "root", "target": "slow"},
            {"source": "root", "target": "fast"},
            {"source": "fast", "target": "child"},
        ],
    }

    plan = SequenceGenerator(graph).generate_plan()

    assert plan["roots"] == ["root"]
    assert plan["predecessors"] == {
        "root": [],
        "slow": ["root"],
        "fast": ["root"],
        "child": ["fast"],
    }
    assert plan["successors"]["fast"] == ["child"]


def test_rejects_cycles() -> None:
    """Cyclic graphs remain invalid workflows."""
    graph = {
        "nodes": [{"id": "a"}, {"id": "b"}],
        "edges": [
            {"source": "a", "target": "b"},
            {"source": "b", "target": "a"},
        ],
    }

    assert not SequenceGenerator(graph).check_dag()
