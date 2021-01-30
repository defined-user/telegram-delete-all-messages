from time import sleep
from typing import List

from pyrogram import Client
from pyrogram.raw.functions.messages import Search
from pyrogram.raw.types import InputPeerSelf, InputMessagesFilterEmpty
from pyrogram.raw.types.messages import ChannelMessages
from pyrogram.errors import FloodWait, UnknownError


def get_dialog_list(telegram_application):
    dialogs = list()
    chunk_of_dialogs = telegram_application.get_dialogs()

    while len(chunk_of_dialogs) > 0:
        dialogs.extend(chunk_of_dialogs)
        chunk_of_dialogs = telegram_application.get_dialogs(offset_date=dialogs[-1].top_message.date)

    return dialogs


def get_message_list(telegram_application, selected_group):
    peer = telegram_application.resolve_peer(selected_group.chat.id)

    messages_response = telegram_application.send(
        Search(
            peer=peer,
            q="",
            filter=InputMessagesFilterEmpty(),
            min_date=0,
            max_date=0,
            offset_id=0,
            add_offset=0,
            max_id=0,
            min_id=0,
            limit=2_147_483_647,
            hash=0,
            from_id=InputPeerSelf(),
        )
    )

    return messages_response["messages"]

if __name__ == "__main__":
    # Get required credentials to run Telegram application
    api_id = int(input("Enter your app_id: "))
    api_hash = input("Enter your app_hash: ")

    # Create an application instance
    app = Client("client", api_id=api_id, api_hash=api_hash)
    app.start()

    try:
        group_type = "group" if input("Select a group (n - to select a supergroup) [Y/n]: ") != 'n' else "supergroup"

        # Get all user's chats of a selected type
        available_dialogs = get_dialog_list(telegram_application=app)
        available_dialogs = [dialog for dialog in available_dialogs if dialog.chat.type == group_type]

        # Select required chat
        print(f"Available {group_type}s:")
        for index, group_dialog in enumerate(available_dialogs, start=1):
            print(f"{index}. {group_dialog.chat.title}")

        selected_group_number = int(input("Enter a number of a group to delete messages in: "))
        selected_group_number -= 1

        if selected_group_number < 0 or selected_group_number >= len(available_dialogs):
            print("Invalid group number selected.")
            exit(1)

        selected_group = available_dialogs[selected_group_number]

        # Get a list of messages
        messages = get_message_list(telegram_application=app, selected_group=selected_group)
        message_ids = [message.id for message in messages]

        # Delete all messages
        print(f"Deleting {len(messages)} messages.")

        for index in range(0, len(message_ids), 100):
            try:
                ids_chunk = message_ids[index:index + 100]
                app.delete_messages(chat_id=selected_group.chat.id, message_ids=ids_chunk)
            except FloodWait as fe:
                print(f"Small pause to avoid flooding Telegram servers: {fe}")
                sleep(fe.x)

        print("Done.")

    except UnknownError as ur:
        print(f"An error occurred during execution: {ur}. Leaving...")

    # Stop the application, otherwise, a leak will occur
    app.stop()
