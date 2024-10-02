from appium import webdriver
import time
from appium.webdriver.common.touch_action import TouchAction
from appium.options.ios import xcuitest
from appium.webdriver.common.mobileby import MobileBy
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.common.touch_action import TouchAction
from appium.webdriver.common.multi_action import MultiAction
from appium.webdriver.webelement import WebElement
from appium.webdriver.common.touch_action import TouchAction
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from random import randrange
import random
import sys
import requests
from password_generator import PasswordGenerator
import os
import json
import math
import requests
import logging
import threading
import signal
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # sets the _MEIPASS attribute to the temporary folder where it's unpacked
    application_path = sys._MEIPASS
else:
    application_path = os.path.dirname(os.path.abspath(__file__))

# Append the application path to sys.path to allow imports from there
sys.path.append(application_path)

# Now, import TINDER_PATHS
from tinder_paths import TINDER_PATHS
print("TINDER_PATHS loaded successfully.")

# Initialize pause flag
paused = False

def handle_pause(signum, frame):
    global paused
    paused = True
    print("Script paused")

def handle_unpause(signum, frame):
    global paused
    paused = False
    print("Script unpaused")

signal.signal(signal.SIGUSR1, handle_pause)
signal.signal(signal.SIGUSR2, handle_unpause)

def check_pause():
    while paused:
        time.sleep(1)

def log_message(message):
    logging.info(f"{time.time():.2f}: {message}")

# Set up logging
logging.basicConfig(filename='account_creation.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')

class TimestampWriter:
    def __init__(self, original_stdout):
        self.original_stdout = original_stdout
        self.start_time = time.time()

    def write(self, text):
        elapsed_time = time.time() - self.start_time
        self.original_stdout.write(f"{elapsed_time:.2f}s: {text}")

    def flush(self):
        self.original_stdout.flush()

sys.stdout = TimestampWriter(open('account_creation.log', 'w', buffering=1))

# Load API keys from command-line arguments
SMSPOOL_API_KEY = sys.argv[7]
DAISY_API_KEY = sys.argv[7]
dob_year = sys.argv[8]
save_containers = sys.argv[9].lower() == 'true'
activate_killswitch = sys.argv[10].lower() == 'true'
killswitch_timeout = int(sys.argv[11]) * 60  # Convert minutes to seconds
killswitch_max_attempts = int(sys.argv[12])
number_of_pictures = int(sys.argv[13])
profile_options_json = sys.argv[14]
proxy_type = sys.argv[15].strip().lower()
use_school = sys.argv[16].lower() == 'on'
schools = sys.argv[17].split(",") if use_school else []

# Validate proxy type
if proxy_type not in ['http', 'socks5']:
    print("Error: Invalid proxy type. Please choose either 'HTTP' or 'Socks5'.")
    sys.exit(1)

print(f"Received profile_options_json: {profile_options_json}")
print(f"Received proxy_type: {proxy_type}")

# Load profile options from JSON
try:
    profile_options = json.loads(profile_options_json)
except json.JSONDecodeError:
    print("Error: Invalid profile options JSON")
    sys.exit(1)

def click_element(driver, xpath, description, retries=5, delay=1):
    """
    Attempts to click an element specified by its XPath with retries.

    Args:
        driver: Appium driver instance.
        xpath (str): XPath of the element to click.
        description (str): Description of the element for logging.
        retries (int): Number of retry attempts.
        delay (int): Delay between retries in seconds.

    Returns:
        bool: True if clicked successfully, False otherwise.
    """
    for attempt in range(1, retries + 1):
        check_pause()
        try:
            element = driver.find_element(By.XPATH, xpath)
            if element.is_displayed():
                element.click()
                print(f"Clicked {description}")
                time.sleep(delay)
                return True
        except Exception as e:
            print(f"Attempt {attempt}: Could not click {description} - {str(e)}")
            time.sleep(delay)
    print(f"Failed to click {description} after {retries} attempts")
    return False

def send_keys_with_retry(driver, xpath, keys, description, retries=5, delay=1):
    """
    Attempts to send keys to an element specified by its XPath with retries.

    Args:
        driver: Appium driver instance.
        xpath (str): XPath of the element.
        keys (str): Keys to send.
        description (str): Description of the element for logging.
        retries (int): Number of retry attempts.
        delay (int): Delay between retries in seconds.

    Returns:
        bool: True if keys were sent successfully, False otherwise.
    """
    for attempt in range(1, retries + 1):
        check_pause()
        try:
            element = driver.find_element(By.XPATH, xpath)
            if element.is_displayed() and element.is_enabled():
                element.clear()
                element.send_keys(keys)
                print(f"Sent keys to {description}: {keys}")
                time.sleep(delay)
                return True
        except Exception as e:
            print(f"Attempt {attempt}: Could not send keys to {description} - {str(e)}")
            time.sleep(delay)
    print(f"Failed to send keys to {description} after {retries} attempts")
    return False


def handle_school_page(driver, use_school, school):
    try:
        # Check if the "If school is your thing" page is present
        school_page = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//XCUIElementTypeStaticText[@name="If school’s your thing..."]'))
        )
        
        if school_page.is_displayed():
            if not use_school or school is None:
                # If the feature is off, skip
                skip_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "//XCUIElementTypeButton[@name='Skip']"))
                )
                skip_button.click()
                print("School page skipped")
                return "skipped"
            else:
                # If the feature is on, handle the input process
                # First, click on the initial text field to open the input window
                initial_field = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//XCUIElementTypeTextField'))
                )
                initial_field.click()
                print("Clicked on initial text field")

                # Now, wait for and interact with the new input field
                input_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//XCUIElementTypeTextField[@name="onboarding_school_name"]'))
                )
                
                if input_field.is_displayed():
                    input_field.send_keys(school)
                    print(f"Entered school: {school}")
                    
                    # Click the Return button
                    return_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//XCUIElementTypeButton[@name="Return"]'))
                    )
                    return_button.click()
                    print("Clicked Return button")

                    # Click 'Done' or equivalent button to submit
                    submit_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, '//XCUIElementTypeButton[@name="button_onboarding_submit"]'))
                    )
                    submit_button.click()
                    print("Clicked submit button")
                    return "entered"
                else:
                    print("School input field not found")
                    return "failed"
            time.sleep(2)  # Wait for the next page to load
        else:
            print("School page not found, moving to next section")
            return "not_found"
    except Exception as e:
        print(f"Error handling school page: {str(e)}")
        return "failed"

