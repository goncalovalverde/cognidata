"""
Unit tests for PatientProtocolService
"""

import pytest
from unittest.mock import patch, MagicMock, call
from datetime import datetime
from uuid import uuid4

from services.patient_protocol_service import PatientProtocolService
from models import Patient, Protocol, PatientProtocol, TestSession


class TestPatientProtocolServiceAssign:
    """Tests for assign_protocol method"""

    @patch("services.patient_protocol_service.SessionLocal")
    def test_assign_protocol_creates_new_assignment(self, mock_session_local):
        """Test creating a new protocol assignment when none exists"""
        # Arrange
        patient_id = str(uuid4())
        protocol_id = str(uuid4())
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock no existing assignment
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        expected_assignment = MagicMock(spec=PatientProtocol)
        expected_assignment.patient_id = patient_id
        expected_assignment.protocol_id = protocol_id
        expected_assignment.status = "pending"
        
        # Act
        result = PatientProtocolService.assign_protocol(patient_id, protocol_id, "test_user")
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("services.patient_protocol_service.SessionLocal")
    def test_assign_protocol_returns_existing_assignment(self, mock_session_local):
        """Test that existing assignment is returned (idempotent)"""
        # Arrange
        patient_id = str(uuid4())
        protocol_id = str(uuid4())
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        existing_assignment = MagicMock(spec=PatientProtocol)
        existing_assignment.patient_id = patient_id
        existing_assignment.protocol_id = protocol_id
        existing_assignment.status = "pending"
        
        mock_db.query.return_value.filter.return_value.first.return_value = existing_assignment
        
        # Act
        result = PatientProtocolService.assign_protocol(patient_id, protocol_id)
        
        # Assert
        assert result == existing_assignment
        # Should NOT add or commit when assignment exists
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
        mock_db.close.assert_called_once()

    @patch("services.patient_protocol_service.SessionLocal")
    def test_assign_protocol_with_custom_assigned_by(self, mock_session_local):
        """Test assignment with custom assigned_by value"""
        # Arrange
        patient_id = str(uuid4())
        protocol_id = str(uuid4())
        assigned_by = "Dr. Smith"
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        PatientProtocolService.assign_protocol(patient_id, protocol_id, assigned_by)
        
        # Assert
        mock_db.add.assert_called_once()
        added_obj = mock_db.add.call_args[0][0]
        assert added_obj.assigned_by == assigned_by

    @patch("services.patient_protocol_service.SessionLocal")
    def test_assign_protocol_closes_session_on_error(self, mock_session_local):
        """Test that session is closed even if error occurs"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            PatientProtocolService.assign_protocol("patient_id", "protocol_id")
        
        mock_db.close.assert_called_once()


class TestPatientProtocolServiceGet:
    """Tests for get_patient_protocols method"""

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_patient_protocols_returns_list(self, mock_session_local):
        """Test retrieving all protocols for a patient"""
        # Arrange
        patient_id = str(uuid4())
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_assignment = MagicMock(spec=PatientProtocol)
        mock_db.query.return_value.filter.return_value.options.return_value.all.return_value = [mock_assignment]
        
        # Act
        result = PatientProtocolService.get_patient_protocols(patient_id)
        
        # Assert
        assert result == [mock_assignment]
        mock_db.expunge_all.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_patient_protocols_empty_list(self, mock_session_local):
        """Test retrieving protocols when patient has none"""
        # Arrange
        patient_id = str(uuid4())
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.options.return_value.all.return_value = []
        
        # Act
        result = PatientProtocolService.get_patient_protocols(patient_id)
        
        # Assert
        assert result == []
        mock_db.close.assert_called_once()

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_patient_protocols_uses_joinedload(self, mock_session_local):
        """Test that joinedload is used to eager-load relationships"""
        # Arrange
        patient_id = str(uuid4())
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Mock the chain: query() -> filter() -> options() -> all()
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_options = MagicMock()
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.options.return_value = mock_options
        mock_options.all.return_value = []
        
        # Act
        PatientProtocolService.get_patient_protocols(patient_id)
        
        # Assert
        mock_filter.options.assert_called_once()
        mock_db.expunge_all.assert_called_once()


class TestPatientProtocolServiceUpdate:
    """Tests for update_protocol_status method"""

    @patch("services.patient_protocol_service.SessionLocal")
    def test_update_protocol_status_changes_status(self, mock_session_local):
        """Test updating protocol status to a new value"""
        # Arrange
        patient_id = str(uuid4())
        protocol_id = str(uuid4())
        new_status = "in_progress"
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_assignment = MagicMock(spec=PatientProtocol)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_assignment
        
        # Act
        result = PatientProtocolService.update_protocol_status(
            patient_id, protocol_id, new_status
        )
        
        # Assert
        assert result == mock_assignment
        assert mock_assignment.status == new_status
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("services.patient_protocol_service.SessionLocal")
    def test_update_protocol_status_to_completed(self, mock_session_local):
        """Test updating status to 'completed'"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_assignment = MagicMock(spec=PatientProtocol)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_assignment
        
        # Act
        PatientProtocolService.update_protocol_status("p_id", "pr_id", "completed")
        
        # Assert
        assert mock_assignment.status == "completed"

    @patch("services.patient_protocol_service.SessionLocal")
    def test_update_protocol_status_returns_none_if_not_found(self, mock_session_local):
        """Test that None is returned when assignment doesn't exist"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = PatientProtocolService.update_protocol_status("p_id", "pr_id", "in_progress")
        
        # Assert
        assert result is None
        mock_db.commit.assert_not_called()

    @patch("services.patient_protocol_service.SessionLocal")
    def test_update_protocol_status_closes_session_on_error(self, mock_session_local):
        """Test that session is closed even if error occurs during update"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            PatientProtocolService.update_protocol_status("p_id", "pr_id", "in_progress")
        
        mock_db.close.assert_called_once()


