from telegram.ext import CommandHandler, MessageHandler, Filters
import birthdays
from telegram.ext.conversationhandler import ConversationHandler
import logging
from config import Base, engine, db_session, updater, dp, job_queue
from DBMessages import DBMessages
from datetime import time


# /start command
def start(bot, update, job_queue):
    messages = DBMessages.query.filter(DBMessages.user == update.message.chat_id).all()
    if len(messages) == 0:
        user = DBMessages(update.message.chat_id)
        db_session.add(user)
        db_session.commit()
    bot.sendMessage(update.message.chat_id, text="Hi! \n I'm BirthdayBot! \n "
                                                 "I will never let you forget to congratulate your friends. \n\n"
                                                 "<b>Birthdays settings</b>\n"
                                                 "/add\n"
                                                 "/remove\n"
                                                 "/year\n"
                                                 "/month\n\n"
                                                 "<b>You can also use</b>\n"
                                                 "/help\n"
                                                 "/exit\n"
                                                 "/reset", parse_mode='HTML')
    m_time = time(9, 0)
    job_queue.run_daily(birthdays.alarm, m_time, days=(0, 1, 2, 3, 4, 5, 6), context=[update])
    print(update.message.from_user.first_name)
    print(update.message.from_user.username)
    return 'Menu'


# do we really need /stop command and what to do with it
def stop(bot, update):
    bot.sendMessage(update.message.chat_id, "stop!")
    return ConversationHandler.END


def reset(bot, update):
    return "Menu"


def m_help(bot, update):
    bot.sendMessage(update.message.chat_id, text="Hi! \n I'm BirthdayBot! \n "
                                                 "I will never let you forget to congratulate your friends. \n\n"
                                                 "<b>Birthdays settings</b>\n"
                                                 "/add\n"
                                                 "/remove\n"
                                                 "/year\n"
                                                 "/month\n\n"
                                                 "<b>You can also use</b>\n"
                                                 "/help\n"
                                                 "/exit\n"
                                                 "reset", parse_mode='HTML')
    return "Menu"


main_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start, pass_job_queue=True)],

    states={
        'Menu': [CommandHandler('add', birthdays.ask_name), CommandHandler('remove', birthdays.remove, pass_args=True),
                 CommandHandler('year', birthdays.show_year), CommandHandler('month', birthdays.show_month),
                 CommandHandler('help', m_help)],

        'Add_AddNameIsLink': [MessageHandler([Filters.text], birthdays.add_name_is_link),
                              CommandHandler('help', m_help), CommandHandler('reset', reset)],

        'Add_IsLinkProvideOrAskDay': [MessageHandler([Filters.text], birthdays.is_link),
                                      CommandHandler('help', m_help), CommandHandler('reset', reset)],

        'Add_ProvideLinkAskDay': [MessageHandler([Filters.text], birthdays.provide_link_ask_day),
                                  CommandHandler('help', m_help), CommandHandler('reset', reset)],

        'Add_AddDayAskMonth': [MessageHandler([Filters.text], birthdays.add_day_ask_month),
                               CommandHandler('help', m_help), CommandHandler('reset', reset)],

        'Add_AddMonthAddBirthday': [MessageHandler([Filters.text], birthdays.add_month_add_birthday),
                                    CommandHandler('help', m_help), CommandHandler('reset', reset)],
    },

    fallbacks=[CommandHandler("exit", stop)]
)


def main():
    Base.metadata.create_all(bind=engine)
    logging.basicConfig(level=logging.ERROR)
    print('Hi!')
    dp.add_handler(main_conversation_handler)
    updater.start_polling()
    updater.idle()


main()
