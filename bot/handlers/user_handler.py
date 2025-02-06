from aiogram.filters import Command, CommandStart
from aiogram import Router, types
from aiogram.types import FSInputFile
from aiogram.utils.markdown import hbold
from ..config import BotConfig
import validators
import tldextract
from pytube import YouTube
import os
import subprocess
import json
import requests

user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(msg: types.Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    # Most event objects have aliases for API methods that can be called in events' context
    # For example if you want to answer to incoming message you can use `message.answer(...)` alias
    # and the target chat will be passed to :ref:`aiogram.methods.send_message.SendMessage`
    # method automatically or call API method directly via
    # Bot instance: `bot.send_message(chat_id=message.chat.id, ...)`
    await msg.answer(f"Hello , {hbold(msg.from_user.full_name)}!")


@user_router.message(Command("reply"))
async def cmd_reply(message: types.Message):
    await message.reply("Reply Message replies! 😃")


@user_router.message(Command("admin_info"))
async def cmd_admin_info(message: types.Message, config: BotConfig):
    if message.from_user.id in config.admin_ids:
        await message.answer("You are an admin.")
    else:
        await message.answer("You are not an admin.")


@user_router.message(Command("dice"))
async def cmd_dice(message: types.Message):
    await message.answer_dice(emoji="🎲")


@user_router.message()
async def cmd_handle_messages(msg: types.Message):
    if validators.url(msg.text):
        name = tldextract.extract(msg.text).domain
        match name:
            case "youtube":
                await download_from_youtube(msg.text)
            case "soundcloud":
                await download_from_soundcloud(msg)


async def download_from_youtube(link):
    try:
        save_path = "downloads\yt"
        os.makedirs(save_path, exist_ok=True)
        yt = YouTube(link)
        stream = yt.streams.get_highest_resolution()
        full_path = os.path.join(save_path, stream.default_filename + ".mp4")
        stream.download(output_path=save_path)
        return full_path
    except Exception as e:
        print(e)


async def download_from_soundcloud(msg: types.Message):
    try:
        save_path = "downloads"
        link = msg.text
        os.makedirs(save_path, exist_ok=True)

        # Debug: Check if youtube-dl is installed
        try:
            subprocess.run(["youtube-dl", "--version"], check=True)
        except FileNotFoundError:
            print(
                "Error: youtube-dl is not installed. Install it using 'pip install yt-dlp' or 'pip install youtube-dl'"
            )
            return None

        # Get the filename
        filename = (
            subprocess.check_output(["youtube-dl", "--get-filename", link])
            .decode("UTF-8")
            .strip()
        )
        print(f"Filename: {filename}")

        # Get metadata (JSON file)
        subprocess.call(["youtube-dl", "--write-info-json", "--skip-download", link])

        # Find JSON file
        json_files = [f for f in os.listdir(os.getcwd()) if f.endswith(".json")]
        if not json_files:
            print("Error: No JSON file found. The download may have failed.")
            return None

        json_file_path = json_files[0]
        print(f"Found JSON file: {json_file_path}")

        # Read JSON file
        with open(json_file_path, "r") as fp:
            data = json.load(fp)

        url = data.get("url", "")
        thumb = data.get("thumbnail", "")
        title = data.get("fulltitle", "")
        artist = data.get("uploader", "Unknown Artist")

        if not url:
            print("Error: No download URL found in JSON.")
            return None

        # Download audio file
        output_path = os.path.join(save_path, f"{title}.mp3")
        with open(output_path, "wb") as fp:
            fp.write(requests.get(url, stream=True).content)

        # Remove JSON metadata file
        json_file_full_path = os.path.join(os.getcwd(), json_file_path)
        try:
            if os.path.isfile(json_file_full_path):
                os.remove(json_file_full_path)

        except Exception as e:
            print(f"Error deleting JSON file: {e}")

        await msg.reply_audio(
            FSInputFile(output_path),
            caption="Enjoy this track! 🎧",
            performer=artist,
            title=title,
        )

        try:
            if os.path.isfile(output_path):
                os.remove(output_path)

        except Exception as e:
            print(f"Error deleting JSON file: {e}")

    except Exception as e:
        print(f"Error: {e}")