def handle_habits(driver, habits_options):
    print("Starting habits setup")
    if habits_options['mode'] == 'skip':
        try:
            driver.find_element(By.XPATH, '//XCUIElementTypeButton[@name="Skip"]').click()
            print("Habits skipped")
        except Exception as e:
            print(f"Habits skip button not found: {str(e)}")
        return

    # Iterate through each sub-question in 'habits'
    for sub_question_key, sub_question_data in TINDER_PATHS['habits']['questions'].items():
        check_pause()
        print(f"Handling habits sub-question: {sub_question_key}")
        option_selected = False

        # Determine the option to select based on mode
        if habits_options['mode'] == 'choose':
            option = habits_options['selections'].get(sub_question_key, None)
            if option and option in sub_question_data['options']:
                xpath = sub_question_data['options'][option]
                print(f"Chosen option for '{sub_question_key}': {option}")
            else:
                option = random.choice(list(sub_question_data['options'].keys()))
                xpath = sub_question_data['options'][option]
                print(f"No valid selection for '{sub_question_key}'. Randomly selected '{option}'")
        elif habits_options['mode'] == 'random':
            option = random.choice(list(sub_question_data['options'].keys()))
            xpath = sub_question_data['options'][option]
            print(f"Randomly selected option for '{sub_question_key}': {option}")
        else:
            print(f"Unknown mode '{habits_options['mode']}' for habits. Skipping.")
            continue

        # Attempt to click the selected option
        clicked = click_element(driver, xpath, f"Habits Option '{option}' for '{sub_question_key}'")
        if not clicked:
            # Attempt to scroll and retry once
            try:
                driver.execute_script("mobile: scroll", {"direction": "down"})
                time.sleep(1)
                clicked = click_element(driver, xpath, f"Habits Option '{option}' for '{sub_question_key}' after scrolling")
            except:
                print(f"Scrolling failed for '{sub_question_key}'")

        if not clicked:
            print(f"Could not find option '{option}' for '{sub_question_key}'")
            break
    print("Habits setup completed")

def handle_what_makes_you_you(driver, what_makes_you_you_options):
    print("Starting 'What Makes You-You' setup")
    if what_makes_you_you_options['mode'] == 'skip':
        try:
            driver.find_element(By.XPATH, '//XCUIElementTypeButton[@name="Skip"]').click()
            print("'What Makes You-You' skipped")
        except Exception as e:
            print(f"'What Makes You-You' skip button not found: {str(e)}")
        return

    # Iterate through each sub-question in 'what_makes_you_you'
    for sub_question_key, sub_question_data in TINDER_PATHS['what_makes_you_you']['questions'].items():
        check_pause()
        print(f"Handling 'What Makes You-You' sub-question: {sub_question_key}")
        option_selected = False

        # Determine the option to select based on mode
        if what_makes_you_you_options['mode'] == 'choose':
            option = what_makes_you_you_options['selections'].get(sub_question_key, None)
            if option and option in sub_question_data['options']:
                xpath = sub_question_data['options'][option]
                print(f"Chosen option for '{sub_question_key}': {option}")
            else:
                option = random.choice(list(sub_question_data['options'].keys()))
                xpath = sub_question_data['options'][option]
                print(f"No valid selection for '{sub_question_key}'. Randomly selected '{option}'")
        elif what_makes_you_you_options['mode'] == 'random':
            option = random.choice(list(sub_question_data['options'].keys()))
            xpath = sub_question_data['options'][option]
            print(f"Randomly selected option for '{sub_question_key}': {option}")
        else:
            print(f"Unknown mode '{what_makes_you_you_options['mode']}' for 'What Makes You-You'. Skipping.")
            continue

        # Attempt to click the selected option
        clicked = click_element(driver, xpath, f"'What Makes You-You' Option '{option}' for '{sub_question_key}'")
        if not clicked:
            # Attempt to scroll and retry once
            try:
                driver.execute_script("mobile: scroll", {"direction": "down"})
                time.sleep(1)
                clicked = click_element(driver, xpath, f"'What Makes You-You' Option '{option}' for '{sub_question_key}' after scrolling")
            except:
                print(f"Scrolling failed for '{sub_question_key}'")

        if not clicked:
            print(f"Could not find option '{option}' for '{sub_question_key}'")
            break
    print("'What Makes You-You' setup completed")