class TestPatientProtocolServiceUnassign:
    """Tests for unassign_protocol method"""

    @patch("services.patient_protocol_service.SessionLocal")
    def test_unassign_protocol_deletes_assignment(self, mock_session_local):
        """Test removing a protocol assignment"""
        # Arrange
        patient_id = str(uuid4())
        protocol_id = str(uuid4())
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_assignment = MagicMock(spec=PatientProtocol)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_assignment
        
        # Act
        result = PatientProtocolService.unassign_protocol(patient_id, protocol_id)
        
        # Assert
        assert result is True
        mock_db.delete.assert_called_once_with(mock_assignment)
        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("services.patient_protocol_service.SessionLocal")
    def test_unassign_protocol_returns_false_if_not_found(self, mock_session_local):
        """Test that False is returned when assignment doesn't exist"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = PatientProtocolService.unassign_protocol("p_id", "pr_id")
        
        # Assert
        assert result is False
        mock_db.delete.assert_not_called()
        mock_db.commit.assert_not_called()

    @patch("services.patient_protocol_service.SessionLocal")
    def test_unassign_protocol_closes_session_on_error(self, mock_session_local):
        """Test that session is closed even if error occurs"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception):
            PatientProtocolService.unassign_protocol("p_id", "pr_id")
        
        mock_db.close.assert_called_once()


