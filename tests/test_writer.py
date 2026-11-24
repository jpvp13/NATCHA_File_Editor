from ach_reversal.parser import parse_ppd
from ach_reversal.writer import preview_selected, serialize

from .helpers import synthetic_ppd


def test_serialize_is_deterministic_for_synthetic_source():
    source = synthetic_ppd(2)
    parsed = parse_ppd(source)
    assert parsed.parsed is not None
    assert serialize(parsed.parsed) == source


def test_selection_preview_contains_only_selected_entry():
    parsed = parse_ppd(synthetic_ppd(2))
    assert parsed.parsed is not None
    selected = parsed.parsed.batches[0].entries[0].trace_number
    preview = preview_selected(parsed.parsed, {selected})
    assert len(preview.batches) == 1
    assert [entry.trace_number for entry in preview.batches[0].entries] == [selected]
