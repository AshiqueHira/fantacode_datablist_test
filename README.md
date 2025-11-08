# 🧾 Data Integrity Validation using Playwright & Python

This project automates the validation of data integrity between a **local Excel file** and the **filtered dataset displayed on [Datablist](https://app.datablist.com/)**.  
It uses **Playwright for web automation** and **Pandas for data comparison**.

---

## 🚀 Project Overview

The goal of this project is to ensure that the data uploaded and filtered on the Datablist web app matches exactly with the locally stored Excel data after applying identical filters.

The automation performs the following steps:

1. **Upload and verify**
   - Navigate to website
   - Upload data
   - Verify the data displayed on the Datablist UI with the source file
3. **Apply filters and Export** ( `Status`, `Amount`, `CreatedDate`)
   - Apply the required filters
   - Export the file in the local path
4. **Verify the exported data**:
   - Apply the same filters for the source data
   - Assert the source file to exported data and validate

---

## 🧰 Tech Stack

- **Language:** Python 3.14
- **Automation Framework:** Playwright
- **Data Processing:** Pandas
- **Testing Framework (optional):** Pytest

---

## ⚙️ Setup Instructions

```bash

#Clone the Repository

git clone https://github.com/AshiqueHira/fantacode_datablist_test.git
cd fantacode_datablist_test

#Install the Pytest plugin:
  pip install pytest-playwright

#Install the required browsers:
  playwright install
  
#Run
pytest tests/test_datablist_upload.py
```
---
Thanks and Regards<br>
Ashique H M<br>
ashiquehira.me@gmail.com<br>
