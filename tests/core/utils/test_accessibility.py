"""
Tests for the accessibility utilities.

This module contains tests for the accessibility utilities in the
science_data_kit.core.utils.accessibility module.
"""

import unittest
from unittest.mock import MagicMock, patch

from science_data_kit.core.utils.accessibility import (
    KeyboardNavigationManager,
    ScreenReaderHelper,
    AccessibilityManager,
    get_accessibility_manager
)


class TestKeyboardNavigationManager(unittest.TestCase):
    """Tests for the KeyboardNavigationManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = MagicMock()
        self.manager = KeyboardNavigationManager(self.logger)

    def test_register_focusable_element(self):
        """Test that register_focusable_element adds an element to the focusable elements."""
        element_id = "test_element"
        element_data = {"on_focus": MagicMock()}
        
        self.manager.register_focusable_element(element_id, element_data)
        
        self.assertIn(element_id, self.manager.focusable_elements)
        self.assertEqual(self.manager.focusable_elements[element_id], element_data)
        self.assertIn(element_id, self.manager.focus_order)
        self.logger.debug.assert_called_once()

    def test_set_focus_order(self):
        """Test that set_focus_order sets the focus order correctly."""
        # Register some elements
        self.manager.register_focusable_element("element1", {"on_focus": MagicMock()})
        self.manager.register_focusable_element("element2", {"on_focus": MagicMock()})
        self.manager.register_focusable_element("element3", {"on_focus": MagicMock()})
        
        # Set the focus order
        self.manager.set_focus_order(["element2", "element3", "element1"])
        
        # Check that the focus order is set correctly
        self.assertEqual(self.manager.focus_order, ["element2", "element3", "element1"])
        
        # Check that a warning is logged for unregistered elements
        self.manager.set_focus_order(["element2", "element4", "element1"])
        self.logger.warning.assert_called_once()
        
        # Check that only registered elements are included in the focus order
        self.assertEqual(self.manager.focus_order, ["element2", "element1"])

    def test_focus_element(self):
        """Test that focus_element focuses an element correctly."""
        # Create a mock on_focus callback
        on_focus = MagicMock()
        
        # Register an element
        self.manager.register_focusable_element("element1", {"on_focus": on_focus})
        
        # Focus the element
        result = self.manager.focus_element("element1")
        
        # Check that the element was focused
        self.assertTrue(result)
        on_focus.assert_called_once()
        self.assertEqual(self.manager.current_focus_index, 0)
        
        # Check that focusing an unregistered element returns False
        result = self.manager.focus_element("element2")
        self.assertFalse(result)
        self.logger.warning.assert_called_once()
        
        # Check that focusing an element without an on_focus callback returns False
        self.manager.register_focusable_element("element3", {})
        result = self.manager.focus_element("element3")
        self.assertFalse(result)
        self.assertEqual(self.logger.warning.call_count, 2)

    def test_focus_next(self):
        """Test that focus_next focuses the next element in the focus order."""
        # Create mock on_focus callbacks
        on_focus1 = MagicMock()
        on_focus2 = MagicMock()
        on_focus3 = MagicMock()
        
        # Register some elements
        self.manager.register_focusable_element("element1", {"on_focus": on_focus1})
        self.manager.register_focusable_element("element2", {"on_focus": on_focus2})
        self.manager.register_focusable_element("element3", {"on_focus": on_focus3})
        
        # Focus the first element
        self.manager.focus_element("element1")
        on_focus1.assert_called_once()
        
        # Focus the next element
        result = self.manager.focus_next()
        
        # Check that the next element was focused
        self.assertTrue(result)
        on_focus2.assert_called_once()
        self.assertEqual(self.manager.current_focus_index, 1)
        
        # Focus the next element again (should wrap around to the first element)
        self.manager.focus_next()
        self.manager.focus_next()
        
        # Check that we're back to the first element
        self.assertEqual(self.manager.current_focus_index, 0)
        self.assertEqual(on_focus1.call_count, 2)

    def test_focus_previous(self):
        """Test that focus_previous focuses the previous element in the focus order."""
        # Create mock on_focus callbacks
        on_focus1 = MagicMock()
        on_focus2 = MagicMock()
        on_focus3 = MagicMock()
        
        # Register some elements
        self.manager.register_focusable_element("element1", {"on_focus": on_focus1})
        self.manager.register_focusable_element("element2", {"on_focus": on_focus2})
        self.manager.register_focusable_element("element3", {"on_focus": on_focus3})
        
        # Focus the first element
        self.manager.focus_element("element1")
        on_focus1.assert_called_once()
        
        # Focus the previous element (should wrap around to the last element)
        result = self.manager.focus_previous()
        
        # Check that the previous element was focused
        self.assertTrue(result)
        on_focus3.assert_called_once()
        self.assertEqual(self.manager.current_focus_index, 2)

    def test_handle_key_event(self):
        """Test that handle_key_event handles key events correctly."""
        # Create mock callbacks
        on_focus = MagicMock()
        on_key = MagicMock(return_value=True)
        
        # Register an element
        self.manager.register_focusable_element("element1", {"on_focus": on_focus, "on_key": on_key})
        
        # Focus the element
        self.manager.focus_element("element1")
        
        # Handle a key event
        result = self.manager.handle_key_event("Enter")
        
        # Check that the key event was handled
        self.assertTrue(result)
        on_key.assert_called_once_with("Enter", [])
        
        # Check that Tab key is handled specially
        with patch.object(self.manager, 'focus_next') as mock_focus_next:
            mock_focus_next.return_value = True
            result = self.manager.handle_key_event("Tab")
            self.assertTrue(result)
            mock_focus_next.assert_called_once()
        
        # Check that Shift+Tab is handled specially
        with patch.object(self.manager, 'focus_previous') as mock_focus_previous:
            mock_focus_previous.return_value = True
            result = self.manager.handle_key_event("Tab", ["shift"])
            self.assertTrue(result)
            mock_focus_previous.assert_called_once()


class TestScreenReaderHelper(unittest.TestCase):
    """Tests for the ScreenReaderHelper class."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = MagicMock()
        self.helper = ScreenReaderHelper(self.logger)

    def test_generate_aria_attributes(self):
        """Test that generate_aria_attributes generates the correct attributes."""
        # Generate attributes with all parameters
        attrs = self.helper.generate_aria_attributes(
            role="button",
            label="Test Button",
            description="A test button",
            expanded=True,
            controls="test_panel",
            live="polite",
            relevant="additions",
            busy=False,
            hidden=False,
            additional_attrs={"aria-pressed": "true"}
        )
        
        # Check that all attributes are set correctly
        self.assertEqual(attrs["aria-role"], "button")
        self.assertEqual(attrs["aria-label"], "Test Button")
        self.assertEqual(attrs["aria-description"], "A test button")
        self.assertEqual(attrs["aria-expanded"], "true")
        self.assertEqual(attrs["aria-controls"], "test_panel")
        self.assertEqual(attrs["aria-live"], "polite")
        self.assertEqual(attrs["aria-relevant"], "additions")
        self.assertEqual(attrs["aria-busy"], "false")
        self.assertEqual(attrs["aria-hidden"], "false")
        self.assertEqual(attrs["aria-pressed"], "true")
        
        # Generate attributes with minimal parameters
        attrs = self.helper.generate_aria_attributes(role="button")
        
        # Check that only the role is set
        self.assertEqual(attrs, {"aria-role": "button"})

    def test_announce(self):
        """Test that announce adds an announcement to the list."""
        # Add an announcement
        self.helper.announce("Test announcement", "polite")
        
        # Check that the announcement was added
        self.assertEqual(len(self.helper.announcements), 1)
        self.assertEqual(self.helper.announcements[0]["message"], "Test announcement")
        self.assertEqual(self.helper.announcements[0]["priority"], "polite")
        self.assertIn("timestamp", self.helper.announcements[0])
        self.logger.debug.assert_called_once()

    def test_get_announcements(self):
        """Test that get_announcements returns and optionally clears the announcements."""
        # Add some announcements
        self.helper.announce("Announcement 1")
        self.helper.announce("Announcement 2")
        
        # Get the announcements without clearing
        announcements = self.helper.get_announcements(clear=False)
        
        # Check that the announcements were returned but not cleared
        self.assertEqual(len(announcements), 2)
        self.assertEqual(announcements[0]["message"], "Announcement 1")
        self.assertEqual(announcements[1]["message"], "Announcement 2")
        self.assertEqual(len(self.helper.announcements), 2)
        
        # Get the announcements with clearing
        announcements = self.helper.get_announcements(clear=True)
        
        # Check that the announcements were returned and cleared
        self.assertEqual(len(announcements), 2)
        self.assertEqual(len(self.helper.announcements), 0)