class TestPatientProtocolServiceAvailable:
    """Tests for get_available_protocols method"""

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_available_protocols_excludes_assigned(self, mock_session_local):
        """Test that assigned protocols are not in available list"""
        # Arrange
        patient_id = str(uuid4())
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # Setup mock chain for two separate queries
        query_calls = []
        def mock_query(model):
            query_mock = MagicMock()
            query_calls.append(query_mock)
            return query_mock
        
        mock_db.query = mock_query
        
        # First query: get assigned IDs
        assigned_filter_mock = MagicMock()
        assigned_filter_mock.all.return_value = [("assigned_id",)]
        
        # Second query: get available protocols
        mock_protocol = MagicMock(spec=Protocol)
        available_filter_mock = MagicMock()
        available_filter_mock.all.return_value = [mock_protocol]
        
        # Configure the side effects
        call_count = [0]
        def mock_query_impl(model):
            query_mock = MagicMock()
            if call_count[0] == 0:
                # First call for assigned IDs
                query_mock.filter.return_value.all.return_value = [("assigned_id",)]
            else:
                # Second call for available protocols
                query_mock.filter.return_value.all.return_value = [mock_protocol]
            call_count[0] += 1
            return query_mock
        
        mock_db.query = mock_query_impl
        
        # Act
        result = PatientProtocolService.get_available_protocols(patient_id)
        
        # Assert
        assert result == [mock_protocol]
        mock_db.close.assert_called_once()

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_available_protocols_all_available(self, mock_session_local):
        """Test when patient has no assigned protocols"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_protocol1 = MagicMock(spec=Protocol)
        mock_protocol2 = MagicMock(spec=Protocol)
        
        call_count = [0]
        def mock_query_impl(model):
            query_mock = MagicMock()
            if call_count[0] == 0:
                # First call for assigned IDs - empty
                query_mock.filter.return_value.all.return_value = []
            else:
                # Second call for available protocols
                query_mock.filter.return_value.all.return_value = [mock_protocol1, mock_protocol2]
            call_count[0] += 1
            return query_mock
        
        mock_db.query = mock_query_impl
        
        # Act
        result = PatientProtocolService.get_available_protocols("patient_id")
        
        # Assert
        assert len(result) == 2
        assert result == [mock_protocol1, mock_protocol2]


class TestPatientProtocolServiceCompletion:
    """Tests for get_protocol_completion_status method"""

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_completion_status_empty_protocol(self, mock_session_local):
        """Test completion status when protocol has no tests"""
        # Arrange
        patient_id = str(uuid4())
        protocol_id = str(uuid4())
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_protocol = MagicMock(spec=Protocol)
        mock_protocol.tests = []  # No tests in protocol
        mock_db.query.return_value.filter.return_value.first.return_value = mock_protocol
        
        # Act
        result = PatientProtocolService.get_protocol_completion_status(patient_id, protocol_id)
        
        # Assert
        assert result["status"] == "empty"
        assert result["total_tests"] == 0
        assert result["percentage"] == 0

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_completion_status_pending(self, mock_session_local):
        """Test completion status when no tests are completed"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_protocol = MagicMock(spec=Protocol)
        mock_protocol.tests = [MagicMock(), MagicMock(), MagicMock()]  # 3 tests
        mock_db.query.return_value.filter.return_value.first.return_value = mock_protocol
        
        # Mock completed tests count = 0
        mock_db.query.return_value.filter.return_value.count.return_value = 0
        
        # Act
        result = PatientProtocolService.get_protocol_completion_status("p_id", "pr_id")
        
        # Assert
        assert result["status"] == "pending"
        assert result["total_tests"] == 3
        assert result["completed_tests"] == 0
        assert result["percentage"] == 0

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_completion_status_in_progress(self, mock_session_local):
        """Test completion status when some tests are completed"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_protocol = MagicMock(spec=Protocol)
        mock_protocol.tests = [MagicMock(), MagicMock(), MagicMock()]  # 3 tests
        mock_db.query.return_value.filter.return_value.first.return_value = mock_protocol
        
        # Mock completed tests count = 2 (out of 3)
        mock_db.query.return_value.filter.return_value.count.return_value = 2
        
        # Act
        result = PatientProtocolService.get_protocol_completion_status("p_id", "pr_id")
        
        # Assert
        assert result["status"] == "in_progress"
        assert result["total_tests"] == 3
        assert result["completed_tests"] == 2
        assert result["percentage"] == 66  # 2/3 = 66%

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_completion_status_completed(self, mock_session_local):
        """Test completion status when all tests are completed"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_protocol = MagicMock(spec=Protocol)
        mock_protocol.tests = [MagicMock(), MagicMock()]  # 2 tests
        mock_db.query.return_value.filter.return_value.first.return_value = mock_protocol
        
        # Mock completed tests count = 2 (all completed)
        mock_db.query.return_value.filter.return_value.count.return_value = 2
        
        # Act
        result = PatientProtocolService.get_protocol_completion_status("p_id", "pr_id")
        
        # Assert
        assert result["status"] == "completed"
        assert result["total_tests"] == 2
        assert result["completed_tests"] == 2
        assert result["percentage"] == 100

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_completion_status_protocol_not_found(self, mock_session_local):
        """Test completion status when protocol doesn't exist"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Act
        result = PatientProtocolService.get_protocol_completion_status("p_id", "pr_id")
        
        # Assert
        assert result is None

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_completion_status_percentage_calculation(self, mock_session_local):
        """Test that percentage is calculated correctly"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # 3 tests, 1 completed = 33.33% → rounds to 33
        mock_protocol = MagicMock(spec=Protocol)
        mock_protocol.tests = [MagicMock(), MagicMock(), MagicMock()]
        mock_db.query.return_value.filter.return_value.first.return_value = mock_protocol
        mock_db.query.return_value.filter.return_value.count.return_value = 1
        
        # Act
        result = PatientProtocolService.get_protocol_completion_status("p_id", "pr_id")
        
        # Assert
        assert result["percentage"] == 33