def handle_hobbies(driver, hobbies_options):
    print("Starting hobbies setup")
    if hobbies_options['mode'] == 'skip':
        try:
            skip_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//XCUIElementTypeButton[@name="Skip"]'))
            )
            skip_button.click()
            print("Hobbies skipped")
            return  # Exit the function after skipping
        except Exception as e:
            print(f"Hobbies skip button not found: {str(e)}")
            return

    selected_hobbies = set()
    all_hobbies = list(TINDER_PATHS['hobbies']['questions']['interests']['options'].keys())

    if hobbies_options['mode'] == 'choose':
        selections = hobbies_options.get('selections', [])
        valid_selections = [hobby for hobby in selections if hobby in all_hobbies]

        if not valid_selections:
            print("No valid hobbies found in selections. Selecting random hobbies.")
            hobbies_options['mode'] = 'random'
            hobbies_options['count'] = 3  # Default count
        else:
            for hobby in valid_selections:
                scroll_attempts = 0
                max_scrolls = 10
                option_selected = False
                direction = 'down'

                while not option_selected and scroll_attempts < max_scrolls:
                    try:
                        driver.find_element(By.XPATH, TINDER_PATHS['hobbies']['questions']['interests']['options'][hobby]).click()
                        print(f"Selected hobby: {hobby}")
                        selected_hobbies.add(hobby)
                        option_selected = True
                    except Exception as e:
                        driver.execute_script("mobile: scroll", {"direction": direction})
                        time.sleep(0.5)
                        scroll_attempts += 1
                        direction = 'up' if direction == 'down' else 'down'

                if not option_selected:
                    print(f"Could not find hobby '{hobby}' after scrolling.")

    if hobbies_options['mode'] == 'random':
        count = min(max(hobbies_options.get('count', 3), 1), 5)  # Ensure count is between 1 and 5
        random.shuffle(all_hobbies)
        for hobby in all_hobbies:
            if len(selected_hobbies) >= count:
                break
            scroll_attempts = 0
            max_scrolls = 10
            option_selected = False
            direction = 'down'

            while not option_selected and scroll_attempts < max_scrolls:
                try:
                    driver.find_element(By.XPATH, TINDER_PATHS['hobbies']['questions']['interests']['options'][hobby]).click()
                    print(f"Randomly selected hobby: {hobby}")
                    selected_hobbies.add(hobby)
                    option_selected = True
                except Exception as e:
                    driver.execute_script("mobile: scroll", {"direction": direction})
                    time.sleep(0.5)
                    scroll_attempts += 1
                    direction = 'up' if direction == 'down' else 'down'

            if not option_selected:
                print(f"Could not find hobby '{hobby}' after scrolling.")
                break
    print("Hobbies setup completed")
  

def switchProxy(proxy, proxy_type):
    # Open the Shadowrocket app
    try:
        driver.activate_app("com.liguangming.Shadowrocket")
        time.sleep(2)  # Wait for app to open
    except Exception as e:
        print(f"Error opening Shadowrocket: {str(e)}")
        return False

    # Handle possible permission dialogs
    try:
        driver.find_element(By.XPATH, """//*[@name="Don't Allow"]""").click()
        time.sleep(2)
    except:
        pass
    try:
        driver.find_element(By.XPATH, """//*[@name="Don't allow"]""").click()
        time.sleep(2)
    except:
        pass

    # Attempt to delete old proxy
    if deleteOldProxy():
        print("Old proxy deleted successfully.")
    else:
        print("No old proxy found or deletion failed.")
        print("Adding new proxy...")
        addProxy(proxy, proxy_type)
        time.sleep(2)  # Wait for UI to update

        # Activate the newly added proxy
        activateNewProxy()

        return True
    # Add new proxy
    print("Adding new proxy...")
    addProxy(proxy, proxy_type)
    time.sleep(2)  # Wait for UI to update

    # Activate the newly added proxy
    activateNewProxy()

    return True


def deleteOldProxy():
    print("Attempting to delete old proxy")
    try:
        proxy_elements = driver.find_elements(by=AppiumBy.IOS_CLASS_CHAIN, value="**/XCUIElementTypeWindow/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[5]")

        if proxy_elements:
            # Click the Sort button
            sort_button = driver.find_element(By.XPATH, '(//XCUIElementTypeButton[@name="Sort"])[2]')
            sort_button.click()
            time.sleep(1)

            # Click the first proxy in the list (if it exists)
            el1 = driver.find_element(by=AppiumBy.IOS_CLASS_CHAIN, value="**/XCUIElementTypeWindow/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[5]")
            el1.click()
            time.sleep(1)
            print("Clicked the first proxy in the list")

            # Click the Delete button
            delete_button = driver.find_element(By.XPATH, '//XCUIElementTypeButton[@name="Delete"]')
            delete_button.click()
            time.sleep(1)

            # Confirm deletion
            driver.find_element(By.XPATH, '//XCUIElementTypeAlert[@name="Confirmation"]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[2]/XCUIElementTypeScrollView[2]/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther[3]').click()
            time.sleep(1)

            print("Old proxy deleted successfully")
    except Exception as e:
        print(f"No old proxy found or error deleting: {str(e)}")
        return False
    return True

def addProxy(proxy, proxy_type):
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@name="Add"]').click()
            break
        except:
            time.sleep(0.5)
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@name="Type"]').click()
            break
        except:
            time.sleep(0.5)
    # Select proxy type based on user input
    try:
        if proxy_type == 'http':
            driver.find_element(By.XPATH, '//*[@name="HTTP"]').click()
        elif proxy_type == 'socks5':
            driver.find_element(By.XPATH, '//*[@name="Socks5"]').click()
        else:
            print(f"Unsupported proxy type: {proxy_type}. Defaulting to HTTP.")
            driver.find_element(By.XPATH, '//*[@name="HTTP"]').click()
    except Exception as e:
        print(f"Error selecting proxy type: {str(e)}. Defaulting to HTTP.")
        driver.find_element(By.XPATH, '//*[@name="HTTP"]').click()
    time.sleep(1)  # Wait for the type to be selected

    address, port, username, password = proxy.split(":")
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@name="Address"]').send_keys(address)
            break
        except:
            time.sleep(0.5)
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@name="Port"]').send_keys(port)
            break
        except:
            time.sleep(0.5)
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@name="User"]').send_keys(username)
            break
        except:
            try:
                driver.find_element(By.XPATH, '//*[@name="Username"]').send_keys(username)
                print("Used 'Username' field instead of 'User'")
                break
            except:
                time.sleep(0.5)
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@name="Password"]').send_keys(password)
            break
        except:
            time.sleep(0.5)
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//XCUIElementTypeButton[@name="Save"]').click()
            print("New proxy added")
            return
        except:
            time.sleep(0.5)


def activateNewProxy():
    print("Attempting to activate new proxy")
    try:
        # Click the newly added proxy (first in the list)
        el1 = driver.find_element(by=AppiumBy.IOS_CLASS_CHAIN, value="**/XCUIElementTypeWindow/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther[1]/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeOther/XCUIElementTypeTable/XCUIElementTypeCell[5]")
        el1.click()
        time.sleep(1)
        print("New proxy activated successfully")
    except Exception as e:
        print(f"Error activating new proxy: {str(e)}")

