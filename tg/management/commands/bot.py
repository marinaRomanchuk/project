from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext, RegexHandler
from telegram.ext import ConversationHandler
from telegram.ext import CommandHandler
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater
from telegram.utils.request import Request
import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import schedule

from tg.models import Message
from tg.models import Profile

from todo.models import Todo

TITLE, DESCRIPTION, COMPLETED, START_DATE, END_DATE, REMIND = range(6)

tit = ""
des = ""
st = datetime.date.today()
en = datetime.date.today()
compl = False
rem = True

sched = BackgroundScheduler()

def log_errors(f):

    def inner(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            error_message = f'Произошла ошибка: {e}'
            print(error_message)
            raise e

    return inner


@log_errors
def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username
        }
    )
    m = Message(
        profile=p,
        text=text
    )
    m.save()

    reply_text = f'Ваш ID = {chat_id}\n{text}'
    update.message.reply_text(
        text=reply_text,
    )


@log_errors
def do_count(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username
        }
    )

    count = Message.objects.filter(profile=p).count()
    update.message.reply_text(
        text=f'У вас {count} сообщений',
    )

@log_errors
def do_see(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username
        }
    )

    count = Todo.objects.count()
    update.message.reply_text(
        text=f'У вас {count} заданий',
    )

    obj = Todo.objects.all()
    for i in range(len(obj)):
        update.message.reply_text(
            text=f'Title: {obj[i].title} \nDescription: {obj[i].description} \nStart date: {obj[i].start} \nEnd date'
                 f': {obj[i].end} \nComplited: {obj[i].completed}',
        )

@log_errors
def do_see_completed(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username
        }
    )

    count = Todo.objects.filter(completed=True).count()
    update.message.reply_text(
        text=f'У вас {count} законченных заданий',
    )

    obj = Todo.objects.filter(completed=True).all()
    for i in range(len(obj)):
        update.message.reply_text(
            text=f'Title: {obj[i].title} \nDescription: {obj[i].description} \nStart date: {obj[i].start} \nEnd date'
                 f': {obj[i].end} \nComplited: {obj[i].completed}',
        )


@log_errors
def do_see_not_completed(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username
        }
    )

    count = Todo.objects.filter(completed=False).count()
    update.message.reply_text(
        text=f'У вас {count} незаконченных заданий',
    )

    obj = Todo.objects.filter(completed=False).all()
    for i in range(len(obj)):
        update.message.reply_text(
            text=f'Title: {obj[i].title} \nDescription: {obj[i].description} \nStart date: {obj[i].start} \nEnd date'
                 f': {obj[i].end} \nComplited: {obj[i].completed}',
        )


@log_errors
def do_new(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username
        }
    )

    update.message.reply_text(
        text=f'Введите title',
    )
    return TITLE

@log_errors
def do_delete(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username
        }
    )

    update.message.reply_text(
        text=f'Введите title',
    )
    return 0

@log_errors
def title_delete(update: Update, context: CallbackContext):
    text = update.message.text

    Todo.objects.filter(title=text).delete()

    update.message.reply_text(
        text=f'Удалено',
    )
    return ConversationHandler.END

@log_errors
def title_update(update: Update, context: CallbackContext):
    text = update.message.text

    c = Todo.objects.filter(title=text).get().completed

    Todo.objects.filter(title=text).update(completed=not c)

    update.message.reply_text(
        text=f'Обновлено',
    )
    return ConversationHandler.END


@log_errors
def title(update: Update, context: CallbackContext):
    text = update.message.text
    global tit
    tit = str(text)

    update.message.reply_text(
        text=f'Введите описание',
    )
    return DESCRIPTION

@log_errors
def description(update: Update, context: CallbackContext):
    text = update.message.text
    global des
    des = str(text)

    reply_keyboard = [['True', 'False']]
    update.message.reply_text(
        text=f'Задача уже выполнена?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return COMPLETED

@log_errors
def completed(update: Update, context: CallbackContext):
    text = update.message.text
    global compl
    compl = bool(text)

    update.message.reply_text(
        text=f'Введите дату начала',
    )
    return START_DATE

@log_errors
def start_date(update: Update, context: CallbackContext):
    text = update.message.text
    global st
    st = datetime.datetime.strptime(text, "%d %m %Y").date()

    # job = sched.add_job("Don't forget about the task for today", run_date=datetime.datetime(2021, 11, 9, 3, 5, 0), args=[chat_id])
    update.message.reply_text(
        text=f'Введите end date',
    )
    return END_DATE

@log_errors
def end_date(update: Update, context: CallbackContext):
    text = update.message.text
    global en
    en = datetime.datetime.strptime(text, '%d %m %Y').date()

    reply_keyboard = [['True', 'False']]
    update.message.reply_text(
        text=f'Напомнить?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return REMIND

@log_errors
def remind(update: Update, context: CallbackContext):
    text = update.message.text
    global rem
    rem = bool(text)

    t = Todo(
        title=tit,
        description=des,
        start=st,
        end=en,
        completed=compl,
        remind_me=rem
    )
    t.save()
    update.message.reply_text('Задание добавлено')
    return ConversationHandler.END

@log_errors
def cancel(update: Update, context: CallbackContext):
    return ConversationHandler.END




class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        # 1 -- правильное подключение
        request = Request(
            connect_timeout=0.5,
            read_timeout=1.0,
        )
        bot = Bot(
            request=request,
            token=settings.TOKEN,
            # base_url=getattr(settings, 'PROXY_URL', None),
        )
        print(bot.get_me())

        # 2 -- обработчики
        updater = Updater(
            bot=bot,
            use_context=True,
        )


        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('new', do_new)],
            states={
                TITLE: [MessageHandler(Filters.text, title)],

                DESCRIPTION: [MessageHandler(Filters.text, description)],

                COMPLETED: [RegexHandler('^(True|False)$', completed)],

                START_DATE: [MessageHandler(Filters.text, start_date)],

                END_DATE: [MessageHandler(Filters.text, end_date)],

                REMIND: [RegexHandler('^(True|False)$', remind)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        updater.dispatcher.add_handler(conv_handler)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('delete', do_delete)],
            states={
                0: [MessageHandler(Filters.text, title_delete)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        updater.dispatcher.add_handler(conv_handler)

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('update', do_delete)],
            states={
                0: [MessageHandler(Filters.text, title_update)],
            },
            fallbacks=[CommandHandler('cancel', cancel)]
        )
        updater.dispatcher.add_handler(conv_handler)

        message_handler_count = CommandHandler('count', do_count)
        updater.dispatcher.add_handler(message_handler_count)

        message_handler_see = CommandHandler('see', do_see)
        updater.dispatcher.add_handler(message_handler_see)

        message_handler_see = CommandHandler('completed', do_see_completed)
        updater.dispatcher.add_handler(message_handler_see)

        message_handler_see = CommandHandler('notcompleted', do_see_not_completed)
        updater.dispatcher.add_handler(message_handler_see)

        message_handler = MessageHandler(Filters.text, do_echo)
        updater.dispatcher.add_handler(message_handler)

        # 3 -- запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        updater.idle()
