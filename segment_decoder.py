import sys
import re
import numpy
import nltk

from nltk.tokenize import texttiling
from nltk.chunk import named_entity

print("-annot")

# Save the file as one string
# Input: File location string
# Output: String containing file text
country = sys.argv[1].split("/")[-3].split("-")[0]

def prepare_file(file_name):
    file = open(file_name, "r")

    file_lines = []
    for line in file:
        file_lines.append(line)

    return file_lines

# Finds Ranks at the beginnings of lines, in ascending order
def find_ranks(file_lines):
    r = 1
    rank_rx = re.compile("^\s*" + str(r) + "[). ]")

    rank_locations = []

    for i in range(0, len(file_lines)):
        line = file_lines[i]
        match = rank_rx.search(line)
        if match:
            # Save the location of the rank
            rank_locations.append(i)
            # Change the regex- add one to the rank
            r += 1
            last_char = match.group(0)[-1:]
            rank_rx = re.compile("^\s*" + str(r) + "[" + last_char + "]")

    return rank_locations

# Finds Ranks at the beginnings of lines, in ascending order
def find_reversed_ranks(file_lines):
    r = 1
    rank_rx = re.compile("^\s*" + str(r) + "[). ]")

    rank_locations = []

    # Start search for rank 1 and end of file
    for i in reversed(range(0, len(file_lines))):
        line = file_lines[i]
        match = rank_rx.search(line)
        if match:
            # Save the location of the rank
            rank_locations.append(i)
            # Change the regex- add one to the rank
            r += 1
            last_char = match.group(0)[-1:]
            rank_rx = re.compile("^\s*" + str(r) + "[" + last_char + "]")

    return list(reversed(rank_locations))

# Extracts named entities from a string of text (paragraph)
# Input: Text string
# Output: Array of tuples (TAG, n-gram)
def extract_named_entities(text):
    named_entities = []
    sentence_lengths = []
    # Separate into sentences
    sent = nltk.sent_tokenize(text)

    # Get sentence Lengths
    for s in sent:
        sentence_lengths.append(len(s))

    sent = [nltk.word_tokenize(s) for s in sent]
    sent = [nltk.pos_tag(s) for s in sent]

    for s in sent:
        output = nltk.ne_chunk(s)
        for o in output:
            if len(o) == 1:
                label = o.label()
                n_gram = o[0][0]

                named_entities.append((label, n_gram))

    return named_entities, sentence_lengths

# Look for start of "Comments" section
def comments_start(start_line, text):
    comment_loc = len(text)-1
    for i in range(start_line + 1, len(text)):
        if re.search("Comment|facebook|twitter|reply|post|tweet", text[i], re.IGNORECASE):
            comment_loc = i
            break

    return comment_loc

def chunk_printer(text, index_pairs, ranks):
    location = "x"
    for i in range(0,len(index_pairs)):

        start = index_pairs[i][0]
        end = index_pairs[i][1]+1
        output = "".join(text[start:end])

        # Find location name
        #check line of rank
        rank_line_words = text[start].split()
        if len(rank_line_words) > 1 and len(rank_line_words) < 10:
            location = re.sub(str(ranks[i]) + "[ .)]*", "", text[start], 1)
            location = location.strip()

        # Use regex to find Capitalized String
        capitalized = re.search("([A-Z][a-z]*)( [A-Z][a-z]*)+", output[0:min(100, len(output))])
        if capitalized:
            if len(capitalized.group().split()) > 1:
                location = capitalized.group()

            # First Named entity in text
            else:
                names, sentence_lens = extract_named_entities(output)
                if len(names) > 0:
                    if len(names[0]) > 1:
                        location = names[0][1]
                    else:
                        location = names[0][0]
                else:
                    location = country

        # First Named entity in text
        else:
            names, sentence_lens = extract_named_entities(output)
            if len(names) > 0:
                if len(names[0]) > 1:
                    location = names[0][1]
                else:
                    location = names[0][0]
            else:
                location = country

        # If the chunk seems too short, add a line to it at a time
        while len(output) < 100 and end < len(text):
            output += text[end]
            end += 1

        sys.stderr.write("Printing " + str(ranks[i]) + "...\n")
        # Print Header
        print(ranks[i], location)
        # Print text
        print(output)

        # Print footer
        print("#####")

