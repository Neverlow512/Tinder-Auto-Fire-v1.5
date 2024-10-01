import subprocess
import flask
import json
import os
import threading
import logging
import time
import sys
import signal
import webbrowser
from flask import Flask, request, render_template, url_for, jsonify, abort
import uuid
import hashlib
from datetime import datetime, timedelta
from functools import wraps
from srn import get_serial_number

# This is where you'll insert the serial number, expiration date, and authorized UDID before compiling for each user
AUTHORIZED_SERIAL = "C02TVAZFHX87"  # Replace with the actual authorized serial number
EXPIRATION_DATE = "2024-10-21"  # Format: "YYYY-MM-DD"
AUTHORIZED_UDID = "00008030-001235042107802E"

app = Flask(__name__, template_folder=os.path.dirname(os.path.abspath(__file__)))
app.secret_key = b'secretkey23hr397fh3tf234r5hx0'
directory = os.path.dirname(os.path.realpath(__file__))

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='tinder_app.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Disable Flask's default logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

appium_process = None
tinder_process = None  # Global variable to store the tinder.py process

def check_serial():
    device_serial = get_serial_number()
    return device_serial == AUTHORIZED_SERIAL

def check_expiration():
    expiration_date = datetime.strptime(EXPIRATION_DATE, "%Y-%m-%d")
    return datetime.now() <= expiration_date

def check_authorization():
    if not check_serial():
        return False, "This software is not authorized for use on this machine."
    if not check_expiration():
        return False, "This software license has expired."
    return True, ""

# Decorator for authorization check
def require_authorization(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        is_authorized, message = check_authorization()
        if not is_authorized:
            return message, 403
        return f(*args, **kwargs)
    return decorated_function

def start_appium_server():
    global appium_process
    appium_process = subprocess.Popen(['appium', '-a', 'localhost', '-p', '1111', '--base-path', '/wd/hub'])
    print("Appium server started")

def stop_appium_server():
    global appium_process
    if appium_process:
        appium_process.terminate()
        appium_process.wait()
        print("Appium server stopped")

class NewThreadedTask(threading.Thread):
    def __init__(self):
        super(NewThreadedTask, self).__init__()

def get_connected_devices():
    try:
        devicelist = subprocess.check_output(['ios-deploy', '-c'])
        devicelist = str(devicelist).replace('b"', '')
        devicelist = devicelist.split("[....]")
        for line in devicelist:
            if ' Found' in line:
                device_id = line.split('Found')[1].split(" ")[1]
                if device_id == AUTHORIZED_UDID:
                    return [device_id]
        return []
    except Exception as e:
        logging.error(f"Error getting connected devices: {e}")
        return []

def get_status():
    if AUTHORIZED_UDID in get_connected_devices():
        return [{'device': AUTHORIZED_UDID, 'status': 'ready', 'pid': 0}]
    return []

def get_config_path():
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))

    config_path = os.path.join(application_path, 'config.json')

    if os.access(os.path.dirname(config_path), os.W_OK):
        logging.debug(f"Using application directory for config: {config_path}")
        return config_path
    else:
        home_dir = os.path.expanduser("~")
        config_path = os.path.join(home_dir, '.tinder_auto_fire_config.json')
        logging.debug(f"Using home directory for config: {config_path}")
        return config_path

@app.route('/')
@require_authorization
def home():
    return render_template('tinder.html', content=gen())

