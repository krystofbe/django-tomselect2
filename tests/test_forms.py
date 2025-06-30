import json
import os
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.core import signing
from django.forms import SelectMultiple
from django.test import override_settings
from django.urls import reverse
from playwright.sync_api import expect, sync_playwright

from django_tomselect2.cache import cache
from django_tomselect2.forms import (
    HeavyTomSelectWidget,
    ModelTomSelectMixin,
    ModelTomSelectWidget,
    TomSelectTagMixin,
    TomSelectWidget,
)
from tests.testapp.models import Artist, Genre


@pytest.mark.playwright
class TestTomSelectMixin:
    def test_build_attrs_with_theme(self):
        """Test that theme is correctly included in tom-select settings"""
        widget = TomSelectWidget(theme="bootstrap4")
        attrs = widget.build_attrs({})
        tom_select_settings = json.loads(attrs["data-tom-select"])

        assert tom_select_settings["theme"] == "bootstrap4"

    def test_build_attrs_with_plugins(self):
        """Test that plugins configuration is properly included in attributes"""
        plugins = {
            "clear_button": {
                "title": "Remove all selected",
            },
            "dropdown_header": {"title": "Custom Header"},
        }
        widget = TomSelectWidget(plugins=plugins)
        attrs = widget.build_attrs({})
        tom_select_settings = json.loads(attrs["data-tom-select"])

        assert tom_select_settings["plugins"] == plugins

    def test_empty_label_handling(self):
        """Test that empty_label is correctly handled for non-required fields"""
        widget = TomSelectWidget(attrs={"class": "my-select"})
        widget.is_required = False
        widget.empty_label = "Custom Empty Label"

        attrs = widget.build_attrs({})
        assert attrs["data-placeholder"] == "Custom Empty Label"

        # Test choices modification
        name = "test_field"
        value = []
        optgroups = widget.optgroups(name, value)
        # First option should be the empty label
        assert optgroups[0][1][0]["label"] == "Custom Empty Label"

    def test_media_includes_correct_files(self):
        """Test that all required JS files are included in media"""
        widget = TomSelectWidget()
        media = widget.media

        # Check JS files
        assert "tom-select/js/tom-select.complete.min.js" in str(media)
        assert "django_tomselect2/django_tomselect.js" in str(media)

    def test_placeholder_rendering(self):
        """Test that placeholder attribute is correctly rendered"""
        # Test with placeholder in attrs
        widget = TomSelectWidget(attrs={"placeholder": "Select an option"})
        attrs = widget.build_attrs({})
        tom_select_settings = json.loads(attrs["data-tom-select"])

        assert tom_select_settings["placeholder"] == "Select an option"

        # Test without placeholder
        widget = TomSelectWidget()
        attrs = widget.build_attrs({})
        tom_select_settings = json.loads(attrs["data-tom-select"])

        assert tom_select_settings["placeholder"] == ""

    def test_tom_select_settings_rendering(self):
        """
        Test that custom tom_select_settings are properly rendered in data-tom-select attribute.
        """
        # Create widget with custom tom_select_settings
        custom_settings = {"preload": True, "maxItems": 5, "customOption": "test-value"}
        widget = TomSelectWidget(tom_select_settings=custom_settings)

        # Build attributes
        attrs = widget.build_attrs({})

        # Parse the data-tom-select JSON string
        rendered_settings = json.loads(attrs["data-tom-select"])

        # Verify each custom setting is present in rendered data
        for key, value in custom_settings.items():
            assert rendered_settings[key] == value, (
                f"Expected {key}={value} in data-tom-select"
            )


