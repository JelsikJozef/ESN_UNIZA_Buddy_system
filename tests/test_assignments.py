"""
Test suite for manual assignment functionality.
"""
import pytest

from src.controller.assignments import Assignment, AssignmentState, create_assignment_state


class TestAssignment:
    """Test Assignment dataclass."""

    def test_create_assignment(self):
        """Test creating an assignment."""
        assignment = Assignment(
            esn_index=0,
            erasmus_index=5,
            timestamp="2026-02-03T10:00:00",
            esn_name="John",
            esn_surname="Doe",
            erasmus_name="Jane",
            erasmus_surname="Smith"
        )

        assert assignment.esn_index == 0
        assert assignment.erasmus_index == 5
        assert assignment.esn_name == "John"
        assert assignment.erasmus_name == "Jane"


class TestAssignmentState:
    """Test AssignmentState management."""

    def test_create_empty_state(self):
        """Test creating an empty assignment state."""
        state = create_assignment_state()
        assert state.get_assignment_count() == 0
        assert len(state.assignments) == 0

    def test_add_assignment(self):
        """Test adding an assignment."""
        state = AssignmentState()

        assignment = state.add_assignment(
            esn_index=0,
            erasmus_index=10,
            esn_name="Alice",
            esn_surname="Brown",
            erasmus_name="Bob",
            erasmus_surname="Green"
        )

        assert state.get_assignment_count() == 1
        assert assignment.esn_index == 0
        assert assignment.erasmus_index == 10
        assert assignment.esn_name == "Alice"
        assert assignment.erasmus_name == "Bob"

    def test_add_duplicate_erasmus_fails(self):
        """Test that assigning the same Erasmus student twice fails."""
        state = AssignmentState()

        # First assignment succeeds
        state.add_assignment(
            esn_index=0,
            erasmus_index=10,
            esn_name="Alice",
            esn_surname="Brown",
            erasmus_name="Bob",
            erasmus_surname="Green"
        )

        # Second assignment with same erasmus_index should fail
        with pytest.raises(ValueError, match="already assigned"):
            state.add_assignment(
                esn_index=1,
                erasmus_index=10,  # Same student
                esn_name="Carol",
                esn_surname="White",
                erasmus_name="Bob",
                erasmus_surname="Green"
            )

    def test_is_erasmus_assigned(self):
        """Test checking if a student is assigned."""
        state = AssignmentState()

        assert not state.is_erasmus_assigned(10)

        state.add_assignment(
            esn_index=0,
            erasmus_index=10,
            esn_name="Alice",
            esn_surname="Brown",
            erasmus_name="Bob",
            erasmus_surname="Green"
        )

        assert state.is_erasmus_assigned(10)
        assert not state.is_erasmus_assigned(11)

    def test_get_assigned_indices(self):
        """Test getting all assigned student indices."""
        state = AssignmentState()

        state.add_assignment(esn_index=0, erasmus_index=10)
        state.add_assignment(esn_index=1, erasmus_index=20)
        state.add_assignment(esn_index=2, erasmus_index=30)

        indices = state.get_assigned_erasmus_indices()

        assert indices == {10, 20, 30}

    def test_remove_assignment(self):
        """Test removing an assignment."""
        state = AssignmentState()

        state.add_assignment(esn_index=0, erasmus_index=10)
        state.add_assignment(esn_index=1, erasmus_index=20)

        assert state.get_assignment_count() == 2

        # Remove first assignment
        removed = state.remove_assignment(10)

        assert removed is True
        assert state.get_assignment_count() == 1
        assert not state.is_erasmus_assigned(10)
        assert state.is_erasmus_assigned(20)

    def test_remove_nonexistent_assignment(self):
        """Test removing an assignment that doesn't exist."""
        state = AssignmentState()

        state.add_assignment(esn_index=0, erasmus_index=10)

        removed = state.remove_assignment(999)

        assert removed is False
        assert state.get_assignment_count() == 1

    def test_get_assignments_for_esn(self):
        """Test getting assignments for a specific ESN member."""
        state = AssignmentState()

        state.add_assignment(esn_index=0, erasmus_index=10)
        state.add_assignment(esn_index=0, erasmus_index=20)
        state.add_assignment(esn_index=1, erasmus_index=30)

        esn_0_assignments = state.get_assignments_for_esn(0)
        esn_1_assignments = state.get_assignments_for_esn(1)
        esn_2_assignments = state.get_assignments_for_esn(2)

        assert len(esn_0_assignments) == 2
        assert len(esn_1_assignments) == 1
        assert len(esn_2_assignments) == 0

    def test_clear_all(self):
        """Test clearing all assignments."""
        state = AssignmentState()

        state.add_assignment(esn_index=0, erasmus_index=10)
        state.add_assignment(esn_index=1, erasmus_index=20)

        assert state.get_assignment_count() == 2

        state.clear_all()

        assert state.get_assignment_count() == 0
        assert len(state.assignments) == 0

    def test_multiple_esn_can_be_in_state(self):
        """Test that one ESN member can have multiple assignments if needed."""
        state = AssignmentState()

        # Same ESN member, different students
        state.add_assignment(esn_index=0, erasmus_index=10)
        state.add_assignment(esn_index=0, erasmus_index=20)

        assert state.get_assignment_count() == 2
        esn_0_assignments = state.get_assignments_for_esn(0)
        assert len(esn_0_assignments) == 2
