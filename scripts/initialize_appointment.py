from project_setup import *

from store.models.appointments import TimeSlot, Days
import os
from datetime import datetime, timedelta

start_time = datetime.strptime("00:00", "%H:%M")
end_time = datetime.strptime("23:59", "%H:%M")
interval = timedelta(minutes=15)

LOCK_FILE = ".lock"


def insert_time_slots():
    data_list = []
    current_time = start_time
    while current_time <= end_time:
        time_ = current_time.strftime("%H:%M")
        data_list.append(TimeSlot(start_time=time_))
        current_time += interval
    TimeSlot.objects.bulk_create(data_list)
    open(LOCK_FILE, "w").write("✧˚·̩̩̥͙˚̩̥̩̥·̩̩̥͙✧·̩̩̥͙˚̩̥̩̥˚·̩̩̥͙✧ 𝒯𝒽𝒾𝓈 𝒻𝒾𝓁𝑒 𝒾𝓈 𝓁𝑜𝒸𝓀𝑒𝒹 ·̩̩̥͙✧·̩̩̥͙˚̩̥̩̥˚·̩̩̥͙✧")


def insert_days():
    day_list = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    Days.objects.bulk_create([Days(day=day) for day in day_list])


if "__main__" == __name__:
    if not os.path.exists(LOCK_FILE):
        insert_time_slots()
        insert_days()
