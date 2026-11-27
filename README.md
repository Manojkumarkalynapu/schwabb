# Course Waitlist Assessment

A small Python implementation for one course offering. It uses only the Python standard library.

## Assumptions

- The prerequisite is the exact name `INTRO`.
- Learners with `INTRO` in their completed prerequisites are eligible.
- If the course is full, all learners may join the waitlist once, including ineligible learners.
- An ineligible learner is retained at its waitlist position and skipped during promotion.
- Only one seat is opened by one drop, so at most one waitlisted learner is promoted.
- State is process-local and in-memory.

## Run

```powershell
python -m unittest -v
```

CLI demonstration:

```powershell
python cli.py enroll alice --completed INTRO
python cli.py status
python cli.py drop alice
```

CLI invocations do not share state. Use `CourseOffering` in Python or add persistence for a
shared service.

## Documentation

- [Design specification](DESIGN.md)
- [AI prompt and use record](AI_PROMPT_RECORD.md)

## Limitations

- No persistence, authentication, or multi-course/multi-term support.
- The CLI creates a fresh offering for each process and is not a shared server.
- A learner's prerequisites cannot be updated in this slice, so an ineligible waitlisted learner
  cannot become eligible until a new service API or persistence model supports updates.
