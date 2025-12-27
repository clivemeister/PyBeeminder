# Creates a new Beeminder goal with a stepped road: flat for N days, jump by 1, repeat M times
from beeminder import Beeminder
import datetime
import argparse
import json

version = 1.0

parser = argparse.ArgumentParser(
    description=f"Version {version}: Create a new 'do more' goal with a stepped road (flat segments followed by jumps)"
)
parser.add_argument('-g', '--goalname', dest='goalname', required=True, type=str, 
                    help="Name (slug) for the new goal")
parser.add_argument('-t', '--title', dest='title', type=str, default=None,
                    help="Title for the goal (defaults to goalname if not specified)")
parser.add_argument('-d', '--days', dest='days_per_step', type=int, default=7,
                    help="Number of days to stay flat before each jump (default: 7)")
parser.add_argument('-s', '--steps', dest='num_steps', type=int, default=10,
                    help="Number of steps (jumps) to include in the road (default: 10)")
parser.add_argument('-u', '--units', dest='units', type=str, default='things',
                    help="Name of the units for this goal (default: 'things')")
parser.add_argument('--ini', dest="ini_filename", type=str, default="beeminder.ini",
                    help="Name of ini file where username and token are stored")
parser.add_argument('-v', '--verbose', dest="verbose", action='store_true',
                    help="Display detailed information about the goal creation process")
parser.add_argument('--dryrun', dest="dryrun", action='store_true',
                    help="Show what would be created without actually creating the goal")
args = parser.parse_args()

# Initialize Beeminder API
pyminder = Beeminder(ini_file=args.ini_filename)

# Use goalname as title if no title specified
goal_title = args.title if args.title else args.goalname

# Calculate the goal date (when the road ends) and final value
# Starting from today, add (days_per_step * num_steps) days
now = datetime.datetime.now()
# Set start to today at noon
start_date = datetime.datetime(now.year, now.month, now.day, 12, 0, 0)
goal_date = start_date + datetime.timedelta(days=args.days_per_step * args.num_steps)
goal_value = args.num_steps  # After M steps, we'll be at value M

if args.verbose:
    print(f"Creating goal: {args.goalname}")
    print(f"Title: {goal_title}")
    print(f"Start date: {start_date}")
    print(f"Goal date: {goal_date}")
    print(f"Final value: {goal_value}")
    print(f"Days per step: {args.days_per_step}")
    print(f"Number of steps: {args.num_steps}")
    print(f"Units: {args.units}")

# Build the roadall matrix for the stepped goal
# Format: [timestamp, value, rate] where 2 of 3 must be specified
# We'll use timestamp and value for each point, with rate set to 0 for flat segments
# and None for the jump points (let Beeminder calculate the rate)
roadall = []

# First segment: start at 0, flat rate
start_timestamp = int(start_date.timestamp())
roadall.append([start_timestamp, 0, 0])  # Start at 0 with flat rate

# Create each step
current_date = start_date
for step in range(1, args.num_steps + 1):
    # End of flat segment (just before the jump)
    current_date = current_date + datetime.timedelta(days=args.days_per_step)
    current_timestamp = int(current_date.timestamp())
    
    # Add a point at the jump: same date, but value increases by 1
    # Use None for rate to let Beeminder calculate it
    roadall.append([current_timestamp, step, 0])  # Jump to new value, then flat again

# Final point: goal date with final value and flat rate
goal_timestamp = int(goal_date.timestamp())
roadall.append([goal_timestamp, goal_value, 0])  # End flat

if args.verbose:
    print("\nRoadall matrix:")
    for idx, point in enumerate(roadall):
        point_date = datetime.datetime.fromtimestamp(point[0])
        print(f"  {idx}: {point_date.date()} - value: {point[1]}, rate: {point[2]}")

if args.dryrun:
    print("\nDRY RUN: Would create goal with the following parameters:")
    print(f"  slug: {args.goalname}")
    print(f"  title: {goal_title}")
    print(f"  goal_type: hustler (do more)")
    print(f"  goaldate: {goal_timestamp}")
    print(f"  goalval: {goal_value}")
    print(f"  rate: None (will be set by roadall)")
    print(f"  gunits: {args.units}")
    print(f"  roadall: {json.dumps(roadall)}")
    print("\nNote: After creation, you would need to update the roadall via a separate API call.")
else:
    # Create the goal
    # According to the API, we need slug, title, goal_type, and 2 of 3: goaldate, goalval, rate
    # For a "do more" goal, we use goal_type='hustler'
    
    print(f"Creating goal '{args.goalname}'...")
    
    try:
        # Create the basic goal first
        # We'll start with a simple road (goaldate, goalval, rate=0)
        values = {
            'auth_token': pyminder.auth_token,
            'slug': args.goalname,
            'title': goal_title,
            'goal_type': 'hustler',  # "do more" goal type
            'goaldate': goal_timestamp,
            'goalval': goal_value,
            'rate': None,  # Let it calculate from goaldate and goalval
            'gunits': args.units
        }
        
        # Create the goal
        result = pyminder._call(f'users/{pyminder.username}/goals.json', 
                               data=values, method='POST')
        
        if args.verbose:
            print(f"Goal created successfully!")
            print(f"Goal URL: https://beeminder.com/{pyminder.username}/{args.goalname}")
        
        # Now update the road to the stepped version
        print(f"Updating road to stepped pattern...")
        json_road = json.JSONEncoder().encode(roadall)
        pyminder.update_road(args.goalname, json_road)
        
        print(f"Success! Goal '{args.goalname}' created with {args.num_steps} steps of {args.days_per_step} days each.")
        print(f"View at: https://beeminder.com/{pyminder.username}/{args.goalname}")
        
        if args.verbose:
            print(f"\nReturned goal data:")
            print(f"  slug: {result.get('slug')}")
            print(f"  title: {result.get('title')}")
            print(f"  goal_type: {result.get('goal_type')}")
            print(f"  losedate: {datetime.datetime.fromtimestamp(result.get('losedate', 0))}")
            
    except Exception as e:
        print(f"Error creating goal: {e}")
        exit(1)
