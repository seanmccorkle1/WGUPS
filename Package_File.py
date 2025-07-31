from dataclasses import dataclass, field
from datetime import datetime, timedelta, time
from typing import Optional

# Class to handle package data
@dataclass
class My_Package:
    package_id: int; addr: str; dest_city: str; dest_state: str; dest_zip: str

    due_by: str
    hub_enroute_delivered: str
    weight_kg: int
    optional_notes: str

    time_start: Optional[datetime] = None         # When it leaves the hub
    time_delivered:  Optional[datetime] = None # When it's delivered

    is_loaded: bool = False
    truck_1_or_2: Optional[int] = None
    

    def isOnATruck(self):
        if self.truck_1_or_2 is None:
            return False
        return True

    def findSpecialID(self):

        chars = self.optional_notes.split()

        if "Can only be on" in self.optional_notes.strip():
            special_arr= [int(e) for e in chars if e.isdigit()]
            return special_arr[0]
        return None

    def edgeCase(self):

        self.optional_notes = self.optional_notes.strip()
        if "Delayed on flight" in self.optional_notes:  # "will not arrive until 9:05 AM"
            self.hub_enroute_delivered = "Delayed"
            time_str = self.optional_notes.split()[-2]

            dt = datetime.strptime(time_str, "%H:%M")
            return timedelta(hours=dt.hour, minutes=dt.minute)

        if "Wrong address" in self.optional_notes:
            return timedelta(hours=10, minutes=20)

        return None