import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import importlib
from state_module.state_registry import STATE_REGISTRY, register_state, auto_register_states


class TestStateRegistry:
    """Tests for state registry functionality."""

    def test_register_state_decorator_functionality(self):
        """Test @register_state decorator adds class to registry."""
        # Clear any existing test_type from registry
        if "test_type" in STATE_REGISTRY:
            del STATE_REGISTRY["test_type"]
        
        @register_state("test_type")
        class TestState:
            pass
        
        assert "test_type" in STATE_REGISTRY
        assert STATE_REGISTRY["test_type"] == TestState

    def test_register_state_decorator_with_existing_type(self):
        """Test @register_state decorator behavior with duplicate registration."""
        # Clear any existing test_duplicate from registry
        if "test_duplicate" in STATE_REGISTRY:
            del STATE_REGISTRY["test_duplicate"]
        
        @register_state("test_duplicate")
        class FirstTestState:
            pass
        
        # Register second class with same type - should overwrite
        @register_state("test_duplicate")
        class SecondTestState:
            pass
        
        assert "test_duplicate" in STATE_REGISTRY
        assert STATE_REGISTRY["test_duplicate"] == SecondTestState

    def test_register_state_decorator_return_value(self):
        """Test that @register_state decorator returns the original class."""
        class OriginalState:
            def test_method(self):
                return "original"
        
        decorated_state = register_state("return_test")(OriginalState)
        
        assert decorated_state == OriginalState
        assert decorated_state().test_method() == "original"

    @patch('importlib.import_module')
    @patch('pkgutil.walk_packages')
    def test_auto_register_states_with_valid_package(self, mock_walk_packages, mock_import_module):
        """Test auto_register_states with valid package."""
        # Mock package structure
        mock_walk_packages.return_value = [
            (None, "test_package.state_user", False),
            (None, "test_package.state_ai", False),
        ]
        
        # Mock modules with state classes
        mock_user_module = MagicMock()
        mock_ai_module = MagicMock()
        
        # Create mock state classes with register_state decorator applied
        @register_state("user")
        class MockUserState:
            pass
        
        @register_state("agent") 
        class MockAIState:
            pass
        
        mock_user_module.MockUserState = MockUserState
        mock_ai_module.MockAIState = MockAIState
        
        def mock_import_side_effect(module_name):
            if module_name == "test_package.state_user":
                return mock_user_module
            elif module_name == "test_package.state_ai":
                return mock_ai_module
            else:
                return MagicMock()
        
        mock_import_module.side_effect = mock_import_side_effect
        
        # Clear registry before test
        original_registry = STATE_REGISTRY.copy()
        STATE_REGISTRY.clear()
        
        try:
            auto_register_states("test_package")
            
            # Verify modules were imported
            assert mock_import_module.call_count >= 2
            
        finally:
            # Restore original registry
            STATE_REGISTRY.clear()
            STATE_REGISTRY.update(original_registry)

    @patch('importlib.import_module')
    def test_auto_register_states_with_import_error(self, mock_import_module):
        """Test auto_register_states handles import errors gracefully."""
        mock_import_module.side_effect = ImportError("Module not found")
        
        # Should not raise exception
        try:
            auto_register_states("nonexistent_package")
        except ImportError:
            pytest.fail("auto_register_states should handle ImportError gracefully")

    @patch('pkgutil.walk_packages')
    def test_auto_register_states_with_invalid_package(self, mock_walk_packages):
        """Test auto_register_states with package that has no submodules."""
        mock_walk_packages.return_value = []  # No submodules
        
        # Should not raise exception
        try:
            auto_register_states("empty_package")
        except Exception as e:
            pytest.fail(f"auto_register_states should handle empty packages gracefully: {e}")

    def test_state_registry_population(self):
        """Test that STATE_REGISTRY is properly populated with built-in states."""
        # After importing state_module, registry should have some states
        from state_module.state_registry import STATE_REGISTRY
        
        # Should contain at least the basic state types
        assert isinstance(STATE_REGISTRY, dict)
        
        # Check for expected state types (these should exist in the actual codebase)
        # Note: The exact state types depend on what's actually registered
        expected_types = ["user", "agent"]  # Based on the actual codebase
        
        # At least some states should be registered
        assert len(STATE_REGISTRY) > 0

    def test_duplicate_state_type_registration_behavior(self):
        """Test behavior when registering duplicate state types."""
        # Clear any existing test_dup from registry
        if "test_dup" in STATE_REGISTRY:
            del STATE_REGISTRY["test_dup"]
        
        class FirstDuplicateState:
            value = "first"
        
        class SecondDuplicateState:
            value = "second"
        
        # Register first state
        register_state("test_dup")(FirstDuplicateState)
        assert STATE_REGISTRY["test_dup"] == FirstDuplicateState
        
        # Register second state with same type - should overwrite
        register_state("test_dup")(SecondDuplicateState)
        assert STATE_REGISTRY["test_dup"] == SecondDuplicateState
        assert STATE_REGISTRY["test_dup"].value == "second"

    def test_registry_as_global_singleton(self):
        """Test that STATE_REGISTRY behaves as a global singleton."""
        from state_module.state_registry import STATE_REGISTRY as registry1
        from state_module.state_registry import STATE_REGISTRY as registry2
        
        assert registry1 is registry2
        
        # Modifications to one should affect the other
        test_key = "singleton_test"
        if test_key in registry1:
            del registry1[test_key]
        
        registry1[test_key] = "test_value"
        assert registry2[test_key] == "test_value"
        
        # Cleanup
        if test_key in registry1:
            del registry1[test_key]

    def test_register_state_with_none_type(self):
        """Test register_state behavior with None as state_type."""
        with pytest.raises((TypeError, ValueError)):
            @register_state(None)
            class NoneTypeState:
                pass

    def test_register_state_with_empty_string_type(self):
        """Test register_state behavior with empty string as state_type."""
        @register_state("")
        class EmptyStringTypeState:
            pass
        
        assert "" in STATE_REGISTRY
        assert STATE_REGISTRY[""] == EmptyStringTypeState
        
        # Cleanup
        if "" in STATE_REGISTRY:
            del STATE_REGISTRY[""]

    @patch('importlib.import_module')
    @patch('pkgutil.walk_packages')
    def test_auto_register_states_module_loading_error_handling(self, mock_walk_packages, mock_import_module):
        """Test that auto_register_states handles module loading errors properly."""
        mock_walk_packages.return_value = [
            (None, "test_package.broken_module", False),
        ]
        
        mock_import_module.side_effect = [
            ImportError("Broken module"),
        ]
        
        # Should not raise exception, should handle gracefully
        try:
            auto_register_states("test_package")
        except Exception as e:
            pytest.fail(f"auto_register_states should handle module loading errors: {e}")

    def test_registry_state_retrieval(self):
        """Test retrieving states from the registry."""
        # Clear and add test state
        if "retrieval_test" in STATE_REGISTRY:
            del STATE_REGISTRY["retrieval_test"]
        
        class RetrievalTestState:
            pass
        
        STATE_REGISTRY["retrieval_test"] = RetrievalTestState
        
        # Test retrieval
        retrieved_state = STATE_REGISTRY.get("retrieval_test")
        assert retrieved_state == RetrievalTestState
        
        # Test non-existent state
        non_existent = STATE_REGISTRY.get("non_existent_state")
        assert non_existent is None
        
        # Cleanup
        if "retrieval_test" in STATE_REGISTRY:
            del STATE_REGISTRY["retrieval_test"]