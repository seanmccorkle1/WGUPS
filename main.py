# Sean Mccorkle · ID #009964461

# pip install pandas
# pip install openpyxl
import pandas as pnd
import time
from datetime import datetime, timedelta, time as timeFn

from Package_File import My_Package
from Truck_File import My_Truck
from Hash_File import PackageHashTable
from Driver_File import My_Driver

# styling
console_line = "––––––––––––––––––––––––––––––––––––––––––––––––––"
count_obj, bin = {"count": 0 }, {"bin": 0}
bold, bold_red, bold_green, bold_yellow, bold_blue, bold_purple, bold_pink, bold_orange, nobold, bullet = "\033[1m", "\033[1;31m", "\033[1;32m", "\033[1;33m","\033[1;34m", "\033[1;35m","\033[1;38;5;205m" , "\033[1;38;5;208m" ,"\033[0m", "·"

num_of_trucks = 3
num_of_drivers = 2

# Don't edit the excel file
def readPackages(file):
    dataframe = pnd.read_excel(file, engine="openpyxl", skiprows=5,header=None)
    dataframe = dataframe.fillna("")
    return dataframe.values.tolist()

def readDistances(file):

    dataframe = pnd.read_excel(file, engine="openpyxl", header=None, skiprows=5)
    dataframe=dataframe.iloc[:, 2:]
    dataframe=dataframe.fillna(0)
    return dataframe.values.tolist()

def readAddresses(file):
    dataframe=pnd.read_excel(file, engine="openpyxl", skiprows=5, usecols="B", header=None)
    dataframe=dataframe.fillna("")

    addrs_from_spreadsheet=dataframe[1].astype(str).str.strip().tolist()
    addrs_from_spreadsheet.insert(0, "4001 South 700 East") # the hub address

    read= set()
    uniques = []
    
    for curr_address in addrs_from_spreadsheet: # filter for uniques
        if curr_address not in read:
            uniques.append(curr_address)
            read.add(curr_address)

    return uniques

def distanceLogic():

    posA=0
    my_reader = readDistances("distances.xlsx")
    my_reader_length = len(my_reader)
    
    distances_list_2D = [[0 for n in range(my_reader_length)] for n2 in range(my_reader_length)] #0.0?
    
    #O(N²)    
    for dist_array in my_reader: 
        
        for posB in range(my_reader_length):      
            # if dist_array[j]  != "":
            if dist_array[posB] is not None and dist_array[posB] != "" and dist_array[posB] != 0:
                val = float(dist_array[posB])
                distances_list_2D[posA][posB] = val
                distances_list_2D[posB][posA] = val
        posA += 1

    return distances_list_2D



# O(N) or linear
def packageLogic(my_hash):
    list= readPackages("packages.xlsx")

    for row in list:
        _id, _addr,  _city, _state, _zip, _dueby, _weight, _notes =  row
        _zip = str(_zip)
        _zip = _zip.replace(",", "").strip()

        _id =  int(_id)
        _status = 'Still in the hub' # starting location

        _package = My_Package(
            package_id= _id,
            addr = _addr,
            dest_city = _city,
            dest_state = _state,
            dest_zip = _zip,
            weight_kg=_weight,
            optional_notes = _notes,
            due_by = _dueby,
            hub_enroute_delivered = _status)
        my_hash.add(_package)

# O(N²)
def sort(my_hash, tr):
    sorted = []

    curr_addr = tr.hub
    pkg_list = tr.getPackagesOfTruck(my_hash)

    while len(pkg_list) >= 1:
        curr_pkg = findClosestPkg(curr_addr, pkg_list)
        sorted.append(curr_pkg.package_id)
        curr_addr = curr_pkg.addr
        pkg_list.remove(curr_pkg)

    tr.pkg_ids = sorted

def alreadyDelivered(package, time_delivered, obj):

    obj["count"] += 1
    correct_format = "%H:%M:%S"

    formatted = datetime.strptime(str(time_delivered), correct_format)

    print(bold_green + "Delivered at " + formatted.strftime("%I:%M %p") + nobold, flush=True)
    time.sleep(0.025)
    
    if obj["count"]== 40: print(console_line)
    return


# O(1)
def findDistanceBetween2(addr1, addr2):

    distances_list =distanceLogic()
    addr_list = readAddresses("packages.xlsx")

    addr1_idx = addr_list.index(addr1)
    addr2_idx = addr_list.index(addr2)

    # [COL][ROW], distances[5][20] is column F row 20
    return distances_list[addr1_idx][addr2_idx]

