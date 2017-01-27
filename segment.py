import sys
import re
import html

corrected = True
'''
Krista Watkins
570 Project
Training
Compares a d.txt file with the corresponding d.out file

Usage: python3 segment.py d.text d.out
Usage with script (to run on all training files): segment.sh training_directory > outputFile

Output:
    Line of info from d.out
    Corresponding Text
    #################
    Line of info from d.out
    Corresponding Text
    #################
    etc.

D.Text
- Store the lines of the text file in an array

D.Out information
- Collect places, ranks, and descriptions from d.out
- store the information line by place name

Descriptions
- Record the line number of each descriptive phrase
- Where the same phrase occurs more than once, choose the instance closest the the location of the other descriptive
    phrases for the place.

Places
- Search for the place name, starting at the first description line and working backwards
- Choose the first instance found

Ranks (if non-0)
- Search for line containing rank, starting at the place name, and working backwards

Locations are stored as {place:(rank_line, place_line, desc_start_line, desc_end_line)}
For a failed search, line number is -1
'''

# text and out file names provided on command line
text_file = open(sys.argv[1], "r")
out_file = open(sys.argv[2], "r")

# Lines in text files
text_lines = []  # String
corrected_text_lines = []
# ranks-- place : rank
ranks = {}    # String : String : int[]
# desc_locs-- place : description : [line numbers]
desc_locs = {}   # String : int()
# ranges-- place : (list of line numbers)
ranges = {}      # String : String
# annotation-- place : line of text
annotations = {}   # String : String

# Store all lines from the text file
for line in text_file:
    line = line.strip()

    text_lines.append(line)
    line = line.replace("&#8217;", "'")
    line = line.replace("&#160;", " ")
    corrected_text_lines.append(html.unescape(line))

# Get ranks and titles from the out file
for line_string in out_file:
    line = line_string.replace("\n", "")
    # If the line isn't empty
    if line.strip() != "":
        rank = int(re.split("[ \t]+", line.strip())[0])
        title = line[len(str(rank)):].split("##")[0].strip()
        descriptions = re.split("%% ?", line)[1].split(";")
        ranks[title] = rank

        # Set up place in dictionary. It contains an array
        desc_locs[title] = {}
        for desc in descriptions:
            desc_locs[title][desc] = []

        # Save annotation
        annotations[title] = line.strip()

# Find the locations of the descriptions in the file
for i in range(len(text_lines)):
    line = text_lines[i]
    corrected_line = corrected_text_lines[i]
    for place, description_dict in desc_locs.items():
        for description, line_numbers in description_dict.items():
            # If the description is in the line, store the line number
            if corrected_line.lower().find(description.strip().lower()) != -1:
                line_numbers.append(i)
            elif line.lower().find(description.strip().lower()) != -1:
                line_numbers.append(i)

# Find the range of line numbers for the descriptive phrases for each place
for place, description_dict in desc_locs.items():
    line_num_sum = 0
    descriptions_sum = 0   # Counts the number of descriptive phrases
    average_line_num = 0.0
    min_line = 10000
    max_line = 0

    for description, line_numbers in description_dict.items():
        # Calculate the average line numbers for descriptions only found once
        if len(line_numbers) == 1:
            line_num_sum += line_numbers[0]
            descriptions_sum += 1
            # Track min and max line numbers
            if line_numbers[0] < min_line:
                min_line = line_numbers[0]
            if line_numbers[0] > max_line:
                max_line = line_numbers[0]
    # Calculate average
    if descriptions_sum > 0:
        average_line_num = (line_num_sum + 0.0) / descriptions_sum

    # Disambiguate descriptions occuring more than once
    for description, line_numbers in description_dict.items():
        if len(line_numbers) > 1:
            # Find the line number closest to the average of the positions of the other descriptive phrases
            nearest_line = line_numbers[0]
            for line_num in line_numbers:
                if abs(line_num - average_line_num) < abs(nearest_line - average_line_num):
                    nearest_line = line_num
            # Retain only the nearest
            line_numbers = [nearest_line]
            # Update average
            descriptions_sum += 1
            line_num_sum += nearest_line
            average_line_num = (line_num_sum + 0.0) / descriptions_sum
            # Update min/max
            if nearest_line < min_line:
                min_line = nearest_line
            if nearest_line > max_line:
                max_line = nearest_line

    ranges[place] = (min_line, max_line)

# Find the line number of the location
for place, rank in ranks.items():
    this_place = place
    this_rank = rank
    desc_start = ranges[this_place][0]
    desc_end = ranges[this_place][1]

    # Check that the description range was altered from its default
    # Ones that weren't have formatting problems
    title_location = -1
    rank_location = -1
    if desc_end >= desc_start:

        # Search for the title of the attraction, working backward from location of the first description
        for n in reversed(range(desc_start+1)):
            # If the title is found, save the line number and break
            if corrected_text_lines[n].lower().find(this_place.strip().lower()) != -1:
                title_location = n
                break
            elif text_lines[n].lower().find(this_place.strip().lower()) != -1:
                title_location = n
                break
    # Reset the start and end to -1 since they're just defaults
    else:
        desc_start = -1
        desc_end = -1

    # Search for rank if title is known and rank exists
    if (title_location != -1 and desc_start != -1) and rank > 0:
        for n in reversed(range(title_location + 1)):
            if text_lines[n].find(str(this_rank)) != -1:
                rank_location = n
                break

    ranges[this_place] = (rank_location, title_location, desc_start, desc_end)

for place, locations in ranges.items():
    rank_loc = locations[0]
    place_loc = locations[1]
    desc_start_loc = locations[2]
    desc_end_loc = locations[3]

    if desc_start_loc != -1 and desc_end_loc != -1:
        min_loc = desc_start_loc
        if place_loc != -1 and place_loc < min_loc:
            min_loc = place_loc
        if rank_loc != -1 and rank_loc < min_loc:
            min_loc = rank_loc

        print(annotations[place])
        for x in range(min_loc, desc_end_loc + 1):
            if corrected:
                try:
                    #line = text_lines[x]
                    #line = html.unescape(text_lines[x])
                    print(corrected_text_lines[x].replace("\n", ""))
                except UnicodeEncodeError:
                    print(text_lines[x].replace("\n", ""))
            else:
                print(text_lines[x].replace("\n", ""))
        print("#####")





