import logging, urllib.request, json, os, shutil
import time

from datetime import datetime
from telegram import Update, ForceReply
from telegram.utils.request import Request
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    context.bot.send_message(chat_id=update.effective_chat.id, text='¡Hola! Con este bot puedes descargar contenido de Instagram. Simplemente envíame una URL de publicación de Instagram y te la enviaré como archivo para que la puedas guardar.')

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    url = update.message.text
    if not url.startswith('https://www.instagram.com/'):
        update.message.reply_text('Esto no es una URL de Instagram... 😕')

    if not url.endswith('/'):
        url = url+'/'


    url = url.split('?', 1)
    url = url[0]
    url = url+'?__a=1'
    print(url)
    req = urllib.request.Request(url, data=None, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'})
    r = urllib.request.urlopen(req).read()
    cont = json.loads(r.decode('utf-8'))

    content = []
    # Detectamos si la URL es de un post
    if not url.startswith('https://www.instagram.com/p'):
        update.message.reply_text('No hemos podido descargar contenido de esta URL. Revisa que sea correcta o contacta.')

    update.message.reply_text('Descargando...')
    owner = cont['graphql']['shortcode_media']['owner']['username']
    id = cont['graphql']['shortcode_media']['shortcode']
    #Detectamos si es una imagen, un vídeo o una colección
    if cont['graphql']['shortcode_media']['__typename'] == 'GraphImage':
        content.append([cont['graphql']['shortcode_media']['shortcode'], cont['graphql']['shortcode_media']['display_url'], '.jpg'])
    if cont['graphql']['shortcode_media']['__typename'] == 'GraphVideo':
        content.append([cont['graphql']['shortcode_media']['shortcode'], cont['graphql']['shortcode_media']['video_url'], '.jpg'])
    elif cont['graphql']['shortcode_media']['__typename'] == 'GraphSidecar':
        for c in cont['graphql']['shortcode_media']['edge_sidecar_to_children']['edges']:
            if c['node']['__typename'] == 'GraphImage':
                content.append([c['node']['shortcode'], c['node']['display_url'], '.jpg'])
            elif c['node']['__typename'] == 'GraphVideo':
                content.append([c['node']['shortcode'], c['node']['video_url'], '.mp4'])

    #@TODO stories
    #if url.startswith('https://www.instagram.com/stories'):
    #   content = cont['graphql']['shortcode_media']['display_url']

    #Creamos un directorio para la descarga con la ID del chat con el usuario y el timestamp actual
    now = time.time()
    #path = os.path.join(pathlib.Path(__file__).parent.resolve())
    path = str(update.effective_chat.id)+str(now)
    os.mkdir(path)
    if not content:
        update.message.reply_text('No se han podido recuperar fotos ni vídeos de esa publicación 😣')
        return
    update.message.reply_text('¡Ya está! Aquí lo tienes 😋')
    for c in content: #Descargamos los archivos
        print(urllib.request.urlretrieve(c[1], path+'/'+str(owner+'_'+c[0]+c[2])))
        update.message.reply_document(document=open(path+'/'+str(owner+'_'+c[0]+c[2]), 'rb'))

    shutil.rmtree(path)
    return





def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater("1808003385:AAHuFmH1Ham8sH41GNu0KaR65FVn5wD3yLc")

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", start))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()