# AI Prompt and Use Record

## Prompt 1: Initial implementation

**Prompt:** "Given implementation_task.txt, implement the one-course enrollment, drop, and FIFO
waitlist feature in the supplied empty workspace. Use a small Python in-memory service and
focused tests. State prerequisites and ineligible waitlist behavior."

**Response summary:** Proposed a `CourseOffering` class with a reentrant lock, enrollment and
drop results, and a waitlist scan for eligible learners.

**Disposition:** Accepted the core service/test structure. Edited the implementation to make
`RLock` private in the dataclass, normalize prerequisite strings, and use explicit result statuses.
Rejected the initial idea of silently discarding ineligible waitlisted learners because retaining
and skipping them better exposes the documented queue policy.

**Verification:** Independent review of the source and test execution:
`python -m unittest -v`.

## Prompt 2: Edge-case review

**Prompt:** "Review the implementation against the acceptance criteria, especially duplicate
requests, repeated drops, FIFO order, prerequisite failure, capacity invariants, and concurrency."

**Response summary:** Identified the need for duplicate waitlist checks, invalid learner/drop
checks, and a focused thread-concurrency test.

**Disposition:** Accepted the duplicate and concurrency checks. Edited the ineligible policy to
preserve waitlist position and added an explicit test. Rejected an extra configurable policy
engine because it was outside scope.

**Verification:** Reviewed `test_course_registration.py` and ran the full unittest suite.

## Prompt 3: Documentation

**Prompt:** "Create proportionate setup, design, limitations, and AI-use documentation for this
bounded feature."

**Response summary:** Proposed separate design, prompt record, and README sections covering
the service boundary and assumptions.

**Disposition:** Accepted; edited for concise setup and explicit limitations.

**Verification:** Confirmed commands and files in the workspace, then ran tests again.
