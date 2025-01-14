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
from datetime import timedelta
from django.utils import timezone
from core.logs import Logger

DATE_FORMAT = "%Y/%m/%d"
logger = Logger("update_slots.log")


def update_slots(days_ahead=7):
    """
    Creates appointment slots for stores for the given day ahead from today.
    """
    target_date = (timezone.now() + timedelta(days=days_ahead)).date()
    day_name = target_date.strftime("%A")

    try:
        # Get day object
        day_obj = Days.objects.filter(day=day_name).first()
        if not day_obj:
            logger.warning(f"No matching day object found for day: {day_name}")
            return None

        # Exclude stores on holiday
        store_on_leave_ids = set(
            StoreHoliday.objects.filter(holiday__date=target_date).values_list(
                "store__id", flat=True
            )
        )

        # Filter stores available on the target day
        stores = StoreAvailability.objects.filter(days=day_obj).exclude(
            store__id__in=store_on_leave_ids
        )

        # Generate appointment slots
        slots_to_create = []
        for store in stores:
            time_slots = TimeSlot.objects.filter(
                start_time__range=(store.start_working_hr, store.end_working_hr)
            )
            for time_slot in time_slots:
                slots_to_create.append(
                    AppointmentSlot(
                        store=store.store, date=target_date, time_slot=time_slot
                    )
                )

        # Bulk create slots
        if slots_to_create:
            AppointmentSlot.objects.bulk_create(slots_to_create, ignore_conflicts=True)
            logger.info(
                f"Created {len(slots_to_create)} appointment slots for {target_date}."
            )
        else:
            logger.info(f"No slots created for {target_date}, no time slots found.")
    except Exception as e:
        logger.error(f"Error updating slots for date {target_date}: {str(e)}")
    return target_date.strftime(DATE_FORMAT)


def delete_old_slots():
    """
    Deletes appointment slots for dates before today.
    """
    try:
        old_appointments = AppointmentSlot.objects.filter(
            date__lt=timezone.now().date()
        )
        count = old_appointments.count()
        if count > 0:
            old_appointments.delete()
            logger.info(f"{count} old appointment slots deleted.")
        else:
            logger.info("No old appointment slots to delete.")
    except Exception as e:
        logger.error(f"Error deleting old slots: {str(e)}")


if __name__ == "__main__":
    try:
        days_ahead = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    except ValueError:
        print("\033[31mError: The argument should be an integer.\033[0m")
        sys.exit(1)

    operational_date = update_slots(days_ahead)
    if operational_date:
        print(f"\033[37;42mSlots created for the date: {operational_date}\033[0m")
    delete_old_slots()
