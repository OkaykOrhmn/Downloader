from aiogram.filters import Command, CommandStart
from aiogram import Router, types
from aiogram.types import InputMediaAudio, FSInputFile, InputMediaVideo, InputMediaPhoto
from aiogram.utils.markdown import hbold
from ..config import BotConfig
import validators
import tldextract
import os
import subprocess
import json
import requests
from urllib.parse import urlparse
import yt_dlp
import instaloader
import asyncio


user_router = Router()


def clean_soundcloud_url(shared_url):
    parsed_url = urlparse(shared_url)
    clean_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
    return clean_url


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
async def cmd_handle_messages(messag: types.Message):
    msg = await messag.reply("⌛ wait for analys data...")
    if validators.url(messag.text):
        name = tldextract.extract(messag.text).domain
        match name:
            # case "spotify":
            #     msg = await msg.edit_text("🎶 wait for download from Spotify...")
            #     await download_from_spotify(msg, messag.text)
            case "instagram":
                msg = await msg.edit_text("📸 wait for download from Instagram...")
                asyncio.create_task(download_from_instagram(msg, messag.text))

            case "youtube" | "youtu":
                msg = await msg.edit_text("🎥 wait for download from Youtube...")
                asyncio.create_task(download_from_youtube(msg, messag.text))

            case "soundcloud":
                msg = await msg.edit_text("🎶 wait for download from SoundCloud...")

                asyncio.create_task(download_from_soundcloud(msg, messag.text))
            case _:
                msg = await msg.edit_text("🤔 sorry, this url is not supported yet...")


# sp = spotipy.Spotify()


# async def download_from_spotify(msg: types.Message, link):
#     try:
#         track_id = link.split("/")[-1].split("?")[0]  # Extract track ID
#         track = sp.track(track_id)
#         # Get track details
#         track_name = track["name"]
#         artist = track["artists"][0]["name"]
#         album = track["album"]["name"]
#         preview_url = track["preview_url"]  # 30-sec preview
#         album_cover = track["album"]["images"][0]["url"]

#         print(track_name)

#     except Exception as e:
#         print(f"Error downloading: {e}")


loader = instaloader.Instaloader()


async def download_instagram_content(url):
    """Downloads Instagram stories, reels, posts, or photos and returns the file path, caption, and username."""
    try:
        # Initialize Instaloader
        loader = instaloader.Instaloader()

        # Extract shortcode from URL
        shortcode = url.split("/")[-2]
        post = instaloader.Post.from_shortcode(loader.context, shortcode)

        # Get uploader username & caption
        username = post.owner_username
        caption = post.caption if post.caption else "No caption available"

        # Create save path
        save_path = "downloads"
        os.makedirs(save_path, exist_ok=True)

        # Download the post
        loader.download_post(post, target=save_path)

        # Find the downloaded file
        media_file = None
        video, photo = None, None  # ✅ Ensure variables are initialized

        for file in os.listdir(save_path):
            file_path = os.path.join(save_path, file)

            if file.endswith(".mp4"):
                video = file_path
            elif file.endswith((".jpg", ".jpeg", ".png")):
                photo = file_path

        # Determine which media file to return
        if video:
            media_file = video
            if photo and os.path.exists(photo):
                os.remove(photo)  # Delete photo if video is available
        elif photo:
            media_file = photo

        # Clean up extra files
        for file in os.listdir(save_path):
            file_path = os.path.join(save_path, file)
            if file_path != media_file:
                os.remove(file_path)

        return media_file, username, caption

    except Exception as e:
        print(f"Error downloading: {e}")
        return None, None, None


async def download_from_instagram(msg: types.Message, link):
    """Handles the /insta command and sends the downloaded Instagram content."""
    try:
        # Extract URL from message
        url = link

        # Download content
        file_path, username, caption = await download_instagram_content(url)
        caption = f"📸 @{username}\n\n{caption}"
        if file_path:
            # Check if it's a video or image
            if file_path.endswith(".mp4"):
                media = FSInputFile(file_path)
                msg = await msg.edit_media(
                    media=InputMediaVideo(media=media, caption=caption),
                )
            else:
                media = FSInputFile(file_path)
                msg = await msg.edit_media(
                    media=InputMediaPhoto(media=media, caption=caption),
                )

            # Delete the file after sending
            os.remove(file_path)
        else:
            msg = await msg.edit_text(
                "⚠️ Could not download the content. Make sure the post is public."
            )

    except Exception as e:
        msg = await msg.edit_text("⚠️ Invalid command. Use: `/insta <Instagram_URL>`")
        print(e)


