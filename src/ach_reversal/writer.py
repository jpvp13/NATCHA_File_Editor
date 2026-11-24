"""Deterministic structural serialization and review-only selection previews."""

from __future__ import annotations

from dataclasses import replace

from ach_reversal.domain.models import Batch, BatchControl, FileControl, NachaFile


def _replace_at(line: str, start: int, end: int, value: str) -> str:
    return line[:start] + value + line[end:]


def serialize(file: NachaFile) -> bytes:
    """Serialize existing records exactly as represented by the parsed model."""

    return file.line_ending.join(line.encode("ascii") for line in file.record_lines) + file.line_ending


def _batch_control(batch: Batch) -> BatchControl:
    entries = len(batch.entries)
    addenda = sum(len(entry.addenda) for entry in batch.entries)
    entry_hash = sum(int(entry.receiving_dfi_identification or "0") for entry in batch.entries) % 10_000_000_000
    debit = sum(entry.amount_cents for entry in batch.entries if entry.transaction_code in {"27", "37", "55", "65", "66", "67"})
    credit = sum(entry.amount_cents for entry in batch.entries if entry.transaction_code in {"22", "32", "52", "62"})
    raw = batch.control.raw
    raw = _replace_at(raw, 4, 10, str(entries + addenda).zfill(6))
    raw = _replace_at(raw, 10, 20, str(entry_hash).zfill(10))
    raw = _replace_at(raw, 20, 32, str(debit).zfill(12))
    raw = _replace_at(raw, 32, 44, str(credit).zfill(12))
    return BatchControl(
        service_class_code=batch.control.service_class_code,
        entry_addenda_count=entries + addenda,
        entry_hash=entry_hash,
        total_debit_cents=debit,
        total_credit_cents=credit,
        company_identification=batch.control.company_identification,
        message_authentication_code=batch.control.message_authentication_code,
        reserved=batch.control.reserved,
        originating_dfi_identification=batch.control.originating_dfi_identification,
        batch_number=batch.control.batch_number,
        raw=raw,
    )


def _file_control(file: NachaFile, batches: tuple[Batch, ...], block_count: int) -> FileControl:
    entries = [entry for batch in batches for entry in batch.entries]
    addenda_count = sum(len(entry.addenda) for entry in entries)
    entry_hash = sum(int(entry.receiving_dfi_identification or "0") for entry in entries) % 10_000_000_000
    debit = sum(entry.amount_cents for entry in entries if entry.transaction_code in {"27", "37", "55", "65", "66", "67"})
    credit = sum(entry.amount_cents for entry in entries if entry.transaction_code in {"22", "32", "52", "62"})
    raw = file.control.raw
    raw = _replace_at(raw, 1, 7, str(len(batches)).zfill(6))
    raw = _replace_at(raw, 7, 13, str(block_count).zfill(6))
    raw = _replace_at(raw, 13, 21, str(len(entries) + addenda_count).zfill(8))
    raw = _replace_at(raw, 21, 31, str(entry_hash).zfill(10))
    raw = _replace_at(raw, 31, 43, str(debit).zfill(12))
    raw = _replace_at(raw, 43, 55, str(credit).zfill(12))
    return FileControl(len(batches), block_count, len(entries) + addenda_count, entry_hash, debit, credit, file.control.reserved, raw)


def preview_selected(file: NachaFile, selected_trace_numbers: set[str]) -> NachaFile:
    """Create a review-only subset without changing transaction semantics.

    This function preserves selected entry records verbatim and recalculates
    structural controls. It is not a reversal generator and cannot be used for
    bank submission.
    """

    batches: list[Batch] = []
    for batch in file.batches:
        entries = tuple(entry for entry in batch.entries if entry.trace_number in selected_trace_numbers)
        if entries:
            selected_batch = replace(batch, entries=entries)
            batches.append(replace(selected_batch, control=_batch_control(selected_batch)))
    lines: list[str] = [file.header.raw]
    for batch in batches:
        lines.append(batch.header.raw)
        for entry in batch.entries:
            lines.append(entry.raw)
            lines.extend(addenda.raw for addenda in entry.addenda)
        lines.append(batch.control.raw)
    content_record_count = len(lines) + 1
    block_count = (content_record_count + 9) // 10
    updated_control = _file_control(file, tuple(batches), block_count)
    lines.append(updated_control.raw)
    while len(lines) % 10:
        lines.append("9" * 94)
    return replace(file, batches=tuple(batches), control=updated_control, padding_record_count=len(lines) - content_record_count, record_lines=tuple(lines))