@app.route('/gen')
@require_authorization
def gen():
    status = get_status()
    header = """
    <div class="container">
        <div class="title-container">
            <h1>Tinder Auto-Fire v1.3</h1>
            <div class="subtitle">by Traffic Heaven</div>
        </div>
    """

    form = f"""
    <style>
    .form-row {{
        display: flex;
        align-items: flex-start;
        margin-bottom: 10px;
    }}
    .api-key-container {{
        display: flex;
        flex-direction: column;
    }}
    .save-api-key-button {{
        margin-top: 20px;
    }}
    .save-containers-container, .killswitch-container, .pictures-dropdown-container {{
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }}
    .save-containers-container {{
        margin-left: 40px;
    }}
    .killswitch-container {{
        margin-left: 1cm;
    }}
    .pictures-dropdown-container {{
        margin-left: 2cm;
    }}
    #savecontainers, #activate_killswitch {{
        width: 20px;
        height: 20px;
    }}
    .killswitch-label {{
        font-weight: bold;
        margin-bottom: 5px;
        color: #ff4500;
    }}
    .killswitch-timeout, .killswitch-max-attempts {{
        margin-top: 10px;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }}
    .killswitch-timeout label, .killswitch-max-attempts label {{
        font-size: 0.9em;
        color: #ff4500;
        margin-bottom: 5px;
    }}
    .custom-number-input {{
        position: relative;
        display: flex;
        width: 80px;
        height: 25px;
    }}

    .custom-number-input input[type=number] {{
        width: 100%;
        height: 100%;
        background-color: black;
        color: #ff4500;
        border: 2px solid #ff4500;
        padding: 0 25px 0 5px;
        font-size: 0.9em;
        text-align: left;
    }}

    .number-input-buttons {{
        position: absolute;
        right: 2px;
        top: 2px;
        bottom: 2px;
        width: 21px;
        display: flex;
        flex-direction: column;
    }}

    .number-input-button {{
        height: 50%;
        background-color: black;
        color: #ff4500;
        border: none;
        border-left: 1px solid #ff4500;
        font-size: 10px;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        user-select: none;
    }}

    .number-input-button:first-child {{
        border-bottom: 1px solid #ff4500;
    }}

    .number-input-button:hover {{
        background-color: #ff4500;
        color: black;
    }}

    .killswitch-options {{
        display: none;
    }}
    #number_of_pictures option {{
        background-color: black;
        color: #ff4500;
    }}
    .control-button {{
        margin-left: 10px;
        margin-top: 10px;
        padding: 10px 20px;
        background-color: #ff4500;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 1em;
    }}
    .control-button:hover {{
        background-color: #e03e00;
    }}
    .button-container {{
        margin-top: 20px;
    }}
    input[type=number]::-webkit-inner-spin-button, 
    input[type=number]::-webkit-outer-spin-button {{ 
        -webkit-appearance: none; 
        margin: 0; 
    }}
    input[type=number] {{
        -moz-appearance: textfield;
    }}
    .categories-container {{
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
    }}
    .category {{
        margin-bottom: 15px;
    }}
    .category label {{
        font-weight: bold;
    }}
    .category-options {{
        margin-top: 10px;
        margin-left: 20px;
    }}
    .category-options.hidden {{
        display: none;
    }}
    .hobby-count {{
        margin-top: 10px;
    }}

    /* New CSS Rules Start Here */
    
    /* Style for the container holding the dropdowns to arrange them horizontally */
    .category-options > div {{
        /* Adds space below each category and arranges dropdowns horizontally */
        margin-bottom: 15px;
        display: flex;
        flex-direction: row;
        flex-wrap: wrap;
        gap: 20px; /* Adjust spacing as needed */
    }}

    /* Style for the individual question containers */
    .category-options > div > div {{
        display: flex;
        flex-direction: column;
        min-width: 200px; /* Adjust width as needed */
    }}

    /* Style for the select (dropdown) elements */
    .category-options select {{
        padding: 8px 12px;
        border: 2px solid #ff4500;
        border-radius: 4px;
        background-color: black;
        color: #ff4500;
        font-size: 0.9em;
        appearance: none; /* Removes default arrow for consistent styling */
        /* Adds a custom arrow with #ff4500 color */
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="5"><polygon points="0,0 10,0 5,5" style="fill:%23ff4500;"/></svg>');
        background-repeat: no-repeat;
        background-position: right 10px center;
        background-size: 10px 5px;
        cursor: pointer;
    }}

    /* Style for labels associated with dropdowns */
    .category-options label {{
        margin-bottom: 5px;
        font-weight: bold;
        color: #ff4500;
    }}

    /* Style for the selected option text */
    .category-options select option {{
        color: #ff4500;
        background-color: black;
    }}

    /* Responsive adjustments */
    @media (max-width: 768px) {{
        .categories-container .category-options > div {{
            flex-direction: column;
            gap: 10px; /* Reduce gap on smaller screens */
        }}
        .category-options select {{
            width: 100%; /* Make dropdowns full width on smaller screens */
        }}
    }}
    .proxy-type-container {{
        display: flex;
        flex-direction: column;
        margin-left: 2cm; /* Adjust based on alignment with "Killswitch" */
    }}

    .proxy-type-container label {{
        font-weight: bold;
        margin-bottom: 5px;
        color: #ff4500;
    }}

    .proxy-type-container select {{
        padding: 12px 12px;
        border: 2px solid #ff4500;
        border-radius: 4px;
        background-color: black;
        color: #ff4500;
        font-size: 0.9em;
        appearance: none;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="10" height="5"><polygon points="0,0 10,0 5,5" style="fill:%23ff4500;"/></svg>');
        background-repeat: no-repeat;
        background-position: right 10px center;
        background-size: 10px 5px;
        cursor: pointer;
        width: 100%; /* Ensures the dropdown matches the width of the Number of Pictures field */
    }}

    </style>

    <div class="categories-container">
        <!-- Habits -->
        <div class="category">
            <label for="habits_mode">Habits:</label>
            <select id="habits_mode" name="habits_mode" onchange="onCategoryModeChange('habits'); saveValue(this);">
                <option value="skip">Skip</option>
                <option value="random">Random</option>
                <option value="choose">Choose</option>
            </select>
            <div id="habits_options" class="category-options hidden">
                <!-- Habits options will be dynamically inserted here -->
            </div>
        </div>
        <!-- What Makes You-You -->
        <div class="category">
            <label for="what_makes_you_you_mode">What Makes You-You:</label>
            <select id="what_makes_you_you_mode" name="what_makes_you_you_mode" onchange="onCategoryModeChange('what_makes_you_you'); saveValue(this);">
                <option value="skip">Skip</option>
                <option value="random">Random</option>
                <option value="choose">Choose</option>
            </select>
            <div id="what_makes_you_you_options" class="category-options hidden">
                <!-- Options will be dynamically inserted here -->
            </div>
        </div>
        <!-- Hobbies -->
        <div class="category">
            <label for="hobbies_mode">Hobbies:</label>
            <select id="hobbies_mode" name="hobbies_mode" onchange="onCategoryModeChange('hobbies'); saveValue(this);">
                <option value="skip">Skip</option>
                <option value="random">Random</option>
                <option value="choose">Choose</option>
            </select>
            <div id="hobbies_options" class="category-options hidden">
                <!-- Options will be dynamically inserted here -->
            </div>
        </div>
    </div>
    <br>Date of Birth (YYYY):<br>
    <input type="text" id="dob" name="dob" size="4" maxlength="4" onkeyup='saveValue(this);'>
    <br>SMS Provider:<br>
    <select name='provider' id='provider' onchange='updateApiKeyField(); saveValue(this);'>
        <option name='smspool' id='smspool' value='smspool'>SMS Pool</option>
        <option name='daisy' id='daisy' value='daisy'>Daisy SMS</option>
    </select>
    <div class="form-row">
        <div class="api-key-container">
            <label for="api_key">API Key:</label>
            <input type="text" id="api_key" name="api_key" required>
            <input type="button" value="Save API Key" onclick="saveApiKey()" class="save-api-key-button">
        </div>
        <div class="save-containers-container">
            <label for="savecontainers">Save Containers:</label>
            <input type="checkbox" id="savecontainers" name="savecontainers" onchange='saveValue(this);'>
        </div>
        <div class="killswitch-container">
            <label for="activate_killswitch" class="killswitch-label">Killswitch:</label>
            <input type="checkbox" id="activate_killswitch" name="activate_killswitch" onchange='saveValue(this); toggleKillswitchOptions();'>
            <div id="killswitch-options" class="killswitch-options">
                <div class="killswitch-timeout">
                    <label for="killswitch_timeout">Minutes per account:</label>
                    <div class="custom-number-input">
                        <input type="number" id="killswitch_timeout" name="killswitch_timeout" min="1" value="30" onchange='saveValue(this);'>
                        <div class="number-input-buttons">
                            <button type="button" class="number-input-button" onclick="changeNumber('killswitch_timeout', 1, event)">▲</button>
                            <button type="button" class="number-input-button" onclick="changeNumber('killswitch_timeout', -1, event)">▼</button>
                        </div>
                    </div>
                </div>
                <div class="killswitch-max-attempts">
                    <label for="killswitch_max_attempts">Max attempts:</label>
                    <div class="custom-number-input">
                        <input type="number" id="killswitch_max_attempts" name="killswitch_max_attempts" min="1" value="3" onchange='saveValue(this);'>
                        <div class="number-input-buttons">
                            <button type="button" class="number-input-button" onclick="changeNumber('killswitch_max_attempts', 1, event)">▲</button>
                            <button type="button" class="number-input-button" onclick="changeNumber('killswitch_max_attempts', -1, event)">▼</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="pictures-dropdown-container">
            <label for="number_of_pictures">Number of Pictures:</label>
            <div class="custom-number-input">
                <input type="number" id="number_of_pictures" name="number_of_pictures" min="3" max="5" value="3" onchange='saveValue(this);'>
                <div class="number-input-buttons">
                    <button type="button" class="number-input-button" onclick="changeNumber('number_of_pictures', 1, event)">▲</button>
                    <button type="button" class="number-input-button" onclick="changeNumber('number_of_pictures', -1, event)">▼</button>
                </div>
            </div>
        </div>
        <div class="proxy-type-container">
            <label for="proxy_type">Proxy Type:</label>
            <select id="proxy_type" name="proxy_type" onchange='saveValue(this);'>
                <option value="http">HTTP</option>
                <option value="socks5">SOCKS5</option>
            </select>
        </div>
    </div>
    <div class="lower-fields">
        <br>Emails:<br>
        <textarea id='emails' name='emails' rows='10' cols='20' onkeyup='saveValue(this);'></textarea>
        <br>Names:<br>
        <textarea id='names' name='names' rows='20' cols='20' onkeyup='saveValue(this);'></textarea>
        <br>Proxies IP:PORT:USER:PASS<br>
        <textarea id='proxies' name='proxies' rows='20' cols='20' onkeyup='saveValue(this);'></textarea>
        <br>Album name:<br>
        <textarea id='album' name='album' rows='5' cols='25' onkeyup='saveValue(this);'></textarea>
        <br>
        <div class="button-container">
            <input type='button' value='Start' class='control-button' onclick='startProcess()'>
            <input type='button' value='Pause' class='control-button' onclick='pauseProcess()'>
            <input type='button' value='Unpause' class='control-button' onclick='unpauseProcess()'>
            <input type='button' value='Stop' class='control-button' onclick='stopProcess()'>
        </div>
    </div>
    """

    saveOptions = f"""
    <script>
    // Define questions and options for Habits and What Makes You-You
    const habitsQuestions = {{
        'drink_frequency': {{
            'question': 'How often do you drink?',
            'options': [
                'Not for me',
                'Sober',
                'Sober curious',
                'On special occasions',
                'Socially on weekends',
                'Most Nights'
            ]
        }},
        'smoke_frequency': {{
            'question': 'How often do you smoke?',
            'options': [
                'Social smoker',
                'Smoker when drinking',
                'Non-smoker',
                'Smoker',
                'Trying to quit'
            ]
        }},
        'workout_frequency': {{
            'question': 'Do you workout?',
            'options': [
                'Everyday',
                'Often',
                'Sometimes',
                'Never'
            ]
        }},
        'pets': {{
            'question': 'Do you have any pets?',
            'options': [
                'Dog',
                'Cat',
                'Reptile',
                'Amphibian',
                'Bird',
                'Fish',
                "Don't have but love",
                'Other',
                'Turtle',
                'Hamster',
                'Rabbit',
                'Pet-free',
                'All the pets',
                'Want a pet',
                'Allergic to pets'
            ]
        }}
    }};

    const whatMakesYouYouQuestions = {{
        'communication_style': {{
            'question': 'What is your communication style?',
            'options': [
                'Big time texter',
                'Phone caller',
                'Video chatter',
                'Bad texter',
                'Better in person'
            ]
        }},
        'receive_love': {{
            'question': 'How do you receive love?',
            'options': [
                'Thoughtful gestures',
                'Presents',
                'Touch',
                'Compliments',
                'Time together'
            ]
        }},
        'education_level': {{
            'question': 'What is your education level?',
            'options': [
                'Bachelors',
                'In College',
                'High School',
                'PhD',
                'In Grad School',
                'Masters',
                'Trade School'
            ]
        }},
        'zodiac_sign': {{
            'question': 'What is your zodiac sign?',
            'options': [
                'Capricorn',
                'Aquarius',
                'Pisces',
                'Aries',
                'Taurus',
                'Gemini',
                'Cancer',
                'Leo',
                'Virgo',
                'Libra',
                'Scorpio',
                'Sagittarius'
            ]
        }}
    }};

    const hobbiesList = [
        'Harry Potter',
        '90s Kid',
        'SoundCloud',
        'Spa',
        'Self Care',
        'Heavy Metal',
        'House Parties',
        'Gin tonic',
        'Gymnastics',
        'Hot Yoga',
        'Meditation',
        'Spotify',
        'Sushi',
        'Hockey',
        'Basketball',
        'Slam Poetry',
        'Home Workout',
        'Theater',
        'Cafe hopping',
        'Aquarium',
        'Sneakers',
        'Instagram',
        'Hot Springs',
        'Walking',
        'Running',
        'Travel',
        'Language Exchange',
        'Movies',
        'Guitarists',
        'Social Development',
        'Gym',
        'Social Media',
        'Hip Hop',
        'Skincare',
        'K-Pop',
        'Potterhead',
        'Trying New Things',
        'Photography',
        'Bollywood',
        'Reading',
        'Singing',
        'Sports',
        'Poetry'
    ];

    function saveValue(e){{
        var id = e.id;
        var val = e.type === 'checkbox' ? e.checked : e.value;
        localStorage.setItem(id, val);
    }}

    function getSavedValue(v){{
        if (!localStorage.getItem(v)) {{
            return "";
        }}
        return localStorage.getItem(v);
    }}

    function loadValues() {{
        document.getElementById("dob").value = getSavedValue("dob");
        document.getElementById("emails").value = getSavedValue("emails");
        document.getElementById("names").value = getSavedValue("names");
        document.getElementById("proxies").value = getSavedValue("proxies");
        document.getElementById("album").value = getSavedValue("album");
        document.getElementById("provider").value = getSavedValue("provider");
        document.getElementById("savecontainers").checked = getSavedValue("savecontainers") === 'true';
        document.getElementById("activate_killswitch").checked = getSavedValue("activate_killswitch") === 'true';
        document.getElementById("killswitch_timeout").value = getSavedValue("killswitch_timeout") || "30";
        document.getElementById("killswitch_max_attempts").value = getSavedValue("killswitch_max_attempts") || "3";
        document.getElementById("number_of_pictures").value = getSavedValue("number_of_pictures") || "3";
        document.getElementById("habits_mode").value = getSavedValue("habits_mode") || "skip";
        document.getElementById("what_makes_you_you_mode").value = getSavedValue("what_makes_you_you_mode") || "skip";
        document.getElementById("hobbies_mode").value = getSavedValue("hobbies_mode") || "skip";
        toggleKillswitchOptions();
        updateApiKeyField();
        onCategoryModeChange('habits');
        onCategoryModeChange('what_makes_you_you');
        onCategoryModeChange('hobbies');
    }}

    function updateApiKeyField() {{
        const provider = document.getElementById('provider').value;
        const apiKeyField = document.getElementById('api_key');

        fetch('/get_api_key?provider=' + provider)
            .then(response => response.json())
            .then(data => {{
                apiKeyField.value = data.api_key || '';
            }});
    }}

    function saveApiKey() {{
        const provider = document.getElementById('provider').value;
        const apiKey = document.getElementById('api_key').value;

        fetch('/save_api_key', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/x-www-form-urlencoded',
            }},
            body: 'provider=' + encodeURIComponent(provider) + '&api_key=' + encodeURIComponent(apiKey)
        }})
        .then(response => response.json())
        .then(data => {{
            alert(data.message);
        }});
    }}

    function toggleKillswitchOptions() {{
        var killswitchCheckbox = document.getElementById('activate_killswitch');
        var killswitchOptions = document.getElementById('killswitch-options');
        if (killswitchCheckbox.checked) {{
            killswitchOptions.style.display = 'block';
        }} else {{
            killswitchOptions.style.display = 'none';
        }}
    }}

    function changeNumber(id, change, event) {{
        if (event) {{
            event.preventDefault();  // Always prevent the default action
        }}
        var input = document.getElementById(id);
        var newValue = parseInt(input.value) + change;
        var min = parseInt(input.min) || 1;  // Default to 1 if min is not set
        var max = parseInt(input.max) || 999;  // Default to a high number if max is not set
        if (newValue >= min && newValue <= max) {{
            input.value = newValue;
            saveValue(input);
        }}
    }}

    function startProcess() {{
        var formData = new FormData();
        formData.append('device', '{AUTHORIZED_UDID}');
        formData.append('provider', document.getElementById('provider').value);
        formData.append('dob', document.getElementById('dob').value);
        formData.append('emails', document.getElementById('emails').value);
        formData.append('names', document.getElementById('names').value);
        formData.append('proxies', document.getElementById('proxies').value);
        formData.append('album', document.getElementById('album').value);
        formData.append('savecontainers', document.getElementById('savecontainers').checked);
        formData.append('activate_killswitch', document.getElementById('activate_killswitch').checked);
        formData.append('killswitch_timeout', document.getElementById('killswitch_timeout').value);
        formData.append('killswitch_max_attempts', document.getElementById('killswitch_max_attempts').value);
        formData.append('number_of_pictures', document.getElementById('number_of_pictures').value);
        formData.append('proxy_type', document.getElementById('proxy_type').value);
        // Collect profile options
        var profile_options = {{}};

        // Habits
        var habits_mode = document.getElementById('habits_mode').value;
        profile_options['habits'] = {{
            'mode': habits_mode
        }};
        if (habits_mode === 'choose') {{
            var selections = {{}};
            for (var key in habitsQuestions) {{
                var radios = document.getElementsByName('habits_' + key);
                for (var i = 0; i < radios.length; i++) {{
                    if (radios[i].checked) {{
                        selections[key] = radios[i].value;
                        break;
                    }}
                }}
            }}
            profile_options['habits']['selections'] = selections;
        }}

        // What Makes You-You
        var what_makes_you_you_mode = document.getElementById('what_makes_you_you_mode').value;
        profile_options['what_makes_you_you'] = {{
            'mode': what_makes_you_you_mode
        }};
        if (what_makes_you_you_mode === 'choose') {{
            var selections = {{}};
            for (var key in whatMakesYouYouQuestions) {{
                var radios = document.getElementsByName('what_makes_you_you_' + key);
                for (var i = 0; i < radios.length; i++) {{
                    if (radios[i].checked) {{
                        selections[key] = radios[i].value;
                        break;
                    }}
                }}
            }}
            profile_options['what_makes_you_you']['selections'] = selections;
        }}

        // Hobbies
        var hobbies_mode = document.getElementById('hobbies_mode').value;
        profile_options['hobbies'] = {{
            'mode': hobbies_mode
        }};
        if (hobbies_mode === 'choose') {{
            var selections = [];
            var checkboxes = document.getElementsByName('hobbies_selection');
            for (var i = 0; i < checkboxes.length; i++) {{
                if (checkboxes[i].checked) {{
                    selections.push(checkboxes[i].value);
                }}
            }}
            profile_options['hobbies']['selections'] = selections;
        }} else if (hobbies_mode === 'random') {{
            var count = document.getElementById('hobbies_random_count').value;
            profile_options['hobbies']['count'] = parseInt(count);
        }}

        formData.append('profile_options', JSON.stringify(profile_options));

        fetch('/start', {{
            method: 'POST',
            body: formData
        }})
        .then(response => response.json())
        .then(data => {{
            console.log(data);
            alert(data.message);
        }})
        .catch(error => {{
            console.error('Error:', error);
            alert('An error occurred while starting the process.');
        }});
    }}

    function stopProcess() {{
        var formData = new FormData();
        formData.append('device', '{AUTHORIZED_UDID}');
        formData.append('stop', 'Stop');

        fetch('/start', {{
            method: 'POST',
            body: formData
        }})
        .then(response => response.json())
        .then(data => {{
            alert(data.message);
        }})
        .catch(error => {{
            console.error('Error:', error);
            alert('Process has been stopped successfully.');
        }});
    }}

    function pauseProcess() {{
        fetch('/pause', {{
            method: 'POST'
        }})
        .then(response => response.json())
        .then(data => {{
            alert(data.message);
        }})
        .catch(error => {{
            console.error('Error:', error);
            alert('An error occurred while pausing the process.');
        }});
    }}

    function unpauseProcess() {{
        fetch('/unpause', {{
            method: 'POST'
        }})
        .then(response => response.json())
        .then(data => {{
            alert(data.message);
        }})
        .catch(error => {{
            console.error('Error:', error);
            alert('An error occurred while unpausing the process.');
        }});
    }}

    function onCategoryModeChange(category) {{
        var mode = document.getElementById(category + '_mode').value;
        var optionsDiv = document.getElementById(category + '_options');
        optionsDiv.innerHTML = ''; // Clear existing options

        if (mode === 'choose') {{
            optionsDiv.classList.remove('hidden');
            if (category === 'habits') {{
                generateHabitsOptions();
            }} else if (category === 'what_makes_you_you') {{
                generateWhatMakesYouYouOptions();
            }} else if (category === 'hobbies') {{
                generateHobbiesOptions();
            }}
        }} else if (mode === 'random') {{
            optionsDiv.classList.remove('hidden');
            if (category === 'hobbies') {{
                var label = document.createElement('label');
                label.innerText = 'Number of hobbies to select randomly:';
                label.style.display = 'block';
                label.style.marginBottom = '5px';

                var inputContainer = document.createElement('div');
                inputContainer.className = 'custom-number-input';
                inputContainer.style.display = 'flex';
                inputContainer.style.alignItems = 'center';

                var input = document.createElement('input');
                input.type = 'number';
                input.id = 'hobbies_random_count';
                input.name = 'hobbies_random_count';
                input.min = '1';
                input.max = '5';
                input.value = getSavedValue('hobbies_random_count') || '3';
                input.onchange = function() {{ saveValue(this); }};
                input.style.width = '40px';
                input.style.textAlign = 'center';
                input.style.marginRight = '5px';

                var buttonsContainer = document.createElement('div');
                buttonsContainer.style.display = 'flex';
                buttonsContainer.style.flexDirection = 'column';

                var upButton = document.createElement('button');
                upButton.type = 'button';
                upButton.innerText = '▲';
                upButton.onclick = function(event) {{ event.preventDefault(); changeNumber('hobbies_random_count', 1); }};
                upButton.style.width = '20px';
                upButton.style.height = '15px';
                upButton.style.padding = '0';
                upButton.style.lineHeight = '15px';

                var downButton = document.createElement('button');
                downButton.type = 'button';
                downButton.innerText = '▼';
                downButton.onclick = function(event) {{ event.preventDefault(); changeNumber('hobbies_random_count', -1); }};
                downButton.style.width = '20px';
                downButton.style.height = '15px';
                downButton.style.padding = '0';
                downButton.style.lineHeight = '15px';

                buttonsContainer.appendChild(upButton);
                buttonsContainer.appendChild(downButton);

                inputContainer.appendChild(input);
                inputContainer.appendChild(buttonsContainer);

                optionsDiv.appendChild(label);
                optionsDiv.appendChild(inputContainer);
            }}
        }} else {{
            optionsDiv.classList.add('hidden');
        }}
    }}

    function generateHabitsOptions() {{
        var optionsDiv = document.getElementById('habits_options');
        optionsDiv.innerHTML = '';
        
        // Create a container for horizontal layout
        var container = document.createElement('div');
        container.style.display = 'flex';
        container.style.flexDirection = 'row';
        container.style.flexWrap = 'wrap';
        container.style.gap = '20px';  // Adjust spacing as needed
        
        for (var key in habitsQuestions) {{
            var qDiv = document.createElement('div');
            qDiv.style.display = 'flex';
            qDiv.style.flexDirection = 'column';
            qDiv.style.minWidth = '200px';  // Adjust width as needed
            
            var qLabel = document.createElement('label');
            qLabel.innerText = habitsQuestions[key].question;
            qLabel.setAttribute('for', 'habits_' + key);
            qDiv.appendChild(qLabel);
            
            var select = document.createElement('select');
            select.name = 'habits_' + key;
            select.id = 'habits_' + key;
            select.onchange = function() {{ saveValue(this); }};
            
            // Add a default option
            var defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.text = 'Select an option';
            select.appendChild(defaultOption);
            
            var options = habitsQuestions[key].options;
            for (var i = 0; i < options.length; i++) {{
                var option = document.createElement('option');
                option.value = options[i];
                option.text = options[i];
                select.appendChild(option);
            }}
            
            // Set saved value if exists
            var savedValue = getSavedValue('habits_' + key);
            if (savedValue) {{
                select.value = savedValue;
            }}
            
            qDiv.appendChild(select);
            container.appendChild(qDiv);
        }}
        
        optionsDiv.appendChild(container);
    }}


    function generateWhatMakesYouYouOptions() {{
        var optionsDiv = document.getElementById('what_makes_you_you_options');
        optionsDiv.innerHTML = '';
        
        // Create a container for horizontal layout
        var container = document.createElement('div');
        container.style.display = 'flex';
        container.style.flexDirection = 'row';
        container.style.flexWrap = 'wrap';
        container.style.gap = '20px';  // Adjust spacing as needed
        
        for (var key in whatMakesYouYouQuestions) {{
            var qDiv = document.createElement('div');
            qDiv.style.display = 'flex';
            qDiv.style.flexDirection = 'column';
            qDiv.style.minWidth = '200px';  // Adjust width as needed
            
            var qLabel = document.createElement('label');
            qLabel.innerText = whatMakesYouYouQuestions[key].question;
            qLabel.setAttribute('for', 'what_makes_you_you_' + key);
            qDiv.appendChild(qLabel);
            
            var select = document.createElement('select');
            select.name = 'what_makes_you_you_' + key;
            select.id = 'what_makes_you_you_' + key;
            select.onchange = function() {{ saveValue(this); }};
            
            // Add a default option
            var defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.text = 'Select an option';
            select.appendChild(defaultOption);
            
            var options = whatMakesYouYouQuestions[key].options;
            for (var i = 0; i < options.length; i++) {{
                var option = document.createElement('option');
                option.value = options[i];
                option.text = options[i];
                select.appendChild(option);
            }}
            
            // Set saved value if exists
            var savedValue = getSavedValue('what_makes_you_you_' + key);
            if (savedValue) {{
                select.value = savedValue;
            }}
            
            qDiv.appendChild(select);
            container.appendChild(qDiv);
        }}
        
        optionsDiv.appendChild(container);
    }}


    function generateHobbiesOptions() {{
        var optionsDiv = document.getElementById('hobbies_options');
        optionsDiv.innerHTML = '';
        var selections = getSavedValue('hobbies_selections').split(',');
        var countSelected = 0;
        for (var i = 0; i < hobbiesList.length; i++) {{
            var hobby = hobbiesList[i];
            var checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.name = 'hobbies_selection';
            checkbox.value = hobby;
            checkbox.id = 'hobby_' + i;
            if (selections.includes(hobby)) {{
                checkbox.checked = true;
                countSelected++;
            }}
            checkbox.onchange = function() {{
                saveHobbiesSelection();
                limitHobbiesSelection();
            }};
            var label = document.createElement('label');
            label.htmlFor = 'hobby_' + i;
            label.innerText = hobby;
            optionsDiv.appendChild(checkbox);
            optionsDiv.appendChild(label);
            optionsDiv.appendChild(document.createElement('br'));
        }}
        limitHobbiesSelection();
    }}

    function saveHobbiesSelection() {{
        var selections = [];
        var checkboxes = document.getElementsByName('hobbies_selection');
        for (var i = 0; i < checkboxes.length; i++) {{
            if (checkboxes[i].checked) {{
                selections.push(checkboxes[i].value);
            }}
        }}
        localStorage.setItem('hobbies_selections', selections.join(','));
    }}

    function limitHobbiesSelection() {{
        var checkboxes = document.getElementsByName('hobbies_selection');
        var maxAllowed = 5;
        var selected = [];
        for (var i = 0; i < checkboxes.length; i++) {{
            if (checkboxes[i].checked) {{
                selected.push(checkboxes[i]);
            }}
        }}
        if (selected.length > maxAllowed) {{
            var lastSelected = selected[selected.length - 1];
            lastSelected.checked = false;
            alert('You can select a maximum of ' + maxAllowed + ' hobbies.');
        }}
    }}

    // Initialize the page on load
    document.addEventListener('DOMContentLoaded', function() {{
        loadValues();
        toggleKillswitchOptions();
    }});
    document.addEventListener('DOMContentLoaded', function() {{
        var form = document.getElementById('mainForm');
        if (form) {{
            form.onsubmit = function(event) {{
                event.preventDefault();
                return false;
            }};
        }}
    }});
    </script>
    """

    table = "<table><tr><th>Device</th><th>Status</th></tr>"
    if status:
        table += f"<tr><td>{status[0]['device']}</td><td>{status[0]['status']}</td></tr>"
    else:
        table += "<tr><td colspan='2'>Authorized device not connected</td></tr>"
    table += "</table>"

    content = f"""
    {header}
    {table}
    <form id="mainForm">
        {form}
    </form>
    {saveOptions}
    </div>
    """

    return content


