from services.retrieval_eval import evaluate_retrieval


def test_retrieval_metrics():
    docs = [[
        {"page_content": "OSPF hello interval and dead interval", "metadata": {"source": "ospf.md"}},
        {"page_content": "BGP path selection", "metadata": {"source": "bgp.md"}},
        {"page_content": "OSPF areas", "metadata": {"source": "ospf.md"}},
    ]]
    result = evaluate_retrieval(docs, [["ospf.md"]], [[]], k=3)
    assert result["recall_at_k"] == 1.0
    assert result["mrr"] == 1.0
    assert result["precision_at_k"] == 0.6667
