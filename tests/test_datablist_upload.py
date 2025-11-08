import os
import pytest
from playwright.sync_api import sync_playwright, Page
from datablist_page import DatablistPage

def test_datablist_data_validation(page: Page):

    # Arrange
    excel_input_path = "tests/test_files/source_dataset.xlsx"
    excel_export_path = "tests/test_files/exports/exported_file.xlsx"

    # Act
    datablist = DatablistPage(page)
    datablist.open()
    datablist.navigate_to_upload_page()
    datablist.upload_excel(excel_input_path)
    datablist.validate_upload_success()
    datablist.continue_to_properiteies()
    datablist.apply_properties_and_continue()
    datablist.import_data()
    datablist.navigate_to_data_display_page()

    datablist.verify_unfiltered_data(path=excel_input_path)

    datablist.apply_filters()
    datablist.export_filtered_data(download_path=excel_export_path)
    datablist.verify_filtered_data(input_path=excel_input_path, exported_path=excel_export_path)