# Linear O(N) because of for loops
def init(num_of_trucks, num_of_drivers):
    starting_trucks = []
    starting_drivers = []

    # If there's 3 trucks, but only 2 drivers, then the extra truck doesn't matter
    for i in range(1, 3, 1): #1-index with ids

        curr_truck = My_Truck(truck_id = i)
        curr_driver=My_Driver(driver_id = i)
        starting_trucks.append(curr_truck)

        curr_driver.assignToTruck(starting_trucks)
        starting_drivers.append(curr_driver)

    return starting_trucks, starting_drivers

def assign(my_hash, tr):     # O(N²) or O(N³)

    while not tr.truckIsFull() and tr.is_idle is True and len(findFreePkgs(my_hash, tr)) >= 1:

        if len(tr.pkg_ids) == 0:   # start at the hub
            address = tr.hub

        else:
            num_pkgs_on_truck = len(tr.pkg_ids)
            last_pkg_id = tr.pkg_ids[num_pkgs_on_truck - 1]
            last_pkg = my_hash.get(last_pkg_id)
            address = last_pkg.addr

        near_pkg = findClosestPkg(address, findFreePkgs(my_hash, tr))
        tr.assignOnePackageToTruck(near_pkg)

        for associated_pkgs_list in associatedPackages(my_hash):

            if near_pkg in associated_pkgs_list:
                for assoc_pkg in associated_pkgs_list:
                    if assoc_pkg.isOnATruck() is False:
                        tr.assignOnePackageToTruck(assoc_pkg)

        sort(my_hash, tr)

#O(N) | This is used to find the closest package (that is not delivered yet) to the truck
def findClosestPkg(curr_addr, pkg_list):

    closest_pkg = None
    closest_dist = None

    for curr_pkg in pkg_list:

        if curr_pkg is not None and closest_pkg is None:
            closest_pkg = curr_pkg
            closest_dist = findDistanceBetween2(closest_pkg.addr, curr_addr)

        elif curr_pkg is not None:
            curr_distance = findDistanceBetween2(curr_pkg.addr, curr_addr)

            if curr_distance < closest_dist:
                closest_pkg = curr_pkg
                closest_dist = curr_distance

                if curr_distance < closest_dist:
                    closest_pkg = curr_pkg # update
                    closest_dist = curr_distance

    return closest_pkg


# Other main algorithm, this delivers the packages
# while condition: all 40 packages are NOT delivered

def deliverAll(my_hash, truck_list):
    datetimes = None

    while not checkIfPkgIsDelivered(my_hash):

        for curr_truck in truck_list:
            curr_truck.hasExitedTheHub(my_hash)
            curr_addr = curr_truck.hub

            while len(curr_truck.pkg_ids) >=1:

                # curr_id = curr_truck.pkg_ids[idx]
                curr_id = curr_truck.pkg_ids[0]
                package= my_hash.get(curr_id)

                travel_distance = findDistanceBetween2(curr_addr, package.addr)
                curr_truck.completeDelivery(my_hash, curr_id, travel_distance)

                curr_addr = package.addr

            curr_truck.sendTruckBackToTheHub(findDistanceBetween2(curr_addr, curr_truck.hub))

        for tr in truck_list:
            assign(my_hash, tr)

#O(N)
def checkIfPkgIsDelivered(my_hash):
    for package in my_hash.slots:
        if package is not None and package.time_delivered is None:
            return False
    return True

# O(N)
def findPkgsInHub(my_hash):
    unassigned_pkgs = []
    for pkg in my_hash.slots:
        if pkg is not None and pkg.isOnATruck() is False:
            unassigned_pkgs.append(pkg)

    return unassigned_pkgs


def findFreePkgs(my_hash, truck):

    unassignable = findExcludedPkgs(my_hash, truck)
    free_pkgs = []

    for pkg in findPkgsInHub(my_hash):
        if pkg is None or pkg in unassignable:
            continue
        # if pkg in unassignable:
        #     continue
        free_pkgs.append(pkg)
    return free_pkgs


# O(N³) aka "cubed"
# 1st loop - All packages - O(N)
# 2nd loop - Each group of associated packages  - O(N)
# 3rd loop - Each package in that group (if it's in it)

