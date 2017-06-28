MonthToNumber = {
    'January': 1, 'February': 2, 'March': 3, 'April': 4,
    'May': 5, 'June': 6, 'July': 7, 'August': 8,
    'September': 9, 'October': 10, 'November': 11, 'December': 12
}

NumberToMonth = {
    1: 'January', 2: 'February', 3: 'March', 4: 'April',
    5: 'May', 6: 'June', 7: 'July', 8: 'August',
    9: 'September', 10: 'October', 11: 'November', 12: 'December'
}


def same_month(self, value):
    left, right = 0, len(self)
    while (left < right):
        middle = (left + right) // 2
        if (MonthToNumber[self[middle]['month']] < MonthToNumber[value['month']]
            or (MonthToNumber[self[middle]['month']] == MonthToNumber[value['month']] and
                        int(self[middle]['day']) < int(value['day']))):
            left = middle + 1
        else:
            right = middle
    answer = []
    while left < len(self) and self[left]['month'] == value['month']:
        answer.append(self[left])
        left += 1
    return answer


def add(self, new_birthday):
    left, right = 0, len(self)
    while (left < right):
        middle = (left + right) // 2
        if MonthToNumber[new_birthday['month']] < MonthToNumber[self[middle]['month']] \
                or (MonthToNumber[new_birthday['month']] == MonthToNumber[self[middle]['month']] and int(new_birthday['day'])
                    < int(self[middle]['day'])):
            right = middle
        else:
            left = middle + 1
    self.insert(left, new_birthday)
