from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, MessageHandler, Filters
import birthdays
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
        db_session.add(user)
        db_session.commit()
    bot.sendMessage(update.message.chat_id, text="Hi! I'm <b>BirthdayBot!</b>\n"
                                                 "I can remind you to congratulate your friends on their birthdays \n\n"
                                                 "I recommend you to start with <b>setting your time zone</b>: "
                                                 "/time_zone, "
                                                 "and then <b>notifications time</b>: /alarm_time.\n"
                                                 "<i>By default your time zone is set to UTC+00:00, "
                                                 "and notifications time is set to 09:00</i>\n"
                                                 "If you, for some reason, don't want to receive notifications, "
                                                 "use /disable. You will be able to reset your time zone and "
                                                 "notifications time any time you want.\n\n"
                                                 "You can control me by sending these commands:\n\n"
                                                 "<b>Birthdays settings</b>\n"
                                                 "/add - add new birthday to your list\n"
                                                 "/remove [name] - delete [name] from your list\n\n"
                                                 "<b>Notifications settings</b>\n"
                                                 "/set - provides quick access to Notification settings\n"
                                                 "/time_zone - set your time zone\n"
                                                 "/alarm_time - set a time for notifications\n"
                                                 "/disable - disable notifications\n\n"
                                                 "<b>View</b>\n"
                                                 "/year - get whole birthday list\n"
                                                 "/month get birthday list for month\n\n"
                                                 "<b>You can also use</b>\n"
                                                 "/help\n"
                                                 "/exit - stop sending me commands. Use /start to proceed.\n"
                                                 "/reset - stop current operation. "
                                                 "You'll be able to send me commands\n\n"
                                                 "For more information please visit (in progress)",
                    parse_mode='HTML')
    return 'Menu'


def settings1(bot, update):
    reply_keyboard = [['choose your time zone'], ['set notifications'], ['disable notifications']]
    update.message.reply_text("<b>Choose one of the options:</b>\n\n"
                              "<i>choose your time zone</i> - UTC format\n"
                              "<i>set notifications</i> - you will be able to choose a time for notifications\n"
                              "<i>disable notifications</i> - you won't receive any notifications from the bot\n\n"
                              "press /reset to exit",
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
            chat_data['is_notifications'] = False
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
        update.message.reply_text("Choose a time for everyday notifications\n"
                                  "Don't worry, you'll be able to change it any time "
                                  "you want by using /settings command\n",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True))
        return "SettingsAnswer"


def notifications_time(bot, update):
    reply_keyboard = [['00:00'], ['01:00'], ['02:00'], ['03:00'], ['04:00'], ['05:00'], ['06:00'],
                      ['07:00'], ['08:00'], ['09:00'], ['10:00'], ['11:00'], ['12:00'],
                      ['13:00'], ['14:00'], ['15:00'], ['16:00'], ['17:00'], ['18:00'],
                      ['19:00'], ['20:00'], ['21:00'], ['22:00'], ['23:00']]
    update.message.reply_text("Choose a time for everyday notifications\n"
                              "Don't worry, you'll be able to change it any time "
                              "you want by using /settings command\n\n"
                              "press /reset to exit",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True))
    return "SettingsAnswer"


def disable_notifications(bot, update, chat_data):
    if 'job' in chat_data:
        job = chat_data['job']
        job.schedule_removal()
        del chat_data['job']
        bot.sendMessage(update.message.chat_id, "Successfully disabled")
        chat_data['is_notifications'] = False
        return "Menu"
    else:
        bot.sendMessage(update.message.chat_id, "Notifications're already disabled")


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
    a1 = m_time.hour
    a2 = m_time.minute
    b1 = mtime_zone.hour
    b2 = mtime_zone.minute
    if (m_time >= chat_data['time_zone']):
        if (a2 - b2 < 0):
            c2 = (a2 - b2) % 60
            c1 = (a1 - b1 - 1) % 24
        else:
            c2 = (a2 - b2) % 60
            c1 = (a1 - b1) % 24
        new_time = time(c1, c2)
    else:
        if (a2 - b2 < 0):
            c2 = (a2 - b2) % 60
            c1 = (a1 - b1 - 1) % 24
        else:
            c2 = (a2 - b2) % 60
            c1 = (a1 - b1) % 24
        new_time = time(c1, c2)
    chat_data['is_notifications'] = True
    job = job_queue.run_daily(birthdays.alarm, new_time, days=(0, 1, 2, 3, 4, 5, 6), context=[update, chat_data],
                              name=new_time)
    chat_data['job'] = job
    return "Menu"


