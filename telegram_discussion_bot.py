from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import logging

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Bot token
TOKEN = "8382958693:AAGZ3CH6kBFVB-NXtKd_4RG0yu3BOOxLiU8"

# Channel + Discussion details
CHANNEL_USERNAME = "queschatt"       # your channel username
DISCUSSION_USERNAME = "yourchattbot" # your linked discussion group username
ORIGINAL_GROUP_ID = None               # We'll auto-detect the first image message


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles images in Group X and creates direct discussion links"""
    if not update.message:
        return

    # Debug: print incoming message chat id
    print(f"Received photo from chat: {update.message.chat.id}")

    global ORIGINAL_GROUP_ID
    # Auto-detect group ID on first image message
    if ORIGINAL_GROUP_ID is None:
        ORIGINAL_GROUP_ID = update.message.chat.id
        print(f"Detected ORIGINAL_GROUP_ID: {ORIGINAL_GROUP_ID}")

    # Only process messages from the original group to prevent looping
    if update.message.chat.id != ORIGINAL_GROUP_ID:
        return

    # Forward the image to the channel
    forwarded = await update.message.forward(chat_id=f"@{CHANNEL_USERNAME}")

    try:
        # Post a dummy comment in the discussion group as a reply to the channel post
        dummy_comment = await context.bot.send_message(
            chat_id=f"@{DISCUSSION_USERNAME}",
            text="🖼️ Discussion for this image 👇",
            reply_to_message_id=forwarded.message_id
        )

        # Build direct link to the image discussion thread using ?comment format
        discussion_link = f"https://t.me/{CHANNEL_USERNAME}/{forwarded.message_id}?comment={dummy_comment.message_id}"

        # Create inline button with direct discussion link
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("💬 Discuss this image", url=discussion_link)]
        ])

        # Reply under the image in Group X with the button
        await update.message.reply_text(
            "Join the discussion here 👇",
            reply_markup=keyboard
        )

    except Exception as e:
        logging.error(f"Error while creating discussion link: {e}")


if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()

    # Handle photo messages
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Bot is running... 🚀")
    app.run_polling()