@pytest.mark.playwright
class TestTomSelectTagMixin:
    def test_build_attrs_includes_tag_settings(self):
        """
        Test that build_attrs includes all tag-related settings.
        """

        class TestWidget(TomSelectTagMixin, SelectMultiple):
            pass

        widget = TestWidget(attrs={"class": "test-class"}, placeholder="Add tags")
        base_attrs = {"name": "test_field"}
        extra_attrs = {"placeholder": "Add tags"}
        built_attrs = widget.build_attrs(base_attrs, extra_attrs=extra_attrs)

        data_tom_select = json.loads(built_attrs["data-tom-select"])

        assert data_tom_select.get("create") is True, "Expected 'create' to be True"
        assert data_tom_select.get("delimiter") == ",", "Expected delimiter to be ','"
        assert data_tom_select.get("persist") is False, "Expected 'persist' to be False"
        assert data_tom_select.get("dropdownParent") == "body", (
            "Expected 'dropdownParent' to be 'body'"
        )
        assert data_tom_select.get("hideSelected") is False, (
            "Expected 'hideSelected' to be False"
        )
        assert data_tom_select.get("placeholder") == "Add tags", (
            "Expected placeholder to be 'Add tags'"
        )
        assert built_attrs.get("class") == "test-class", (
            "Expected class to be 'test-class'"
        )

    def test_create_new_tag_attributes(self):
        """
        Test that the 'create' attribute is set to True for tag creation.
        """

        class TestWidget(TomSelectTagMixin, SelectMultiple):
            pass

        widget = TestWidget()
        base_attrs = {"name": "test_field"}
        built_attrs = widget.build_attrs(base_attrs)

        data_tom_select = json.loads(built_attrs["data-tom-select"])

        assert data_tom_select.get("create") is True, "Expected 'create' to be True"

    def test_delimiter_settings(self):
        """
        Test that the delimiter is correctly set for tag separation.
        """

        class TestWidget(TomSelectTagMixin, SelectMultiple):
            pass

        widget = TestWidget()
        base_attrs = {"name": "test_field"}
        built_attrs = widget.build_attrs(base_attrs)

        data_tom_select = json.loads(built_attrs["data-tom-select"])

        assert data_tom_select.get("delimiter") == ",", "Expected delimiter to be ','"

    def test_dropdown_parent_setting(self):
        """
        Test that the dropdown parent is correctly set to 'body'.
        """

        class TestWidget(TomSelectTagMixin, SelectMultiple):
            pass

        widget = TestWidget()
        base_attrs = {"name": "test_field"}
        built_attrs = widget.build_attrs(base_attrs)

        data_tom_select = json.loads(built_attrs["data-tom-select"])

        assert data_tom_select.get("dropdownParent") == "body", (
            "Expected 'dropdownParent' to be 'body'"
        )