def unranked_chunk_printer(chunk):
    location = ""
    # Use regex to find Capitalized String in head of text
    capitalized = re.search("([A-Z][a-z]*)( [A-Z][a-z]*)+", chunk[0:min(100, len(chunk))])
    if capitalized:
        if len(capitalized.group().split()) > 1:
            location = capitalized.group()

        # First Named entity in text
        else:
            names, sentence_lens = extract_named_entities(chunk)
            if len(names) > 0:
                if len(names[0]) > 1:
                    location = names[0][1]
                else:
                    location = names[0][0]
            else:
                location = country

    # First Named entity in text
    else:
        names, sentence_lens = extract_named_entities(chunk)
        if len(names) > 0:
            if len(names[0]) > 1:
                location = names[0][1]
            else:
                location = names[0][0]
        else:
            location = country

    # Print header
    print(0, location)
    # Print text
    print(chunk)
    # Print footer
    print("#####")


# Divide the file into segments by paragraph
# Input: String containing file
# Output: Array of paragraphs
#   or empty array if segmentation fails
def segment_paragraphs(file_string):
    try:
        tiler = texttiling.TextTilingTokenizer()
        return tiler.tokenize(file_string)
    except Exception:
        return []

# Represent text as string of long and short paragraphs
def paragraph_length_code(paragraphs, shortest_paragraph):
    code = ""
    for p in paragraphs:
        if len(p.split()) < shortest_paragraph:
            code += "s"
        else:
            code += "l"
    return code

def run_this():
    # Paragraph start, end indices
    paragraphs_indicies = []

    file_title = sys.argv[1].split("/")[-1]
    sys.stderr.write("Reading "+ country + " " + file_title+ ":...\n")
    text = prepare_file(sys.argv[1])

    rank_locations = find_ranks(text)

    # Split on Rank
    if len(rank_locations) > 2:
        sys.stderr.write("Ranks Found\n")
        # All but the last location
        for i in range(0, len(rank_locations) - 1):
            paragraphs_indicies.append((rank_locations[i], rank_locations[i+1]-1))

        # For last paragraph, cut off "comments" section
        last_location = rank_locations[-1]

        paragraphs_indicies.append((last_location, comments_start(last_location, text)-1))

        chunk_printer(text, paragraphs_indicies, list(range(1,len(rank_locations)+1)))

    # Search for reversed Rank
    else:
        rev_rank_locations = find_reversed_ranks(text)
        # Reversed Ranks Found
        if len(rev_rank_locations) > 2:
            sys.stderr.write("Ranks Found\n")
            # All but the last location
            for i in range(0, len(rev_rank_locations) - 1):
                paragraphs_indicies.append((rev_rank_locations[i], rev_rank_locations[i+1]-1))

            # For last paragraph, cut off "comments" section
            last_location = rank_locations[-1]
            paragraphs_indicies.append((last_location, comments_start(last_location, text)-1))

            chunk_printer(text, paragraphs_indicies, list(reversed(range(1,len(rev_rank_locations)+1))))

        # No rank found in either direction
        # Try texttiling
        else:
            sys.stderr.write("TextTiling Attempt...\n")
            whole_text = "".join(text)
            tiled = segment_paragraphs(whole_text)

            if len(tiled) > 2:
                end = len(tiled)
                # Check if the last section's non-attraction related
                if re.search("comment|facebook|post", tiled[-1], re.IGNORECASE):
                    end -= 1
                    # If there are many sections, check the second-to-last paragraph too
                    if len(tiled) > 6 and re.search("comment|facebook|post", tiled[-2], re.IGNORECASE):
                        end -= 1

                # Skip the first chunk. Usually website navigation
                for i in range(1,end):
                    unranked_chunk_printer(tiled[i])

            # Split based on paragraph length
            else:
                sys.stderr.write("Split by Regex...\n")
                split_on_single_n = False
                p = re.split("^\s$", whole_text, re.MULTILINE)
                # Split on one newline instead
                if len(p) < 3:
                    p = re.split("\n+", whole_text, re.MULTILINE)
                    split_on_single_n = True

                length_code = paragraph_length_code(p, 4)

                sl_matches = re.finditer("sl+", length_code)
                if sl_matches:
                    if len(list(sl_matches)) >=3:
                        for match in sl_matches:
                            p_text = "".join(p[match.start():match.end()])
                            unranked_chunk_printer(p_text)
                            exit(0)

                l_match = re.search("l+", whole_text)
                if (l_match):
                    p_text = "".join(p[l_match.start():l_match.end()])
                    unranked_chunk_printer(p_text)
                    exit(0)

                # If all else fails, just treat the whole file as an attraction
                unranked_chunk_printer(whole_text)

run_this()
