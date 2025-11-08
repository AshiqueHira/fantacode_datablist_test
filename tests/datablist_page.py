from playwright.sync_api import Page, expect
import pandas as pd
import os, time, re

class DatablistPage:
    def __init__(self, page: Page):
        self.page = page

    def open(self):
        self.page.goto("https://app.datablist.com/")

    def navigate_to_upload_page(self):
        self.page.goto("https://app.datablist.com/")
        self.page.get_by_text("Start with a CSV/Excel file").wait_for(state="visible")
        self.page.get_by_text("Start with a CSV/Excel file").click()

    def upload_excel(self, file_path: str):
        self.page.set_input_files("input[type='file']", file_path)

    def validate_upload_success(self):
        self.page.wait_for_selector("text=Your file is valid!")
        expect(self.page.locator("text=Your file is valid!")).to_be_visible()

    def continue_to_properiteies(self):
        self.page.get_by_role("button", name="Continue to Properties").click()


    def apply_properties_and_continue(self):
        self.page.locator("div").filter(has_text=re.compile(r"^CustomerIdNumber$")).get_by_role("button").click()
        self.page.get_by_label("Property Type").select_option("Text")
        self.page.get_by_role("button", name="Save Property").click()
        self.page.get_by_role("button", name="Continue").click()

    def import_data(self):
        self.page.get_by_role("button", name="Import").click()
        expect(self.page.locator("h1.h1")).to_have_text("Success!")
        

    def navigate_to_data_display_page(self):
        self.page.get_by_role("link", name="Back to collection").click()



    def verify_unfiltered_data(self, path: str):

        df_excel = pd.read_excel(path, dtype=str)

        # Optional: Ensure consistent string formatting
        df_excel = df_excel.apply(lambda x: x.str.strip())

        seen_rows = set()
        web_data = []

        while True:
            rows = self.page.locator("div[class^='row_virtual']").all()

            for row in rows:
                cells = [cell.strip() for cell in row.locator(".cell-inner span").all_inner_texts()]
                if len(cells) >= 6:
                    row_tuple = tuple(cells[:6])
                    if row_tuple not in seen_rows:
                        seen_rows.add(row_tuple)
                        web_data.append(cells[:6])

            # Scroll down
            self.page.mouse.wheel(0, 1500)
            self.page.wait_for_timeout(800)

            # Stop if no new rows are added after a few scrolls
            if len(seen_rows) > 0 and len(web_data) == len(seen_rows):
                # wait one more time to ensure no new rows render
                time.sleep(1)
                new_rows = self.page.locator("div[class^='row_virtual']").all()
                if all(tuple(r.locator(".cell-inner span").all_inner_texts()[:6]) in seen_rows for r in new_rows):
                    break

        print(f"✅ Total rows captured from web: {len(web_data)}")

        df_web = pd.DataFrame(web_data, columns=["CustomerId", "CustomerName", "Country", "Status", "Amount", "CreatedDate"])
        df_web = df_web.astype(str).apply(lambda x: x.str.strip())

         # --- Step 4: Compare ---
        assert df_excel.equals(df_web), "❌ Data mismatches found between Excel and web data."

        # print("✅ All data matched successfully!")
        # comparison = df_excel.eq(df_web)
        # mismatches = df_excel[~comparison.all(axis=1)]

        # --- Step 4: Save the web data to a new Excel file for debugging purposes ---
        # output_path = os.path.join(os.getcwd(), "web_data_output.xlsx")
        # df_web.to_excel(output_path, index=False)
        # print(f"📁 Web data exported to: {output_path}")

        # if mismatches.empty:
        #     print("✅ All data matched successfully!")
        # else:
        #     print("❌ Data mismatches found:")
        #     print(mismatches)
        
    def apply_filters(self):
        self.page.locator(".btn.btn-light").first.click()
        self.page.get_by_label("Select a property").select_option("Status")
        self.page.get_by_label("Select an operator").select_option("is")
        self.page.get_by_role("textbox", name="Enter a value *").fill("Active")

        self.page.get_by_role("button", name="Add filter", exact=True).click()
        self.page.get_by_label("Select a property").nth(1).select_option("Amount")
        self.page.get_by_label("Select an operator").nth(1).select_option("ge")
        self.page.get_by_role("spinbutton", name="Enter a value *").fill("1000")

        self.page.get_by_role("button", name="Add filter", exact=True).click()
        self.page.get_by_label("Select a property").nth(2).select_option("CreatedDate")
        self.page.get_by_label("Select an operator").nth(2).select_option("contains")
        self.page.get_by_role("textbox", name="Enter a value *").nth(1).fill("2023")
        self.page.get_by_role("button", name="Apply").click()

    def export_filtered_data(self, download_path: str):
        self.page.get_by_role("button", name="Export").click()
        self.page.get_by_role("listitem").filter(has_text="Export filtered items").click()
        self.page.get_by_label("Export Format").select_option("Microsoft Excel (.xlsx)")
        with self.page.expect_download() as download_info:
            self.page.locator("#modal").get_by_role("button", name="Export").click()
        download = download_info.value
        # Save the downloaded file to your defined location
        download.save_as(download_path)
    
    def verify_filtered_data(self, input_path: str, exported_path: str):
        # --- Step 1: Load datasets ---
        df_input = pd.read_excel(input_path, dtype=str)
        df_input["Amount"] = pd.to_numeric(df_input["Amount"], errors="coerce")

        df_exported = pd.read_excel(exported_path, dtype=str)
        df_exported["Amount"] = pd.to_numeric(df_exported["Amount"], errors="coerce")

        # --- Step 2: Locally apply same filters as website ---
        df_expected = df_input[
            (df_input["Status"].str.strip().eq("Active")) &
            (df_input["Amount"] >= 1000) &
            (df_input["CreatedDate"].str.contains("2023", na=False))
        ].copy()

        # --- Step 3: Sort and reset index for reliable comparison ---
        df_expected = df_expected.sort_values(by=["CustomerId"]).reset_index(drop=True)
        df_exported = df_exported.sort_values(by=["CustomerId"]).reset_index(drop=True)


        assert df_expected.equals(df_exported), "❌ Data mismatches found between Source filtered file and exported data."
        print("✅ All data matched successfully!")
        # --- Step 4: Compare datasets ---
        # if df_expected.equals(df_exported):
        #     print("✅ Filtered data validation successful — exported file matches expected results.")
        # else:
        #     print("❌ Validation failed — mismatches found.")

        #     # --- Step 5: Find differences ---
        #     merged = df_expected.merge(df_exported, on=list(df_expected.columns), how="outer", indicator=True)
        #     mismatched_rows = merged[merged["_merge"] != "both"]

        #     print("Mismatched rows:")
        #     print(mismatched_rows)

        #     # Optional: save mismatches
        #     mismatched_rows.to_excel("filtered_data_mismatches.xlsx", index=False)
        #     print("📁 Saved mismatches to: filtered_data_mismatches.xlsx")
       
            