@pytest.mark.playwright
class TestTomSelectWidget(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        # to ignore django.core.exceptions.SynchronousOnlyOperation:
        # You cannot call this from an async context - use a thread or sync_to_async.
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=True,
        )
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

    @classmethod
    def tearDownClass(cls):
        cls.page.close()
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        self.url = reverse("tomselect2_widget")

    def test_basic_select_rendering(self):
        """
        Test that the TomSelect widget is rendered correctly on the page.
        """
        self.page.goto(self.live_server_url + self.url)
        # Locate the TomSelect wrapper by a specific selector
        tom_select_wrapper = self.page.locator(".ts-wrapper")
        expect(tom_select_wrapper).to_be_visible()
        # Ensure that the underlying select element is present and hidden
        select_element = self.page.locator("select#id_number")
        expect(select_element).to_have_class("tomselected ts-hidden-accessible")

    def test_single_selection(self):
        """
        Test selecting an option from the TomSelect widget and verifying the selection.
        """
        self.page.goto(self.live_server_url + self.url)
        tom_select_control = self.page.locator(".ts-control")
        expect(tom_select_control).to_be_visible()

        # Click to focus the input and open the dropdown
        tom_select_control.click()

        # Wait for the dropdown options to be visible
        dropdown = self.page.locator(".ts-dropdown-content")
        expect(dropdown).to_be_visible()

        # Select the first option with value "1" (One)
        first_option = dropdown.locator("div.option[data-value='1']")
        first_option_text = first_option.inner_text()
        first_option.click()

        # Verify that the selected option is reflected in the widget
        selected_item = self.page.locator(".ts-control .item")
        expect(selected_item).to_have_text(first_option_text)

    def test_clear_selection(self):
        """
        Test the functionality of clearing a selection in the TomSelect widget.
        """
        self.page.goto(self.live_server_url + self.url)
        tom_select_control = self.page.locator(".ts-control")
        expect(tom_select_control).to_be_visible()

        # Select an option first
        tom_select_control.click()
        dropdown = self.page.locator(".ts-dropdown-content")
        expect(dropdown).to_be_visible()

        # Select using correct Tom Select option structure
        first_option = dropdown.locator("div.option[data-value='1']")
        first_option_text = first_option.inner_text()
        first_option.click()

        # Verify selection using the item div
        selected_item = self.page.locator(".ts-control .item")
        expect(selected_item).to_have_text(first_option_text)

        # Clear the selection by clicking the 'x' button
        clear_button = self.page.locator(".ts-wrapper .clear-button")
        expect(clear_button).to_be_visible()
        clear_button.click()

        # Verify that the selection is cleared by checking the item div is gone
        selected_item = self.page.locator(".ts-control .item")
        expect(selected_item).not_to_be_visible()

    def test_placeholder_display(self):
        """
        Test that the placeholder text is displayed correctly when no selection is made.
        """
        self.page.goto(self.live_server_url + self.url)

        # Get the select element to verify the placeholder configuration
        select_element = self.page.locator("select#id_number")
        tom_select_data = json.loads(select_element.get_attribute("data-tom-select"))

        # Verify placeholder in tom-select configuration
        assert tom_select_data["placeholder"] == "", (
            "Expected empty placeholder in tom-select configuration"
        )

        # Verify placeholder in data attribute
        placeholder_attr = select_element.get_attribute("data-placeholder")
        assert placeholder_attr == "", "Expected empty data-placeholder attribute"

    def test_custom_theme_rendering(self):
        """
        Test that a custom theme is applied correctly to the TomSelect widget.
        """
        # Override the TOMSELECT2_THEME setting to use a custom theme
        with override_settings(TOMSELECT2_THEME="default"):
            self.page.goto(self.live_server_url + self.url)

            # Get the select element and verify its data-tom-select attribute contains the theme
            select_element = self.page.locator("select#id_number")
            data_tom_select = select_element.get_attribute("data-tom-select")
            tom_select_config = json.loads(data_tom_select)

            assert tom_select_config["theme"] == "default", (
                f"Expected theme 'default' in data-tom-select configuration, got {tom_select_config.get('theme')}"
            )


