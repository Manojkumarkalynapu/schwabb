"""In-memory course enrollment, drop, and FIFO waitlist service."""

from dataclasses import dataclass, field
from threading import RLock
from typing import Iterable


@dataclass(frozen=True)
class OperationResult:
    status: str
    message: str
    learner_id: str | None = None


@dataclass
class CourseOffering:
    course_id: str
    capacity: int
    prerequisite: str
    enrolled: dict[str, frozenset[str]] = field(default_factory=dict)
    waitlist: list[tuple[str, frozenset[str]]] = field(default_factory=list)
    _lock: RLock = field(default_factory=RLock, repr=False)

    def __post_init__(self) -> None:
        if not self.course_id.strip():
            raise ValueError("course_id must not be empty")
        if self.capacity < 0:
            raise ValueError("capacity must not be negative")
        if not self.prerequisite.strip():
            raise ValueError("prerequisite must not be empty")

    def _normalize_prerequisites(
        self, completed_prerequisites: Iterable[str]
    ) -> frozenset[str]:
        normalized = frozenset(
            item.strip()
            for item in completed_prerequisites
            if isinstance(item, str) and item.strip()
        )
        return normalized

    def _validate_learner(self, learner_id: str) -> None:
        if not isinstance(learner_id, str) or not learner_id.strip():
            raise ValueError("learner_id must be a non-empty string")

    def is_eligible(self, completed_prerequisites: Iterable[str]) -> bool:
        return self.prerequisite in self._normalize_prerequisites(
            completed_prerequisites
        )

    def enroll(
        self, learner_id: str, completed_prerequisites: Iterable[str]
    ) -> OperationResult:
        self._validate_learner(learner_id)
        learner_id = learner_id.strip()
        completed = self._normalize_prerequisites(completed_prerequisites)

        with self._lock:
            if learner_id in self.enrolled:
                return OperationResult(
                    "already_enrolled",
                    "Learner is already enrolled.",
                    learner_id,
                )

            if any(waiting_id == learner_id for waiting_id, _ in self.waitlist):
                return OperationResult(
                    "already_waitlisted",
                    "Learner is already on the waitlist.",
                    learner_id,
                )

            if len(self.enrolled) < self.capacity:
                if self.prerequisite not in completed:
                    return OperationResult(
                        "prerequisite_failed",
                        "Learner does not satisfy the required prerequisite.",
                        learner_id,
                    )
                self.enrolled[learner_id] = completed
                return OperationResult(
                    "enrolled",
                    "Learner was enrolled.",
                    learner_id,
                )

            self.waitlist.append((learner_id, completed))
            return OperationResult(
                "waitlisted",
                "Course is full; learner was added to the waitlist.",
                learner_id,
            )

    def drop(self, learner_id: str) -> OperationResult:
        self._validate_learner(learner_id)
        learner_id = learner_id.strip()

        with self._lock:
            if learner_id not in self.enrolled:
                return OperationResult(
                    "invalid_drop",
                    "Learner is not enrolled.",
                    learner_id,
                )

            del self.enrolled[learner_id]
            promoted = self._promote_waitlisted()
            if promoted is None:
                return OperationResult(
                    "dropped",
                    "Learner was dropped; no eligible learner was promoted.",
                    learner_id,
                )
            return OperationResult(
                "dropped_promoted",
                f"Learner was dropped; {promoted} was promoted.",
                learner_id,
            )

    def _promote_waitlisted(self) -> str | None:
        remaining: list[tuple[str, frozenset[str]]] = []
        promoted: str | None = None

        for waiting_id, completed in self.waitlist:
            if (
                promoted is None
                and len(self.enrolled) < self.capacity
                and self.prerequisite in completed
            ):
                promoted = waiting_id
                self.enrolled[waiting_id] = completed
                continue
            remaining.append((waiting_id, completed))

        self.waitlist = remaining
        return promoted

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            return {
                "course_id": self.course_id,
                "capacity": self.capacity,
                "prerequisite": self.prerequisite,
                "enrolled": sorted(self.enrolled),
                "waitlist": [
                    {"learner_id": learner_id, "eligible": self.prerequisite in completed}
                    for learner_id, completed in self.waitlist
                ],
            }
