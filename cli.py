"""Command-line interface for the course registration feature."""

import argparse

from course_registration import CourseOffering


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Single-course registration demo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    enroll = subparsers.add_parser("enroll")
    enroll.add_argument("learner_id")
    enroll.add_argument(
        "--completed",
        action="append",
        default=[],
        help="completed prerequisite name; repeat as needed",
    )

    drop = subparsers.add_parser("drop")
    drop.add_argument("learner_id")

    subparsers.add_parser("status")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    offering = CourseOffering("CS101", 2, "INTRO")

    # This CLI is an isolated demo; status is therefore stateful only within a process.
    # Interactive services can replace this setup with a persistent service instance.
    if args.command == "status":
        print(offering.snapshot())
    elif args.command == "enroll":
        print(offering.enroll(args.learner_id, args.completed))
    else:
        print(offering.drop(args.learner_id))


if __name__ == "__main__":
    main()
