"""Typed, source-linked models for the structural PPD parser."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class ParseIssue:
    code: str
    message: str
    record_number: Optional[int] = None
    field: Optional[str] = None
    severity: str = "error"


@dataclass(frozen=True)
class FileHeader:
    priority_code: str
    immediate_destination: str
    immediate_origin: str
    file_creation_date: str
    file_creation_time: str
    file_id_modifier: str
    record_size: str
    blocking_factor: str
    format_code: str
    immediate_destination_name: str
    immediate_origin_name: str
    reference_code: str
    raw: str


@dataclass(frozen=True)
class BatchHeader:
    service_class_code: str
    company_name: str
    company_discretionary_data: str
    company_identification: str
    standard_entry_class_code: str
    company_entry_description: str
    company_descriptive_date: str
    effective_entry_date: str
    settlement_date: str
    originator_status_code: str
    originating_dfi_identification: str
    batch_number: str
    raw: str


@dataclass(frozen=True)
class EntryDetail:
    transaction_code: str
    receiving_dfi_identification: str
    check_digit: str
    dfi_account_number: str
    amount_cents: int
    individual_identification_number: str
    individual_name: str
    discretionary_data: str
    addenda_record_indicator: str
    trace_number: str
    raw: str
    record_number: int
    addenda: tuple["AddendaRecord", ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class AddendaRecord:
    addenda_type_code: str
    payment_related_information: str
    addenda_sequence_number: str
    entry_detail_sequence_number: str
    raw: str
    record_number: int


@dataclass(frozen=True)
class BatchControl:
    service_class_code: str
    entry_addenda_count: int
    entry_hash: int
    total_debit_cents: int
    total_credit_cents: int
    company_identification: str
    message_authentication_code: str
    reserved: str
    originating_dfi_identification: str
    batch_number: str
    raw: str


@dataclass(frozen=True)
class Batch:
    header: BatchHeader
    entries: tuple[EntryDetail, ...]
    control: BatchControl
    source_record_start: int


@dataclass(frozen=True)
class FileControl:
    batch_count: int
    block_count: int
    entry_addenda_count: int
    entry_hash: int
    total_debit_cents: int
    total_credit_cents: int
    reserved: str
    raw: str


@dataclass(frozen=True)
class NachaFile:
    header: FileHeader
    batches: tuple[Batch, ...]
    control: FileControl
    padding_record_count: int
    record_lines: tuple[str, ...]
    line_ending: bytes = b"\n"


@dataclass(frozen=True)
class SourceFile:
    content: bytes
    sha256: str
    parsed: Optional[NachaFile]
    issues: tuple[ParseIssue, ...]
