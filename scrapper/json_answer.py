import time
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def setup_driver():
    """Set up Chrome WebDriver with appropriate options"""
    try:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-extensions')
        
        download_dir = os.path.join(os.getcwd(), "my_scraped_data")
        os.makedirs(download_dir, exist_ok=True)
        
        prefs = {
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
            "profile.default_content_settings.popups": 0
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
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
        
        username_field = WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        password_field = driver.find_element(By.NAME, "password")
        login_button = driver.find_element(By.TAG_NAME, "button")
        
        username_field.send_keys(username)
        password_field.send_keys(password)
        login_button.click()
        
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
                try:
                    WebDriverWait(driver, 10).until(
                        lambda d: "login" not in d.current_url.lower()
                    )
                    print("Login might have succeeded - redirected from login page")
                    return True
                except:
                    print("Login status unclear")
                    return False
            
    except Exception as e:
        print(f"Error during login: {e}")
        return False

def get_exam_links(driver):
    """Extract all exam scoreboard links from the listing page"""
    try:
        print("Extracting exam links...")
        
        if "exams" not in driver.current_url:
            driver.get("https://aishikshya.admin.fuseclassroom.com/exams?academicYearId=65d47ca75d5d1d2a9d6c6124&filterBy=all&showAll=Only%20mine")
        
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CLASS_NAME, "listing"))
        )
        
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        exam_listings = soup.find_all('div', class_='listing')
        
        exam_data = []
        for exam in exam_listings:
            try:
                title_elem = exam.find('span', class_='listing--title')
                if not title_elem:
                    continue
                    
                title = title_elem.text.strip()
                
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

def wait_for_page_load(driver, timeout=15):
    """Wait for page to be completely loaded"""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
        time.sleep(2)
        return True
    except TimeoutException:
        print("  Warning: Page load timeout, continuing anyway...")
        return False

def change_rows_per_page(driver, rows=200, retries=3):
    """Change the number of rows displayed per page with enhanced error handling"""
    for attempt in range(retries):
        try:
            print(f"  Changing rows per page to {rows} (Attempt {attempt + 1}/{retries})...")
            
            wait_for_page_load(driver)
            
            # Find and click the dropdown button
            dropdown_button = WebDriverWait(driver, 45).until(
                EC.element_to_be_clickable((By.ID, "pageDropDown"))
            )
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", dropdown_button)
            time.sleep(1)
            
            driver.execute_script("arguments[0].click();", dropdown_button)
            
            # Wait for dropdown menu to appear
            rows_option = WebDriverWait(driver, 45).until(
                EC.element_to_be_clickable((By.XPATH, f"//a[@data-page='{rows}']"))
            )
            
            driver.execute_script("arguments[0].click();", rows_option)
            
            # CRITICAL: Wait for the page to reload with new rows
            print(f"  Waiting 25 seconds for table to reload with {rows} rows...")
            time.sleep(25)
            
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
            )
            
            wait_for_page_load(driver, timeout=20)
            
            # Verify the change
            total_element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "react-bootstrap-table-pagination-total"))
            )
            total_text = total_element.text.strip()
            
            if f"1 to {rows}" in total_text or (str(rows) in total_text and "Showing" in total_text):
                print(f"  Successfully changed to {rows} rows per page")
                return True
            else:
                print(f"  Verification unclear for {rows} rows per page, text: {total_text}")
                match = re.search(r'1 to (\d+)', total_text)
                if match and int(match.group(1)) > 10:
                    print(f"  Accepting {match.group(1)} rows as better than default 10")
                    return True
                
        except (TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException) as e:
            print(f"  Error changing rows per page: {e}")
            if attempt < retries - 1:
                print(f"  Retrying in 5 seconds...")
                time.sleep(5)
                continue
            
    print(f"  Failed to change rows per page to {rows} after all attempts")
    return False

def get_total_results(driver, retries=3):
    """Get the total number of results from the pagination info with retries"""
    for attempt in range(retries):
        try:
            total_element = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "react-bootstrap-table-pagination-total"))
            )
            total_text = total_element.text.strip()
            
            match = re.search(r'of\s+(\d+)\s+Results', total_text, re.IGNORECASE)
            if match:
                total = int(match.group(1))
                print(f"  Total results found: {total}")
                return total
                
            match = re.search(r'of\s+(\d+)', total_text)
            if match:
                total = int(match.group(1))
                print(f"  Total results found (alternative pattern): {total}")
                return total
                
            print(f"  Could not parse total from text: {total_text}")
            if attempt < retries - 1:
                time.sleep(2)
                continue
                
        except (TimeoutException, NoSuchElementException, WebDriverException) as e:
            print(f"  Error getting total results: {e}")
            if attempt < retries - 1:
                time.sleep(2)
                continue
                
    print("  Failed to get total results, defaulting to 0")
    return 0

