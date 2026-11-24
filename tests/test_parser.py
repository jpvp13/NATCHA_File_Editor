from ach_reversal.parser import parse_ppd

from .helpers import synthetic_ppd


def test_parser_preserves_hash_and_ppd_fields():
    source = synthetic_ppd(2)
    parsed = parse_ppd(source)
    assert parsed.sha256
    assert parsed.parsed is not None
    assert parsed.parsed.header.record_size == "094"
    assert parsed.parsed.batches[0].header.standard_entry_class_code == "PPD"
    assert len(parsed.parsed.batches[0].entries) == 2
    assert parsed.parsed.batches[0].entries[0].dfi_account_number == "00000000000012345"


def test_parser_rejects_bad_record_length():
    parsed = parse_ppd(b"1" * 93 + b"\n")
    assert parsed.parsed is None
    assert any(issue.code == "invalid_record_length" for issue in parsed.issues)


def test_parser_detects_addenda_and_associates_it():
    source = synthetic_ppd(1).decode("ascii").splitlines()
    source.insert(3, "7" + "05" + "SYNTHETIC ADDENDA".ljust(80) + "0001" + "0000001")
    # The fixture's controls intentionally do not match after insertion; association is still inspectable.
    parsed = parse_ppd(("\n".join(source)).encode("ascii"))
    assert parsed.parsed is not None
    assert len(parsed.parsed.batches[0].entries[0].addenda) == 1
