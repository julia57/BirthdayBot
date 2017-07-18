from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, Filters
import birthdays
from telegram.ext.conversationhandler import ConversationHandler
import logging
from config import Base, engine, db_session, updater, dp, job_queue
from DBMessages import DBMessages
from datetime import time


# /start command
def start(bot, update, chat_data):
    print(chat_data)
    if 'time_zone' not in chat_data:
        chat_data['time_zone'] = time(0, 0)
    if 'sign' not in chat_data:
        chat_data['sign'] = True
    if 'days' not in chat_data:
        chat_data['days'] = 0
    if 'user_time' not in chat_data:
        chat_data['user_time'] = time(9, 0)
    messages = DBMessages.query.filter(DBMessages.user == update.message.chat_id).all()
    if len(messages) == 0:
        user = DBMessages(update.message.from_user.id)
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
                                                 "/settings\n"
                                                 "/help\n"
                                                 "/exit\n"
                                                 "/reset", parse_mode='HTML')
    return 'Menu'


def settings1(bot, update):
    reply_keyboard = [['choose your time zone'], ['set notifications'], ['disable notifications']]
    update.message.reply_text("<b>Choose one of the options:</b>\n\n"
                              "<i>'choose your time zone'</i> - UTC format"
                              "<i>'set notifications'</i> - you will be able to choose a time for notifications\n\n"
                              "<i>'disable notifications'</i> - you won't receive any notifications from the bot\n\n",
                              parse_mode='HTML',
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True))
    return "Settings"


def settings(bot, update, chat_data):
    text = update.message.text
    if not text == 'disable notifications' and not text == 'set notifications' and not text == 'choose your time zone':
        bot.sendMessage(update.message.chat_id, "I don't understand...\n"
                                                "Try again")
        return 'Menu'
    if text == 'disable notifications':
        if 'job' in chat_data:
            job = chat_data['job']
            job.schedule_removal()
            del chat_data['job']
            bot.sendMessage(update.message.chat_id, "Successfully disabled")
            return "Menu"
        else:
            bot.sendMessage(update.message.chat_id, "Notifications're already disabled")
    if text == 'choose your time zone':
        reply_keyboard = [['UTC-12.00'], ['UTC-11.00'], ['UTC-10.00'], ['UTC-9.30'], ['UTC-9.00'],
                          ['UTC-8.00'], ['UTC-7.00'], ['UTC-6.00'], ['UTC-5.00'], ['UTC-4.00'],
                          ['UTC-3.30'], ['UTC-3.00'], ['UTC-2.00'], ['UTC-1.00'], ['UTC-00.00'],
                          ['UTC+1.00'], ['UTC+2.00'], ['UTC+3.00'], ['UTC+3.30'], ['UTC+4.00'],
                          ['UTC+4.30'], ['UTC+5.00'], ['UTC+5.30'], ['UTC+5.45'], ['UTC+6.00'], ['UTC+6.30'],
                          ['UTC+7.00'],
                          ['UTC+8.00'], ['UTC+8.30'], ['UTC+8.45'], ['UTC+9.00'], ['UTC+9.30'],
                          ['UTC+10.00'], ['UTC+10.30'], ['UTC+11.00'], ['UTC+12.00'], ['UTC+12.45'],
                          ['UTC+13.00'], ['UTC+14.00']]
        update.message.reply_text("<b>Choose your time zone in UTC format</b>\n\n"
                                  "Don't worry, you'll be able to change it any time "
                                  "you want by using /settings command\n",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, parse_mode='HTML',
                                                                   one_time_keyboard=True), parse_mode='HTML')
        return "TimeZone"
    else:
        reply_keyboard = [['00:00'], ['01:00'], ['02:00'], ['03:00'], ['04:00'], ['05:00'], ['06:00'],
                          ['07:00'], ['08:00'], ['09:00'], ['10:00'], ['11:00'], ['12:00'],
                          ['13:00'], ['14:00'], ['15:00'], ['16:00'], ['17:00'], ['18:00'],
                          ['19:00'], ['20:00'], ['21:00'], ['22:00'], ['23:00']]
        update.message.reply_text("Choose a time for everyday notifications in the time zone UTC+0\n"
                                  "Don't worry, you'll be able to change it any time "
                                  "you want by using /settings command\n",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True))
        return "SettingsAnswer"


def settings_result(bot, update, job_queue, chat_data):
    answer = update.message.text.split(':')
    if (len(answer) != 2):
        bot.sendMessage(update.message.chat_id, "I don't understand...\n"
                                                "Try again")
        return 'Menu'
    if not answer[0].isdigit() or not answer[1].isdigit():
        bot.sendMessage(update.message.chat_id, "I don't understand...\n"
                                                "Try again")
        return 'Menu'
    hour = int(answer[0])
    minutes = int(answer[1])
    if (not (hour < 24 and hour > -1)) or (not (minutes < 60 and minutes > -1)):
        bot.sendMessage(update.message.chat_id, "I don't understand...\n"
                                                "Try again")
        return 'Menu'
    if 'job' in chat_data:
        job = chat_data['job']
        job.schedule_removal()
        del chat_data['job']
    m_time = time(hour, minutes)
    chat_data['user_time'] = m_time
    mtime_zone = chat_data['time_zone']
    if chat_data['sign'] == False:
        if (m_time >= chat_data['time_zone']):
            m_time = m_time - mtime_zone
            chat_data['days'] = 0
        else:
            m_time = m_time - mtime_zone
            chat_data['days'] = -1
    else:
        if (m_time + chat_data['time_zone'] > m_time):
            m_time = m_time + mtime_zone
            chat_data['days'] = 0
        else:
            m_time = m_time + mtime_zone
            chat_data['days'] = 1
    job = job_queue.run_daily(birthdays.alarm, m_time, days=(0, 1, 2, 3, 4, 5, 6), context=[update, chat_data],
                              name=m_time)
    chat_data['job'] = job
    return "Menu"