def scrape_submission(driver, submission_url, student_name):
    """Scrape detailed submission data for a student"""
    try:
        print(f"    Scraping submission for {student_name}")
        driver.get(submission_url)
        
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CLASS_NAME, "question--card"))
        )
        
        wait_for_page_load(driver)
        
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
                options_metadata = []
                
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
                    'options_metadata': json.dumps(options_metadata),
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

def navigate_to_next_page(driver, current_page, retries=3):
    """Navigate to the next page with improved error handling and longer waits"""
    for attempt in range(retries):
        try:
            print(f"  Navigating to page {current_page + 1} (Attempt {attempt + 1}/{retries})...")
            
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "react-bootstrap-table-pagination"))
            )
            
            wait_for_page_load(driver)
            
            next_button_selectors = [
                "//a[contains(text(), 'Next page')]",
                "//a[contains(@title, 'Next page')]",
                "//a[contains(@aria-label, 'Next')]",
                f"//a[@title='{current_page + 1}']",
                f"//a[contains(text(), '{current_page + 1}')]"
            ]
            
            next_button = None
            for selector in next_button_selectors:
                try:
                    buttons = driver.find_elements(By.XPATH, selector)
                    for button in buttons:
                        parent_li = button.find_element(By.XPATH, "./..")
                        parent_class = parent_li.get_attribute('class') or ''
                        if 'disabled' not in parent_class.lower():
                            next_button = button
                            print(f"  Found clickable next button with selector: {selector}")
                            break
                    if next_button:
                        break
                except:
                    continue
            
            if not next_button:
                print("  No clickable next button found")
                return False
            
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_button)
            time.sleep(1)
            
            WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable(next_button)
            )
            
            driver.execute_script("arguments[0].click();", next_button)
            print(f"  Clicked next page button")
            
            print(f"  Waiting 15 seconds for page to load...")
            time.sleep(15)
            
            WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
            )
            
            wait_for_page_load(driver, timeout=10)
            
            try:
                total_element = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "react-bootstrap-table-pagination-total"))
                )
                total_text = total_element.text.strip()
                
                match = re.search(r'(\d+) to (\d+)', total_text)
                if match:
                    start_num = int(match.group(1))
                    if start_num > 10:
                        print(f"  Successfully navigated to new page - showing from {start_num}")
                        return True
                    elif current_page == 1 and start_num == 1:
                        print(f"  Page navigation unclear, continuing... Text: {total_text}")
                        return True
                
            except Exception as e:
                print(f"  Could not verify page navigation: {e}")
                return True
            
        except Exception as e:
            print(f"  Error during page navigation: {e}")
            if attempt < retries - 1:
                print(f"  Retrying navigation in 5 seconds...")
                time.sleep(5)
                continue
            else:
                print(f"  Failed to navigate after {retries} attempts")
                return False
    
    return False

