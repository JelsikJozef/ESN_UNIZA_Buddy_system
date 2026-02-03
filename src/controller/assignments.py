"""
Assignment controller - manages manual buddy assignments.

This module handles the state and logic for manual assignments,
separate from the ranking algorithm.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Set


@dataclass
class Assignment:
    """Represents a single manual buddy assignment."""
    esn_index: int
    erasmus_index: int
    timestamp: str

    # Optional metadata
    esn_name: str = ""
    esn_surname: str = ""
    erasmus_name: str = ""
    erasmus_surname: str = ""


@dataclass
class AssignmentState:
    """Manages the collection of all assignments in a session."""
    assignments: List[Assignment] = field(default_factory=list)

    def add_assignment(
        self,
        esn_index: int,
        erasmus_index: int,
        esn_name: str = "",
        esn_surname: str = "",
        erasmus_name: str = "",
        erasmus_surname: str = ""
    ) -> Assignment:
        """
        Create a new assignment.

        Args:
            esn_index: Index of ESN member
            erasmus_index: Index of Erasmus student
            esn_name: ESN member first name
            esn_surname: ESN member surname
            erasmus_name: Erasmus student first name
            erasmus_surname: Erasmus student surname

        Returns:
            The created Assignment object

        Raises:
            ValueError: If student is already assigned
        """
        # Check if student is already assigned
        if self.is_erasmus_assigned(erasmus_index):
            raise ValueError(f"Erasmus student (index {erasmus_index}) is already assigned")

        assignment = Assignment(
            esn_index=esn_index,
            erasmus_index=erasmus_index,
            timestamp=datetime.now().isoformat(),
            esn_name=esn_name,
            esn_surname=esn_surname,
            erasmus_name=erasmus_name,
            erasmus_surname=erasmus_surname
        )

        self.assignments.append(assignment)
        return assignment

    def remove_assignment(self, erasmus_index: int) -> bool:
        """
        Remove an assignment by Erasmus student index.

        Args:
            erasmus_index: Index of the Erasmus student to unassign

        Returns:
            True if assignment was removed, False if not found
        """
        original_length = len(self.assignments)
        self.assignments = [a for a in self.assignments if a.erasmus_index != erasmus_index]
        return len(self.assignments) < original_length

    def is_erasmus_assigned(self, erasmus_index: int) -> bool:
        """Check if an Erasmus student is already assigned."""
        return any(a.erasmus_index == erasmus_index for a in self.assignments)

    def get_assigned_erasmus_indices(self) -> Set[int]:
        """Get set of all assigned Erasmus student indices."""
        return {a.erasmus_index for a in self.assignments}

    def get_assignments_for_esn(self, esn_index: int) -> List[Assignment]:
        """Get all assignments for a specific ESN member."""
        return [a for a in self.assignments if a.esn_index == esn_index]

    def get_assignment_count(self) -> int:
        """Get total number of assignments."""
        return len(self.assignments)

    def clear_all(self) -> None:
        """Clear all assignments."""
        self.assignments.clear()


def create_assignment_state() -> AssignmentState:
    """Factory function to create a new assignment state."""
    return AssignmentState()
