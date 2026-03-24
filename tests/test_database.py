"""
Unit tests for database context manager
"""

import pytest
from unittest.mock import patch, MagicMock
from database.context import get_db_session


class TestDatabaseContext:
    """Tests for database context manager"""

    def test_get_db_session_returns_context_manager(self):
        """Test that get_db_session returns a context manager"""
        gen = get_db_session()
        assert hasattr(gen, "__enter__") and hasattr(gen, "__exit__")

    def test_get_db_session_context(self):
        """Test using get_db_session as context manager"""
        with get_db_session() as db:
            assert db is not None
            assert hasattr(db, "query")

    @patch("database.context.SessionLocal")
    def test_get_db_session_commits_on_success(self, mock_session_local):
        """Test that session commits on successful operation"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        with get_db_session() as db:
            pass

        mock_db.commit.assert_called_once()
        mock_db.close.assert_called_once()

    @patch("database.context.SessionLocal")
    def test_get_db_session_rollbacks_on_error(self, mock_session_local):
        """Test that session rolls back on exception"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        with pytest.raises(ValueError):
            with get_db_session() as db:
                raise ValueError("Test error")

        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()
        mock_db.commit.assert_not_called()

    @patch("database.context.SessionLocal")
    def test_get_db_session_always_closes(self, mock_session_local):
        """Test that session is always closed even on exception"""
        mock_db = MagicMock()
        mock_session_local.return_value = mock_db

        try:
            with get_db_session() as db:
                raise RuntimeError("Test error")
        except RuntimeError:
            pass

        mock_db.close.assert_called_once()
