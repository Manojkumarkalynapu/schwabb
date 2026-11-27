import threading
import unittest

from course_registration import CourseOffering


class CourseOfferingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.offering = CourseOffering("CS101", 2, "INTRO")

    def test_available_capacity_and_prerequisite_success(self) -> None:
        result = self.offering.enroll("alice", ["INTRO"])
        self.assertEqual(result.status, "enrolled")
        self.assertEqual(self.offering.snapshot()["enrolled"], ["alice"])

    def test_full_course_waitlists_only_after_duplicate_check(self) -> None:
        self.offering.enroll("alice", ["INTRO"])
        self.offering.enroll("bob", ["INTRO"])

        first = self.offering.enroll("carol", ["INTRO"])
        duplicate = self.offering.enroll("carol", ["INTRO"])

        self.assertEqual(first.status, "waitlisted")
        self.assertEqual(duplicate.status, "already_waitlisted")
        self.assertEqual(len(self.offering.waitlist), 1)

    def test_duplicate_enrollment_request_is_not_duplicated(self) -> None:
        self.offering.enroll("alice", ["INTRO"])
        result = self.offering.enroll("alice", ["INTRO"])

        self.assertEqual(result.status, "already_enrolled")
        self.assertEqual(self.offering.snapshot()["enrolled"], ["alice"])

    def test_fifo_promotion_promotes_first_eligible_waitlisted_learner(self) -> None:
        self.offering.enroll("alice", ["INTRO"])
        self.offering.enroll("bob", ["INTRO"])
        self.offering.enroll("not-ready", [])
        self.offering.enroll("carol", ["INTRO"])
        self.offering.enroll("dave", ["INTRO"])

        result = self.offering.drop("alice")

        self.assertEqual(result.status, "dropped_promoted")
        self.assertIn("carol", self.offering.enrolled)
        self.assertNotIn("not-ready", self.offering.enrolled)
        self.assertNotIn("carol", [item[0] for item in self.offering.waitlist])

    def test_waitlist_is_fifo_among_eligible_learners(self) -> None:
        self.offering.enroll("alice", ["INTRO"])
        self.offering.enroll("bob", ["INTRO"])
        self.offering.enroll("carol", ["INTRO"])
        self.offering.enroll("dave", ["INTRO"])

        self.offering.drop("alice")
        self.assertIn("carol", self.offering.enrolled)
        self.offering.drop("bob")
        self.assertIn("dave", self.offering.enrolled)

    def test_prerequisite_failure_does_not_enroll_or_waitlist_if_available(self) -> None:
        result = self.offering.enroll("alice", [])
        self.assertEqual(result.status, "prerequisite_failed")
        self.assertEqual(self.offering.snapshot()["enrolled"], [])
        self.assertEqual(self.offering.snapshot()["waitlist"], [])

    def test_ineligible_waitlisted_learner_is_skipped_and_retained(self) -> None:
        self.offering.enroll("alice", ["INTRO"])
        self.offering.enroll("bob", ["INTRO"])
        self.offering.enroll("not-ready", [])
        self.offering.enroll("carol", ["INTRO"])

        self.offering.drop("alice")

        self.assertIn("not-ready", [item[0] for item in self.offering.waitlist])
        self.assertIn("carol", self.offering.enrolled)

    def test_invalid_drop_and_repeated_drop_are_clear_and_noop(self) -> None:
        invalid = self.offering.drop("nobody")
        self.offering.enroll("alice", ["INTRO"])
        dropped = self.offering.drop("alice")
        repeated = self.offering.drop("alice")

        self.assertEqual(invalid.status, "invalid_drop")
        self.assertEqual(dropped.status, "dropped")
        self.assertEqual(repeated.status, "invalid_drop")
        self.assertEqual(self.offering.snapshot()["enrolled"], [])

    def test_empty_learner_id_is_invalid(self) -> None:
        with self.assertRaises(ValueError):
            self.offering.enroll("  ", ["INTRO"])

    def test_concurrent_enrollment_respects_capacity(self) -> None:
        threads = [
            threading.Thread(
                target=self.offering.enroll,
                args=(learner_id, ["INTRO"]),
            )
            for learner_id in ("one", "two", "three", "four")
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        snapshot = self.offering.snapshot()
        self.assertLessEqual(len(snapshot["enrolled"]), 2)
        self.assertEqual(len(snapshot["enrolled"]) + len(snapshot["waitlist"]), 4)

    def test_negative_capacity_is_invalid(self) -> None:
        with self.assertRaises(ValueError):
            CourseOffering("CS101", -1, "INTRO")


if __name__ == "__main__":
    unittest.main()
