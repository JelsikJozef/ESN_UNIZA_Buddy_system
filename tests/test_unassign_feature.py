"""
Test the unassign feature for Erasmus students.
"""
import pytest
from src.controller.assignments import AssignmentState


def test_remove_assignment():
    """Test that we can remove an assignment by Erasmus index."""
    state = AssignmentState()

    # Add some assignments
    state.add_assignment(
        esn_index=0,
        erasmus_index=10,
        esn_name="John",
        esn_surname="Doe",
        erasmus_name="Alice",
        erasmus_surname="Smith"
    )

    state.add_assignment(
        esn_index=1,
        erasmus_index=11,
        esn_name="Jane",
        esn_surname="Doe",
        erasmus_name="Bob",
        erasmus_surname="Johnson"
    )

    assert state.get_assignment_count() == 2
    assert state.is_erasmus_assigned(10)
    assert state.is_erasmus_assigned(11)

    # Remove one assignment
    result = state.remove_assignment(10)

    assert result is True
    assert state.get_assignment_count() == 1
    assert not state.is_erasmus_assigned(10)
    assert state.is_erasmus_assigned(11)

    # Try to remove non-existent assignment
    result = state.remove_assignment(99)
    assert result is False
    assert state.get_assignment_count() == 1


def test_remove_assignment_allows_reassignment():
    """Test that after removing an assignment, the student can be reassigned."""
    state = AssignmentState()

    # Add assignment
    state.add_assignment(
        esn_index=0,
        erasmus_index=10,
        esn_name="John",
        esn_surname="Doe",
        erasmus_name="Alice",
        erasmus_surname="Smith"
    )

    assert state.is_erasmus_assigned(10)

    # Try to reassign - should fail
    with pytest.raises(ValueError, match="already assigned"):
        state.add_assignment(
            esn_index=1,
            erasmus_index=10,
            esn_name="Jane",
            esn_surname="Doe",
            erasmus_name="Alice",
            erasmus_surname="Smith"
        )

    # Remove assignment
    state.remove_assignment(10)
    assert not state.is_erasmus_assigned(10)

    # Now reassignment should work
    state.add_assignment(
        esn_index=1,
        erasmus_index=10,
        esn_name="Jane",
        esn_surname="Doe",
        erasmus_name="Alice",
        erasmus_surname="Smith"
    )

    assert state.get_assignment_count() == 1
    assert state.is_erasmus_assigned(10)

    # Check that it's assigned to the new ESN member
    assignments = state.get_assignments_for_esn(1)
    assert len(assignments) == 1
    assert assignments[0].erasmus_index == 10


def test_get_assignments_for_esn_after_removal():
    """Test that get_assignments_for_esn works correctly after removing assignments."""
    state = AssignmentState()

    # Add multiple assignments for one ESN member
    state.add_assignment(esn_index=0, erasmus_index=10, esn_name="John", esn_surname="Doe", erasmus_name="Alice", erasmus_surname="Smith")
    state.add_assignment(esn_index=0, erasmus_index=11, esn_name="John", esn_surname="Doe", erasmus_name="Bob", erasmus_surname="Johnson")
    state.add_assignment(esn_index=1, erasmus_index=12, esn_name="Jane", esn_surname="Doe", erasmus_name="Carol", erasmus_surname="Williams")

    assert len(state.get_assignments_for_esn(0)) == 2
    assert len(state.get_assignments_for_esn(1)) == 1

    # Remove one assignment from ESN member 0
    state.remove_assignment(10)

    assert len(state.get_assignments_for_esn(0)) == 1
    assert len(state.get_assignments_for_esn(1)) == 1

    # Remove the other assignment from ESN member 0
    state.remove_assignment(11)

    assert len(state.get_assignments_for_esn(0)) == 0
    assert len(state.get_assignments_for_esn(1)) == 1


def test_clear_all_assignments():
    """Test that clear_all removes all assignments."""
    state = AssignmentState()

    # Add some assignments
    state.add_assignment(esn_index=0, erasmus_index=10, esn_name="John", esn_surname="Doe", erasmus_name="Alice", erasmus_surname="Smith")
    state.add_assignment(esn_index=1, erasmus_index=11, esn_name="Jane", esn_surname="Doe", erasmus_name="Bob", erasmus_surname="Johnson")
    state.add_assignment(esn_index=2, erasmus_index=12, esn_name="Jack", esn_surname="Doe", erasmus_name="Carol", erasmus_surname="Williams")

    assert state.get_assignment_count() == 3

    # Clear all
    state.clear_all()

    assert state.get_assignment_count() == 0
    assert not state.is_erasmus_assigned(10)
    assert not state.is_erasmus_assigned(11)
    assert not state.is_erasmus_assigned(12)

    # Should be able to add new assignments after clearing
    state.add_assignment(esn_index=0, erasmus_index=10, esn_name="John", esn_surname="Doe", erasmus_name="Alice", erasmus_surname="Smith")
    assert state.get_assignment_count() == 1
