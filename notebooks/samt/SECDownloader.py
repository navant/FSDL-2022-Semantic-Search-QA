"""
Script to download files from SEC's EDGAR database.

The main function to call is `download_sec_forms(driver, ticker, form_type, year_selection, out_dir, verbose)`
Docstring has more details.

Bottom of script has usage example.
"""


import os
import time
from pathlib import Path

import pandas as pd

# Converting webpages to pdf. May require installation of wkhtmltopdf.
import pdfkit
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    NoSuchElementException,
)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService

# Convenience package to load webdrivers
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def init_chrome(headless=True):
    """
    Creates a chrome-based web driver.
        Args:
            headless: Set True to run browser in background.

        Returns:
            Selenium driver.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--print-to-pdf")
    if headless:
        options.add_argument("--headless")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.maximize_window()
    return driver


def init_firefox(headless=True):
    """
    Creates a firefox-based web driver.
        Args:
            headless: Set True to run browser in background.

        Returns:
            Selenium driver.
    """
    options = webdriver.FirefoxOptions()
    options.add_argument("--print-to-pdf")
    if headless:
        options.add_argument("--headless")

    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
    driver.maximize_window()
    return driver


def download_sec_forms(driver, ticker, form_type, year_selection, out_dir, verbose=False):
    """
    Downloads all forms for a ticker that qualify as 'recent enough' to have an 'interactive data' option, which usually corresponds to the last 10 years or so.

    Format for saved files is <output_dir>/<ticker>_<filing_type>_<date>.pdf

    Args:
        driver: Selenium web driver
        ticker: Abbreviation of company, e.g. AAPL
        form-type: e.g. '10-K' or '8-K'.
        out_dir: Save directory for downloaded PDF files.
        year_selection: Which documents to select. Has several options
                   - Get documents since year by entering a single year, e.g. year_selection = '2010'
                   - Get documents in date range by entering tuple of endpoint years, e.g. year_selection = ['2010', '2014']
                   - Else, attempt to download all documents on page (note, some old ones don't have links and will fail)
        verbose: Display message after successful or failed download.
    """

    # Various xpaths for navigating EDGAR XML
    filing_search_field_path = '//input[@name="type"]'
    search_button_path = '//input[@type="submit"]'
    num_results = '//select[@name="count"]'
    results_100 = '//option[@value="100"]'
    search_table_row_path = '//table[@summary="Results"]/tbody/tr'
    document_format_files_path = '//table[@summary="Document Format Files"]/tbody/tr'
    menu_dropdown_path = '//a[@id="menu-dropdown-link"]'
    open_as_html_path = '//a[@id="form-information-html"]'

    base_url = "https://www.sec.gov/cgi-bin/browse-edgar?CIK=" + ticker + "&owner=exclude&action=getcompany"
    driver.get(base_url)

    try:
        # Display all possible results for selected form_type.
        search_bar = driver.find_element("xpath", filing_search_field_path)
        search_bar.clear()
        search_bar.click()
        search_bar.send_keys(form_type)
        entries_button = driver.find_element("xpath", num_results)
        entries_button.click()
        results = driver.find_element("xpath", results_100)
        results.click()
        search_button = driver.find_element("xpath", search_button_path)
        search_button.click()

        # Cache current url so we can return to it after downloading a selected file.
        results_url = driver.current_url
        num_rows = len(driver.find_elements("xpath", search_table_row_path))

    except NoSuchElementException:
        if verbose:
            print(f"No page exists for {ticker}")
        return

    # Wait for results to load
    time.sleep(1)

    def results_table_entry(row, col):
        """
        Convenience function for traversing search results table.
        """
        return driver.find_elements("xpath", search_table_row_path)[row].find_elements("xpath", "td")[col]

    if isinstance(year_selection, str):
        start_year = int(year_selection)
        selected_indices = [
            i for i in range(1, num_rows) if int(results_table_entry(i, -2).text.split("-")[0]) >= start_year
        ]

    elif isinstance(year_selection, list):
        assert len(year_selection) == 2

        start_year = int(year_selection[0])
        end_year = int(year_selection[1])
        assert end_year >= start_year

        selected_indices = [
            i
            for i in range(1, num_rows)
            if (
                int(results_table_entry(i, -2).text.split("-")[0]) >= start_year
                and int(results_table_entry(i, -2).text.split("-")[0]) <= end_year
            )
        ]
    else:
        selected_indices = list(range(1, num_rows))

    if verbose:
        print(f"{ticker}: Search returned {len(selected_indices)} files.")

    # Attempt to download each file in selection, one by one.
    for index in selected_indices:

        filing_type = results_table_entry(index, 0).text.replace("/", "-")
        date = results_table_entry(index, -2).text
        out_file = ticker + "_" + filing_type + "_" + date + ".pdf"

        # Sometimes other filing types spontaneously appear in search results.
        # '/' replaced with '-' otherwise it causes problems with saving files.
        if not (filing_type == form_type.replace("/", "-")):
            continue

        if Path(out_dir + "/" + out_file).is_file():
            if verbose:
                print(f'\tFile {out_dir + "/" + out_file} already exists.')
            break

        # Enter subpage relating to specific filing.
        try:
            results_table_entry(index, 1).find_element("xpath", 'a[@id="documentsbutton"]').click()
        except ElementClickInterceptedException:
            if verbose:
                print("Click interrupted, waiting to try again")
            time.sleep(5)
            driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
            results_table_entry(index, 1).find_element("xpath", 'a[@id="documentsbutton"]').click()

        time.sleep(0.5)

        try:
            main_doc_table = driver.find_elements("xpath", document_format_files_path)

            # (row, col) = (1,2) contains the link to the document.
            link_to_form = main_doc_table[1].find_elements("xpath", 'td[@scope="row"]')[2].find_element("xpath", "a")
            link_to_form.click()

            time.sleep(0.5)

            menu_dropdown = driver.find_elements("xpath", menu_dropdown_path)

            # Some pages have a menu bar at top
            if menu_dropdown:

                # Give menu 5 seconds to load, trying every 0.5 seconds.
                for _ in range(10):
                    try:
                        menu_dropdown[0].click()
                    except ElementClickInterceptedException:
                        time.sleep(0.5)
                    else:
                        break

                open_as_html_button = driver.find_element("xpath", open_as_html_path)
                open_as_html_button.click()

                # Switch to tab with html version of document.
                driver.switch_to.window(driver.window_handles[-1])

                if verbose:
                    print(f'\tSaving {out_dir + "/" + out_file} ...', end="")
                pdfkit.from_url(driver.current_url, out_dir + "/" + out_file)
                if verbose:
                    print(f"\tDONE")

                # Quit current tab
                driver.close()

                driver.switch_to.window(driver.window_handles[0])
                driver.switch_to.default_content()

            # Others take you straight to the html form.
            else:

                pdfkit.from_url(driver.current_url, out_dir + "/" + out_file)
                if verbose:
                    print(f'\tSaved {out_dir + "/" + out_file}')

        except:
            if verbose:
                print(f'\tUnable to save {out_dir + "/" + out_file}')

        driver.get(results_url)


if __name__ == "__main__":

    # Set headless = False for debugging.
    driver = init_firefox(headless=True)
    form_type = "10-K"
    year_selection = "2022"
    out_dir = "./reports_10-K_2022"

    os.makedirs(out_dir, exist_ok=True)

    df = pd.read_csv("sp500.csv")
    df.sort_values("Symbol")
    for ticker in df["Symbol"]:

        # Try twice before moving on.
        for _ in range(2):
            try:
                download_sec_forms(driver, ticker, form_type, year_selection, out_dir, verbose=True)
            except:
                pass
            else:
                break

    driver.quit()