@pytest.mark.playwright
class TestTomSelectMultipleWidget(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        # to ignore django.core.exceptions.SynchronousOnlyOperation:
        # You cannot call this from an async context - use a thread or sync_to_async.
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=True,
        )

        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

    @classmethod
    def tearDownClass(cls):
        cls.page.close()
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        self.url = reverse("tomselect2_multiple_widget")

    def test_multiple_selection(self):
        """
        Test that multiple options can be selected in the TomSelect multiple widget.
        """
        self.page.goto(self.live_server_url + self.url)
        tom_select_control = self.page.locator(".ts-control")
        expect(tom_select_control).to_be_visible()

        # Click to focus the input and open the dropdown
        tom_select_control.click()

        # Wait for the dropdown options to be visible
        dropdown_content = self.page.locator(".ts-dropdown-content")
        expect(dropdown_content).to_be_visible()

        # Select multiple options
        options_to_select = ["1", "2"]  # Values corresponding to "One" and "Two"
        for value in options_to_select:
            option = dropdown_content.locator(f"div.option[data-value='{value}']")
            expect(option).to_be_visible()
            option.click()

        # Verify that the selected options are reflected in the widget
        selected_items = self.page.locator(".ts-control .item")
        expect(selected_items).to_have_count(len(options_to_select))
        selected_texts = selected_items.all_inner_texts()
        expected_texts = ["One", "Two"]
        assert selected_texts == expected_texts, (
            f"Expected selected items {expected_texts}, got {selected_texts}"
        )

    def test_remove_selected_items(self):
        """
        Test that selected items can be removed from the TomSelect multiple widget.
        """
        self.page.goto(self.live_server_url + self.url)
        tom_select_control = self.page.locator(".ts-control")
        expect(tom_select_control).to_be_visible()

        # Select multiple options first
        tom_select_control.click()
        dropdown_content = self.page.locator(".ts-dropdown-content")
        expect(dropdown_content).to_be_visible()

        options_to_select = ["1", "2", "3"]  # Select "One", "Two", "Three"
        for value in options_to_select:
            option = dropdown_content.locator(f"div.option[data-value='{value}']")
            option.click()

        # Verify selection
        selected_items = self.page.locator(".ts-control .item")
        expect(selected_items).to_have_count(3)

        # Remove one selected item ("Two") by clicking it and pressing backspace
        item_to_remove = selected_items.nth(1)  # Second item ("Two")
        item_to_remove.click()
        self.page.keyboard.press("Backspace")

        # Verify that the item has been removed
        selected_items = self.page.locator(".ts-control .item")
        expect(selected_items).to_have_count(2)
        selected_texts = selected_items.all_inner_texts()
        expected_texts = ["One", "Three"]
        assert selected_texts == expected_texts, (
            f"Expected selected items {expected_texts}, got {selected_texts}"
        )

    def test_max_items_limit(self):
        """
        Test that the widget respects a configured maximum number of items.
        """
        # Override the widget to set a maxItems limit
        with override_settings(TOMSELECT2_TOM_SELECT_SETTINGS={"maxItems": 2}):
            self.page.goto(self.live_server_url + self.url)
            tom_select_control = self.page.locator(".ts-control")
            expect(tom_select_control).to_be_visible()

            # Select multiple options up to the limit
            tom_select_control.click()
            dropdown_content = self.page.locator(".ts-dropdown-content")
            expect(dropdown_content).to_be_visible()

            options_to_select = ["1", "2"]  # Select two options
            for value in options_to_select:
                option = dropdown_content.locator(f"div.option[data-value='{value}']")
                option.click()

            # Verify that two items are selected
            selected_items = self.page.locator(".ts-control .item")
            expect(selected_items).to_have_count(2)
            selected_texts = selected_items.all_inner_texts()
            expected_texts = ["One", "Two"]
            assert selected_texts == expected_texts, (
                f"Expected selected items {expected_texts}, got {selected_texts}"
            )

            # Try to open the dropdown again
            tom_select_control.click()

            # Verify that the dropdown is not visible
            expect(dropdown_content).not_to_be_visible()

    def test_selected_items_display(self):
        """
        Test that selected items are displayed correctly in the widget.
        """
        self.page.goto(self.live_server_url + self.url)
        tom_select_control = self.page.locator(".ts-control")
        expect(tom_select_control).to_be_visible()

        # Select multiple options
        tom_select_control.click()
        dropdown_content = self.page.locator(".ts-dropdown-content")
        expect(dropdown_content).to_be_visible()

        options_to_select = ["2", "4"]  # Select "Two" and "Four"
        for value in options_to_select:
            option = dropdown_content.locator(f"div.option[data-value='{value}']")
            option.click()

        # Verify that the selected items are displayed in the correct order
        selected_items = self.page.locator(".ts-control .item")
        expect(selected_items).to_have_count(2)
        selected_texts = selected_items.all_inner_texts()
        expected_texts = ["Two", "Four"]
        assert selected_texts == expected_texts, (
            f"Expected selected items {expected_texts}, got {selected_texts}"
        )


