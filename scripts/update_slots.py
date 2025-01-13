import sys

if __name__ == "__main__":
    from project_setup import *
from store.models.appointments import (
    StoreAvailability,
    Stores,
    Days,
    StoreHoliday,
    TimeSlot,
    AppointmentSlot,
)
from datetime import datetime
from django.utils import timezone

DATE_FORMATE = "%Y/%m/%d"


def UpdateSlot(day=7):
    day = (timezone.now() + timezone.timedelta(days=day)).strftime(DATE_FORMATE)
    date_obj = datetime.strptime(day, DATE_FORMATE)
    store_on_leave_ids = StoreHoliday.objects.filter(
        holiday__date=date_obj.date()
    ).values_list("store__id", flat=True)

    day_name = date_obj.strftime("%A")
    day_obj = Days.objects.filter(day=day_name).first()

    stores = (
        StoreAvailability.objects.filter(days=day_obj)
        .select_related("store")
        .exclude(store__id__in=store_on_leave_ids)
    )

    for store in stores:
        print(store.store.name, store.start_working_hr, store.end_working_hr)
        slots = TimeSlot.objects.filter(
            start_time__range=(store.start_working_hr, store.end_working_hr)
        )
        print(slots)
        for slot in slots:
            try:
                AppointmentSlot.objects.create(
                    store=store.store, date=date_obj.date(), time_slot=slot
                )
            except Exception as e:
                print(f"\033[31m{e}")
        print("\n\n")
    return date_obj.strftime(DATE_FORMATE)


def DeleteSlot():
    AppointmentSlot.objects.filter(date__lt=timezone.now().date()).delete()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            argument_value = int(sys.argv[1])
            UpdateSlot(argument_value)
        except:
            print("The argument should be an integer.")
    else:
        UpdateSlot()
    DeleteSlot()
