import birthdays
from datetime import time, datetime
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove


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
    update.message.reply_text("<b>Choose your time zone in UTC format</b>\n\n",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, parse_mode='HTML',
                                                               one_time_keyboard=True), parse_mode='HTML')
    return "TimeZone"


def time_zone2(bot, update, chat_data, job_queue):
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
        if text[0] == '+':
            sign = True
        else:
            sign = False
        text = text[1:]
        text = text.split('.')
        hour = int(text[0])
        minutes = int(text[1])
        n_time = time(hour, minutes)
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
        reply_keyboard = [["/alarm_time", "/disable"], ['/skip', '/reset']]
        bot.sendMessage(update.message.chat_id, "Great! Now let's <b>set notifications time</b>\n\n"
                                                "By default the notifications time is <b>09:00</b>\n"
                                                "press /alarm_time to proceed\n"
                                                "press /disable to disable notifications\n"
                                                "or you can /skip this step", parse_mode='HTML',
                        reply_markup=ReplyKeyboardMarkup(reply_keyboard, parse_mode='HTML', one_time_keyboard=True))
        return "Settings2_Wait_Answer"
    else:
        bot.sendMessage(update.message.chat_id, "I don't understand, try again")
        reply_keyboard = [['UTC-12.00'], ['UTC-11.00'], ['UTC-10.00'], ['UTC-9.30'], ['UTC-9.00'],
                          ['UTC-8.00'], ['UTC-7.00'], ['UTC-6.00'], ['UTC-5.00'], ['UTC-4.00'],
                          ['UTC-3.30'], ['UTC-3.00'], ['UTC-2.00'], ['UTC-1.00'], ['UTC-00.00'],
                          ['UTC+1.00'], ['UTC+2.00'], ['UTC+3.00'], ['UTC+3.30'], ['UTC+4.00'],
                          ['UTC+4.30'], ['UTC+5.00'], ['UTC+5.30'], ['UTC+5.45'], ['UTC+6.00'], ['UTC+6.30'],
                          ['UTC+7.00'],
                          ['UTC+8.00'], ['UTC+8.30'], ['UTC+8.45'], ['UTC+9.00'], ['UTC+9.30'],
                          ['UTC+10.00'], ['UTC+10.30'], ['UTC+11.00'], ['UTC+12.00'], ['UTC+12.45'],
                          ['UTC+13.00'], ['UTC+14.00']]
        update.message.reply_text("<b>Choose your time zone in UTC format</b>\n\n",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard, parse_mode='HTML',
                                                                   one_time_keyboard=True), parse_mode='HTML')
        return "TimeZone"


def set1(bot, update, chat_data):
    reply_keyboard = [["/time_zone"], ["/skip", '/reset']]
    bot.send_message(update.message.chat_id, "Let's start with <b>setting your time zone</b>\n\n"
                                             "By default your time zone is set to <b>UTC+00:00</b>\n"
                                             "press /time_zone to choose your time zone\n"
                                             "or you can /skip this step\n\n", parse_mode='HTML',
                     reply_markup=ReplyKeyboardMarkup(reply_keyboard, parse_mode='HTML', one_time_keyboard=True))
    return "Settings1_Wait_Answer"


def skip_time_zone_settings(bot, update):
    reply_keyboard = [["/alarm_time", "/disable"], ['/skip', '/reset']]
    bot.sendMessage(update.message.chat_id, "Great! Now let's <b>set notifications time</b>\n\n"
                                            "By default the notifications time is <b>09:00</b>\n"
                                            "press /alarm_time to proceed\n"
                                            "press /disable to disable notifications\n"
                                            "or you can /skip this step", parse_mode='HTML',
                    reply_markup=ReplyKeyboardMarkup(reply_keyboard, parse_mode='HTML', one_time_keyboard=True))
    return "Settings2_Wait_Answer"


