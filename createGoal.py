# Create a new goal
import datetime
from beeminder import Beeminder
import argparse

version=1.0

parser = argparse.ArgumentParser(description=f"Version {version}: Create a new goal for the user")
parser.add_argument('goalname', type=str, help="Short name of goal, used in the URL (required)")
parser.add_argument('--title', type=str, default='', help="Title for the goal, used in the graph")
parser.add_argument('--type', choices=['hustler','biker', 'fatloser', 'gainer', 'inboxer', 'drinker', 'custom'], dest='goaltype', default="hustler", 
                    help="Goal type: options are 'hustler' (do more), 'biker' (odometer), 'fatloser' (weight loss), 'gainer' (weight gain), 'inboxer' (inbox fewer),'drinker' (do less), or 'custom'")
parser.add_argument('-d', '--date', default="2099-12-31", dest='goaldate', type=str, help="End date for goal, in yyyy-mm-dd format" )
parser.add_argument('-t', '--target', default=None, type=float, help="End quantity for goal" )
parser.add_argument('-r','--rate', type=float, required=True, help="Rate, in units per day (required)")
parser.add_argument('-s', '--start', dest='initval', type=float, default='0', help="Initial value")
parser.add_argument('-u','--units', type=str, required=True, help="Units for the goal (required)")
parser.add_argument('--test',dest="isTest", action='store_true', help="Test goal creation - API will be called but goal will not be created")
parser.add_argument('--ini',dest="ini_filename", type=str, default="beeminder.ini", help="Name of ini file where username and token are stored")
parser.add_argument('-b','--buffer',default=0,help="Days of initial buffer with flat graph, before slope starts at the target rate")
parser.add_argument('-v','--verbose',dest="verbose", action='store_true', help="Display version of this program")
args = parser.parse_args()

pyminder = Beeminder(ini_file=args.ini_filename)

print(f"Creating a new goal called {pyminder.get_username()}/{args.goalname} of type {args.goaltype}, with a rate of {args.rate} {args.units}/day")
if args.isTest:
    print(" - running in test mode, goal will not be created")

rc = pyminder.create_goal(slug=args.goalname,
                          title=args.title,
                          goal_type = args.goaltype,
                     gunits=args.units,
                     goaldate=args.goaldate,
                     goalval=args.target,
                     rate=args.rate,
                     initval=args.initval,
                     buffer=args.buffer,
                     test=args.isTest
                     )
print(rc)