def findExcludedPkgs(my_hash, truck):
    associated_pkgs_2D = associatedPackages(my_hash)
    unassignable_pkgs = []

    for pkg in my_hash.slots:

        if pkg is None:
            continue

        special_id = pkg.findSpecialID()

        if pkg.isOnATruck():
            unassignable_pkgs.append(pkg)  # already on a truck, exclude it

        elif special_id is not None and special_id is not truck.truck_id:
            unassignable_pkgs.append(pkg)

            if len(associated_pkgs_2D) >=1:

                for associated_pkgs in associated_pkgs_2D:
                    if pkg in associated_pkgs:

                        for pkg2 in associated_pkgs:
                            if pkg2 not in unassignable_pkgs:
                                unassignable_pkgs.append(pkg2) # constrained, go to unassignable

        elif pkg.edgeCase() is not None and pkg.edgeCase() > truck.time_elapsed:
            if pkg not in unassignable_pkgs:
                unassignable_pkgs.append(pkg)

    return unassignable_pkgs

# O(N³)
def associatedPackages(my_hash):
    assoc_list = []

    for curr_pkg in my_hash.slots:
        if curr_pkg is not None:
            if "Must be delivered with" in curr_pkg.optional_notes.strip():
                associated_pkgs = directlyAssociatedPackages(my_hash, curr_pkg)
                combined = False
                combined_array = None

        if curr_pkg is not None and "Must be delivered with" in curr_pkg.optional_notes.strip():

            associated_pkgs = directlyAssociatedPackages(my_hash, curr_pkg)

            if len(assoc_list) != 0:

                for curr_pkg in associated_pkgs:

                    for arr in assoc_list:
                        if curr_pkg in arr:
                            combined = True
                            combined_array = arr     # append the pkg to the array of associated pkgs

                            break

            if combined is True:   #O(N)
                for curr_pkg in associated_pkgs:
                    if curr_pkg not in combined_array:
                        combined_array.append(curr_pkg)
            elif  combined is False:
                assoc_list.append(associated_pkgs)

            combined = False
            combined_array = None

    return assoc_list


# O(N²)
def directlyAssociatedPackages(hash, directly_associated):

    linked_package_ids = []

    if "Must be delivered with" in directly_associated.optional_notes.strip():

        directly_associated_pkgs = [directly_associated]
        notes_array = directly_associated.optional_notes.replace(",",  " ").split()

        for ele in notes_array:
            if ele.isdigit():
                linked_package_ids.append(int(ele))


        for linked_id in linked_package_ids:
            directly_associated = hash.get(linked_id)
            directly_associated_pkgs.append(directly_associated)
            other_pkgs = directlyAssociatedPackages(hash, directly_associated)

            if other_pkgs is not None:
                for curr_pkg in other_pkgs:
                    if curr_pkg not in directly_associated_pkgs:
                        directly_associated_pkgs.append(curr_pkg)
        return directly_associated_pkgs
    return

def greet():   # Prints welcome stuff, only run once at start
    print(bold +"C950 – " + '"WGUPS"'+ " project" + nobold)

def start(hash, truck_list, bin):

    if bin == 1: greet()

    user_input = None

    while user_input is None:

        print(console_line)
        print(bold_blue+ "Options"+nobold)
        print(bold_yellow+"(1)"+nobold +" Create status report")
        print(bold_blue+"(2)"+nobold+ " Find a specific package")
        print(bold_red +"(3)"+nobold + " Exit the console")

        user_input = input(bold_yellow +"\n"+"Pick one of the options [1, 2, 3]: " + nobold)
        user_input = user_input.strip()

        #isdigit() has to come first otherwise it gives an error instead of..
        # ..just returning false on the condition...

        if user_input.isdigit() and (int(user_input) ==1 or int(user_input) == 2 or int(user_input) == 3 ):
            if int(user_input) == 1:
                opt1AllPkgs(hash, truck_list)
            elif int(user_input) == 2:
                opt2SpecificPkg(hash, truck_list)
            elif int(user_input) == 3:
                quitFn()

        elif isAQuit(user_input): # "exit" or "quit "
            quitFn()
        elif user_input.isdigit() and int(user_input) >= 4:  # but not in the range
            print(bold_red+"Number is too high"+nobold)
        elif user_input.isdigit() and int(user_input) <=0:
            print(bold_red + "Number is too low" + nobold)
        else:
            resolveError(user_input)


