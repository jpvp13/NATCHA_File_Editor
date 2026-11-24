"""Synthetic-only PPD fixture builders."""

from __future__ import annotations


def field(value: str, width: int, *, numeric: bool = False) -> str:
    return value.zfill(width) if numeric else value.ljust(width)


def file_header() -> str:
    return "1" + "01" + " 123456789" + " 987654321" + "261123" + "1200" + "A" + "094" + "10" + "1" + "SYNTHETIC BANK".ljust(23) + "MCS TEST ORIGIN".ljust(23) + "".ljust(8)


def batch_header(batch_number: int = 1) -> str:
    return "5" + "220" + "MCS PAYROLL".ljust(16) + "".ljust(20) + "1234567890" + "PPD" + "PAYROLL".ljust(10) + "261123" + "261124" + "   " + "1" + "12345678" + str(batch_number).zfill(7)


def entry(trace: int, *, amount: int = 12345, code: str = "22", account: str = "00000000000012345", addenda: bool = False) -> str:
    line = "6" + code + "12345678" + "9" + field(account, 17) + field(str(amount), 10, numeric=True) + f"EMP{trace:012d}".ljust(15) + f"SYNTHETIC EMPLOYEE {trace}".ljust(22)[:22] + "  " + ("1" if addenda else "0") + "123456" + str(trace).zfill(9)
    return line


def batch_control(entries: list[str]) -> str:
    count = len(entries)
    entry_hash = sum(int(line[3:11]) for line in entries) % 10_000_000_000
    credit = sum(int(line[29:39]) for line in entries if line[1:3] in {"22", "32"})
    debit = sum(int(line[29:39]) for line in entries if line[1:3] in {"27", "37"})
    return "8" + "220" + str(count).zfill(6) + str(entry_hash).zfill(10) + str(debit).zfill(12) + str(credit).zfill(12) + "1234567890" + "".ljust(19) + "".ljust(6) + "12345678" + "0000001"


def file_control(batch_count: int, records: list[str], debit: int, credit: int) -> str:
    entries = [line for line in records if line.startswith("6")]
    entry_hash = sum(int(line[3:11]) for line in entries) % 10_000_000_000
    block_count = (2 + len(records) + 1 + 9) // 10
    return "9" + str(batch_count).zfill(6) + str(block_count).zfill(6) + str(len(entries)).zfill(8) + str(entry_hash).zfill(10) + str(debit).zfill(12) + str(credit).zfill(12) + "".ljust(39)


def synthetic_ppd(entry_count: int = 2) -> bytes:
    entries = [entry(index + 1) for index in range(entry_count)]
    batch = [batch_header(), *entries, batch_control(entries)]
    credit = sum(int(line[29:39]) for line in entries)
    records = [file_header(), *batch]
    records.append(file_control(1, records, 0, credit))
    while len(records) % 10:
        records.append("9" * 94)
    return "\n".join(records).encode("ascii") + b"\n"
