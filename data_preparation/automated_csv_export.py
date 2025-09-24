import time
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import csv
import re

def setup_driver():
    """Set up Chrome WebDriver with appropriate options"""
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        
        # Set download preferences
        download_dir = os.path.join(os.getcwd(), "exports")
        os.makedirs(download_dir, exist_ok=True)
        
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Initialize the driver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        return driver
    except Exception as e:
        print(f"Error setting up driver: {e}")
        return None

def login(driver, username, password):
    """Log in to the admin portal"""
    try:
        print("Logging in...")
        driver.get("https://aishikshya.admin.fuseclassroom.com/login")
        
        # Wait for and fill login form
        username_field = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.TAG_NAME, "button")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        
        # Wait for login to complete
        try:
            WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.CLASS_NAME, "listing"))
            )
            print("Login successful!")
            return True
        except TimeoutException:
            if "login" in driver.current_url.lower():
                print("Login failed - still on login page")
                return False
            else:
                print("Login might have succeeded but couldn't find listing element")
                return True
                
    except Exception as e:
        print(f"Error during login: {e}")
        return False

def get_exam_links(driver):
    """Extract all exam scoreboard links from the listing page"""
    try:
        print("Extracting exam links...")
        
        # Navigate to exams page if not already there
        if "exams" not in driver.current_url:
            driver.get("https://aishikshya.admin.fuseclassroom.com/exams?academicYearId=65d47ca75d5d1d2a9d6c6124&filterBy=all&showAll=Only%20mine")
        
        # Wait for page to load
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CLASS_NAME, "listing"))
        )
        
        # Parse page with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        exam_listings = soup.find_all('div', class_='listing')
        
        exam_data = []
        for exam in exam_listings:
            try:
                title_elem = exam.find('span', class_='listing--title')
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                
                # Find the scoreboard link
                scoreboard_link = None
                for a in exam.find_all('a', href=True):
                    if 'scoreboard' in a['href']:
                        scoreboard_link = a['href']
                        break
                
                if not scoreboard_link:
                    print(f"No scoreboard link found for {title}")
                    continue
                
                full_url = urljoin("https://aishikshya.admin.fuseclassroom.com", scoreboard_link)
                
                exam_data.append({
                    'title': title,
                    'url': full_url
                })
            except Exception as e:
                print(f"Error extracting exam data: {e}")
                continue
        
        print(f"Found {len(exam_data)} exams")
        return exam_data
        
    except Exception as e:
        print(f"Error getting exam links: {e}")
        return []

def change_rows_per_page(driver, rows=500, retries=3):
    """Change the number of rows displayed per page with retries"""
    fallback_rows = [200, 100, 50]  # Fallback options if 500 fails
    for attempt in range(retries):
        try:
            print(f"  Changing rows per page to {rows} (Attempt {attempt + 1}/{retries})...")
            
            # Ensure page is fully loaded
            WebDriverWait(driver, 45).until(
                lambda d: d.execute_script('return document.readyState') == 'complete'
            )
            
            # Find and click the dropdown button using JavaScript
            dropdown_button = WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.ID, "pageDropDown"))
            )
            driver.execute_script("arguments[0].click();", dropdown_button)
            
            # Wait for dropdown menu to appear
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, f"//a[@data-page='{rows}']"))
            )
            
            # Click the desired rows option using JavaScript
            rows_option = driver.find_element(By.XPATH, f"//a[@data-page='{rows}']")
            driver.execute_script("arguments[0].click();", rows_option)
            
            # Wait for table to reload
            WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
            )
            
            # Verify the change
            total_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "react-bootstrap-table-pagination-total"))
            )
            total_text = total_element.text.strip()
            if f"1 to {rows}" in total_text or str(rows) in total_text:
                print(f"  Successfully changed to {rows} rows per page")
                return True
            else:
                print(f"  Failed to verify {rows} rows per page, text: {total_text}")
                
                # Try fallback row counts
                if rows == 500 and attempt == retries - 1:
                    for fallback in fallback_rows:
                        print(f"  Trying fallback rows per page: {fallback}")
                        if change_rows_per_page(driver, fallback, retries=1):
                            return True
                return False
                
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(f"  Error changing rows per page: {e}")
            if attempt < retries - 1:
                print("  Retrying...")
                time.sleep(5)
            continue
    print(f"  Failed to change rows per page to {rows} after {retries} attempts")
    return False