def time_zone(bot, update, chat_data, job_queue):
    text = update.message.text.split(" ")[0]
    reply_keyboard = [['UTC-12.00'], ['UTC-11.00'], ['UTC-10.00'], ['UTC-9.30'], ['UTC-9.00'],
                      ['UTC-8.00'], ['UTC-7.00'], ['UTC-6.00'], ['UTC-5.00'], ['UTC-4.00'],
                      ['UTC-3.30'], ['UTC-3.00'], ['UTC-2.00'], ['UTC-1.00'], ['UTC-00.00'],
                      ['UTC+1.00'], ['UTC+2.00'], ['UTC+3.00'], ['UTC+3.30'], ['UTC+4.00'],
                      ['UTC+4.30'], ['UTC+5.00'], ['UTC+5.30'], ['UTC+5.45'], ['UTC+6.00'], ['UTC+6.30'], ['UTC+7.00'],
                      ['UTC+8.00'], ['UTC+8.30'], ['UTC+8.45'], ['UTC+9.00'], ['UTC+9.30'],
                      ['UTC+10.00'], ['UTC+10.30'], ['UTC+11.00'], ['UTC+12.00'], ['UTC+12.45'],
                      ['UTC+13.00'], ['UTC+14.00']]
    answer = [text]
    if answer in reply_keyboard:
        text = text[3:]
        print(text)
        if text[0] == '+':
            sign = True
        else:
            sign = False
        text = text[1:]
        text = text.split('.')
        hour = int(text[0])
        minutes = int(text[1])
        n_time = time(hour, minutes)
        print(sign, n_time)
        chat_data['sign'] = sign
        chat_data['time_zone'] = n_time
        if 'job' in chat_data:
            job = chat_data['job']
            job.schedule_removal()
            del chat_data['job']
        m_time = chat_data['user_time']
        mtime_zone = chat_data['time_zone']
        if chat_data['sign'] == False:
            if (m_time >= chat_data['time_zone']):
                m_time = m_time - mtime_zone
                chat_data['days'] = 0
            else:
                m_time = m_time - mtime_zone
                chat_data['days'] = -1
        else:
            if (m_time + chat_data['time_zone'] > m_time):
                m_time = m_time + mtime_zone
                chat_data['days'] = 0
            else:
                m_time = m_time + mtime_zone
                chat_data['days'] = 1
        job = job_queue.run_daily(birthdays.alarm, m_time, days=(0, 1, 2, 3, 4, 5, 6), context=[update, chat_data],
                                  name=m_time)
        chat_data['job'] = job
        return 'Menu'
    bot.sendMessage(update.message.chat_id, "I don't understand")
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
                                                 "/settings\n"
                                                 "/help\n"
                                                 "/exit\n"
                                                 "/reset", parse_mode='HTML')
    return "Menu"


main_conversation_handler = ConversationHandler(
    entry_points=[CommandHandler('start', start, pass_chat_data=True)],

    states={
        'Menu': [CommandHandler('add', birthdays.ask_name), CommandHandler('remove', birthdays.remove, pass_args=True),
                 CommandHandler('year', birthdays.show_year), CommandHandler('month', birthdays.show_month),
                 CommandHandler('help', m_help), CommandHandler('settings', settings1)],

        'Add_AddNameIsLink': [MessageHandler([Filters.text], birthdays.add_name_is_link),
                              CommandHandler('help', m_help), CommandHandler('reset', reset),
                              CommandHandler('settings', settings)],

        'Add_IsLinkProvideOrAskDay': [MessageHandler([Filters.text], birthdays.is_link),
                                      CommandHandler('help', m_help), CommandHandler('reset', reset),
                                      CommandHandler('settings', settings)],

        'Add_ProvideLinkAskDay': [MessageHandler([Filters.text], birthdays.provide_link_ask_day),
                                  CommandHandler('help', m_help), CommandHandler('reset', reset),
                                  CommandHandler('settings', settings)],

        'Add_AddDayAskMonth': [MessageHandler([Filters.text], birthdays.add_day_ask_month),
                               CommandHandler('help', m_help), CommandHandler('reset', reset),
                               CommandHandler('settings', settings)],

        'Add_AddMonthAddBirthday': [MessageHandler([Filters.text], birthdays.add_month_add_birthday),
                                    CommandHandler('help', m_help), CommandHandler('reset', reset),
                                    CommandHandler('settings', settings)],
        'Settings': [MessageHandler([Filters.text], settings, pass_chat_data=True),
                         CommandHandler('help', m_help), CommandHandler('reset', reset),
                         CommandHandler('settings', settings)],
        'SettingsAnswer': [MessageHandler([Filters.text], settings_result, pass_job_queue=True, pass_chat_data=True),
                         CommandHandler('help', m_help), CommandHandler('reset', reset),
                         CommandHandler('settings', settings)],
        'TimeZone': [MessageHandler([Filters.text], time_zone, pass_chat_data=True, pass_job_queue=True),
                           CommandHandler('help', m_help), CommandHandler('reset', reset),
                           CommandHandler('settings', settings)]
    },

    fallbacks=[CommandHandler("exit", stop)]
)


def main():
    Base.metadata.create_all(bind=engine)
    logging.basicConfig(level=logging.ERROR)
    dp.add_handler(main_conversation_handler)
    updater.start_polling(bootstrap_retries=-1)
    updater.idle()


if __name__ == "__main__":
    main()
