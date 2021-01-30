# telegram-delete-all-messages
Delete all your messages in groups and supergroups with python script.

## Installation
To use this script you have to download the project and install it's
requirements. It's recommended to use a virtual environment, such as
`venv` or `conda`. This example shows how to setup your project
using `conda`:

### Linux
```
# Create a new Python 3.8 environment
conda create -n telegram-cleaner python=3.8
conda activate telegram-cleaner

# Get a local project copy
git clone https://github.com/define-user/telegram-delete-all-messages
cd telegram-delete-all-messages

# Install dependencies
pip install -r requirements.txt
```

In order to let the script work, you'll have to register your own
Telegram application. To do so you need to get special credentials.
Here are some simply steps to follow:

## Obtain standalone telegram app API credentials
- Login to the official telegram [website](https://my.telegram.org/)
- Select `API development tools` link
- Create standalone application
- Copy app_id and app_hash

## Usage
> You need both App api_id and App api_hash to use script.

#### Start
To start the script simply execute:
```
python telegram-message-cleaner.py
```

The script will prompt you to enter such credentials:
- Your application credentials (required to register your app).
- Your phone number and a code sent you by Telegram (required to
sign in your account).
