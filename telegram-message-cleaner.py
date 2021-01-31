import configparser
import os
from time import sleep
from dataclasses import dataclass
from typing import List

from pyrogram import Client
from pyrogram.types import Dialog, Chat, User, Message


@dataclass(frozen=True)
class ApplicationCredentials:
    api_id: int
    api_hash: str


def get_application_credentials() -> ApplicationCredentials:
    """
    This function retrieves application credentials. It looks for them in such order:
      - From a config file, path to which is stored under `$TELEGRAM_APPLICATION_CREDENTIALS` environment variable.
      - From a config file, located in current directory.
      - From both `$TGAPP_ID` and `$TGAPP_HASH` environment variables.
      - From direct user input.
    """

    path_to_config = os.getenv(key="TELEGRAM_APPLICATION_CREDENTIALS", default=None)

    if not path_to_config:
        path_to_config = os.path.join(os.path.dirname(__file__), "config.ini")
        path_to_config = path_to_config if os.path.exists(path=path_to_config) else None

    if path_to_config:
        config = configparser.ConfigParser()
        config.read(filenames=path_to_config)

        return ApplicationCredentials(api_id=int(config["pyrogram"]["api_id"]), api_hash=config["pyrogram"]["api_hash"])

    api_id, api_hash = os.getenv(key="TGAPP_ID", default=None), os.getenv(key="TGAPP_HASH", default=None)

    if not api_id or not api_hash:
        api_id, api_hash = int(input("Enter your api_id: ")), input("Enter your api_hash: ")

    return ApplicationCredentials(api_id=api_id, api_hash=api_hash)


def select_dialog(dialogs: List[Dialog]) -> Dialog:
    """
    This function displays all dialogues to user, then lets them select a specific one,
    in order to keep working on it.
    """

    print("Available dialogues:")

    for index, dialog in enumerate(dialogs, start=1):
        names_to_display = [dialog.chat.title, dialog.chat.first_name, dialog.chat.last_name]
        names_to_display = (name for name in names_to_display if name)
        names_to_display = " ".join(names_to_display)

        print(f'{index:>4}. Type: {dialog.chat.type:>10}. Title: "{names_to_display}".')

    selected_number = 0

    while selected_number <= 0 or selected_number > len(dialogs):
        selected_number = int(input("Select a chat by it's unique number: "))

    selected_number -= 1

    return dialogs[selected_number]


def get_user_messages(client: Client, dialog: Dialog, user: User, deep_search: bool = True) -> List[Message]:
    """
    Search for user messages in a given chat. If `deep_search` is equal to True, then all messages
    are fetched and checked manually. Otherwise, Telegram back-end based search is used, which is
    much faster, but usually misses messages, if they were sent long ago or a lot of messages have
    been deleted recently.
    """

    if deep_search:
        return [message for message in client.iter_history(chat_id=dialog.chat.id) if message.from_user == user]

    messages = list()

    # The maximum number of messages, that can be retrieved per one search,
    # seems to be equal to 999, though I haven't found any specific info on this.
    MAX_CHUNK_SIZE = 500
    current_offset = 0

    while True:
        messages_chunk = client.search_messages(
            chat_id=dialog.chat.id, offset=current_offset, limit=MAX_CHUNK_SIZE, from_user=user.id
        )

        if len(messages_chunk) == 0:
            break

        messages.extend(messages_chunk)
        current_offset += MAX_CHUNK_SIZE

    return messages


def delete_messages(client: Client, dialog: Dialog, messages: List[Message]) -> bool:
    """
    This function deletes all given messages from the selected chat.
    """

    operation_statuses = list()

    # The maximum number of messages, that can be deleted per one request,
    # is equal to 100, though it looks like it's not stated anywhere in the documentation.
    MAX_CHUNK_SIZE = 100

    for index in range(0, len(messages), MAX_CHUNK_SIZE):
        messages_chunk = messages[index : index + MAX_CHUNK_SIZE]
        message_ids = [message.message_id for message in messages_chunk]

        status = client.delete_messages(chat_id=dialog.chat.id, message_ids=message_ids, revoke=True)
        operation_statuses.append(status)

    return all(operation_statuses)


if __name__ == "__main__":
    # Get required credentials to run Telegram application
    app_credentials = get_application_credentials()

    # Create an application instance
    with Client(session_name="client", api_id=app_credentials.api_id, api_hash=app_credentials.api_hash) as app:

        # Get all user's dialogues
        available_dialogs = [dialog for dialog in app.iter_dialogs()]

        # Prompt user to select a specific one
        selected_dialog = select_dialog(dialogs=available_dialogs)

        print("Started messages search, this step might take up to several minutes.")
        user_messages = get_user_messages(client=app, dialog=selected_dialog, user=app.get_me())

        print("Found", len(user_messages), "messages in selected chat")
        status = delete_messages(client=app, dialog=selected_dialog, messages=user_messages)

        status_message = "Successfully deleted specified messages." if status else "Some messages could not be deleted."
        print(status_message)

