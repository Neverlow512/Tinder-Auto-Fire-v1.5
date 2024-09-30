import subprocess

commands = [
    "brew install node",
    "npm install -g appium",
    "npm install wd",
    "brew install carthage",
    "npm i -g webpack",
    "brew install libimobiledevice",
    "npm install -g authorize-ios",
    "brew install ios-deploy",
    "sudo xcode-select -r",
    "brew install ideviceinstaller",
    "appium driver install xcuitest@4.32.10",
    "pip3 install Appium-Python-Client==2.7.1",
    "pip3 install requests",
    "pip3 install selenium==4.7.2",
    "pip3 install random-password-generator"
    "pip3 install licensing"
    "pip3 pyinstaller"
    "pip3 pyarmor"
    "pip3 install pysocks"
]

for command in commands:
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

    if output:
        print(f"Output: {output.decode()}")
    if error:
        print(f"Error: {error.decode()}")