def quitFn():
    print(bold_red+"Closing..."+nobold)
    quit()

def isAQuit(p):
    if type(p)==str and (p.strip().lower() == "exit" or p.strip().lower()== "quit"):
        return True
    return False


# Only used in startMenu(), gives a msg based on which type of error it is
def resolveError(wrong_input):
    if not wrong_input.isdigit():
        print(bold_red +"Input must be a number." + nobold)
    elif wrong_input.isdigit() and wrong_input!=1 and wrong_input!=2 and wrong_input!=3:
        print(bold_red + "Input has to be within the range 1 - 3" + nobold)
    else:
        print("Try again")


def findCombinedMiles(truck_list, given_datetime):

    total_mi = 0

    time_delta = (
        timedelta(
            hours=given_datetime.hour,
            minutes=given_datetime.minute))

    for tr in truck_list:


        if len(tr.mi_tuples) >= 1:

            back_idx = len(tr.mi_tuples) - 1

            while back_idx >=1:

                timestamp_mileage = tr.mi_tuples[back_idx][0] # (miles, time)
                timestamp_timedelta = tr.mi_tuples[back_idx][1]

                if timestamp_timedelta <= time_delta:
                    total_mi += timestamp_mileage
                    print(bold_blue + "Truck %d: " % tr.truck_id + "%0.2f miles" % timestamp_mileage + nobold)

                    break   # the user-given time has been reached
                else:
                    back_idx -= 1

            if back_idx ==0:
                print(bold_blue + "Truck %d: " % tr.truck_id + "0 miles" + nobold)
                
    if given_datetime.time() >= timeFn(12, 8):
        print(bold_green +"All packages delivered at 12:08 PM"+nobold)
        print("\n"+bold_yellow + "Time given: " + given_datetime.strftime("%I:%M %p")  + nobold)

    else:
        print("\n"+ bold_yellow + "Time given: " + given_datetime.strftime("%I:%M %p")  + nobold)

    if int(total_mi) == total_mi:
        total_mi = int(total_mi)
        print(bold_purple+ "Total: "+ str(total_mi) + " miles" + nobold)
    else:
        print(bold_purple+ "Total: "+ "%0.2f miles" % total_mi + nobold)


def opt1AllPkgs(ht, trucks):

    desired_time = promptTime()

    for package in range(1, len(ht.slots) + 1):
        if package is not None:
            packageInfo(ht, package, desired_time, sleep=False) # calls repeated printout

    findCombinedMiles(trucks, desired_time)
    start(ht, trucks, 0)

def opt2SpecificPkg(ht, truck_list):
    given_time = promptTime()
    pkg_id = promptUserForPackage(ht)
    
    print(console_line)
    print("Status at " +bold +given_time.strftime("%I:%M %p") + "..."+nobold )

    packageInfo(ht, pkg_id, given_time, sleep=True)
    start(ht, truck_list, 0)

def calculateTimeLeft(curr_time, delivery_time):

    hours_string=""
    mins_string= ""

    #delivery_time is in the future (greater number), in this fn
    hr, min =   delivery_time - curr_time, delivery_time - curr_time
    hr //= 60 # same as Math.floor() in js
    min %= 60 # the remainder is equal to the minutes

    if hr==0:     hours_string += ""
    elif hr==1:  hours_string += "1 hour and "
    elif hr >=2: hours_string  += f"{hr} hours and "

    if min==0:     mins_string+=""
    elif min ==1:  mins_string+= "1 minute"
    elif min >= 2: mins_string += f'{min} minutes'

    return hours_string + mins_string

