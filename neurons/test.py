import random
import datetime

def generate_random_datetime():
    year = random.randint(2000, 2022)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime.datetime(year, month, day, hour, minute, second)

random_datetime = generate_random_datetime()
print(random_datetime)

date_string = '2019-06-07 14:17:48'

# get datetime from string
datetime_obj = datetime.datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
print(datetime_obj)