def get_total_results(driver, retries=3):
    """Get the total number of results from the pagination info with retries"""
    for attempt in range(retries):
        try:
            # Wait for the pagination total element
            total_element = WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.CLASS_NAME, "react-bootstrap-table-pagination-total"))
            )
            total_text = total_element.text.strip()
            
            # Extract the total number using regex
            match = re.search(r'of\s+(\d+)\s+Results', total_text, re.IGNORECASE)
            if match:
                total = int(match.group(1))
                print(f"  Extracted total results: {total}")
                return total
            print("  No total results found in text:", total_text)
            if attempt < retries - 1:
                print("  Retrying...")
                time.sleep(5)
            continue
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(f"  Error getting total results: {e}")
            if attempt < retries - 1:
                print("  Retrying...")
                time.sleep(5)
            continue
    print("  Failed to get total results after retries")
    return 0

def export_all_scoreboard_data(driver, exam_url, exam_title):
    """Export all data from a scoreboard with pagination"""
    try:
        print(f"Processing: {exam_title}")
        
        # Navigate to scoreboard
        driver.get(exam_url)
        
        # Wait for table to load and page to be fully ready
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
        )
        WebDriverWait(driver, 45).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        
        # Change to show 500 rows per page
        if not change_rows_per_page(driver, 500):
            print("  Failed to change rows per page, using default...")
        
        # Get total number of results
        total_results = get_total_results(driver)
        print(f"  Total results: {total_results}")
        
        if total_results == 0:
            print("  No results found, skipping export...")
            return None
        
        all_data = []
        page_num = 1
        processed_count = 0
        
        while processed_count < total_results:
            print(f"  Processing page {page_num}...")
            
            # Wait for table to load
            WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
            )
            
            # Parse current page
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table')
            
            if not table:
                print("  No table found")
                break
            
            # Extract table headers if first page
            if page_num == 1:
                thead = table.find('thead')
                if thead:
                    headers = [th.text.strip() for th in thead.find_all('th')]
                    all_data.append(headers)
                else:
                    print("  No table header found")
                    break
            
            # Extract table rows
            tbody = table.find('tbody')
            if not tbody:
                print("  No table body found")
                break
                
            rows = tbody.find_all('tr')
            if not rows:
                print("  No rows found in table body")
                break
                
            for row in rows:
                cells = [td.text.strip() for td in row.find_all('td')]
                if cells:  # Only add non-empty rows
                    all_data.append(cells)
                    processed_count += 1
            
            print(f"  Processed {processed_count} of {total_results} records")
            
            # Check if we need to go to next page
            if processed_count >= total_results:
                break
                
            # Find and click next page button
            try:
                next_button = WebDriverWait(driver, 45).until(
                    EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Next page') or contains(@aria-label, 'Next')]"))
                )
                
                # Check if next button is disabled
                parent_li = next_button.find_element(By.XPATH, "./..")
                if 'disabled' in parent_li.get_attribute('class'):
                    print("  Next button is disabled, reached last page")
                    break
                
                # Click the next page button using JavaScript
                driver.execute_script("arguments[0].scrollIntoView();", next_button)
                driver.execute_script("arguments[0].click();", next_button)
                
                # Wait for the next page to load
                WebDriverWait(driver, 45).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
                )
                
                page_num += 1
                
            except (NoSuchElementException, TimeoutException):
                print("  No next page button found or not clickable")
                break
            except Exception as e:
                print(f"  Error navigating to next page: {e}")
                break
        
        # Save to CSV
        safe_title = "".join(c for c in exam_title if c.isalnum() or c in " _-").rstrip()
        filename = f"exports/{safe_title}.csv"
        
        # Create exports directory if it doesn't exist
        os.makedirs("exports", exist_ok=True)
        
        # Save data to CSV
        if len(all_data) > 1:  # At least headers + one row
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerows(all_data)
            print(f"  Saved {len(all_data)-1} records to {filename}")
            return filename
        else:
            print(f"  No data found for {exam_title}")
            return None
            
    except Exception as e:
        print(f"  Error processing {exam_title}: {e}")
        return None

def main():
    # Setup
    driver = setup_driver()
    if not driver:
        print("Failed to setup WebDriver")
        return
    
    try:
        # Login
        if not login(driver, "instructor1@fuse.ai", "@Fu53nepal"):
            print("Login failed. Exiting...")
            return
        
        # Get all exam links
        exams = get_exam_links(driver)
        
        if not exams:
            print("No exams found. Exiting...")
            return
        
        # Process each exam
        for i, exam in enumerate(exams, 1):
            print(f"\nProcessing exam {i}/{len(exams)}: {exam['title']}")
            export_all_scoreboard_data(driver, exam['url'], exam['title'])
            time.sleep(3)  # Be polite with requests between exams
        
        print("All exams processed successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()