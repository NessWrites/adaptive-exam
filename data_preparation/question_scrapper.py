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
import json  # Added for potential JSON handling if needed

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

def scrape_submission(driver, submission_url, student_name):
    """Scrape detailed submission data for a student"""
    try:
        print(f"    Scraping submission for {student_name} at {submission_url}")
        driver.get(submission_url)
        
        # Wait for questions to load
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CLASS_NAME, "question--card"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        questions = []
        
        for idx, card in enumerate(soup.find_all('div', class_='question--card'), 1):
            try:
                is_correct = 'question--card__correct' in card.get('class', [])
                
                q_text_elem = card.find('li', class_='question--text')
                q_text = q_text_elem.text.strip() if q_text_elem else ''
                
                img_elem = card.find('div', class_='uploaded-img')
                img_url = urljoin("https://aishikshya.admin.fuseclassroom.com", img_elem.find('img')['src']) if img_elem and img_elem.find('img') else None
                
                marks_elem = card.find('div', class_='helper')
                marks = marks_elem.text.strip() if marks_elem else ''
                
                option_list = card.find('ul', class_='question--option')
                q_type = 'unknown'
                selected_options = []
                options_metadata = []  # List of dicts for options
                
                if option_list:
                    inputs = option_list.find_all('input')
                    if inputs:
                        input_types = {inp.get('type') for inp in inputs}
                        if input_types == {'radio'}:
                            q_type = 'single'
                        elif input_types == {'checkbox'}:
                            q_type = 'multiple'
                        
                        for inp in inputs:
                            option_label = inp.find_next_sibling('span').text.strip() if inp.find_next_sibling('span') else ''
                            option_value = inp.get('value', '')
                            is_selected = 'checked' in inp.attrs
                            option_id = inp.get('id', '')
                            
                            options_metadata.append({
                                'label': option_label,
                                'value': option_value,
                                'id': option_id,
                                'selected': is_selected
                            })
                            
                            if is_selected:
                                selected_options.append(option_label)
                
                questions.append({
                    'question_number': idx,
                    'question_text': q_text,
                    'img_url': img_url,
                    'marks': marks,
                    'type': q_type,
                    'selected_options': ','.join(selected_options),
                    'options_metadata': json.dumps(options_metadata),  # Store as JSON string
                    'is_correct': is_correct
                })
            except Exception as e:
                print(f"    Error extracting question {idx} for {student_name}: {e}")
                continue
        
        print(f"    Extracted {len(questions)} questions for {student_name}")
        return questions
        
    except Exception as e:
        print(f"    Error scraping submission for {student_name}: {e}")
        return []

def export_all_scoreboard_data(driver, exam_url, exam_title):
    """Export all data from a scoreboard with pagination and scrape submissions"""
    base_url = "https://aishikshya.admin.fuseclassroom.com/"
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
        
        students = []
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
            
            # Extract table rows (skip headers, as we'll define our own)
            tbody = table.find('tbody')
            if not tbody:
                print("  No table body found")
                break
                
            rows = tbody.find_all('tr')
            if not rows:
                print("  No rows found in table body")
                break
                
            for row in rows:
                tds = row.find_all('td')
                if len(tds) < 7:
                    continue
                    
                try:
                    # Student info
                    student_div = tds[0].find('div', class_='students')
                    name = student_div.find('span', class_='students--name').text.strip() if student_div else ''
                    email = student_div.find('span', class_='students--email').text.strip() if student_div else ''
                    
                    score = tds[1].text.strip()
                    # tds[2] is empty
                    submitted_at = tds[3].text.strip()
                    
                    plagiarism_div = tds[4].find('div')
                    plagiarism = plagiarism_div.find('span').text.strip() if plagiarism_div and plagiarism_div.find('span') else ''
                    
                    status = tds[5].text.strip()
                    
                    submission_a = tds[6].find('a', href=True)
                    submission_url = urljoin(base_url, submission_a['href']) if submission_a else None
                    
                    students.append({
                        'name': name,
                        'email': email,
                        'score': score,
                        'submitted_at': submitted_at,
                        'plagiarism': plagiarism,
                        'status': status,
                        'submission_url': submission_url
                    })
                    processed_count += 1
                except Exception as e:
                    print(f"  Error extracting row: {e}")
                    continue
            
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
        
        # Save scoreboard to CSV
        safe_title = "".join(c for c in exam_title if c.isalnum() or c in " _-").rstrip()
        filename = f"exports/{safe_title}_scoreboard.csv"
        
        os.makedirs("exports", exist_ok=True)
        
        if students:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'email', 'score', 'submitted_at', 'plagiarism', 'status', 'submission_url']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(students)
            print(f"  Saved {len(students)} student records to {filename}")
        else:
            print(f"  No student data found for {exam_title}")
            return None
        
        # Now scrape submissions for each student
        submissions_dir = f"exports/{safe_title}_submissions"
        os.makedirs(submissions_dir, exist_ok=True)
        
        for idx, student in enumerate(students, 1):
            if student['submission_url']:
                print(f"  Processing submission {idx}/{len(students)} for {student['name']}")
                questions = scrape_submission(driver, student['submission_url'], student['name'])
                
                if questions:
                    safe_name = "".join(c for c in student['name'] if c.isalnum() or c in " _-").rstrip()
                    sub_filename = f"{submissions_dir}/{safe_name}_submission.csv"
                    
                    with open(sub_filename, 'w', newline='', encoding='utf-8') as f:
                        fieldnames = ['question_number', 'question_text', 'img_url', 'marks', 'type', 'selected_options', 'options_metadata', 'is_correct']
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(questions)
                    print(f"    Saved {len(questions)} questions to {sub_filename}")
                
                time.sleep(2)  # Delay between submissions to avoid rate limiting
            else:
                print(f"  No submission URL for {student['name']}, skipping...")
        
        return filename
            
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