def packageInfo(ht, package_id, given_datetime, sleep):

    pkg = ht.get(package_id)

    time_now= timedelta(hours=given_datetime.hour, minutes=given_datetime.minute)
    t = (datetime.combine(datetime.today(), timeFn.min) + time_now).time()

    print(bold_orange + "Package #" + str(pkg.package_id)+nobold, flush = True)
    if sleep: time.sleep(0.125)

    if pkg is not None and package_id ==9 and t>= timeFn(10,20):
        print("  " + bullet  + " Street" +"\t" +"410 State St"+"\n" + "  "+"  address" +"\t"+ "Salt Lake City" +", " + "UT" + " " + "84111", flush=True)

    else:
        print("  " + bullet  + " Address" +"\t" +str(pkg.addr) +"\n" + "          " +"\t"+ str(pkg.dest_city) +", "+str(pkg.dest_state) + " " + str(pkg.dest_zip), flush=True)

    if sleep: time.sleep(0.125)

    print("  " + bullet + " Weight"+"\t"+ str(pkg.weight_kg) + " kg", flush=True)
    if sleep: time.sleep(0.125)

    if str(pkg.due_by).strip() == "EOD":
        print("  " + bullet + " Due by"+ "\t" + "End of day (EOD)",  flush=True)
    else:
        print("  " + bullet + " Due by" + "\t"+ "10:30 AM", flush=True)
    if sleep: time.sleep(0.125)

    STILL_AT_THE_HUB  = pkg.time_start > time_now
    OUT_FOR_DELIVERY = pkg.time_delivered > time_now

    if given_datetime.time() <= timeFn(9,4) and pkg.package_id in [6, 25, 28, 32]:

        print( "  " + bullet+" Truck" +"\t" + "Will be on truck #" + str(pkg.truck_1_or_2), flush=True)

        print(bold_pink + "In freight, will arrive at the hub at 9:05 AM" + nobold, flush=True)

    elif STILL_AT_THE_HUB:
        print( "  " + bullet+" Truck" +"\t" + "Will be on truck #" + str(pkg.truck_1_or_2), flush=True)
        print(bold_blue+ "Package is still at the hub" + nobold, flush = True)

    elif OUT_FOR_DELIVERY:

        print( "  " + bullet+" Truck" +"\t" + "#" + str(pkg.truck_1_or_2), flush=True)

        delivery_timestamp_datetime = datetime.strptime(str(pkg.time_delivered), "%H:%M:%S")

        h, m = delivery_timestamp_datetime.hour, delivery_timestamp_datetime.minute
        h2, m2 = given_datetime.hour, given_datetime.minute

        # a higher number means "further in time"
        delivery_time_as_num = h*60+ m
        curr_time_as_num  = h2 * 60+ m2

        print(bold_yellow + "Out for delivery: " + "Expected to arrive at " + delivery_timestamp_datetime.strftime("%I:%M %p") + f" in " + calculateTimeLeft(curr_time_as_num, delivery_time_as_num) + nobold,flush=True)

    else:   # delivered already
        print( "  " + bullet+" Truck" +"\t" + "#" + str(pkg.truck_1_or_2), flush=True)
        alreadyDelivered(pkg, time_delivered=pkg.time_delivered, obj=count_obj)

    if sleep: time.sleep(0.125)

    return

def promptTime():

    t = None

    while t is None:
        try:
            t = input("What time? Type it like this – " + bold_blue +"HH:MM AM/PM: "+nobold)
            t = datetime.strptime(t.strip(), "%I:%M %p")

        except:
            if isAQuit(t):
                quitFn()
            print(bold_red+"Error: "+ "Wrong time format" + nobold)
    return t

def promptUserForPackage(ht):
    package_id = None

    while package_id is None:
        user_input = input("What is the ID of the package? "   + bold_blue +"Type only the number: " + nobold)

        if user_input.isdigit():
            if ht.get(int(user_input)) is not None:  # check if it exists
                package_id = int(user_input.strip())
            else:
                print(bold_red +  "Package #" + user_input + " not found" + nobold)

        elif user_input[0] == "#" and user_input.strip().slice(1).isdigit():
            if int(user_input.strip().slice(1)) >= 1 and int(user_input.strip().slice(1)) <= 40:
                package_id=int(user_input.slice(1))
        else:
            print(bold_red + "Invalid, please try again." + nobold)
    return package_id

def main():
    delivery_ht = PackageHashTable()
    packageLogic(delivery_ht)

    trucks, drivers = init(num_of_trucks, num_of_drivers)
    late_time = None

    # "Delayed on flight" packages
    for pkg in delivery_ht.slots:

        if pkg is not None and pkg.edgeCase() == timedelta(hours=9, minutes=5):
            if late_time is None or late_time > pkg.edgeCase():
                late_time = pkg.edgeCase()

    if len(trucks) >= 2:
        idx_of_last = len(trucks) - 1
        trucks[idx_of_last].time_elapsed = late_time

    for tr in trucks:
        assign(delivery_ht, tr)

    bin["bin"] += 1

    deliverAll(delivery_ht, trucks) #  run logic first
    start(delivery_ht,  trucks, bin["bin"]) # then show the menu

if __name__ == "__main__":
    main()