@pytest.mark.playwright
class TestHeavyTomSelectMixin:
    @pytest.fixture(autouse=True)
    def setup_cache(self):
        # Clear the cache before each test
        cache.clear()

    @patch("django_tomselect2.forms.reverse")
    def test_ajax_url_configuration_with_data_view(self, mock_reverse):
        """
        Test that the widget correctly configures the AJAX URL using data_view.
        """
        # Setup mock return value for reverse
        mock_reverse.return_value = "/mocked-url/"

        widget = HeavyTomSelectWidget(data_view="mock_view")
        expected_url = "/mocked-url/"

        assert widget.get_url() == expected_url, (
            "AJAX URL should be the reversed data_view URL."
        )

        # Ensure reverse was called with the correct view name
        mock_reverse.assert_called_once_with("mock_view")

    def test_ajax_url_configuration_with_data_url(self):
        """
        Test that the widget correctly configures the AJAX URL using data_url.
        """
        widget = HeavyTomSelectWidget(data_url="/custom-data-url/")
        expected_url = "/custom-data-url/"

        assert widget.get_url() == expected_url, (
            "AJAX URL should be the provided data_url."
        )

    @patch("django_tomselect2.forms.reverse")
    def test_dependent_fields_handling(self, mock_reverse):
        """
        Test that dependent fields are correctly handled and set in the widget's attributes.
        """
        mock_reverse.return_value = "/mocked-url/"

        dependent_fields = {"country": "country_field"}
        widget = HeavyTomSelectWidget(
            data_view="mock_view", dependent_fields=dependent_fields
        )

        built_attrs = widget.build_attrs({})
        expected_dependent_fields = "country"

        assert built_attrs.get("data-dependent-fields") == expected_dependent_fields, (
            "Dependent fields should be correctly set in attributes."
        )

    @patch("django_tomselect2.forms.reverse")
    def test_cache_registration(self, mock_reverse):
        """
        Test that the widget is properly registered in the cache after rendering.
        """
        mock_reverse.return_value = "/mocked-url/"

        widget = HeavyTomSelectWidget(data_view="mock_view")

        # Render the widget which should trigger cache registration
        widget.render("test_field", None)

        cache_key = widget._get_cache_key()
        cached_data = cache.get(cache_key)

        assert cached_data is not None, (
            "Widget should be registered in the cache after rendering."
        )
        assert cached_data["url"] == "/mocked-url/", (
            "Cached URL should match the reversed data_view URL."
        )
        assert cached_data["widget"].__class__ == HeavyTomSelectWidget, (
            "Cached widget should be an instance of HeavyTomSelectWidget."
        )

    def test_field_id_generation(self):
        """
        Test that each widget generates a unique field_id and it is correctly set.
        """
        widget1 = HeavyTomSelectWidget(data_url="/url/1/")
        widget2 = HeavyTomSelectWidget(data_url="/url/2/")

        # Ensure both widgets have different UUIDs
        assert widget1.uuid != widget2.uuid, "Each widget should have a unique UUID."

        # Ensure field_id is correctly generated using signing
        signed_field_id1 = widget1.field_id
        signed_field_id2 = widget2.field_id

        # Verify that the field_id can be unsign'd back to the UUID
        original_uuid1 = signing.loads(signed_field_id1)
        original_uuid2 = signing.loads(signed_field_id2)

        assert original_uuid1 == widget1.uuid, (
            "field_id should correctly contain the signed UUID for widget1."
        )
        assert original_uuid2 == widget2.uuid, (
            "field_id should correctly contain the signed UUID for widget2."
        )
        assert original_uuid1 != original_uuid2, (
            "Each widget's field_id should correspond to its unique UUID."
        )

    @pytest.fixture
    def mock_queryset(self):
        """
        Fixture to provide a mock queryset.
        """
        return Genre.objects.all()