@app.route('/save_api_key', methods=['POST'])
@require_authorization
def save_api_key():
    api_key = request.form['api_key']
    provider = request.form['provider']

    logging.debug(f"Attempting to save API key for provider: {provider}")

    config_path = get_config_path()
    logging.debug(f"Config path: {config_path}")

    # Load existing config or create new one
    if os.path.exists(config_path):
        logging.debug("Config file exists, loading it")
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
    else:
        logging.debug("Config file does not exist, creating new config")
        config = {}

    # Update the config with the new API key
    if provider == 'smspool':
        config['smspool_api_key'] = api_key
    elif provider == 'daisy':
        config['daisy_api_key'] = api_key

    logging.debug(f"Updated config: {config}")

    # Save the updated config back to the file
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(config_path), exist_ok=True)

        with open(config_path, 'w') as config_file:
            json.dump(config, config_file, indent=4)
        logging.debug("Config file saved successfully")
    except Exception as e:
        logging.error(f"Error saving config file: {str(e)}")
        return jsonify({"message": f"Error saving API Key: {str(e)}"}), 500

    return jsonify({"message": f"API Key for {provider} saved successfully!"})

@app.route('/get_api_key')
@require_authorization
def get_api_key():
    provider = request.args.get('provider')
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            if provider == 'smspool':
                api_key = config.get('smspool_api_key', '')
            elif provider == 'daisy':
                api_key = config.get('daisy_api_key', '')
            else:
                api_key = ''
    else:
        api_key = ""

    return jsonify({"api_key": api_key})