def changeLocation(coords):
    try:
        coords=str(coords).split(",")
        print(str(coords))
    except:
        print("Coords format issue.")
    while True:
        check_pause()
        try:
            print(str(coords[0])+","+str(coords[1]))
            break
        except Exception as e:
            print("Coords issue: "+str(e))
            time.sleep(0.5)
    for i in range(2):
        try:
            driver.execute_script("mobile: pressButton", {"name": "home"})
            time.sleep(1.5)
        except:
            time.sleep(0.5)
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@name="NewTerm"]').click()
            time.sleep(2.5)
            break
        except:
            time.sleep(0.5)
            print("NewTerm not found")
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//XCUIElementTypeApplication[@name="NewTerm"]').send_keys('locsim start -x "'+str(coords[0])+'" -y "'+str(coords[1])+'"')
            time.sleep(2.5)
            break
        except:
            time.sleep(0.5)
            print("NewTerm Window not found?")
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@name="Return"]').click()
            time.sleep(1.5)
            print("Location set")
            return
        except:
            time.sleep(0.5)
            print("Run not found")

def reactivateSMS(orderid):
    url = "https://api.smspool.net/sms/resend"
    payload={'orderid' : orderid, 'key': 'yourkey'}
    files=[]
    headers = {}
    try:
        response = requests.request("POST", url, headers=headers, data=payload, files=files).json()
        print("SMS reactivated")
        return True
    except:
        time.sleep(1)
        print("Error reactivating number")

def smsHandler(orderid, provider):
    checker=0
    code=checkNumber(orderid, provider)
    if code != False:
        print("Code received")
    else:
        print("Code not received")
        while True:
            check_pause()
            try:
                time.sleep(1)
                driver.find_element(By.XPATH, '//*[@name="backButton"]').click()
                time.sleep(1)
                print("Back button clicked")
                return False
            except:
                print("Back button not found")
                time.sleep(0.5)
                return False
    while True:
        check_pause()
        try:
            if driver.find_element(By.XPATH, '//*[@label="Enter your code"]').is_enabled():
                print("Enter your code found")
                while True:
                    check_pause()
                    try:
                        print("Entering code")
                        driver.find_element(By.XPATH, '//*[@name="inputView"]').send_keys(str(code))
                        time.sleep(2)
                        print("Code: "+str(code) + " was entered")
                        break
                    except:
                        time.sleep(0.5)
                        print("Email field not found")
                while True:
                    check_pause()
                    try:
                        driver.find_element(By.XPATH, '//*[@name="continueButton"]').click()
                        time.sleep(1)
                        break
                    except:
                        time.sleep(0.5)
                        print("continueButton not found")
        except:
            print("Enter your code not found")
            time.sleep(0.5)
        try:
            if driver.find_element(By.XPATH, '//*[@label="My email code"]').is_enabled():
                time.sleep(1)
                for i in range(2):
                    driver.find_element(By.XPATH, '//*[@name="backButton"]').click()
                    time.sleep(2)
                    print("Back button clicked")
                return False
        except:
            print("My email code not found")
            time.sleep(0.5)
            checker+=1
            if checker > 9:
                return False
            try:
                if driver.find_element(By.XPATH, '//XCUIElementTypeTextField').is_enabled():
                    print("Email field found")
                    return True
            except:
                print("TextField for email not found")
                time.sleep(0.5)

def deleteUsedPhotos(album, number_of_pictures):
    for i in range(2):
        try:
            driver.execute_script("mobile: pressButton", {"name": "home"})
            time.sleep(1.5)
        except:
            time.sleep(0.5)
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@label="Photos"]').click()
            break
        except:
            driver.activate_app("com.apple.Photos")
            print("Issue opening Photos")
            time.sleep(0.5)
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@label="Albums"]').click()
            break
        except:
            print("Issue opening Photos")
            time.sleep(0.5)
    scrollDown=0
    while True:
        check_pause()
        if scrollDown > 5:
            try:
                action=TouchAction(driver)
                action.long_press(None, 180, 270).move_to(None, 170, 131).release().perform()
                scrollDown=0
            except:
                print("Scroll issue")
        try:
            driver.find_element(By.XPATH, '//XCUIElementTypeButton[@name="See All"]').click()
            time.sleep(1)
        except:
            time.sleep(0.5)
        try:
            driver.find_element(By.XPATH, '//*[@label="'+str(album)+'"]').click()
            time.sleep(2)
            break
        except:
            time.sleep(0.5)
            scrollDown+=1
    for i in range(number_of_pictures):
        time.sleep(1.5)
        while True:
            check_pause()
            try:
                driver.find_element(By.XPATH, '//XCUIElementTypeStaticText[@name="Select"]').click()
                print("Clicked select on: "+str(i+1))
                time.sleep(2)
                break
            except:
                time.sleep(0.5)
        while True:
            check_pause()
            try:
                driver.find_element(By.XPATH, '(//XCUIElementTypeImage)[1]').click()  # Select the first image
                print("First image selected")
                break
            except:
                time.sleep(1.5)
        time.sleep(1)
        while True:
            check_pause()
            try:
                driver.find_element(By.XPATH, '//XCUIElementTypeButton[@name="Delete"]').click()
                break
            except:
                time.sleep(1)
        time.sleep(1)
        while True:
            check_pause()
            try:
                driver.find_element(By.XPATH, '(//XCUIElementTypeButton[@name="Delete"])[2]').click()
                break
            except:
                time.sleep(1)
        time.sleep(1)
        while True:
            check_pause()
            try:
                driver.find_element(By.XPATH, '//XCUIElementTypeButton[@name="Delete Photo"]').click()
                break
            except:
                time.sleep(1)
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@label="Albums"]').click()
            print("Clicked back")
            break
        except:
            print("Failed to click back")
    while True:
        check_pause()
        try:
            driver.terminate_app("com.apple.Photos")
            time.sleep(2)
            print("Terminated photos")
            return
        except:
            print("Failed to terminate app!")
            time.sleep(0.5)
        return

