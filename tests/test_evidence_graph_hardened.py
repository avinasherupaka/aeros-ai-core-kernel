from aeros.kernel.api.demo_data import get_demo_event_bundle
from aeros.kernel.assurance.evidence_graph import EvidenceGraphQuery, query_snapshot


def test_get_event_evidence_returns_evidence_nodes():
    bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
    q = EvidenceGraphQuery(bundle.evidence_graph)
    evidence = q.get_event_evidence(bundle.event.event_id)
    assert evidence
    assert all(n.node_type.value == "EvidenceItem" for n in evidence)


def test_get_impacted_entities_returns_batch_and_product():
    bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
    q = EvidenceGraphQuery(bundle.evidence_graph)
    entities = q.get_impacted_entities(bundle.event.event_id)
    entity_types = {e.node_type.value for e in entities}
    assert entity_types & {"Batch", "Product", "MaterialLot"}


def test_get_risks_returns_risk_nodes():
    bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
    q = EvidenceGraphQuery(bundle.evidence_graph)
    risks = q.get_risks(bundle.event.event_id)
    assert risks
    assert all(n.node_type.value == "Risk" for n in risks)


def test_get_lineage_path_starts_with_event():
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    q = EvidenceGraphQuery(bundle.evidence_graph)
    path = q.get_lineage_path(bundle.event.event_id)
    assert path
    assert path[0]["node_id"] == bundle.event.event_id


def test_to_neptune_like_triples():
    bundle = get_demo_event_bundle("event::biotech_cold_room_temperature_excursion")
    q = EvidenceGraphQuery(bundle.evidence_graph)
    triples = q.to_neptune_like_triples()
    assert triples
    assert all("subject" in t and "predicate" in t and "object" in t for t in triples)


def test_query_snapshot_helper():
    bundle = get_demo_event_bundle("event::api_reactor_temperature_excursion")
    q = query_snapshot(bundle.evidence_graph)
    evidence = q.get_event_evidence(bundle.event.event_id)
    assert isinstance(evidence, list)


def test_get_missing_evidence_returns_unlinked_items():
    bundle = get_demo_event_bundle("event::pharma_osd_humidity_excursion_compression")
    q = EvidenceGraphQuery(bundle.evidence_graph)
    required = bundle.impact.required_evidence
    missing = q.get_missing_evidence(bundle.event.event_id, required)
    assert isinstance(missing, list)