@pytest.mark.playwright
class TestModelTomSelectMixin:
    class TestWidget(ModelTomSelectMixin, HeavyTomSelectWidget):
        """Test class that combines the mixin with a concrete widget class"""

    def test_queryset_filtering(self, db):
        """
        Test that the queryset is correctly filtered based on search fields and search terms.
        """
        # Create sample genres
        genre1 = Genre.objects.create(title="Rock Music")
        genre2 = Genre.objects.create(title="Jazz Fusion")
        genre3 = Genre.objects.create(title="Classical Orchestra")

        # Initialize the mixin with search_fields
        mixin = self.TestWidget()
        mixin.model = Genre
        mixin.search_fields = ["title__icontains"]
        mixin.queryset = Genre.objects.all()

        # Filter with term that matches genre1 and genre2
        filtered_qs = mixin.filter_queryset(None, "Music")
        assert genre1 in filtered_qs
        assert genre2 not in filtered_qs
        assert genre3 not in filtered_qs

        # Filter with term that matches genre2
        filtered_qs = mixin.filter_queryset(None, "Jazz")
        assert genre2 in filtered_qs
        assert genre1 not in filtered_qs
        assert genre3 not in filtered_qs

    def test_search_fields_validation(self):
        """
        Test that the mixin raises NotImplementedError when search_fields are not defined.
        """
        mixin = self.TestWidget()
        mixin.model = Genre
        mixin.queryset = Genre.objects.all()
        mixin.search_fields = []

        with pytest.raises(NotImplementedError):
            mixin.get_search_fields()

    def test_label_from_instance(self):
        """
        Test that label_from_instance returns the correct label representation.
        """
        genre = Genre(title="Electronic Dance")
        expected_label = "Electronic Dance"

        mixin = self.TestWidget()
        label = mixin.label_from_instance(genre)
        assert label == expected_label

        # Override label_from_instance
        class CustomMixin(ModelTomSelectMixin, HeavyTomSelectWidget):
            def label_from_instance(self, obj):
                return obj.title.upper()

        custom_mixin = CustomMixin()
        expected_custom_label = "ELECTRONIC DANCE"
        custom_label = custom_mixin.label_from_instance(genre)
        assert custom_label == expected_custom_label

    @pytest.mark.django_db
    def test_result_from_instance(self):
        """
        Test that result_from_instance returns the correct dictionary representation.
        """
        genre = Genre.objects.create(title="Hip Hop")
        expected_result = {"id": genre.pk, "text": genre.title}

        mixin = self.TestWidget()
        mixin.label_from_instance = MagicMock(return_value=genre.title)
        result = mixin.result_from_instance(genre, request=None)
        assert result == expected_result

    @patch("django_tomselect2.forms.reverse")
    def test_cache_registration_with_queryset(self, mock_reverse):
        """
        Test that the widget is properly registered in the cache after rendering.
        """
        mock_reverse.return_value = "/mocked-url/"

        # Create a ModelTomSelectWidget instance
        widget = ModelTomSelectWidget(
            model=Genre,
            search_fields=["title__icontains"],
            max_results=10,
            theme="default",
        )

        # Render the widget which should trigger cache registration
        widget.render("test_field", None)

        # Verify reverse was called with the correct view name
        mock_reverse.assert_called_with("django_tomselect2:auto-json")

        # Construct the expected cache key
        cache_key = f"tomselect_{widget.uuid}"

        # Retrieve the cached data
        cached_data = cache.get(cache_key)
        assert cached_data is not None, (
            "Widget should be registered in the cache after rendering."
        )

        # Verify cached URL
        assert cached_data["url"] == "/mocked-url/", (
            "Cached URL should match the reversed data_view URL."
        )

        # Verify cached attributes

        # Verify other cached configurations
        assert cached_data["search_fields"] == tuple(widget.search_fields), (
            "Search fields should be cached correctly."
        )
        assert cached_data["max_results"] == widget.max_results, (
            "Max results should be cached correctly."
        )


