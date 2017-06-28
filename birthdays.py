from telegram import ReplyKeyboardMarkup
from datetime import date, timedelta
from DBMessages import DBMessages
from DBBirthdays import DBBirthdays
from config import db_session
import birthday_class


def ask_name(bot, update):
    bot.sendMessage(update.message.chat_id, "Enter a name:\n")
    return 'Add_AddNameIsLink'


def add_name_is_link(bot, update):
    messages = DBMessages.query.filter(DBMessages.user == update.message.chat_id).first()
    name = update.message.text.strip()
    is_wrong = DBBirthdays.query.filter(DBBirthdays.name == name).filter(DBBirthdays.user ==
                                                                         update.message.chat_id).all()
    if len(is_wrong) > 0:
        bot.sendMessage(update.message.chat_id, "Such record already exists.\n Enter a name:\n")
        return "Add_AddNameIsLink"
    messages.name = name
    db_session.commit()
    reply_keyboard = [["Yes", "No"]]
    update.message.reply_text("Do you want to provide a link? \n",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))
    return 'Add_IsLinkProvideOrAskDay'


def is_link(bot, update):
    if update.message.text == "Yes":
        bot.sendMessage(update.message.chat_id, "provide a link")
        return "Add_ProvideLinkAskDay"
    elif update.message.text == "No":
        reply_keyboard = [['1', '2', '3', '4', '5', '6', '7'], ['8', '9', '10', '11', '12', '13'],
                          ['14', '15', '16', '17', '18', '19'], ['20', '21', '22', '23', '24', '25'],
                          ['26', '27', '28', '29', '30', '31']]
        update.message.reply_text("Enter the day: \n",
                                  reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                                   one_time_keyboard=True))
        return 'Add_AddDayAskMonth'
    else:
        bot.sendMessage("Impossible answer")
        return "Menu"


def provide_link_ask_day(bot, update):
    messages = DBMessages.query.filter(DBMessages.user == update.message.chat_id).first()
    text = update.message.text.strip()
    messages.link = text
    db_session.commit()
    reply_keyboard = [['1', '2', '3', '4', '5', '6', '7'], ['8', '9', '10', '11', '12', '13'],
                      ['14', '15', '16', '17', '18', '19'], ['20', '21', '22', '23', '24', '25'],
                      ['26', '27', '28', '29', '30', '31']]
    update.message.reply_text("Enter the day: \n",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True))
    return 'Add_AddDayAskMonth'


def add_day_ask_month(bot, update):
    messages = DBMessages.query.filter(DBMessages.user == update.message.chat_id).first()
    messages.day = update.message.text.strip()
    if not messages.day.isdigit():
        bot.sendMessage(update.message.chat_id, "date must be digit")
        return "Add_AddDayAskMonth"
    if int(messages.day) > 31 or int(messages.day) < 1:
        bot.sendMessage(update.message.chat_id, "impossible date")
        return "Add_AddDayAskMonth"
    db_session.commit()
    reply_keyboard = [['January', 'February', 'March'], ['April', 'May', 'June'],
                      ['July', 'August', 'September'], ['October', 'November', 'December']]
    update.message.reply_text("Enter the month: \n",
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard,
                                                               one_time_keyboard=True))
    return 'Add_AddMonthAddBirthday'


def add_month_add_birthday(bot, update):
    messages = DBMessages.query.filter(DBMessages.user == update.message.chat_id).first()
    day = messages.day
    month = update.message.text.strip()
    name = messages.name
    link = messages.link
    if month not in birthday_class.MonthToNumber:
        bot.sendMessage(update.message.chat_id, "Wrong month")
        return "Add_AddMonthAddBirthday"
    if month == "February" and (str(day) == '31' or str(day) == '30'):
        bot.sendMessage(update.message.chat_id, text="No such day in February:(")
        return "Menu"
    if month in {'April', 'June', 'September', 'November'} and str(day) == '31':
        bot.sendMessage(update.message.chat_id, text="This month contains only 30 days;)")
        return "Menu"
    n_date = date(2016, birthday_class.MonthToNumber[month], int(day))
    new_birthday = DBBirthdays(update.message.chat_id, n_date, name, link)
    db_session.add(new_birthday)
    db_session.commit()
    bot.sendMessage(update.message.chat_id, "New birthday successfully added!")
    return "Menu"