def scrape_exam_data(driver, exam_url, exam_title):
    """Scrape all data from a scoreboard and submissions, save to JSON"""
    base_url = "https://aishikshya.admin.fuseclassroom.com/"
    try:
        print(f"Processing: {exam_title}")
        
        driver.get(exam_url)
        
        WebDriverWait(driver, 45).until(
            EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
        )
        wait_for_page_load(driver)
        
        change_rows_per_page(driver, 200)
        
        total_results = get_total_results(driver)
        print(f"  Total results: {total_results}")
        
        if total_results == 0:
            print("  No results found, skipping...")
            return None
        
        exam_data = {}
        page_num = 1
        processed_count = 0
        max_pages = 100
        
        while processed_count < total_results and page_num <= max_pages:
            print(f"  Processing page {page_num}... (Processed: {processed_count}/{total_results})")
            
            WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
            )
            wait_for_page_load(driver)
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            table = soup.find('table')
            
            if not table:
                print("  No table found on current page")
                break
            
            tbody = table.find('tbody')
            if not tbody:
                print("  No table body found")
                break
                
            rows = tbody.find_all('tr')
            if not rows:
                print("  No rows found in table body")
                break
                
            page_processed = 0
            for row in rows:
                tds = row.find_all('td')
                if len(tds) < 7:
                    continue
                    
                try:
                    student_div = tds[0].find('div', class_='students')
                    if not student_div:
                        continue
                        
                    name_elem = student_div.find('span', class_='students--name')
                    email_elem = student_div.find('span', class_='students--email')
                    
                    name = name_elem.text.strip() if name_elem else ''
                    email = email_elem.text.strip() if email_elem else ''
                    
                    if name in exam_data:
                        print(f"  Skipping duplicate student: {name}")
                        continue
                    
                    score = tds[1].text.strip()
                    submitted_at = tds[3].text.strip()
                    
                    plagiarism_div = tds[4].find('div')
                    plagiarism = plagiarism_div.find('span').text.strip() if plagiarism_div and plagiarism_div.find('span') else ''
                    
                    status = tds[5].text.strip()
                    
                    submission_a = tds[6].find('a', href=True)
                    submission_url = urljoin(base_url, submission_a['href']) if submission_a else None
                    
                    student_data = {
                        'email': email,
                        'score': score,
                        'submitted_at': submitted_at,
                        'plagiarism': plagiarism,
                        'status': status,
                        'submission_url': submission_url,
                        'questions': []
                    }
                    
                    if submission_url and name:
                        student_data['questions'] = scrape_submission(driver, submission_url, name)
                        
                        # Navigate back to the scoreboard page
                        driver.get(exam_url)
                        
                        WebDriverWait(driver, 45).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "table-responsive"))
                        )
                        wait_for_page_load(driver)
                        
                        # Re-navigate to the correct page if we were on a page > 1
                        if page_num > 1:
                            print(f"  Returning to page {page_num} after submission scrape...")
                            for nav_page in range(2, page_num + 1):
                                if not navigate_to_next_page(driver, nav_page - 1):
                                    print(f"  Failed to return to page {page_num}, will continue from page 1")
                                    page_num = 1 # Reset to avoid infinite loop
                                    break
                    
                    exam_data[name] = student_data
                    processed_count += 1
                    page_processed += 1
                    
                    print(f"  Processed student {processed_count}: {name}")
                    
                except Exception as e:
                    print(f"  Error extracting data for student: {e}")
                    continue
            
            print(f"  Completed page {page_num}: processed {page_processed} new students")
            
            if processed_count >= total_results:
                print("  All students processed!")
                break
                
            if not navigate_to_next_page(driver, page_num):
                print(f"  Could not navigate to next page, stopping at page {page_num}")
                print(f"  Total processed: {processed_count}/{total_results}")
                break
                
            page_num += 1
        
        safe_title = "".join(c for c in exam_title if c.isalnum() or c in " _-").rstrip()
        filename = f"my_scraped_data/{safe_title}_data.json"
        
        os.makedirs("my_scraped_data", exist_ok=True)
        
        if exam_data:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(exam_data, f, ensure_ascii=False, indent=2)
            print(f"  Saved {len(exam_data)} student records to {filename}")
            print(f"  Final count: {processed_count}/{total_results} students processed")
            return filename
        else:
            print(f"  No data collected for {exam_title}")
            return None
            
    except Exception as e:
        print(f"  Error processing {exam_title}: {e}")
        return None

def main():
    """Main execution function"""
    driver = setup_driver()
    if not driver:
        print("Failed to setup WebDriver")
        return
    
    try:
        if not login(driver, "instructor1@fuse.ai", "@Fu53nepal"):
            print("Login failed. Exiting...")
            return
        
        exams = get_exam_links(driver)
        
        if not exams:
            print("No exams found. Exiting...")
            return
        
        # Create a set of all exam titles you want to skip.
        unwanted_exam_titles = {
            "AIF 2025 Entrance Exam - April 7th",
            "AIF 2025 Entrance Re Exam - April 9th",
            "AIF 2025 Entrance Exam (Sazience)",
            "AI Fellowship 2025 Internal Examination",
            "AIF 2025 Entrance Exam - April 5th",
            "AIF 2025 Entrance Exam - April 6th"
        }

        # Filter the list of exams, keeping only those whose titles are NOT in the unwanted set.
        filtered_exams = [
            exam for exam in exams 
            if exam['title'] not in unwanted_exam_titles
        ]

        print(f"Found {len(filtered_exams)} exams to process after filtering")
        
        for i, exam in enumerate(filtered_exams, 1):
            print(f"\n{'='*60}")
            print(f"Processing exam {i}/{len(filtered_exams)}: {exam['title']}")
            print(f"{'='*60}")
            
            result = scrape_exam_data(driver, exam['url'], exam['title'])
            
            if result:
                print(f"✓ Successfully processed: {exam['title']}")
            else:
                print(f"✗ Failed to process: {exam['title']}")
            
            if i < len(filtered_exams):
                print("Waiting 5 seconds before next exam...")
                time.sleep(5)
        
        print(f"\n{'='*60}")
        print("All exams processing completed!")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"An error occurred in main: {e}")
    
    finally:
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main()