@pytest.mark.playwright
class TestModelTomSelectWidget(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        # to ignore django.core.exceptions.SynchronousOnlyOperation:
        # You cannot call this from an async context - use a thread or sync_to_async.
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def test_model_field_rendering(self):
        """
        Verify that the TomSelect widgets are rendered with correct HTML structure and attributes.
        """
        self.page.goto(self.live_server_url + reverse("model_tomselect2_widget"))
        artist_select = self.page.query_selector("#id_artist-ts-control")
        primary_genre_select = self.page.query_selector("#id_primary_genre-ts-control")

        assert artist_select is not None, "Artist TomSelect widget should be rendered."
        assert primary_genre_select is not None, (
            "Primary Genre TomSelect widget should be rendered."
        )
        assert artist_select.get_attribute("placeholder") == "", (
            "Artist widget placeholder should be empty."
        )
        assert primary_genre_select.get_attribute("placeholder") == "", (
            "Primary Genre widget placeholder should be empty."
        )

    def test_ajax_search(self):
        """
        Simulate user input to trigger AJAX search and validate the search results.
        """
        # create Artist instances
        Artist.objects.create(title="Artist 1")
        Artist.objects.create(title="Artist 2")
        Artist.objects.create(title="Specific Artist")

        self.page.goto(self.live_server_url + reverse("model_tomselect2_widget"))
        self.page.click(".ts-wrapper")  # Click on the first ts-wrapper
        artist_input = self.page.query_selector("#id_artist-ts-control")
        artist_input.fill("Artist")
        self.page.wait_for_selector(".ts-dropdown-content .option")
        options = self.page.query_selector_all(".ts-dropdown-content .option")
        assert len(options) > 0, "AJAX search should return at least one option."

    def test_initial_value_display(self):
        """
        Ensure that the widgets display initial values correctly when the form is loaded with pre-selected data.
        """
        # Create necessary Artist and Genre instances
        Artist.objects.create(id=1, title="Artist 1")
        Genre.objects.create(id=2, title="Genre 2")

        url = reverse("model_tomselect2_widget") + "?artist=1&primary_genre=2"
        self.page.goto(self.live_server_url + url)

        # The correct selectors based on the actual HTML structure
        artist_selected = self.page.query_selector("#id_artist + .ts-wrapper .item")
        primary_genre_selected = self.page.query_selector(
            "#id_primary_genre + .ts-wrapper .item"
        )

        assert artist_selected.inner_text() == "ARTIST 1", (
            "Artist widget should display the initial selected value."
        )
        assert primary_genre_selected.inner_text() == "GENRE 2", (
            "Primary Genre widget should display the initial selected value."
        )

    def test_dependent_field_filtering(self):
        """
        Test that selecting a value in the Artist widget filters the options in the Primary Genre widget.
        """
        # Create necessary Artist and Genre instances
        specific_artist = Artist.objects.create(title="Specific Artist")
        Genre.objects.create(title="Filtered Genre 1", artist=specific_artist)
        Genre.objects.create(title="Filtered Genre 2", artist=specific_artist)
        Genre.objects.create(title="Unrelated Genre")

        self.page.goto(self.live_server_url + reverse("model_tomselect2_widget"))

        # Click on the ts-control div for Artist to focus
        self.page.click("#id_artist + .ts-wrapper .ts-control")
        artist_input = self.page.query_selector("#id_artist + .ts-wrapper input")
        artist_input.fill("Specific Artist")

        # TomSelect auto-selects when there is a single exact match, so no
        # dropdown is shown.  Wait until the selected item is present; if it
        # is not selected automatically, fall back to <Enter>.
        try:
            self.page.wait_for_selector("#id_artist + .ts-wrapper .item", timeout=3000)
        except Exception:
            # The item is not selected automatically – press Enter to pick the
            # first highlighted option.
            self.page.keyboard.press("Enter")
            self.page.wait_for_selector("#id_artist + .ts-wrapper .item")

        # Click on the ts-control div for Primary Genre to focus
        self.page.click("#id_primary_genre + .ts-wrapper .ts-control")
        primary_genre_input = self.page.query_selector(
            "#id_primary_genre + .ts-wrapper input"
        )
        primary_genre_input.fill("Filtered Genre")

        # Wait for dropdown to be visible
        self.page.wait_for_selector(".ts-dropdown[style*='display: block']")
        filtered_options = self.page.query_selector_all(
            "#id_primary_genre-ts-dropdown .option"
        )

        # Get the actual text content of each option
        option_texts = [option.text_content().strip() for option in filtered_options]

        assert len(option_texts) == 2, "Should only show the two filtered genres"
        assert all(text.startswith("FILTERED GENRE") for text in option_texts), (
            "Primary Genre options should be filtered based on selected Artist."
        )


@pytest.mark.playwright
class TestModelTomSelectTagWidget(StaticLiveServerTestCase):
    @classmethod
    def setUpClass(cls):
        # to ignore django.core.exceptions.SynchronousOnlyOperation:
        # You cannot call this from an async context - use a thread or sync_to_async.
        os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
        super().setUpClass()
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(
            headless=True,
        )
        cls.context = cls.browser.new_context()
        cls.page = cls.context.new_page()

    @classmethod
    def tearDownClass(cls):
        cls.page.close()
        cls.context.close()
        cls.browser.close()
        cls.playwright.stop()
        super().tearDownClass()

    def setUp(self):
        # Navigate to the tag widget form
        self.url = reverse("model_tomselect2_tag_widget")
        self.page.goto(self.live_server_url + self.url)

    def test_tag_creation(self):
        """Test creating a new tag through the widget"""
        self.page.goto(self.live_server_url + reverse("model_tomselect2_tag_widget"))

        # Click the input to focus
        self.page.click("#id_genres-ts-control")

        # Type the new tag name
        genres_input = self.page.query_selector("#id_genres-ts-control")
        genres_input.fill("TestTag")

        # Wait for the create option to appear
        self.page.wait_for_selector(".ts-dropdown-content .create")

        # Click the "Add TestTag..." option
        self.page.click(".ts-dropdown-content .create")

        # Verify the tag was created and selected
        selected_items = self.page.query_selector_all(".ts-control .item")
        assert len(selected_items) == 1
        assert selected_items[0].inner_text() == "TestTag"

    def test_existing_tag_selection(self):
        """Test selecting an existing tag"""
        # Create a test genre
        Genre.objects.create(title="Existing Genre")

        self.page.goto(self.live_server_url + reverse("model_tomselect2_tag_widget"))

        # Click the input and type
        self.page.click("#id_genres-ts-control")
        genres_input = self.page.query_selector("#id_genres-ts-control")
        genres_input.fill("Existing")

        # Wait for and click the option
        self.page.wait_for_selector(".ts-dropdown[style*='display: block']")
        self.page.wait_for_selector(".ts-dropdown-content .option")
        self.page.click(".ts-dropdown-content .option")

        # Verify selection
        selected_items = self.page.query_selector_all(".ts-control .item")
        assert len(selected_items) == 1
        assert "Existing Genre" in selected_items[0].inner_text()

    def test_multiple_tag_handling(self):
        """Test handling multiple tags"""
        self.page.goto(self.live_server_url + reverse("model_tomselect2_tag_widget"))

        test_tags = ["Tag One", "Tag Two", "Tag Three"]

        for tag in test_tags:
            # Click input and type tag
            self.page.click("#id_genres-ts-control")
            genres_input = self.page.query_selector("#id_genres-ts-control")
            genres_input.fill(tag)

            # Wait for create option and click it
            self.page.wait_for_selector(".ts-dropdown-content .create")
            self.page.click(".ts-dropdown-content .create")

        # Verify all tags were added
        selected_items = self.page.query_selector_all(".ts-control .item")
        assert len(selected_items) == len(test_tags)
        selected_texts = [item.inner_text() for item in selected_items]
        assert all(tag in selected_texts for tag in test_tags)
