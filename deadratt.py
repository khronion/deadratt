# deadratt (c) 2024 Khronion
#
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

from nsdotpy.session import NSSession
from httpx import HTTPStatusError
from time import time

VERSION = "0.1"

user = input("User Nation: ")
while True:
    mode = input("Mode? (major=1, minor=2): ")
    if mode in ["1", "2"]:
        break

print("""

    (\,/)                        The only thing worse than a FattKatt is a
    xx   '''//,        _       ____                 __              __ ______
  ,/_;~,        \,    / '     / __ \___  ____ _____/ /  _________ _/ //_  __/
  "'   \    (    \    !      / / / / _ \/ __ `/ __  /  / ___/ __ `/ __// /  
        ',|  \    |__.'     / /_/ /  __/ /_/ / /_/ /  / /  / /_/ / /_ / /   
        '~  '~----''       /_____/\___/\__,_/\__,_/  /_/   \__,_/\__//_/
                                  deadratt (c) 2024 Khronion - v{}
""".format(VERSION))

session = NSSession("dead_ratt", VERSION, "Isle Khronion", user)

print("""
t       - Target a region
<ENTER> - Poll a targeted region for updates

c       - Check a region's key details
d       - view current time Delta
o       - Override time delta
""")

delta = 0 # used to offset predictions
target = ""
last_known_update = 0

"""
Ideal program flow:

User sets target (t REGION)
    - pull lastupdate, reject if lastupdate is more than 7200 seconds into the future
    - store region name and lastupdate+86400
    - print key region info

User asks to poll data (p)
    - print stored lastupdate + 86400 (eta) + delta to update based on stored info
    - if time - eta < 3600, update delta = true_lastupdate - eta and apply to future target calculations
    
User checks a region (c region)
    - print key region info but do not switch target
    
User asks to view delta (d)
"""
print("")
while True:
    query = input("deadratt> ")
    try:
        command = query[0]
    except IndexError:
        command = "_"
    selection = query[2:]

    try:
        match command:
            # set target
            case "t":
                # pull last known update time
                if mode == '1':
                    update = int(session.api_request(api="region", target=selection, shard="lastmajorupdate")["lastmajorupdate"])
                else:
                    update = int(session.api_request(api="region", target=selection, shard="lastminorupdate")["lastminorupdate"])

                # proceed only if update didn't occur recently
                if time() - update > 3600:
                    # store target name
                    target = selection

                    # store eta
                    last_known_update = update

                    print("  Target set. Use <ENTER> to poll target for updates.")

                else:
                    print("  Region recently updated. Select new target.")

            case "c":
                major = int(session.api_request(api="region", target=selection, shard="lastmajorupdate")["lastmajorupdate"])
                minor = int(session.api_request(api="region", target=selection, shard="lastminorupdate")["lastminorupdate"])
                delegate = session.api_request(api="region", target=selection, shard="delegate")["delegate"]
                endos = session.api_request(api="region", target=selection, shard="delegatevotes")["delegatevotes"]
                tags = session.api_request(api="region", target=selection, shard="tags")["tags"]["tag"]
                print("""Region: {region}
    Delegate: {delegate} ({endos}e)
    Governor: {has_governor}
    Password: {has_password}
    
    Next Major (estimate): {major_eta}s
    Next Minor (estimate): {minor_eta}s
                """.format(
                    region = selection,
                    delegate = delegate,
                    endos = endos,
                    has_governor = "Governorless" not in tags,
                    has_password = "Password" in tags,
                    major_eta = major+86400-int(time()),
                    minor_eta = minor+86400-int(time())))
            case "d":
                print("  Delta currently set to {}s".format(delta))
                print("  Use o to manually override.")
            case "o":
                print("**Manually overriding delta.")
                print("**Old delta: {}s".format(delta))
                delta = int(selection)
                print("**New delta: {}s".format(delta))
            case "q":
                exit()
            case "h":
                print("valid commands are:")
                print("  t - Target a region")
                print("  c - Check a region")
                print("  d - Discover delta value")
                print("  o - Override delta value")
                print("  ENTER - Ping target region and check for update")

            case _:
                if mode == '1':
                    current_update = int(session.api_request(api="region", target=target, shard="lastmajorupdate")["lastmajorupdate"])
                else:
                    current_update = int(session.api_request(api="region", target=target, shard="lastminorupdate")["lastminorupdate"])

                # check if region has updated - if so, warn user and recalculate delta
                if current_update != last_known_update:
                    print("**TARGET UPDATED {} seconds ago**".format(time() - current_update))
                    delta = current_update - (last_known_update + 86400)
                    print("**Updated delta: {} seconds**".format(delta))

                # otherwise print ETA
                else:
                    print("  Target Region: {}".format(target))
                    print("  Target ETA:    {} seconds".format(last_known_update + 86400 + delta - int(time())))

    except HTTPStatusError:
        print("**Error: {} does not exist.".format(selection))
    except ValueError:
        print("**Error: No target specified.")