def notifications_time(bot, update):
    reply_keyboard = [['00:00'], ['01:00'], ['02:00'], ['03:00'], ['04:00'], ['05:00'], ['06:00'],
                      ['07:00'], ['08:00'], ['09:00'], ['10:00'], ['11:00'], ['12:00'],
                      ['13:00'], ['14:00'], ['15:00'], ['16:00'], ['17:00'], ['18:00'],
                      ['19:00'], ['20:00'], ['21:00'], ['22:00'], ['23:00']]
    update.message.reply_text("Choose a time for everyday notifications\n",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True))
    return "SettingsAnswer"


def settings_result(bot, update, job_queue, chat_data):
    answer = update.message.text.split(':')
    if (len(answer) != 2):
        bot.sendMessage(update.message.chat_id, "I don't understand, try again")
        reply_keyboard = [['00:00'], ['01:00'], ['02:00'], ['03:00'], ['04:00'], ['05:00'], ['06:00'],
                          ['07:00'], ['08:00'], ['09:00'], ['10:00'], ['11:00'], ['12:00'],
                          ['13:00'], ['14:00'], ['15:00'], ['16:00'], ['17:00'], ['18:00'],
                          ['19:00'], ['20:00'], ['21:00'], ['22:00'], ['23:00']]
        update.message.reply_text("Choose a time for everyday notifications\n",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True))
        return "SettingsAnswer"
    if not answer[0].isdigit() or not answer[1].isdigit():
        bot.sendMessage(update.message.chat_id, "I don't understand, try again")
        reply_keyboard = [['00:00'], ['01:00'], ['02:00'], ['03:00'], ['04:00'], ['05:00'], ['06:00'],
                    ['07:00'], ['08:00'], ['09:00'], ['10:00'], ['11:00'], ['12:00'],
                      ['13:00'], ['14:00'], ['15:00'], ['16:00'], ['17:00'], ['18:00'],
                      ['19:00'], ['20:00'], ['21:00'], ['22:00'], ['23:00']]
        update.message.reply_text("Choose a time for everyday notifications\n",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True))
        return "SettingsAnswer"
    hour = int(answer[0])
    minutes = int(answer[1])
    if (not (hour < 24 and hour > -1)) or (not (minutes < 60 and minutes > -1)):
        bot.sendMessage(update.message.chat_id, "I don't understand, try again")
        reply_keyboard = [['00:00'], ['01:00'], ['02:00'], ['03:00'], ['04:00'], ['05:00'], ['06:00'],
                          ['07:00'], ['08:00'], ['09:00'], ['10:00'], ['11:00'], ['12:00'],
                        ['13:00'], ['14:00'], ['15:00'], ['16:00'], ['17:00'], ['18:00'],
                          ['19:00'], ['20:00'], ['21:00'], ['22:00'], ['23:00']]
        update.message.reply_text("Choose a time for everyday notifications\n",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True))
        return "SettingsAnswer"
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
    key_board = [["/add"], ["/month", "/help"]]
    bot.sendMessage(update.message.chat_id, "All set.\n",
                    reply_markup=ReplyKeyboardMarkup(key_board,
                                                     one_time_keyboard=False))
    return "Menu"


def skip_alarm_time_settings(bot, update, chat_data):
    key_board = [["/add"], ["/month", "/help"]]
    bot.sendMessage(update.message.chat_id, "All set.\n",
                    reply_markup=ReplyKeyboardMarkup(key_board,
                                                     one_time_keyboard=False))
    return "Menu"


def disable_notifications(bot, update, chat_data):
    if 'job' in chat_data:
        job = chat_data['job']
        job.schedule_removal()
        del chat_data['job']
        bot.sendMessage(update.message.chat_id, "Successfully disabled")
        chat_data['is_notifications'] = False
        key_board = [["/add"], ["/month", "/help"]]
        bot.sendMessage(update.message.chat_id, "All set.\n",
                        reply_markup=ReplyKeyboardMarkup(key_board,
                                                         one_time_keyboard=False))
        return "Menu"
    else:
        bot.sendMessage(update.message.chat_id, "Notifications're already disabled", reply_markup=ReplyKeyboardRemove())
    key_board = [["/add"], ["/month", "/help"]]
    bot.sendMessage(update.message.chat_id, "All set.\n",
                    reply_markup=ReplyKeyboardMarkup(key_board,
                                                     one_time_keyboard=False))
    return "Menu"
