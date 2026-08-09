from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .values import VocabularyType


@dataclass(frozen=True, slots=True)
class ProposalNote:
    value: str

    def __post_init__(self) -> None:
        cleaned = self.value.strip()
        if not cleaned:
            raise ValueError("proposal note is required")
        if len(cleaned) > 1000:
            raise ValueError("proposal note must be at most 1000 characters")
        object.__setattr__(self, "value", cleaned)


@dataclass(frozen=True, slots=True)
class VocabularyProposal:
    proposal_id: str
    vocabulary_type: VocabularyType
    note: ProposalNote
    status: str
    created_at: datetime

    @classmethod
    def create(
        cls,
        *,
        proposal_id: str,
        vocabulary_type: VocabularyType,
        note: ProposalNote,
        created_at: datetime,
    ) -> VocabularyProposal:
        if not proposal_id.strip():
            raise ValueError("proposal_id is required")
        if created_at.tzinfo is None:
            raise ValueError("proposal created_at must be timezone-aware")
        return cls(
            proposal_id=proposal_id,
            vocabulary_type=vocabulary_type,
            note=note,
            status="PENDING",
            created_at=created_at,
        )