async def download_from_youtube(msg: types.Message, link):
    try:
        save_path = "downloads"
        os.makedirs(save_path, exist_ok=True)

        # yt-dlp options for downloading the video
        ydl_opts = {
            "format": "best",  # Download the best available quality
            "outtmpl": os.path.join(
                save_path, "%(title)s.%(ext)s"
            ),  # Define filename template
            "noplaylist": True,  # Don't download playlists
            "quiet": True,  # Suppress output (optional)
        }

        # Download video using yt-dlp
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)
            video_title = info_dict.get("title", "Downloaded Video")
            thumbnail_url = info_dict.get("thumbnail", None)  # Get the thumbnail URL
            video_width = info_dict.get("width", None)

        # Path to the downloaded file
        video_file = os.path.join(save_path, f"{video_title}.mp4")
        if thumbnail_url:
            thumbnail_path = os.path.join(save_path, f"{video_title}_thumbnail.jpg")
            response = requests.get(thumbnail_url)
            with open(thumbnail_path, "wb") as file:
                file.write(response.content)
        else:
            thumbnail_path = None

        # Send the downloaded video as a message
        msg = await msg.edit_media(
            media=InputMediaVideo(
                media=FSInputFile(video_file),
                caption=f"Title: {video_title} \n\nEnjoy this Video! 📽️\n",
                supports_streaming=True,
                width=video_width if video_width else None,
                thumb=FSInputFile(thumbnail_path)
                if thumbnail_path
                else None,  # Set thumbnail if available
            ),
        )

    except Exception as e:
        msg = await msg.edit_text("⚠️ Something went wrong!")
        print(e)

    finally:
        # Cleanup: Delete downloaded files after sending
        try:
            if os.path.exists(video_file):
                os.remove(video_file)  # Delete the video file
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)  # Delete the thumbnail file
        except Exception as cleanup_error:
            print(f"Error deleting files: {cleanup_error}")


# async def download_from_youtube(msg, link):
#     try:
#         save_path = "downloads"
#         os.makedirs(save_path, exist_ok=True)
#         yt = YouTube(
#             link,
#         )
#         stream = yt.streams.get_highest_resolution()
#         full_path = os.path.join(save_path, stream.default_filename + ".mp4")
#         stream.download(output_path=save_path)
#         msg = await msg.edit_media(
#             media=InputMediaVideo(
#                 media=full_path,
#                 caption="Enjoy this Video! 📽️",
#             ),
#         )
#     except Exception as e:
#         msg = await msg.edit_text("⚠️ somthing wrong!")
#         print(e)


async def download_from_soundcloud(msg: types.Message, link):
    try:
        save_path = "downloads"
        os.makedirs(save_path, exist_ok=True)
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

        subprocess.call(["youtube-dl", "--write-info-json", "--skip-download", link])

        json_files = [f for f in os.listdir(os.getcwd()) if f.endswith(".json")]
        if not json_files:
            print("Error: No JSON file found. The download may have failed.")
            return None

        json_file_path = json_files[0]
        print(f"Found JSON file: {json_file_path}")

        with open(json_file_path, "r") as fp:
            data = json.load(fp)

        url = data.get("url", "")
        thumb = data.get("thumbnail", "")
        title = data.get("fulltitle", "")
        artist = data.get("uploader", "Unknown Artist")

        if not url:
            print("Error: No download URL found in JSON.")
            return None

        output_path = os.path.join(save_path, f"{title}.mp3")
        with open(output_path, "wb") as fp:
            fp.write(requests.get(url, stream=True).content)

        json_file_full_path = os.path.join(os.getcwd(), json_file_path)
        try:
            if os.path.isfile(json_file_full_path):
                os.remove(json_file_full_path)

        except Exception as e:
            print(f"Error deleting JSON file: {e}")
        if thumb:
            thumbnail_path = os.path.join(save_path, f"{title}_thumbnail.jpg")
            response = requests.get(thumb)
            with open(thumbnail_path, "wb") as file:
                file.write(response.content)
        else:
            thumbnail_path = None
        audio_file = FSInputFile(output_path)
        thumbnail = FSInputFile(thumbnail_path)
        msg = await msg.edit_media(
            media=InputMediaAudio(
                media=audio_file,
                caption="Enjoy this track! 🎧",
                performer=artist,
                title=title,
                thumbnail=thumbnail,
            ),
        )

        try:
            if os.path.isfile(output_path):
                os.remove(output_path)

        except Exception as e:
            print(f"Error deleting JSON file: {e}")
        try:
            if os.path.isfile(thumbnail_path):
                os.remove(thumbnail_path)

        except Exception as e:
            print(f"Error deleting JSON file: {e}")

    except Exception as e:
        msg = await msg.edit_text("⚠️ somthing wrong!")

        print(f"Error: {e}")
