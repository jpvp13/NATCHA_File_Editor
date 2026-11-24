"""Parser for the structural subset of domestic PPD NACHA files."""

from __future__ import annotations

import hashlib
from dataclasses import replace

from ach_reversal.domain.models import (
    AddendaRecord,
    Batch,
    BatchControl,
    BatchHeader,
    EntryDetail,
    FileControl,
    FileHeader,
    NachaFile,
    ParseIssue,
    SourceFile,
)

RECORD_LENGTH = 94


def _text(line: str, start: int, end: int) -> str:
    return line[start:end]


def _integer(line: str, start: int, end: int, *, field: str, record_number: int, issues: list[ParseIssue]) -> int:
    value = _text(line, start, end)
    try:
        return int(value)
    except ValueError:
        issues.append(ParseIssue("invalid_numeric_field", f"{field} is not numeric: {value!r}", record_number, field))
        return 0


def _split_content(content: bytes) -> tuple[list[str], bytes, list[ParseIssue]]:
    issues: list[ParseIssue] = []
    line_ending = b"\r\n" if b"\r\n" in content else b"\n"
    raw_lines = content.splitlines()
    if content and not raw_lines:
        raw_lines = [content]
    lines: list[str] = []
    for number, raw in enumerate(raw_lines, 1):
        try:
            line = raw.decode("ascii")
        except UnicodeDecodeError:
            issues.append(ParseIssue("non_ascii_input", "NACHA records must be ASCII", number))
            line = raw.decode("ascii", errors="replace")
        lines.append(line)
        if len(raw) != RECORD_LENGTH:
            issues.append(ParseIssue("invalid_record_length", f"Expected 94 characters, got {len(raw)}", number))
    return lines, line_ending, issues