class TestAccessibilityManager(unittest.TestCase):
    """Tests for the AccessibilityManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.logger = MagicMock()
        self.manager = AccessibilityManager(self.logger)

    def test_register_focusable_element(self):
        """Test that register_focusable_element delegates to the keyboard manager."""
        # Create mock callbacks
        on_focus = MagicMock()
        on_key = MagicMock()
        
        # Mock the keyboard manager
        self.manager.keyboard_manager = MagicMock()
        
        # Register an element
        self.manager.register_focusable_element("test_element", on_focus, on_key)
        
        # Check that the keyboard manager was called
        self.manager.keyboard_manager.register_focusable_element.assert_called_once()
        args, kwargs = self.manager.keyboard_manager.register_focusable_element.call_args
        self.assertEqual(args[0], "test_element")
        self.assertEqual(args[1]["on_focus"], on_focus)
        self.assertEqual(args[1]["on_key"], on_key)

    def test_set_focus_order(self):
        """Test that set_focus_order delegates to the keyboard manager."""
        # Mock the keyboard manager
        self.manager.keyboard_manager = MagicMock()
        
        # Set the focus order
        self.manager.set_focus_order(["element1", "element2"])
        
        # Check that the keyboard manager was called
        self.manager.keyboard_manager.set_focus_order.assert_called_once_with(["element1", "element2"])

    def test_focus_element(self):
        """Test that focus_element delegates to the keyboard manager."""
        # Mock the keyboard manager
        self.manager.keyboard_manager = MagicMock()
        self.manager.keyboard_manager.focus_element.return_value = True
        
        # Focus an element
        result = self.manager.focus_element("test_element")
        
        # Check that the keyboard manager was called and the result was returned
        self.manager.keyboard_manager.focus_element.assert_called_once_with("test_element")
        self.assertTrue(result)

    def test_handle_key_event(self):
        """Test that handle_key_event delegates to the keyboard manager."""
        # Mock the keyboard manager
        self.manager.keyboard_manager = MagicMock()
        self.manager.keyboard_manager.handle_key_event.return_value = True
        
        # Handle a key event
        result = self.manager.handle_key_event("Enter", ["ctrl"])
        
        # Check that the keyboard manager was called and the result was returned
        self.manager.keyboard_manager.handle_key_event.assert_called_once_with("Enter", ["ctrl"])
        self.assertTrue(result)

    def test_generate_aria_attributes(self):
        """Test that generate_aria_attributes delegates to the screen reader helper."""
        # Mock the screen reader helper
        self.manager.screen_reader_helper = MagicMock()
        self.manager.screen_reader_helper.generate_aria_attributes.return_value = {"aria-role": "button"}
        
        # Generate ARIA attributes
        attrs = self.manager.generate_aria_attributes("button", label="Test Button")
        
        # Check that the screen reader helper was called and the result was returned
        self.manager.screen_reader_helper.generate_aria_attributes.assert_called_once_with("button", label="Test Button")
        self.assertEqual(attrs, {"aria-role": "button"})

    def test_announce(self):
        """Test that announce delegates to the screen reader helper."""
        # Mock the screen reader helper
        self.manager.screen_reader_helper = MagicMock()
        
        # Make an announcement
        self.manager.announce("Test announcement", "assertive")
        
        # Check that the screen reader helper was called
        self.manager.screen_reader_helper.announce.assert_called_once_with("Test announcement", "assertive")

    def test_toggle_high_contrast_mode(self):
        """Test that toggle_high_contrast_mode toggles the high contrast mode."""
        # Check initial state
        self.assertFalse(self.manager.high_contrast_mode)
        
        # Toggle high contrast mode
        result = self.manager.toggle_high_contrast_mode()
        
        # Check that high contrast mode was enabled
        self.assertTrue(result)
        self.assertTrue(self.manager.high_contrast_mode)
        self.logger.info.assert_called_once()
        
        # Toggle high contrast mode again
        result = self.manager.toggle_high_contrast_mode()
        
        # Check that high contrast mode was disabled
        self.assertFalse(result)
        self.assertFalse(self.manager.high_contrast_mode)
        self.assertEqual(self.logger.info.call_count, 2)

    def test_set_text_scaling_factor(self):
        """Test that set_text_scaling_factor sets the text scaling factor."""
        # Check initial state
        self.assertEqual(self.manager.text_scaling_factor, 1.0)
        
        # Set text scaling factor
        self.manager.set_text_scaling_factor(1.5)
        
        # Check that text scaling factor was set
        self.assertEqual(self.manager.text_scaling_factor, 1.5)
        self.logger.info.assert_called_once()
        
        # Try to set an invalid text scaling factor
        self.manager.set_text_scaling_factor(0)
        
        # Check that text scaling factor was not changed
        self.assertEqual(self.manager.text_scaling_factor, 1.5)
        self.logger.warning.assert_called_once()

    def test_get_accessibility_settings(self):
        """Test that get_accessibility_settings returns the correct settings."""
        # Mock the screen reader helper
        self.manager.screen_reader_helper = MagicMock()
        self.manager.screen_reader_helper.get_announcements.return_value = [{"message": "Test"}]
        
        # Set some settings
        self.manager.high_contrast_mode = True
        self.manager.text_scaling_factor = 1.5
        
        # Get the settings
        settings = self.manager.get_accessibility_settings()
        
        # Check that the settings are correct
        self.assertEqual(settings["high_contrast_mode"], True)
        self.assertEqual(settings["text_scaling_factor"], 1.5)
        self.assertEqual(settings["announcements"], [{"message": "Test"}])
        self.manager.screen_reader_helper.get_announcements.assert_called_once_with(clear=False)


class TestGetAccessibilityManager(unittest.TestCase):
    """Tests for the get_accessibility_manager function."""

    def test_get_accessibility_manager(self):
        """Test that get_accessibility_manager returns the singleton instance."""
        # Get the manager
        manager1 = get_accessibility_manager()
        
        # Get the manager again
        manager2 = get_accessibility_manager()
        
        # Check that the same instance was returned both times
        self.assertIs(manager1, manager2)
        self.assertIsInstance(manager1, AccessibilityManager)


if __name__ == "__main__":
    unittest.main()