def time_zone1(bot, update):
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
                              "you want by using /settings command\n\n"
                              "press /reset to exit",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, parse_mode='HTML',
                                                               one_time_keyboard=True), parse_mode='HTML')
    return "TimeZone"


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
        a1 = m_time.hour
        a2 = m_time.minute
        b1 = mtime_zone.hour
        b2 = mtime_zone.minute

        if (m_time >= chat_data['time_zone']):
            if (a2 - b2 < 0):
                c2 = (a2 - b2) % 60
                c1 = (a1 - b1 - 1) % 24
            else:
                c2 = (a2 - b2) % 60
                c1 = (a1 - b1) % 24
            new_time = time(c1, c2)
        else:
            if (a2 - b2 < 0):
                c2 = (a2 - b2) % 60
                c1 = (a1 - b1 - 1) % 24
            else:
                c2 = (a2 - b2) % 60
                c1 = (a1 - b1) % 24
            new_time = time(c1, c2)
        job = job_queue.run_daily(birthdays.alarm, new_time, days=(0, 1, 2, 3, 4, 5, 6), context=[update, chat_data],
                                  name=new_time)
        chat_data['job'] = job
        return 'Menu'
    bot.sendMessage(update.message.chat_id, "I don't understand")
    return 'Menu'


# do we really need /stop command and what to do with it
def stop(bot, update):
    bot.sendMessage(update.message.chat_id, "You've decided to stop talking to me...\n"
                                            "Press /start when you change your mind.")
    return ConversationHandler.END


def reset(bot, update):
    return "Menu"


def m_help(bot, update):
    bot.sendMessage(update.message.chat_id, text="I'm <b>BirthdayBot!</b>\n"
                                                 "I can remind you to congratulate your friends on their birthdays \n\n"
                                                 "I recommend you to start with <b>setting your time zone</b>: "
                                                 "/time_zone, "
                                                 "and then <b>notifications time</b>: /alarm_time.\n"
                                                 "<i>By default your time zone is set to UTC+00:00, "
                                                 "and notifications time is set to 09:00</i>\n"
                                                 "If you, for some reason, don't want to receive notifications, "
                                                 "use /disable. You will be able to reset your time zone and "
                                                 "notifications time any time you want.\n\n"
                                                 "You can control me by sending these commands:\n\n"
                                                 "<b>Birthdays settings</b>\n"
                                                 "/add - add new birthday to your list\n"
                                                 "/remove [name] - delete [name] from your list\n\n"
                                                 "<b>Notifications settings</b>\n"
                                                 "/set - provides quick access to Notification settings\n"
                                                 "/time_zone - set your time zone\n"
                                                 "/alarm_time - set a time for notifications\n"
                                                 "/disable - disable notifications\n\n"
                                                 "<b>View</b>\n"
                                                 "/year - get whole birthday list\n"
                                                 "/month get birthday list for month\n\n"
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
                 CommandHandler('set', settings1),
                 CommandHandler('time_zone', time_zone1),
                 CommandHandler('alarm_time', notifications_time),
                 CommandHandler('disable', disable_notifications, pass_chat_data=True)],

        'Add_AddNameIsLink': [MessageHandler([Filters.text], birthdays.add_name_is_link),
                              CommandHandler('help', m_help),
                              CommandHandler('reset', reset),
                              CommandHandler('settings', settings)],

        'Add_IsLinkProvideOrAskDay': [MessageHandler([Filters.text], birthdays.is_link),
                                      CommandHandler('help', m_help),
                                      CommandHandler('reset', reset),
                                      CommandHandler('settings', settings)],

        'Add_ProvideLinkAskDay': [MessageHandler([Filters.text], birthdays.provide_link_ask_day),
                                  CommandHandler('help', m_help),
                                  CommandHandler('reset', reset),
                                  CommandHandler('settings', settings, pass_chat_data=True)],

        'Add_AddDayAskMonth': [MessageHandler([Filters.text], birthdays.add_day_ask_month),
                               CommandHandler('help', m_help),
                               CommandHandler('reset', reset),
                               CommandHandler('settings', settings)],

        'Add_AddMonthAddBirthday': [MessageHandler([Filters.text], birthdays.add_month_add_birthday),
                                    CommandHandler('help', m_help),
                                    CommandHandler('reset', reset),
                                    CommandHandler('settings', settings)],

        'Settings': [MessageHandler([Filters.text], settings, pass_chat_data=True),
                     CommandHandler('help', m_help),
                     CommandHandler('reset', reset),
                     CommandHandler('settings', settings)],

        'SettingsAnswer': [MessageHandler([Filters.text], settings_result, pass_job_queue=True, pass_chat_data=True),
                           CommandHandler('help', m_help),
                           CommandHandler('reset', reset),
                           CommandHandler('settings', settings)],

        'TimeZone': [MessageHandler([Filters.text], time_zone, pass_chat_data=True, pass_job_queue=True),
                     CommandHandler('help', m_help),
                     CommandHandler('reset', reset),
                     CommandHandler('settings', settings)]
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
