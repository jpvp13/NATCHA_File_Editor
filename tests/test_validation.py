from ach_reversal.parser import parse_ppd
from ach_reversal.validation import validate_ppd

from .helpers import synthetic_ppd


def test_synthetic_ppd_controls_reconcile():
    parsed = parse_ppd(synthetic_ppd(20))
    assert parsed.parsed is not None
    assert validate_ppd(parsed.parsed) == ()


def test_wrong_file_hash_is_reported():
    lines = synthetic_ppd(2).decode("ascii").splitlines()
    file_control_index = next(index for index, line in enumerate(lines) if line.startswith("9") and line != "9" * 94)
    line = lines[file_control_index]
    lines[file_control_index] = line[:21] + str(int(line[21:31]) + 1).zfill(10) + line[31:]
    source = ("\n".join(lines) + "\n").encode("ascii")
    parsed = parse_ppd(source)
    assert parsed.parsed is not None
    assert any(issue.code == "file_hash_mismatch" for issue in validate_ppd(parsed.parsed))
