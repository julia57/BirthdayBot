from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, Filters
import birthdays
import settings
from telegram.ext.conversationhandler import ConversationHandler
import logging
from config import Base, engine, db_session, updater, dp, job_queue
from DBMessages import DBMessages
from datetime import time


# /start command
def start(bot, update, chat_data, job_queue):
    if 'is_notifications' not in chat_data:
        chat_data['is_notifications'] = True
        job = job_queue.run_daily(birthdays.alarm, time(9, 0), days=(0, 1, 2, 3, 4, 5, 6), context=[update, chat_data],
                                  name='default')
        chat_data['job'] = job
    if 'time_zone' not in chat_data:
        chat_data['time_zone'] = time(0, 0)
    if 'sign' not in chat_data:
        chat_data['sign'] = True
    if 'user_time' not in chat_data:
        chat_data['user_time'] = time(9, 0)
    messages = DBMessages.query.filter(DBMessages.user == update.message.chat_id).all()
    if len(messages) == 0:
        user = DBMessages(update.message.from_user.id)
        print(update.message.from_user.username, update.message.from_user.id)
        db_session.add(user)
        db_session.commit()
    key_board = [["/add"], ["/month", "/help"]]
    bot.sendMessage(update.message.chat_id, text="Hi! I'm <b>BirthdayBot!</b>\n"
                                                 "Press /help for more information\n\n"
                                                 "If you're new here I highly recommend to start with settings "
                                                 "by using /set command\n\n",
                    parse_mode='HTML', reply_markup=ReplyKeyboardMarkup(key_board,
                                         one_time_keyboard=False))
    return 'Menu'


# do we really need /stop command and what to do with it
def stop(bot, update):
    bot.sendMessage(update.message.chat_id, "You've decided to stop talking to me...\n"
                                            "Press /start when you change your mind.",
                    reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def reset(bot, update):
    key_board = [["/add"], ["/month", "/help"]]
    update.message.reply_text(
        text="Use /help if you got stuck",
        reply_markup=ReplyKeyboardMarkup(key_board,
                                         one_time_keyboard=False)
    )
    return "Menu"


def m_help(bot, update):
    bot.sendMessage(update.message.chat_id, text="I'm <b>BirthdayBot!</b>\n"
                                                 "I can remind you to congratulate your friends on their birthdays \n\n"
                                                 "I recommend you to start with <b>setting your time zone"
                                                 " and notifications time</b>: "
                                                 "/set\n"
                                                 "<i>By default your time zone is set to UTC+00:00, "
                                                 "and notifications time is set to 09:00</i>\n"
                                                 "You will be able to reset your time zone and "
                                                 "notifications time any time you want.\n\n"
                                                 "You can control me by sending these commands:\n\n"
                                                 "<b>Birthdays settings</b>\n"
                                                 "/add - add new birthday to your list\n"
                                                 "/remove [name] - delete [name] from your list\n\n"
                                                 "<b>Notifications settings</b>\n"
                                                 "/set - all settings step by step\n\n"
                                                 "<b>View</b>\n"
                                                 "/year - get whole birthday list\n"
                                                 "/month - get birthday list for month\n\n"
                                                 "<b>You can also use</b>\n"
                                                 "/help\n"
                                                 "/exit - stop sending me commands. Use /start to proceed.\n"
                                                 "/reset - stop current operation. "
                                                 "You'll be able to send me commands\n\n"
                                                 "For more information please visit (in progress)",
                    parse_mode='HTML')
    return "Menu"


main_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start, pass_chat_data=True, pass_job_queue=True)],

    states={
        'Menu': [CommandHandler('add', birthdays.ask_name),
                 CommandHandler('remove', birthdays.remove, pass_args=True),
                 CommandHandler('year', birthdays.show_year, pass_chat_data=True),
                 CommandHandler('month', birthdays.show_month, pass_chat_data=True),
                 CommandHandler('help', m_help),
                 CommandHandler('set', settings.set1, pass_chat_data=True)],

        'Add_AddNameIsLink': [MessageHandler([Filters.text], birthdays.add_name_is_link),
                              CommandHandler('help', m_help),
                              CommandHandler('reset', reset)],

        'Add_IsLinkProvideOrAskDay': [MessageHandler([Filters.text], birthdays.is_link),
                                      CommandHandler('help', m_help),
                                      CommandHandler('reset', reset)],

        'Add_ProvideLinkAskDay': [MessageHandler([Filters.text], birthdays.provide_link_ask_day),
                                  CommandHandler('help', m_help),
                                  CommandHandler('reset', reset)],

        'Add_AddDayAskMonth': [MessageHandler([Filters.text], birthdays.add_day_ask_month),
                               CommandHandler('help', m_help),
                               CommandHandler('reset', reset)],

        'Add_AddMonthAddBirthday': [MessageHandler([Filters.text], birthdays.add_month_add_birthday),
                                    CommandHandler('help', m_help),
                                    CommandHandler('reset', reset)],

        'SettingsAnswer': [MessageHandler([Filters.text], settings.settings_result, pass_job_queue=True, pass_chat_data=True),
                           CommandHandler('help', m_help),
                           CommandHandler('reset', reset)],

        'TimeZone': [MessageHandler([Filters.text], settings.time_zone2, pass_chat_data=True, pass_job_queue=True),
                     CommandHandler('help', m_help),
                     CommandHandler('reset', reset)],

        'Settings1_Wait_Answer': [CommandHandler('time_zone', settings.time_zone1),
                                  CommandHandler('skip', settings.skip_time_zone_settings),
                                  CommandHandler('reset', reset)],

        'Settings2_Wait_Answer': [CommandHandler('alarm_time', settings.notifications_time),
                                  CommandHandler('disable', settings.disable_notifications, pass_chat_data=True),
                                  CommandHandler('skip', settings.skip_alarm_time_settings, pass_chat_data=True),
                                  CommandHandler('reset', reset)]
    },

    fallbacks=[CommandHandler("exit", stop)]
)


def main():
    Base.metadata.create_all(bind=engine)
    logging.basicConfig(level=logging.ERROR)
    dp.add_handler(main_conversation_handler)
    dp.add_handler(CommandHandler('help', m_help))
    updater.start_polling(bootstrap_retries=-1)
    updater.idle()


if __name__ == "__main__":
    main()
