## Add Bot code here
import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from cryptography.fernet import Fernet
import os

# Get Port no. and Bot Token from Environment Variables
PORT = int(os.environ.get('PORT', '8443'))
TOKEN = os.environ.get('TOKEN')

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi, I am a bot to encrypt/decrypt password. Use /help for more information')

def help(update, context):
    """Send a message when the command /help is issued."""
    reply = """Following are the list of messages that you can use-
    1. setkey | setkey key - Sets encryption/decryption key. Make sure input key is valid
    2. getkey - Returns encryption/decryption key
    3. encrypt password | encrypt key password - Returns encrypted password. Input password shouldnt contain whitespaces
    4. decrypt encrypted_password | decrypt key encrypted_password - Returns decrypted password. Input encrypted_password should be a valid encryption
    5. /getrandomkey - Returns random key to encrypt & decrypt
    6. resetkey - Resets key if any
    """
    update.message.reply_text(reply)

def setkey(update, context):
    """
    Update user's encryption/decryption key
    1. If no key is provided in input, generate a new key
    2. else use user provide key as new key
    """
    message = update.message.text.strip().split(' ')
    if len(message) == 1:
        context.user_data['KEY'] = Fernet.generate_key().decode('utf-8')
        reply = "Key has been set"
    elif len(message) == 2:
        try:
            Fernet(message[-1].encode('utf-8'))
            context.user_data['KEY'] = message[-1]
            reply = "Key has been set"
        except:
            reply = "Invalid Key"
    else:
        reply = "Invalid Input"
    update.message.reply_text(reply)

def getrandomkey(update, context):
    """
    Return random Fernet key
    """
    update.message.reply_text(Fernet.generate_key().decode('utf-8'))

def resetkey(update, context):
    """
    Resets key if any
    """
    context.user_data['KEY'] = ''
    update.message.reply_text('Key has been reset')

def getkey(update, context):
    """
    Returns user's encryption/decryption key
    """
    if 'KEY' in context.user_data and len(context.user_data['KEY']) > 0:
        update.message.reply_text(context.user_data['KEY'])
    else:
        update.message.reply_text("No key has been set by you yet")

def encrypt(update, context):
    """
    Encrypts user's message
    1. If no key is provided in input, encrypts message using already set user's key
    2. else use input key to encrypt the message
    """
    message = update.message.text.strip().split(' ')
    key = ''
    password = ''
    if len(message) == 2:
        key = context.user_data['KEY'] if 'KEY' in context.user_data else ''
        password = message[-1]
    elif len(message) == 3:
        key = message[-2]
        password = message[-1]

    if len(password) == 0:
        update.message.reply_text("Invalid Input")
    elif len(key) == 0:
        update.message.reply_text("Set key first")
    else:
        key = key.encode('utf-8')
        password = password.encode('utf-8')
        try:
            update.message.reply_text(Fernet(key).encrypt(password).decode('utf-8'))
        except:
            update.message.reply_text("Failed to Encrypt. Check if key and message are valid")

def decrypt(update, context):
    """
    Decrypts user's message
    1. If no key is provided in input, decrypt message using already set user's key
    2. else use input key to decrypt the message
    """
    message = update.message.text.strip().split(' ')
    key = ''
    encrypted_password = ''
    if len(message) == 2:
        key = context.user_data['KEY'] if 'KEY' in context.user_data else ''
        encrypted_password = message[-1]
    elif len(message) == 3:
        key = message[-2]
        encrypted_password = message[-1]

    if len(encrypted_password) == 0:
        update.message.reply_text("Invalid Input")
    elif len(key) == 0:
        update.message.reply_text("Set key first")
    else:
        key = key.encode('utf-8')
        encrypted_password = encrypted_password.encode('utf-8')
        try:
            update.message.reply_text(Fernet(key).decrypt(encrypted_password).decode('utf-8'))
        except:
            update.message.reply_text("Failed to Decrypt. Check if key and encrypted message are valid")

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("getrandomkey",getrandomkey))

    # on noncommand i.e message
    dp.add_handler(MessageHandler(Filters.regex(r'^getkey') | Filters.regex(r'^Getkey'), getkey))
    dp.add_handler(MessageHandler(Filters.regex(r'^setkey') | Filters.regex(r'^Setkey'), setkey))
    dp.add_handler(MessageHandler(Filters.regex(r'^resetkey') | Filters.regex(r'^Resetkey'), resetkey))
    dp.add_handler(MessageHandler(Filters.regex(r'^encrypt') | Filters.regex(r'^Encrypt'), encrypt))
    dp.add_handler(MessageHandler(Filters.regex(r'^decrypt') | Filters.regex(r'^Decrypt'), decrypt))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url='https://vipul-password-bot.herokuapp.com/' + TOKEN
    )

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