def deleteContainer(name):
    """
    Deletes a container with the given name.

    Args:
        name (str): The name of the container to be deleted.
    """
    print("Running Delete!")
    try:
        driver.terminate_app('com.cardify.tinder')
    except:
        pass
    while True:
        check_pause()
        try:
            driver.execute_script("mobile: pressButton", {"name": "home"})
            time.sleep(1.5)
            bumble=driver.find_element(By.XPATH, '//*[@label="Tinder"]')
            action = TouchAction(driver)
            action.long_press(bumble).release().perform()
            driver.refresh
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[contains(@label,"Container")]').click()
            time.sleep(2)
            driver.find_element(By.XPATH, '(//*[@name="Settings"])[2]').click()
            break
        except Exception as e:
            print(str(e))
    while True:
        check_pause()
        try:
            driver.find_element(By.XPATH, '//*[@label="Delete Containers"]').click()
        except:
            time.sleep(0.25)
        try:
            driver.find_element(By.XPATH, '//*[@name="Edit"]').click()
        except:
            time.sleep(0.3)
        try:
            driver.find_element(By.XPATH, '//*[@name="Delete '+str(name)+'"]').click()
        except:
            time.sleep(0.3)
        try:
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@name="Delete"]').click()
            time.sleep(0.5)
            break
        except:
            time.sleep(0.3)
    time.sleep(1)
    try:
        driver.find_element(By.XPATH, '//*[@name="Delete"]').click()
        time.sleep(0.5)
    except:
        time.sleep(0.3)
    try:
        driver.find_element(By.XPATH, '//*[@label="Done"]').click()
        time.sleep(0.5)
    except:
        time.sleep(0.3)
    print("Container deleted..")
    return

def buyNumber(provider):
    if provider == "smspool":
        url = "https://api.smspool.net/purchase/sms"
        payload = {'key': SMSPOOL_API_KEY, 'service': 'Tinder', 'country': 'GB'}
        files = []
        headers = {}
        while True:
            check_pause()
            try:
                response = requests.request("POST", url, headers=headers, data=payload, files=files).json()
                orderid = response['order_id']
                number = response['phonenumber']
                return orderid + ":" + number
            except:
                time.sleep(1)
                print("Error buying number")
    elif provider == "daisy":
        try:
            buy_sms = f"https://daisysms.com/stubs/handler_api.php?api_key={DAISY_API_KEY}&action=getNumber&service=oi&max_price=1.50"
            response = requests.get(buy_sms).text.split(":")
            order_id = response[1]
            phone_number = response[2]
            return str(order_id) + ":" + str(phone_number)
        except:
            print("Issue buying number, probably out of credit or stock.")
            return None

def checkNumber(orderid, provider):
    if provider == "smspool":
        url = "https://api.smspool.net/sms/check"
        payload = {'key': SMSPOOL_API_KEY, 'orderid': orderid}
        files = []
        headers = {}
        for i in range(33):
            check_pause()
            try:
                response = requests.request("POST", url, headers=headers, data=payload, files=files).json()
                if response['sms'] != "":
                    print("SMS: " + str(response['sms']))
                    return response['sms']
                else:
                    time.sleep(1)
            except:
                time.sleep(1)
                print("Error checking number")
        else:
            return False
    elif provider == "daisy":
        for i in range(30):
            check_pause()
            try:
                buy_sms = f"https://daisysms.com/stubs/handler_api.php?api_key={DAISY_API_KEY}&action=getStatus&id={orderid}"
                response = requests.get(buy_sms).text
                print(response)
                if response.__contains__("STATUS_OK"):
                    code = response.split(":")[1]
                    print(code)
                    return code
                else:
                    print("No message yet")
                    time.sleep(0.5)
            except:
                print("No message yet")
                time.sleep(0.5)
        else:
            return False

def crane(apilink):
    print("Crane")
    try:
        driver.terminate_app('com.cardify.tinder')
        print("Terminated Tinder")
    except:
        pass
    try:
        driver.terminate_app('com.apple.Photos')
    except:
        pass
    while True:
        check_pause()
        for i in range(2):
            try:
                driver.execute_script("mobile: pressButton", {"name": "home"})
                time.sleep(1.5)
            except Exception as e:
                time.sleep(0.5)
                print("Home button error: " + str(e))
        try:
            instagram=driver.find_element(By.XPATH, '//*[@label="Tinder"]')
            action = TouchAction(driver)
            action.long_press(instagram).release().perform()
            driver.refresh
            print("Long pressed on Tinder")
            time.sleep(1)
            driver.find_element(By.XPATH, '//*[contains(@label,"Container")]').click()
            time.sleep(1)
            break
        except Exception as e:
            print("1: "+str(e))
    while True:
        check_pause()
        try:
            add=driver.find_element(By.XPATH, '//*[@label="New Container"]')
            if add.is_enabled():
                add.click()
                break
        except Exception as e:
            try:
                action = TouchAction(driver)
                action.long_press(None, 170, 556).move_to(None, 170, 120).release().perform()
            except:
                time.sleep(0.5)
                print("scroll Issue")
    digits=randrange(10000, 9999999999)
    print("digit: "+str(digits))
    while True:
        check_pause()
        try:
            inputBox = driver.find_element(By.XPATH, '//*[@value="Name"]')
            addbot=driver.find_element(By.XPATH, '//*[@label="Create"]')
            if inputBox.is_enabled():
                inputBox.send_keys(str(digits))
                print("Digits entered")
                if inputBox.text == str(digits):
                    addbot.click()
                    print("Container created")
                    break
                else:
                    addbot.clear()
        except Exception as e:
            driver.refresh
            print(str(e))
            time.sleep(2)
    while True:
        check_pause()
        try:
            driver.activate_app("com.cardify.tinder")
            time.sleep(2)
            print("Tinder activated")
            break
        except:
            print("Issue opening Tinder")
            time.sleep(0.5)
    return digits

use_attempts = activate_killswitch