def parse_ppd(content: bytes) -> SourceFile:
    """Parse a source file without changing its bytes.

    The parser recognizes file, batch, entry, addenda, control, and padding
    records. Reversal-specific eligibility and transformations are deliberately
    outside this function.
    """

    digest = hashlib.sha256(content).hexdigest()
    lines, line_ending, issues = _split_content(content)
    if not lines:
        issues.append(ParseIssue("empty_file", "The source file is empty"))
        return SourceFile(content, digest, None, tuple(issues))
    if any(len(line) != RECORD_LENGTH for line in lines):
        return SourceFile(content, digest, None, tuple(issues))
    if lines[0][0] != "1":
        issues.append(ParseIssue("missing_file_header", "First record must be a file header (1)", 1))
        return SourceFile(content, digest, None, tuple(issues))

    header_line = lines[0]
    header = FileHeader(
        priority_code=_text(header_line, 1, 3),
        immediate_destination=_text(header_line, 3, 13),
        immediate_origin=_text(header_line, 13, 23),
        file_creation_date=_text(header_line, 23, 29),
        file_creation_time=_text(header_line, 29, 33),
        file_id_modifier=_text(header_line, 33, 34),
        record_size=_text(header_line, 34, 37),
        blocking_factor=_text(header_line, 37, 39),
        format_code=_text(header_line, 39, 40),
        immediate_destination_name=_text(header_line, 40, 63),
        immediate_origin_name=_text(header_line, 63, 86),
        reference_code=_text(header_line, 86, 94),
        raw=header_line,
    )
    if header.record_size != "094":
        issues.append(ParseIssue("invalid_record_size", "File header record size must be 094", 1, "record_size"))
    if header.blocking_factor != "10":
        issues.append(ParseIssue("invalid_blocking_factor", "File header blocking factor must be 10", 1, "blocking_factor"))
    if header.format_code != "1":
        issues.append(ParseIssue("invalid_format_code", "File header format code must be 1", 1, "format_code"))

    batches: list[Batch] = []
    current_header: BatchHeader | None = None
    current_entries: list[EntryDetail] = []
    current_start = 0
    current_control: BatchControl | None = None
    padding_count = 0
    file_control: FileControl | None = None
    active_entry_index: int | None = None

    def finish_batch(record_number: int) -> None:
        nonlocal current_header, current_entries, current_control, current_start
        if current_header is None:
            issues.append(ParseIssue("orphan_batch_control", "Batch control has no batch header", record_number))
        elif current_control is None:
            issues.append(ParseIssue("missing_batch_control", "Batch is missing its batch control", record_number))
        else:
            batches.append(Batch(current_header, tuple(current_entries), current_control, current_start))
        current_header = None
        current_entries = []
        current_control = None

    for record_number, line in enumerate(lines[1:], 2):
        record_type = line[0]
        if record_type == "5":
            if current_header is not None:
                issues.append(ParseIssue("nested_batch", "Batch header encountered before prior batch closed", record_number))
                finish_batch(record_number)
            current_start = record_number
            current_header = BatchHeader(
                service_class_code=_text(line, 1, 4),
                company_name=_text(line, 4, 20),
                company_discretionary_data=_text(line, 20, 40),
                company_identification=_text(line, 40, 50),
                standard_entry_class_code=_text(line, 50, 53),
                company_entry_description=_text(line, 53, 63),
                company_descriptive_date=_text(line, 63, 69),
                effective_entry_date=_text(line, 69, 75),
                settlement_date=_text(line, 75, 78),
                originator_status_code=_text(line, 78, 79),
                originating_dfi_identification=_text(line, 79, 87),
                batch_number=_text(line, 87, 94),
                raw=line,
            )
            active_entry_index = None
        elif record_type == "6":
            if current_header is None:
                issues.append(ParseIssue("orphan_entry", "Entry detail has no batch header", record_number))
                continue
            entry = EntryDetail(
                transaction_code=_text(line, 1, 3),
                receiving_dfi_identification=_text(line, 3, 11),
                check_digit=_text(line, 11, 12),
                dfi_account_number=_text(line, 12, 29),
                amount_cents=_integer(line, 29, 39, field="amount", record_number=record_number, issues=issues),
                individual_identification_number=_text(line, 39, 54),
                individual_name=_text(line, 54, 76),
                discretionary_data=_text(line, 76, 78),
                addenda_record_indicator=_text(line, 78, 79),
                trace_number=_text(line, 79, 94),
                raw=line,
                record_number=record_number,
            )
            current_entries.append(entry)
            active_entry_index = len(current_entries) - 1
        elif record_type == "7":
            if current_header is None or active_entry_index is None:
                issues.append(ParseIssue("orphan_addenda", "Addenda has no preceding entry detail", record_number))
                continue
            addenda = AddendaRecord(
                addenda_type_code=_text(line, 1, 3),
                payment_related_information=_text(line, 3, 83),
                addenda_sequence_number=_text(line, 83, 87),
                entry_detail_sequence_number=_text(line, 87, 94),
                raw=line,
                record_number=record_number,
            )
            current_entries[active_entry_index] = replace(current_entries[active_entry_index], addenda=current_entries[active_entry_index].addenda + (addenda,))
        elif record_type == "8":
            current_control = BatchControl(
                service_class_code=_text(line, 1, 4),
                entry_addenda_count=_integer(line, 4, 10, field="entry_addenda_count", record_number=record_number, issues=issues),
                entry_hash=_integer(line, 10, 20, field="entry_hash", record_number=record_number, issues=issues),
                total_debit_cents=_integer(line, 20, 32, field="total_debit", record_number=record_number, issues=issues),
                total_credit_cents=_integer(line, 32, 44, field="total_credit", record_number=record_number, issues=issues),
                company_identification=_text(line, 44, 54),
                message_authentication_code=_text(line, 54, 73),
                reserved=_text(line, 73, 79),
                originating_dfi_identification=_text(line, 79, 87),
                batch_number=_text(line, 87, 94),
                raw=line,
            )
            finish_batch(record_number)
            active_entry_index = None
        elif record_type == "9":
            if line == "9" * RECORD_LENGTH:
                padding_count += 1
            elif len(batches) or current_header is not None:
                file_control = FileControl(
                    batch_count=_integer(line, 1, 7, field="batch_count", record_number=record_number, issues=issues),
                    block_count=_integer(line, 7, 13, field="block_count", record_number=record_number, issues=issues),
                    entry_addenda_count=_integer(line, 13, 21, field="entry_addenda_count", record_number=record_number, issues=issues),
                    entry_hash=_integer(line, 21, 31, field="entry_hash", record_number=record_number, issues=issues),
                    total_debit_cents=_integer(line, 31, 43, field="total_debit", record_number=record_number, issues=issues),
                    total_credit_cents=_integer(line, 43, 55, field="total_credit", record_number=record_number, issues=issues),
                    reserved=_text(line, 55, 94),
                    raw=line,
                )
            else:
                issues.append(ParseIssue("orphan_file_control", "File control has no batches", record_number))
        else:
            issues.append(ParseIssue("unknown_record_type", f"Unsupported record type {record_type!r}", record_number))

    if file_control is not None:
        parsed = NachaFile(header, tuple(batches), file_control, padding_count, tuple(lines), line_ending)
        return SourceFile(content, digest, parsed, tuple(issues))
    issues.append(ParseIssue("missing_file_control", "File is missing a file control record"))
    return SourceFile(content, digest, None, tuple(issues))
