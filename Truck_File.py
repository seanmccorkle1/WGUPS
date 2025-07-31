from dataclasses import dataclass, field
from datetime import datetime, timedelta, time
from typing import List, Tuple, Optional

# Class to handle the 3 trucks (effectively 2, because there's only 2 drivers)
@dataclass
class My_Truck:

    truck_id: int
    capacity: int = 16 # "Each truck can carry a maximum of 16 packages"

    # the trucks always travel at 18mph
    mph: int = 18

    hub: str = "4001 South 700 East"
    driver: Optional[str] = None
    is_idle: bool = True; # starts idle
    total_mi: float = 0.0 # it could be a km distance ending in a decimal

    #"seconds=30,000" is around 8 AM
    time_elapsed: timedelta = field(default_factory=lambda: timedelta(hours=8, minutes=0, seconds=0))

    mi_tuples: List[ Tuple[float, timedelta] ] = field(default_factory = list)
    datetimes: List[datetime] = field(default_factory = list)
    pkg_ids: List[int] = field(default_factory = list)

    max_time_both_trucks = {"max": timedelta(hours=0, minutes=0, seconds=0) }

    # O(1)
    def assignOnePackageToTruck(self, package):
        curr_load = len(self.pkg_ids)

        if curr_load  < self.capacity:
            self.pkg_ids.append(package.package_id)    # assign package info to the truck
            package.truck_1_or_2 = self.truck_id
        return False

    def hasExitedTheHub(self, ht):
        for curr_id in self.pkg_ids:
            package = ht.get(curr_id)
            package.time_start = self.time_elapsed
            package.hub_enroute_delivered = "Out for delivery"

    def truckIsFull(self):
        if len(self.pkg_ids) >= self.capacity:
            return True
        return False

    def completeDelivery(self, ht, package_id, distance_traveled):
        
        package = ht.get(package_id)
        # _10_20 = datetime.strptime("10:20 AM", "%I:%M %p")
        # time_in_the_day = (datetime.combine(datetime.today(), time.min) + self.time_elapsed).time()

        self.pkg_ids.remove(package_id) #remove it
        self.is_idle = False

        self.addTraveledMilesToTruck(distance_traveled) # update the distance

        self.time_elapsed += timedelta(minutes=(distance_traveled / self.mph * 60)) # update how much time passed

        package.hub_enroute_delivered = "Delivered"
        package.time_delivered = self.time_elapsed  # record the time

        self.mi_tuples.append( (self.total_mi, self.time_elapsed) )
        self.datetimes.append(self.time_elapsed)

        self.max_time_both_trucks["max"] = max(self.time_elapsed,   self.max_time_both_trucks["max"])
        
    def sendTruckBackToTheHub(self, distance_from_home_mi):

        self.addTraveledMilesToTruck(distance_from_home_mi)

        # use distance from the hub
        self.time_elapsed += timedelta(minutes=(distance_from_home_mi / self.mph * 60))

        self.mi_tuples.append((self.total_mi, self.time_elapsed)) # update tuple list
        self.is_idle = True


    # O(1)
    def addTraveledMilesToTruck(self, miles):
        self.total_mi += miles


    def getPackagesOfTruck(self, hash):
        array = []
        for curr_id in self.pkg_ids:
            array.append(hash.get(curr_id))

        return array