def createAccount(email, albumName, name, provider, coords, city, proxy, use_attempts, killswitch_max_attempts, killswitch_timeout, number_of_pictures, profile_options, use_school, school):
    check_pause()
    profile_options = profile_options or {}
    profile_options.setdefault('habits', {'mode': 'skip'})
    profile_options.setdefault('hobbies', {'mode': 'skip', 'count': 0})
    profile_options.setdefault('what_makes_you_you', {'mode': 'skip'})

    if use_attempts:
        start_time = time.time()
        timeout = killswitch_timeout
        timeout_attempts = 0
    else:
        start_time = None
        timeout = None
        timeout_attempts = None
    try:
        print(f"Starting account creation process. Timeout set to {timeout} seconds." if use_attempts else "Starting account creation process without timeout.")

        log_message(f"Starting account creation for {email}. Timeout: {timeout}")

        # Step 1: Click create account button
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if use_attempts and timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="create_account_button"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("create_account_button not found")

        # Step 2: Handle phone number input and SMS verification
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            numberOrder = buyNumber(provider)
            number = str(numberOrder).split(":")[1]
            orderid = str(numberOrder).split(":")[0]
            try:
                time.sleep(2)
                driver.find_element(By.XPATH, '//XCUIElementTypeTextField').clear()
                time.sleep(2)
            except:
                print("TextField not found")
            try:
                driver.find_element(By.XPATH, '//XCUIElementTypeTextField').send_keys(number)
                time.sleep(2)
                driver.find_element(By.XPATH, '//*[@name="continue_button"]').click()
                time.sleep(2)
            except:
                time.sleep(0.5)
                print("Number field not found")
            print("Checking for code")
            trySMS = smsHandler(orderid, provider)
            print("Handler: " + str(trySMS))
            if trySMS == True:
                break
            elif trySMS == False:
                print("Number dead")
                return "Bad"

        # Step 3: Enter email
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//XCUIElementTypeTextField').send_keys(email)
                time.sleep(2)
                break
            except:
                time.sleep(0.5)
                print("Email field not found")

        # Step 4: Click Next
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="Next"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("Next not found")

        # Step 5: Click Skip
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="SKIP"]').click()
                time.sleep(3)
                break
            except:
                time.sleep(0.5)
                print("SKIP not found")

        # Step 6: Click button_onboarding_submit
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("button_onboarding_submit not found")

        # Step 7: Enter First Name
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//XCUIElementTypeTextField').send_keys(name)
                time.sleep(2)
                break
            except:
                time.sleep(0.5)
                print("First Name field not found")

        # Step 8: Click Return
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="Return"]').click()
                time.sleep(3)
                break
            except:
                time.sleep(0.5)
                print("Return not found")

        # Step 9: Click Let's go
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//XCUIElementTypeButton[@name="Let\'s go"]').click()
                print("Clicked lets go")
                time.sleep(2)
                break
            except:
                time.sleep(0.5)
                print("Let's go not found")

        # Step 10: Enter Date of Birth
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                randomMonth = random.randint(1, 12)
                if randomMonth < 10:
                    randomMonth = "0" + str(randomMonth)
                randomDay = random.randint(1, 28)
                if randomDay < 10:
                    randomDay = "0" + str(randomDay)
                randomDOB = f"{randomMonth}{randomDay}{dob_year}"
                print("DOB: " + str(randomDOB))
                driver.find_element(By.XPATH, '(//XCUIElementTypeTextField)[1]').send_keys(str(randomDOB))
                time.sleep(4)
                year = driver.find_element(By.XPATH, '(//XCUIElementTypeTextField)[5]').text
                if str(year) == "Y":
                    print("Year not set")
                    driver.find_element(By.XPATH, '(//XCUIElementTypeTextField)[5]').send_keys(dob_year)
                    time.sleep(2)
                    print("Year set")
                break
            except:
                time.sleep(0.5)
                print("DOB field not found")

        # Step 11: Click Done and Submit
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="Done"]').click()
                time.sleep(1)
            except:
                print("Done not found")
            try:
                driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                print("Clicked submit")
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("button_onboarding_submit not found")

        # Step 12: Select Woman
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="Woman"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)

        # Step 13: Click button_onboarding_submit
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("button_onboarding_submit not found")

        # Step 14: Click Skip
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="Skip"]').click()
                time.sleep(3)
                break
            except:
                time.sleep(0.5)
                print("Skip not found")

        # Step 15: Select Men
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="Men"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)

        # Step 16: Click button_onboarding_submit twice
        for _ in range(2):
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            while True:
                try:
                    driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                    time.sleep(1)
                    break
                except:
                    time.sleep(0.5)
                    print("button_onboarding_submit not found")

        # Step 17: Select "Still figuring it out"
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="Still figuring it out"]').click()
                time.sleep(1)
                break
            except:
                try:
                    if driver.find_element(By.XPATH, '//*[@name="Skip"]').is_enabled():
                        break
                except:
                    pass
                time.sleep(0.5)

        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                time.sleep(3)
                break
            except:
                try:
                    if driver.find_element(By.XPATH, '//*[@name="Skip"]').is_enabled():
                        break
                except:
                    pass
                time.sleep(0.5)
                print("button_onboarding_submit not found")

        # Step 18: Handle School Page
        school_page_result = handle_school_page(driver, use_school, school)
        if school_page_result == "failed":
            print("Failed to handle school page correctly")
            return False
        elif school_page_result == "not_found":
            print("School page not found, continuing with account creation")
        else:
            print(f"School page handled: {school_page_result}")

        # Step 19: Handle Habits
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred during habits setup. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts and timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached during habits setup.")
                    return "Max attempts reached"
            try:
                if 'habits' in profile_options:
                    handle_habits(driver, profile_options['habits'])
                    time.sleep(1)
                    driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                else:
                    time.sleep(4)
                    handle_habits(driver, {'mode': 'skip'})
                break  # Exit the loop after successful execution
            except Exception as e:
                print(f"Error during habits setup: {str(e)}")
                time.sleep(0.5)

        # Step 20: Handle What Makes You-You
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred during 'What Makes You-You' setup. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts and timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached during 'What Makes You-You' setup.")
                    return "Max attempts reached"
            try:
                if 'what_makes_you_you' in profile_options:
                    handle_what_makes_you_you(driver, profile_options['what_makes_you_you'])
                    time.sleep(1)
                    driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                else:
                    time.sleep(4)
                    handle_what_makes_you_you(driver, {'mode': 'skip'})
                break  # Exit the loop after successful execution
            except Exception as e:
                print(f"Error during 'What Makes You-You' setup: {str(e)}")
                time.sleep(0.5)

        # Step 21: Handle Hobbies
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred during hobbies setup. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts and timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached during hobbies setup.")
                    return "Max attempts reached"
            try:
                if 'hobbies' in profile_options:
                    handle_hobbies(driver, profile_options['hobbies'])
                    time.sleep(1)
                    driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                else:
                    time.sleep(4)
                    handle_hobbies(driver, {'mode': 'skip'})
                break  # Exit the loop after successful execution
            except Exception as e:
                print(f"Error during hobbies setup: {str(e)}")
                time.sleep(0.5)


        # Step 22: Click on Photo Cell
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//XCUIElementTypeCell').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("Photo CELL not found")

        # Step 23: Allow Access to Photos and Select Gallery
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="Allow Access to All Photos"]').click()
                time.sleep(1)
            except:
                time.sleep(0.5)
                print("Allow Access to All Photos not found")
            try:
                driver.find_element(By.XPATH, '//*[@name="Gallery"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("Gallery not found")

        # Step 24: Select Album
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@label="' + str(albumName) + '"]').click()
                time.sleep(3)
                break
            except:
                time.sleep(0.5)
                print("albumName not found")

        # Step 25: Select Media
        for i in range(number_of_pictures):
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '(//*[@name="Select Media"])[' + str(i + 1) + ']').click()
                time.sleep(1)
            except:
                time.sleep(0.5)
                print("Select Media not found")

        # Step 26: Click Done
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="Done"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("Done not found")

        # Step 27: Click button_onboarding_submit
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                time.sleep(2)
                break
            except:
                time.sleep(0.5)
                print("button_onboarding_submit not found")

        # Step 28: Handle various pop-ups and buttons
        closeClicked = False
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '(//*[@name="OK"])[1]').click()
                print("OK clicked 1")
                time.sleep(1)
            except:
                time.sleep(0.3)
                print("close not found")
            try:
                driver.find_element(By.XPATH, '(//*[@name="OK"])[2]').click()
                print("OK clicked 2")
                time.sleep(1)
            except:
                time.sleep(0.3)
                print("close not found")
            try:
                driver.find_element(By.XPATH, '//*[@name="secondary_button_push_view"]').click()
                print("secondary_button_push_view clicked")
                time.sleep(1)
                break
            except:
                time.sleep(1)
                print("secondary_button_push_view not found")
                try:
                    driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                    print("button_onboarding_submit clicked")
                    time.sleep(1)
                    print("button_onboarding_submit clicked")
                except:
                    time.sleep(0.5)
                    print("button_onboarding_submit not found check 2")
                try:
                    driver.find_element(By.XPATH, '//*[@name="close_button"]').click()
                    print("close clicked")
                    closeClicked = True
                    time.sleep(1)
                except:
                    time.sleep(0.5)
                    print("close not found")
                try:
                    driver.find_element(By.XPATH, '//*[@name="close"]').click()
                    print("close clicked")
                    closeClicked = True
                    time.sleep(1)
                except:
                    time.sleep(0.5)
                    print("close not found")

        if closeClicked == False:
            while True:
                check_pause()
                if use_attempts and (time.time() - start_time > timeout):
                    return "Timeout"
                try:
                    driver.find_element(By.XPATH, '//*[@name="button_onboarding_submit"]').click()
                    time.sleep(3)
                    break
                except:
                    time.sleep(0.5)
                    print("button_onboarding_submit not found")
            while True:
                check_pause()
                if use_attempts and (time.time() - start_time > timeout):
                    return "Timeout"
                try:
                    actions = TouchAction(driver)
                    actions.tap(None, 33, 81, 1).perform()
                    print("Clicked")
                    time.sleep(1)
                    break
                except:
                    time.sleep(0.5)
                    print("Coordinates not found")

        alrSkip = False
        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@label="Skip"]').click()
                alrSkip = True
                time.sleep(3)
                break
            except:
                time.sleep(0.5)
                print("SKIP not found")
            try:
                driver.find_element(By.XPATH, '//*[@name="I Accept"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("I Accept not found")
            try:
                driver.find_element(By.XPATH, '//*[@name="I accept"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("I accept not found")
            try:
                driver.find_element(By.XPATH, '//*[@label="I ACCEPT"]').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.5)
                print("I ACCEPT not found")
            try:
                driver.find_element(By.XPATH, '//*[@name="close"]').click()
                print("close clicked")
                closeClicked = True
                time.sleep(1)
            except:
                time.sleep(0.5)
                print("close not found")

        time.sleep(1.5)
        if alrSkip == False:
            while True:
                check_pause()
                if use_attempts and (time.time() - start_time > timeout):
                    return "Timeout"
                try:
                    driver.find_element(By.XPATH, '//*[@label="Skip"]').click()
                    time.sleep(3)
                    break
                except:
                    time.sleep(0.5)
                    print("SKIP not found")
        time.sleep(5)

        # Handle Dismiss button
        for attempt in range(3):
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                dismiss_button = driver.find_element(By.XPATH, '//*[@label="Dismiss"]')
                if dismiss_button.is_displayed():
                    dismiss_button.click()
                    print(f"Dismiss clicked on attempt {attempt + 1}")
                    time.sleep(1.5)
                    break
            except:
                print(f"Dismiss button not found on attempt {attempt + 1}")
                time.sleep(1)

        # Handle TCF consent if it appears, checking up to 3 times
        for attempt in range(3):
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                tcf_accept_button = driver.find_element(By.XPATH, '//XCUIElementTypeButton[@name="I Accept"]')
                if tcf_accept_button.is_displayed():
                    tcf_accept_button.click()
                    print(f"TCF 'I Accept' button clicked on attempt {attempt + 1}")
                    time.sleep(1)
                    break
            except:
                print(f"TCF consent dialog not detected on attempt {attempt + 1}")
                time.sleep(1)

        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.activate_app("com.apple.mobilenotes")
                time.sleep(2)
                break
            except:
                print("Issue opening Notes")

        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                driver.find_element(By.XPATH, '//*[@name="New note"]').click()
                print("New note clicked")
            except:
                time.sleep(0.5)
            try:
                driver.find_element(By.XPATH, '//*[@name="New Note"]').click()
                print("New Note clicked")
            except:
                time.sleep(0.5)
            try:
                driver.find_element(By.XPATH, '//*[@name="Note"]').click()
                print("Note clicked")
                time.sleep(1.5)
                driver.find_element(By.XPATH, '//*[@name="Paste"]').click()
                time.sleep(2)
                print("Paste clicked")
                break
            except:
                time.sleep(0.5)

        while True:
            check_pause()
            if use_attempts and (time.time() - start_time > timeout):
                timeout_attempts += 1
                print(f"Timeout occurred. Attempt {timeout_attempts} of {killswitch_max_attempts}")
                return "Timeout"
            else:
                if timeout_attempts >= killswitch_max_attempts:
                    print("Max timeout attempts reached.")
                    return "Max attempts reached"
            try:
                getTokens = str(driver.find_element(By.XPATH, '//*[@name="Note"]').get_dom_attribute("value"))
                driver.find_element(By.XPATH, '//*[@name="Note"]').clear()
            except:
                print("Issue getting tokens")
            try:
                driver.terminate_app("com.apple.mobilenotes")
            except:
                time.sleep(0.5)
            try:
                getTokens = getTokens + "," + str(coords) + "," + str(city) + "," + str(name) + "," + str(email) + "," + str(proxy)
                print("Tokens: " + str(getTokens))
                with open('tokens.txt', 'a') as f:
                    f.write(getTokens)
                    f.write("\n")
                    print("Tokens saved")
                    f.close()
                    break
            except Exception as e:
                print("Tokens not found:" + str(e))

        print("Account creation process completed.")
        return True
    
    finally:
        if use_attempts:
            elapsed_time = time.time() - start_time
            print(f"Account creation process took {elapsed_time:.2f} seconds.")

# Rest of the code remains the same, including check_pause() calls where necessary

# Initialize driver and start the main process
desired_caps = {
    "xcodeOrgId": "9VG3A52D8L",
    "xcodeSigningId": "iPhone Developer",
    "platformName": "iOS",
    "automationName": "XCUITest",
    "udid": sys.argv[1],
    "deviceName": "iPhone",
    "bundleId": "com.cardify.tinder",
    "updatedWDABundleID": "NumbLegacy.TinderLegacyNumb.WebDriverAgentRunner",
    "showXcodeLog": True,
    "newCommandTimeout": "1000",
    "useNewWDA": True,
    "noReset": True
}
while True:
    try:
        driver = webdriver.Remote("http://localhost:1111/wd/hub", desired_caps)
        print("Started")
        break
    except:
        print("Driver not executed; try restarting the Appium Server and make sure your device's JB is still running.")
        time.sleep(0.5)
emails=sys.argv[2].split(",")
proxies=sys.argv[3].split(",")
albumName=sys.argv[4]
names=sys.argv[5].split(",")
provider=sys.argv[6]

min_length = min(len(names), len(proxies))
timeout_attempts = 0
for i in range(min_length):
    email = emails[i]
    print(f"Name: {names[i]}")
    print(f"Proxy: {proxies[i]}")
    proxy = proxies[i]
    school = schools[i] if i < len(schools) else None

    while True:
        check_pause()
        switchProxy(proxies[i], proxy_type)
        proxy_ip, proxy_port, proxy_user, proxy_pass = proxy.split(':')
        if proxy_type == 'http':
            pproxies = {
                "http": f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}",
                "https": f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
            }
        elif proxy_type == 'socks5':
            pproxies = {
                "http": f"socks5://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}",
                "https": f"socks5://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}"
            }
        else:
            pproxies = None 

        response = requests.get("https://ipinfo.io/json", proxies=pproxies)
        data = json.loads(response.text)
        coords = str(data['loc'])
        city = str(data['region'])
        changeLocation(coords)
        resetContainer = crane("apilink")


        creation = createAccount(email, albumName, names[i], provider, coords, city, proxy,
                                 use_attempts=activate_killswitch,
                                 killswitch_max_attempts=killswitch_max_attempts,
                                 killswitch_timeout=killswitch_timeout,
                                 number_of_pictures=number_of_pictures,
                                 profile_options=profile_options,
                                 use_school=use_school,
                                 school=school)
        if creation == True:
            print("Account successfully created.")
            deleteUsedPhotos(albumName, number_of_pictures)
            if not save_containers:
                deleteContainer(resetContainer)
            break
        elif creation == False:
            print("Account creation failed, deleting container.")
            deleteContainer(resetContainer)
            deleteUsedPhotos(albumName, number_of_pictures)
            break
        elif creation == "Bad":
            print("Number bad, let's delete container.")
            deleteContainer(resetContainer)
            break
        elif creation == "Timeout":
            print(f"Killswitch triggered: Account creation timed out.")
            deleteContainer(resetContainer)
            timeout_attempts += 1
            if timeout_attempts >= killswitch_max_attempts:
                print(f"Max timeout attempts ({killswitch_max_attempts}) reached. Stopping further processing.")
                sys.exit(1)
            else:
                print(f"Retrying account creation. Attempt {timeout_attempts + 1} of {killswitch_max_attempts}")
                continue
        elif creation == "Max attempts reached":
            print(f"Max attempts ({killswitch_max_attempts}) reached. Stopping further processing.")
            sys.exit(1)
