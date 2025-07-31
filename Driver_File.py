# from dataclasses import dataclass, field
from dataclasses import dataclass
# from datetime import timedelta
# from typing import List, Optional, Tuple

@dataclass
class My_Driver:
 
    driver_id: int # 1 or 2
    truck: bool = None

    def assignToTruck(self, truck_list):

        for tr in truck_list:

            if tr.driver is None:
                tr.driver = self
                self.truck = tr
                return True
        return False