def show_year(bot, update):
    birthday_list = DBBirthdays.query.filter(DBBirthdays.user == update.message.chat_id).\
        order_by(DBBirthdays.date).all()
    number_of_birthdays = len(birthday_list)
    answer = ""
    if number_of_birthdays == 0:
        bot.sendMessage(update.message.chat_id, "No birthdays yet:(\nUse /add to add one.")
    else:
        today = date.today()
        today = date(2016, today.month, today.day)
        left, right = 0, number_of_birthdays
        while (left < right):
            middle = (left + right) // 2
            if (birthday_list[middle].date < today):
                left = middle + 1
            else:
                right = middle
        left = left % number_of_birthdays
        if birthday_list[left].date == today:
            answer = answer + "<b>Today:</b>\n-" + birthday_list[left].name + "\n"
        elif birthday_list[left].date == today + timedelta(days=1):
            answer = answer + "<b>Tomorrow:</b>\n-" + birthday_list[left].name + "\n"
        else:
            answer = answer + "<b>" + str(birthday_list[left].date.day) + " " + \
                     birthday_class.NumberToMonth[birthday_list[left].date.month] + ":</b>\n" + birthday_list[left].name + "\n"
        last = birthday_list[left].date
        for u in range(1, number_of_birthdays):
            u = (u + left) % number_of_birthdays
            this = birthday_list[u]
            if this.date == last:
                answer += "-" + this.name + "\n"
            elif this.date == today + timedelta(days=1):
                answer += "\n<b>Tomorrow:</b>\n-" + this.name + "\n"
            else:
                answer += "\n<b>" + str(this.date.day) + " " + birthday_class.NumberToMonth[this.date.month] \
                          + ":</b>\n-" + this.name + "\n"
            last = this.date
    bot.sendMessage(update.message.chat_id, answer, parse_mode="HTML")
    return "Menu"


def show_month(bot, update):
    today = date.today()
    today = date(2016, today.month, today.day)
    month_later = today + timedelta(days=31)
    birthday_list = DBBirthdays.query.filter(DBBirthdays.user ==
                                             update.message.chat_id).filter(DBBirthdays.date >=
                                             today).filter(DBBirthdays.date < month_later).\
        order_by(DBBirthdays.date).all()
    number_of_birthdays = len(birthday_list)
    answer = ""
    if number_of_birthdays == 0:
        bot.sendMessage(update.message.chat_id, "No birthdays yet:(\nUse /add to add one.")
    else:
        left = 0
        if birthday_list[left].date == today:
            answer = answer + "<b>Today:</b>\n-" + birthday_list[left].name + "\n"
        elif birthday_list[left].date == today + timedelta(days=1):
            answer = answer + "<b>Tomorrow:</b>\n-" + birthday_list[left].name + "\n"
        else:
            answer = answer + "<b>" + str(birthday_list[left].date.day) + " " + \
                     birthday_class.NumberToMonth[birthday_list[left].date.month] + ":</b>\n-" + \
                     birthday_list[left].name + "\n"
        last = birthday_list[left].date
        for u in range(1, number_of_birthdays):
            this = birthday_list[u]
            if this.date == last:
                answer += "-" + this.name + "\n"
            elif this.date == today + timedelta(days=1):
                answer += "\n<b>Tomorrow:</b>\n" + "-" + this.name + "\n"
            else:
                answer += "\n<b>" + str(this.date.day) + " " + birthday_class.NumberToMonth[this.date.month] \
                          + ":</b>\n" + this.name + "\n"
            last = this.date
    bot.sendMessage(update.message.chat_id, answer, parse_mode="HTML")
    return "Menu"


def remove(bot, update, args):
    name_to_remove = ""
    if len(args) == 0:
        bot.sendMessage(update.message.chat_id, text="Try: /remove <name> \n"
                                                     "example: /remove Alexander Pushkin")
        return "Menu"
    for i in args:
        name_to_remove = i + " "
    name_to_remove = name_to_remove.strip()
    candidates = DBBirthdays.query.filter(DBBirthdays.name == name_to_remove).all()
    if len(candidates) == 0:
        bot.sendMessage(update.message.chat_id, "No such record")
    else:
        bot.sendMessage(update.message.chat_id, "Successfully removed")
        db_session.delete(candidates[0])
        db_session.commit()


def alarm(bot, job):
    update = job.context[0]
    today = date.today()
    today = date(2016, today.month, today.day)
    notification = DBBirthdays.query.filter(DBBirthdays.date == today).filter(DBBirthdays.user ==
                                                                              update.message.chat_id).all()
    if len(notification) != 0:
        text = "<b>Today:</b>\n"
    for i in notification:
        text = text + "-" + i.name + "\n"
        if i.link is not None:
            text = text + " " + i.link + "\n"
    notification = DBBirthdays.query.filter(DBBirthdays.date == today + timedelta(days=1)).filter(DBBirthdays.user ==
                                                                              update.message.chat_id).all()
    if len(notification) != 0:
        text = text + "<b>Tomorrow:</b>\n"
    for i in notification:
        text = text + "-" + i.name + "\n"
        if i.link is not None:
            text = text + " " + i.link + "\n"
    if text != "":
        bot.sendMessage(update.message.chat_id, text, parse_mode="HTML")