@app.route('/check_config')
@require_authorization
def check_config():
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        return jsonify(config)
    else:
        return jsonify({"message": "Config file does not exist"}), 404

@app.route('/pause', methods=['POST'])
@require_authorization
def pause():
    global tinder_process
    if tinder_process and tinder_process.poll() is None:
        try:
            tinder_process.send_signal(signal.SIGUSR1)
            logging.info("Pause signal sent.")
            return jsonify({"message": "Process paused successfully."})
        except Exception as e:
            logging.error(f"Error pausing the process: {str(e)}")
            return jsonify({"message": f"Error pausing the process: {str(e)}"}), 500
    else:
        return jsonify({"message": "Process is not running."}), 400

@app.route('/unpause', methods=['POST'])
@require_authorization
def unpause():
    global tinder_process
    if tinder_process and tinder_process.poll() is None:
        try:
            tinder_process.send_signal(signal.SIGUSR2)
            logging.info("Unpause signal sent.")
            return jsonify({"message": "Process unpaused successfully."})
        except Exception as e:
            logging.error(f"Error unpausing the process: {str(e)}")
            return jsonify({"message": f"Error unpausing the process: {str(e)}"}), 500
    else:
        return jsonify({"message": "Process is not running."}), 400

@app.route('/start', methods=['POST'])
@require_authorization
def cmd():
    global tinder_process
    status = get_status()
    stop = request.form.get('stop')
    device = request.form.get('device')

    logging.debug(f"Received start request for device: {device}")

    if device != AUTHORIZED_UDID:
        logging.warning(f"Unauthorized device attempt: {device}")
        return jsonify({"message": "Unauthorized device"}), 403

    if not status:
        logging.warning("Authorized device not connected")
        return jsonify({"message": "Authorized device not connected"}), 400

    if stop:
        if tinder_process and tinder_process.poll() is None:
            tinder_process.terminate()
            tinder_process.wait()
            tinder_process = None
            logging.info(f"Stopped task on {device}")
            return jsonify({"message": f"Stopped task on {device}"})
        else:
            logging.warning("No running task found for this device")
            return jsonify({"message": "No running task found for this device"}), 400

    # Collect form data
    dob = request.form.get('dob')
    emails = request.form.get('emails')
    names = request.form.get('names')
    album = request.form.get('album')
    proxies = request.form.get('proxies')
    provider = str(request.form.get('provider'))
    savecontainers = 'true' if request.form.get('savecontainers') == 'true' else 'false'
    activate_killswitch = 'true' if request.form.get('activate_killswitch') == 'true' else 'false'
    killswitch_timeout = request.form.get('killswitch_timeout', '30')
    killswitch_max_attempts = request.form.get('killswitch_max_attempts', '3')
    number_of_pictures = request.form.get('number_of_pictures', '3')
    
    # Collect proxy_type from form data
    proxy_type = request.form.get('proxy_type', 'http').lower()
    if proxy_type not in ['http', 'socks5']:
        logging.warning(f"Invalid proxy type received: {proxy_type}. Defaulting to 'http'.")
        proxy_type = 'http'

    # Get profile_options from form data
    profile_options_json = request.form.get('profile_options')
    try:
        profile_options = json.loads(profile_options_json)
        logging.debug(f"Received profile options: {profile_options}")
    except json.JSONDecodeError:
        logging.error("Invalid profile options JSON")
        profile_options = {}
        profile_options_json = json.dumps(profile_options)  # Ensure profile_options_json is valid JSON

    # Get API key from config
    config_path = get_config_path()
    if os.path.exists(config_path):
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
            api_key = config.get(f"{provider}_api_key", "")
    else:
        api_key = ""

    logging.debug(f"API key retrieved for provider: {provider}")

    try:
        emails = emails.replace("\r\n", ",").replace("\n", ",").strip(",")
        names = names.replace("\r\n", ",").replace("\n", ",").strip(",")
        proxies = proxies.replace("\r\n", ",").replace("\n", ",").strip(",")
        logging.debug(f"Processed inputs - Names: {names}, Emails: {emails}, Proxies: {proxies}")
    except Exception as e:
        logging.error(f"Variable processing error: {str(e)}")
        return jsonify({"message": f"Error processing input: {str(e)}"}), 400

    for x in status:
        logging.debug(f"Checking status: {x}")
        if x["device"] == device and x["status"] == 'ready':
            time.sleep(2)  # Add a 2-second delay before starting tinder.py

            # Determine the path to tinder.py
            if getattr(sys, 'frozen', False):
                tinder_path = os.path.join(sys._MEIPASS, 'tinder.py')
            else:
                tinder_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tinder.py')

            logging.debug(f"Tinder.py path: {tinder_path}")

            try:
                command = [
                    'python3', tinder_path, device, emails, proxies, album,
                    names, provider, api_key, dob, savecontainers, activate_killswitch,
                    killswitch_timeout, killswitch_max_attempts, number_of_pictures,
                    profile_options_json,
                    proxy_type  # Pass the JSON string as is
                ]
                logging.debug(f"Executing command: {' '.join(command)}")

                p = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid  # Necessary for signal handling
                )

                # Store the process globally
                tinder_process = p

                # Wait for a short time to check if the process started successfully
                time.sleep(5)
                if p.poll() is None:
                    # Process is still running, assume it started successfully
                    pid = p.pid
                    x["pid"] = pid
                    x["status"] = "Creating accounts"
                    logging.info(f"Started task on {device} with PID {pid}")

                    # Start a thread to monitor the process output
                    def monitor_output():
                        for line in p.stdout:
                            logging.info(f"Tinder.py output: {line.strip()}")
                        for line in p.stderr:
                            logging.error(f"Tinder.py error: {line.strip()}")

                    threading.Thread(target=monitor_output, daemon=True).start()

                    return jsonify({"message": f"Started task on {device}", "pid": pid})
                else:
                    # Process ended quickly, check for errors
                    stdout, stderr = p.communicate()
                    error_message = stderr if stderr else "Unknown error occurred"
                    logging.error(f"Process failed to start: {error_message}")
                    return jsonify({"message": f"Error starting task: {error_message}"}), 500

            except Exception as e:
                logging.error(f"Error starting subprocess: {str(e)}")
                return jsonify({"message": f"Error starting task: {str(e)}"}), 500

    logging.warning("No matching device found or device not ready")
    return jsonify({"message": "No matching device found or device not ready"}), 400

# No additional routes or functions are defined after this point.

if __name__ == '__main__':
    is_authorized, message = check_authorization()
    if not is_authorized:
        print(message)
        sys.exit(1)

    # Set up logging
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='tinder_autofire.log',
                        filemode='w')

    # Also log to console
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    start_appium_server()
    webbrowser.open('http://127.0.0.1:1200')
    app.run(threaded=True, host='127.0.0.1', port=1200)
