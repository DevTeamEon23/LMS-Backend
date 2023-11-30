import os
from datetime import datetime
from enum import Enum
# from dateutil import tz
import pandas as pd
from dateutil.relativedelta import relativedelta


# Directory Definitions
dt_fmt = '%Y_%m_%d'
config_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(config_dir)
logs_dir = os.path.join(root_dir, 'logs/')
temp_dir = os.path.join(root_dir, 'temp')
backups_dir = os.path.join(root_dir, 'backups/')

dirs = [logs_dir]
status = [os.makedirs(_dir, exist_ok=True) for _dir in dirs if not os.path.exists(_dir)]

app_dir = os.path.join(root_dir, 'app')

# # Get the current time in UTC
# current_time_utc = datetime.utcnow()

# # Define the UTC timezone
# utc_tz = tz.tzutc()

# # Define the IST timezone
# ist_tz = tz.gettz('Asia/Kolkata')

# # Convert the current time from UTC to IST
# current_time_ist = current_time_utc.astimezone(ist_tz)

env_file = os.path.join(root_dir, '.env')

dt_fmt_1 = '%Y%m%d'
dt_fmt_2 = '%Y%m%d_%H%M%S'
dt_fmt_3 = '%Y-%m-%d %H:%M:%S'
dt_fmt_4 = '%Y-%m-%d %H:%M:%S.%f'
dt_fmt_5 = '%Y-%m-%d %H:%M:%S%z'

UTC = 'UTC'
EST = 'US/Eastern'
IST = 'Asia/Kolkata'





