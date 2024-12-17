from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import csv
import time
import undetected_chromedriver as uc 
 # Ensure this is installed
import csv
import pandas as pd

# Initialize the undetected Chrome driver
driver = uc.Chrome()

df = pd.read_csv('CAA.csv', header=None)

# Convert the first column (index 0) to a list
urls = df[0].tolist()


username = ""
password = ""
login_url = "https://caconnect.icai.org/login"



# Open CSV file in write mode
with open("member_data.csv", mode="w", newline="", encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Member Name", "Mobile", "Website", "Email"])  # Write header
    try:
        # Open login page
        driver.get(login_url)
        print("Logging in...")
        
        # Login process
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(username)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()
        
        # Wait for login to complete
        time.sleep(3)
        
        # Loop through each URL
        for url in urls:
            try:
                driver.get(url)
                time.sleep(3)  # Increased wait time for page load
                
                try:
                    # Member Name - Using XPath to get text node after h5
                    member_name = driver.execute_script("""
                        var element = document.evaluate("//h5[contains(text(), 'Member Name')]/parent::div", 
                        document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        return element.childNodes[2].textContent.trim();
                    """)
                    
                    # Mobile Number
                    mobile = driver.execute_script("""
                        var element = document.evaluate("//h5[contains(text(), 'Mobile')]/following-sibling::p", 
                        document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        return element.textContent.trim();
                    """)
                    
                    # Website
                    try:
                        website = driver.execute_script("""
                            var element = document.evaluate("//h5[contains(text(), 'Website')]/following-sibling::p/a", 
                            document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                            return element ? element.getAttribute('href') : 'No website provided';
                        """)
                    except:
                        website = "No website provided"
                    
                    # Email
                    email = driver.execute_script("""
                        var element = document.evaluate("//h5[contains(text(), 'Email')]/following-sibling::p", 
                        document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                        return element.textContent.trim();
                    """)
                    
                    # Verify data is not empty
                    if not member_name or not mobile or not email:
                        raise Exception("Required data is missing")
                    
                    # Print and append data to CSV file
                    print(f"\nSuccessfully scraped data for URL: {url}")
                    print(f"Member Name: {member_name}")
                    print(f"Mobile: {mobile}")
                    print(f"Website: {website}")
                    print(f"Email: {email}")
                    print("-" * 50)
                    
                    writer.writerow([member_name, mobile, website, email])
                    
                except Exception as e:
                    print(f"Error extracting specific data from {url}: {str(e)}")
                    # Try alternative method using pure XPath
                    try:
                        # Alternative XPath method
                        member_name = driver.find_element(By.XPATH, "//div[contains(@class, 'col-md-6')][.//h5[contains(text(),'Member Name')]]").text.replace('Member Name', '').strip()
                        mobile = driver.find_element(By.XPATH, "//div[contains(@class, 'col-md-6')][.//h5[contains(text(),'Mobile')]]/p").text.strip()
                        try:
                            website_elem = driver.find_element(By.XPATH, "//div[contains(@class, 'col-md-6')][.//h5[contains(text(),'Website')]]/p/a")
                            website = website_elem.get_attribute('href')
                        except:
                            website = "No website provided"
                        email = driver.find_element(By.XPATH, "//div[contains(@class, 'col-md-6')][.//h5[contains(text(),'Email')]]/p").text.strip()
                        
                        print(f"\nSuccessfully scraped data using alternative method for URL: {url}")
                        print(f"Member Name: {member_name}")
                        print(f"Mobile: {mobile}")
                        print(f"Website: {website}")
                        print(f"Email: {email}")
                        print("-" * 50)
                        
                        writer.writerow([member_name, mobile, website, email])
                    except Exception as e2:
                        print(f"Alternative method also failed for {url}: {str(e2)}")
                        writer.writerow(["Error", "Error", "Error", "Error"])
                
            except Exception as e:
                print(f"Error accessing URL {url}: {str(e)}")
                continue
            
    except Exception as e:
        print(f"Major error occurred: {str(e)}")
    finally:
        driver.quit()
        print("\nScraping completed. Check member_data.csv for results.")
