from datetime import datetime
# from datetime import time
# from collections import defaultdict
# from bank_holidays import get_bank_holidays_for_year as get_bh


# Hours rates for different occupations and days. (0 - Sunday, 6 - Saturday).
# FLT - Forklift Driver, HB - Handballer, CH - Chargehand
RATES = {
    'FLT': {
        0: {14.30: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 13.26: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        1: {14.30: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 13.26: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        2: {14.30: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 13.26: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        3: {14.30: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 13.26: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        4: {14.30: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 13.26: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        5: {15.60: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 14.30: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        6: {15.60: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 14.30: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        7: {15.60: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], },
            },
    'HB': {
        0: {14.30: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 13.26: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        1: {14.30: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 13.26: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        2: {14.30: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 13.26: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        3: {14.30: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 13.26: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        4: {14.30: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 13.26: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        5: {15.60: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 14.30: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        6: {15.60: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 14.30: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        7: {15.60: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], },
          },
    'CH': {
        0: {15.91: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 14.88: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        1: {15.91: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 14.88: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        2: {15.91: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 14.88: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        3: {15.91: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 14.88: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        4: {15.91: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 14.88: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        5: {17.16: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 15.91: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        6: {17.16: [0, 1, 2, 3, 4, 5, 6, 19, 20, 21, 22, 23], 15.91: [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18]},
        7: {17.16: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23], },
          }
        }


# Function to determine the day of the week
def which_day(date, bank_hlds_list):
    if date in bank_hlds_list:
        return 7
    return date.weekday()


# Function to determine the hour rate based on the day of the week, hour and occupation
def check_rate(weekday, hour, occupation):
    if weekday in [0, 1, 2, 3]:
        if hour in RATES[occupation][weekday][list(RATES[occupation][weekday].keys())[1]]:
            return list(RATES[occupation][weekday].keys())[1]
        else:
            return list(RATES[occupation][weekday].keys())[0]
    elif weekday == 4:
        if hour < 24:
            if hour in RATES[occupation][weekday][list(RATES[occupation][weekday].keys())[1]]:
                return list(RATES[occupation][weekday].keys())[1]
            else:
                return list(RATES[occupation][weekday].keys())[0]
        else:
            return list(RATES[occupation][weekday + 1].keys())[0]
    elif weekday == 5:
        if hour in RATES[occupation][weekday][list(RATES[occupation][weekday].keys())[1]]:
            return list(RATES[occupation][weekday].keys())[1]
        else:
            return list(RATES[occupation][weekday].keys())[0]
    elif weekday == 6:
        if hour < 24:
            if hour in RATES[occupation][weekday][list(RATES[occupation][weekday].keys())[1]]:
                return list(RATES[occupation][weekday].keys())[1]
            else:
                return list(RATES[occupation][weekday].keys())[0]
        else:
            return list(RATES[occupation][0].keys())[0]
    else:
        return list(RATES[occupation][weekday].keys())[0]


# Function to calculate the salary
def salary_calc(shifts, bank_hlds_list):
    salary = []
    shift_details = []
    for week in shifts:
        week_wage = 0
        for i in shifts[week]:
            shift_weekday = which_day(shifts[week][i]['date'], bank_hlds_list)
            shift_wage = 0
            for j in range(shifts[week][i]['duration'].hour):
                shift_wage += check_rate(shift_weekday, shifts[week][i]['time'].hour + j, shifts[week][i]['profession'])
            if shifts[week][i]['time'].minute != 0:
                shift_wage -= ((check_rate(shift_weekday, shifts[week][i]['time'].hour, shifts[week][i]['profession']) -
                                check_rate(shift_weekday,
                                           shifts[week][i]['time'].hour + shifts[week][i]['duration'].hour,
                                           shifts[week][i]['profession'])) * shifts[week][i]['time'].minute / 60)
            week_wage += shift_wage
    #     salary.append(f'{week} - {week_wage}')
    # return salary

            # Add shift details
            shift_details.append({
                'week': week,
                'date': shifts[week][i]['date'].strftime('%Y-%m-%d'),
                'hours': shifts[week][i]['duration'].hour,
                'amount': round(shift_wage, 2)
            })
        salary.append(f'{week} - {round(week_wage, 2)}')
    return salary, shift_details


# Using for testing
# Function for read from file list of shifts.
# def read_from_file():
#     '''
#     Data in the file should be in the following format:
#     2024-11-12	6	18:00	FLT
#
#     separated by tabs
#     '''
#     with open(r'C:\Personal\TLP\tlp.txt', 'r') as f:
#         data = f.readlines()
#         data = [x.strip().split('\t') for x in data]
#     return data


# Function to calculate the week number. New financial year starts on {year}-04-06
def week_count(date):
    year = date.year
    fiscal_year_starts = datetime.strptime(f'{year}-04-06', '%Y-%m-%d')
    if date < fiscal_year_starts:
        year -= 1
        fiscal_year_starts = datetime.strptime(f'{year}-04-06', '%Y-%m-%d')
    week_day = fiscal_year_starts.weekday()
    number = ((date - fiscal_year_starts).days + week_day) // 7 + 1
    return number


# Using for testing
# Function for preparing data in dictionary shift_dict.
# def shift():
#     shift_dict = defaultdict(dict)
#     txt = read_from_file()
#     for i in range(len(txt)):
#         date = datetime.strptime(txt[i][0], '%Y-%m-%d')
#         week_number = week_count(date)
#         start_time = list(map(int, (txt[i][2].split(':'))))
#         start_time = time(start_time[0], start_time[1])
#         duration = time(int(txt[i][1]))
#         shift_dict[week_number][i] = {'date': date, 'time': start_time, 'duration': duration, 'profession': txt[i][3]}
#     return shift_dict


# Using for testing
# if __name__ == '__main__':
#     bank_holidays_list = [datetime.strptime(x, '%Y-%m-%d') for x in get_bh('england-and-wales')]
#     sal = salary_calc(shift(), bank_holidays_list)
#     for x in sal:
#         print(x)
#     str_sal = '\n'.join(sal)
#     print(str_sal)
