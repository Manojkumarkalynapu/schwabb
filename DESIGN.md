# Course Waitlist Design

## Boundary

`CourseOffering` is the bounded service for one course offering. It owns the enrollment set,
ordered waitlist, capacity, and prerequisite. `enroll`, `drop`, `is_eligible`, and `snapshot`
are the public operations. The `CourseOffering` constructor validates a non-empty course ID,
non-negative capacity, and a non-empty prerequisite name.

## Data and invariants

- An enrolled learner is stored once in `enrolled`.
- A waitlisted learner is stored once as `(learner_id, completed_prerequisites)`.
- The waitlist preserves arrival order.
- `len(enrolled) <= capacity` is maintained inside the offering lock.
- A learner cannot be both enrolled and waitlisted.
- Prerequisites are represented as exact, trimmed names.

## Enrollment

For an available seat, enrollment succeeds only if the learner completed the required
prerequisite. For a full course, a learner (eligible or ineligible) may join the waitlist once.
Prerequisite failure is an immediate rejection only for an available seat.

Duplicate enrollments return `already_enrolled` or `already_waitlisted`; they do not alter
state. Empty learner IDs raise `ValueError`.

## Waitlist promotion

Dropping an enrolled learner opens a seat. Promotion scans the waitlist in arrival order and
promotes the earliest learner who satisfies the prerequisite. Ineligible learners remain in the
same relative position; they are skipped during promotion and are not removed. The service
currently promotes at most one learner per drop because one drop opens one seat.

This policy is consistent: it neither removes ineligible learners nor lets them bypass eligible
learners. An ineligible learner could become eligible in a real system only after reenrollment;
this slice stores no external prerequisite updates, so it cannot become eligible automatically.

## Concurrency and persistence

The implementation uses an in-memory store and a reentrant lock around every state-changing
operation and snapshot read. This is a small, thread-safe process-local prototype. It provides
no cross-process persistence or atomicity, database transaction guarantees, or crash recovery.
Persistence would need to be added by a starter project if one existed.

## CLI

The CLI demonstrates single operations but is intentionally non-persistent across invocations.
The service API and tests are the primary runnable interface.
