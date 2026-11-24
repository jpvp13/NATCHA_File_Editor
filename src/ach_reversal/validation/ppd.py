"""Validation for the structural PPD subset; no eligibility decisions."""

from __future__ import annotations

from ach_reversal.domain.models import Batch, NachaFile, ParseIssue


def _entry_hash(batch: Batch) -> int:
    return sum(int(entry.receiving_dfi_identification or "0") for entry in batch.entries) % 10_000_000_000


def _counts(batch: Batch) -> tuple[int, int, int]:
    entries = len(batch.entries)
    addenda = sum(len(entry.addenda) for entry in batch.entries)
    return entries, addenda, entries + addenda


def _debit_credit(file: NachaFile) -> tuple[int, int]:
    debit = credit = 0
    for batch in file.batches:
        for entry in batch.entries:
            if entry.transaction_code in {"27", "37", "55", "65", "66", "67"}:
                debit += entry.amount_cents
            elif entry.transaction_code in {"22", "32", "52", "62"}:
                credit += entry.amount_cents
    return debit, credit


def validate_ppd(file: NachaFile) -> tuple[ParseIssue, ...]:
    """Return structural/control issues. Unknown reversal semantics are not errors here."""

    issues: list[ParseIssue] = []
    if not file.batches:
        issues.append(ParseIssue("no_batches", "File contains no batches"))
    if file.header.record_size != "094":
        issues.append(ParseIssue("invalid_record_size", "Record size must be 094", 1, "record_size"))

    expected_entries = expected_addenda = expected_hash = 0
    expected_debit, expected_credit = _debit_credit(file)
    for batch_index, batch in enumerate(file.batches, 1):
        entries, addenda, total = _counts(batch)
        expected_entries += entries
        expected_addenda += addenda
        expected_hash += _entry_hash(batch)
        if batch.header.standard_entry_class_code != "PPD":
            issues.append(ParseIssue("unsupported_sec_code", "Phase 1 only recognizes PPD batches", batch.source_record_start, "standard_entry_class_code"))
        if batch.control.entry_addenda_count != total:
            issues.append(ParseIssue("batch_count_mismatch", f"Batch {batch_index} count does not match entries/addenda", batch.source_record_start, "entry_addenda_count"))
        if batch.control.entry_hash != _entry_hash(batch):
            issues.append(ParseIssue("batch_hash_mismatch", f"Batch {batch_index} entry hash does not match entries", batch.source_record_start, "entry_hash"))
        if batch.control.total_debit_cents != sum(entry.amount_cents for entry in batch.entries if entry.transaction_code in {"27", "37", "55", "65", "66", "67"}):
            issues.append(ParseIssue("batch_debit_mismatch", f"Batch {batch_index} debit total does not match entries", batch.source_record_start, "total_debit"))
        if batch.control.total_credit_cents != sum(entry.amount_cents for entry in batch.entries if entry.transaction_code in {"22", "32", "52", "62"}):
            issues.append(ParseIssue("batch_credit_mismatch", f"Batch {batch_index} credit total does not match entries", batch.source_record_start, "total_credit"))
        for entry in batch.entries:
            if entry.addenda_record_indicator == "0" and entry.addenda:
                issues.append(ParseIssue("addenda_indicator_mismatch", "Entry has addenda records but indicator is 0", entry.record_number, "addenda_record_indicator"))
            if entry.addenda_record_indicator == "1" and not entry.addenda:
                issues.append(ParseIssue("missing_addenda", "Entry indicates addenda but none were parsed", entry.record_number, "addenda_record_indicator"))
            if entry.amount_cents < 0:
                issues.append(ParseIssue("negative_amount", "ACH amount cannot be negative", entry.record_number, "amount"))

    if file.control.batch_count != len(file.batches):
        issues.append(ParseIssue("file_batch_count_mismatch", "File batch count does not match parsed batches", None, "batch_count"))
    if file.control.entry_addenda_count != expected_entries + expected_addenda:
        issues.append(ParseIssue("file_count_mismatch", "File entry/addenda count does not match parsed records", None, "entry_addenda_count"))
    if file.control.entry_hash != expected_hash % 10_000_000_000:
        issues.append(ParseIssue("file_hash_mismatch", "File entry hash does not match parsed entries", None, "entry_hash"))
    if file.control.total_debit_cents != expected_debit:
        issues.append(ParseIssue("file_debit_mismatch", "File debit total does not match parsed entries", None, "total_debit"))
    if file.control.total_credit_cents != expected_credit:
        issues.append(ParseIssue("file_credit_mismatch", "File credit total does not match parsed entries", None, "total_credit"))
    expected_records_without_padding = 2 + sum(2 + len(batch.entries) + sum(len(entry.addenda) for entry in batch.entries) for batch in file.batches)
    expected_blocks = (expected_records_without_padding + 9) // 10
    if file.control.block_count != expected_blocks:
        issues.append(ParseIssue("file_block_count_mismatch", "File block count does not match parsed records", None, "block_count"))
    if (expected_records_without_padding + file.padding_record_count) % 10 != 0:
        issues.append(ParseIssue("invalid_block_padding", "File records are not aligned to a 10-record block", None, "block_count"))
    return tuple(issues)