class TestPatientProtocolServiceGetForProtocol:
    """Tests for get_patient_protocols_for_protocol method"""

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_patient_protocols_for_protocol_returns_list(self, mock_session_local):
        """Test retrieving all patient assignments for a protocol"""
        # Arrange
        protocol_id = str(uuid4())
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_assignment1 = MagicMock(spec=PatientProtocol)
        mock_assignment2 = MagicMock(spec=PatientProtocol)
        mock_db.query.return_value.filter.return_value.options.return_value.all.return_value = [
            mock_assignment1, mock_assignment2
        ]
        
        # Act
        result = PatientProtocolService.get_patient_protocols_for_protocol(protocol_id)
        
        # Assert
        assert result == [mock_assignment1, mock_assignment2]
        mock_db.expunge_all.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_patient_protocols_for_protocol_empty(self, mock_session_local):
        """Test when protocol has no patient assignments"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        mock_db.query.return_value.filter.return_value.options.return_value.all.return_value = []
        
        # Act
        result = PatientProtocolService.get_patient_protocols_for_protocol("protocol_id")
        
        # Assert
        assert result == []

    @patch("services.patient_protocol_service.SessionLocal")
    def test_get_patient_protocols_for_protocol_uses_joinedload(self, mock_session_local):
        """Test that joinedload is used for eager-loading patient relationships"""
        # Arrange
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_query = MagicMock()
        mock_filter = MagicMock()
        mock_options = MagicMock()
        
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.options.return_value = mock_options
        mock_options.all.return_value = []
        
        # Act
        PatientProtocolService.get_patient_protocols_for_protocol("protocol_id")
        
        # Assert
        mock_filter.options.assert_called_once()


class TestPatientProtocolServiceIntegration:
    """Integration tests covering realistic workflows"""

    @patch("services.patient_protocol_service.SessionLocal")
    def test_assign_then_get_workflow(self, mock_session_local):
        """Test assigning protocol and then retrieving it"""
        # This would be more complex in real integration tests
        # For now, just verify the workflow chain can be called
        patient_id = str(uuid4())
        protocol_id = str(uuid4())
        
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        # First call: assign
        mock_db.query.return_value.filter.return_value.first.return_value = None
        PatientProtocolService.assign_protocol(patient_id, protocol_id)
        
        # Verify add and commit were called
        assert mock_db.add.call_count >= 1
        assert mock_db.commit.call_count >= 1

    @patch("services.patient_protocol_service.SessionLocal")
    def test_status_lifecycle_workflow(self, mock_session_local):
        """Test status changes: pending → in_progress → completed"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db
        
        mock_assignment = MagicMock(spec=PatientProtocol)
        mock_db.query.return_value.filter.return_value.first.return_value = mock_assignment
        
        # Change from pending to in_progress
        PatientProtocolService.update_protocol_status("p_id", "pr_id", "in_progress")
        assert mock_assignment.status == "in_progress"
        
        # Change to completed
        PatientProtocolService.update_protocol_status("p_id", "pr_id", "completed")
        assert mock_assignment.status == "completed"
        
        # Verify commits
        assert mock_db.commit.call_count >= 2
