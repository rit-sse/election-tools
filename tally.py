"""
tally.py - Tallies winners for each election position.

USAGE:

python tally.py votes.csv

Where votes.csv is exported from Qualtrics.

Written for Python 3.6
"""

import sys
import csv
import os
import re

def parse_positions(header1, header2):
    """
    Parse the positions people are running for, given the first two CSV rows
    (both rows are headers)
    Args:
        header1 - iterable of str, csv headers
        header2 - iterable of str, csv headers
    Returns:
        (positions, col_map, order_indices, default_order), where:
            positions: a dict mapping position name to a list of candidates
            col_map: a list of (col_index, position, name) indicating who this
                column is recording a vote for
            order_indices: list of (col_index, position) which contains the
                voting record's unique initial ordering for `position` is found
                in column number `col_index`
            default_order: a dict mapping position name to list of candidate
                names, indicating default sorting order for that candidate
    """
    # From observation:
    # 1. Generally the multi-choice questions are
    #    numbered here as QN_M, where N is the question number (i.e., President)
    #    and M is the candidate number (i.e., Robin Williams).
    # 2. The sub-headings in `heading2` seem to be formatted as
    #    {Position} - {Name}
    # 3. The column which contains the initial ordering appears in `heading1` as
    #    QN_DO, where N is the question number. In `heading2` this appears as
    #    {Position} - Display Order

    positions = {}
    col_map = []
    order_indices = []
    default_order = {}

    # Iterate through both headers side-by-side
    for index, (h1, h2) in enumerate(zip(header1, header2)):
        if re.match(r'Q\d+_\d+', h1):
            # This seems like a heading for a candidate.
            # Extract their name and position.
            mat = re.match(r'(.+) - (.+)', h2)
            position = mat.group(1)
            name = mat.group(2)
            # Append their data to our running log
            if position not in positions:
                positions[position] = []
            positions[position].append(name)
            col_map.append((index, position, name))
            if position not in default_order:
                default_order[position] = []
            default_order[position].append(name)
        elif re.match(r'Q\d+_DO', h1):
            # This seems like a heading for the display order.
            # Extract the position it's referencing and store it.
            mat = re.match(r'(.+) - Display Order', h2)
            position = mat.group(1)
            order_indices.append((index, position))

    return (positions, col_map, order_indices, default_order)


def parse_vote_row(row, col_map, order_indices, default_order):
    """
    Parses a single vote
    Args:
        row: iterable of str, csv row
        col_map: a list of (col_index, position, name) indicating who this
            column is recording a vote for
        order_indices: list of (col_index, position) which contains the
                voting record's unique initial ordering for `position` is found
                in column number `col_index`
        default_order: a dict mapping position name to list of candidate
                names, indicating default sorting order for that candidate
    Returns:
        dict mapping position to a list of names, from most preferred to least
    """
    # NOTE: The software does not record votes if you haven't reordered
    # the ranking. So, we need to set a default ranking based on the voter's
    # default displayed order, and override it with whatever custom order they
    # may have made.

    # A dict mapping position name to list of (rank, name) tuples indicating
    # what rank-preference the voter has for that person.
    tmp_votes = {}
    
    # Fill 'tmp_votes' with the default ordering
    for position, candidate_order in default_order.items():
        tmp_votes[position] = list(enumerate(candidate_order, 1))

    # Fill `tmp_votes` with default values according to this voter's shuffle.
    for col_index, position in order_indices:
        # The contents of this column are pipe-delimeted, needs to be split
        initial_order_str = row[col_index]
        # A list of candidate names
        initial_order = initial_order_str.split('|')
        # A list of (rank, name), where rank is 1-indexed
        initial_order_indexed = list(enumerate(initial_order, 1))
        tmp_votes[position] = initial_order_indexed
    
    # Iterate through this voter's custom choices, adjusting `tmp_votes`
    for col_index, position, name in col_map:
        vote = row[col_index]
        vote = vote.strip()
        if vote:
            vote = int(vote)
            # We need to look-up the index of this name and update it
            idx = [n for _, n in tmp_votes[position]].index(name)
            tmp_votes[position][idx] = (vote, name)
        else:
            # no vote was recorded for this candidate, keep default
            pass
    
    # Construct the final vote mapping by sorting and removing the vote rank
    ret = {}
    for position, indexed_rankings in tmp_votes.items():
        # sort based on their prefered rank, ascending (least first)
        sorted_rankings = sorted(indexed_rankings, key=lambda x: x[0])
        unindexed_rankings = [name for _, name in sorted_rankings]
        ret[position] = unindexed_rankings

    return ret


def parse_votes(fname):
    """
    Reads the given file name to parse running officers and votes.
    Args:
        fname - the file name of the voting results
    Returns:
        (positions, votes) where:
            positions: a dict mapping position name to a list of candidates
            votes: a list of everyone's ranked votes, as a dict mapping from
                   position to a list of names, from most prefered to least
    """
    with open(fname, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        # Read headings to get officer names
        header1 = next(reader)
        header2 = next(reader)
        positions, col_map, order_indices, default_order = parse_positions(header1, header2)
        # Throw out the third sub-heading
        next(reader)
        # Parse the remainder of the votes
        votes = []
        for row in reader:
            votes.append(parse_vote_row(row, col_map, order_indices, default_order))
        return (positions, votes)


def perform_stv(positions, votes):
    """
    Performs Single Transferrable Vote algorithm on the given vote records for
    all candidates.
    Args:
        positions: a dict mapping position name to a list of candidates
        votes: a list of everyone's ranked votes, as a dict mapping from
                position to a list of names, from most prefered to least
    Returns:
        [(position, winner_name)]
    """
    results = []
    # Perform STV candidate-by-candidate
    for position, candidates in positions.items():
        while len(candidates) > 1:
            print('Starting round for', position)
            # Count how many first-preference votes each candidate has collected
            # Start the count at zero.
            vote_count = dict(((candidate, 0) for candidate in candidates))
            for vote in votes:
                try:
                    preferred_candidate = vote[position][0]
                except KeyError as e:
                    print('hmm', position, vote)
                    raise e
                vote_count[preferred_candidate] += 1
            # Figure out who has the least votes
            vote_count_lst = list(vote_count.items())
            # Find least favored by sorting by the number of votes, ascending
            least_favored = sorted(vote_count_lst, key=lambda x: x[1])[0][0]
            # Eliminate the least favored candidate from everyone's votes
            for vote in votes:
                vote[position].remove(least_favored)
            candidates.remove(least_favored)
        # A winner has been selected
        results.append((position, candidates[0]))
    return results


def main():
    # Ensure that the file name was specified
    if len(sys.argv) != 2:
        print('Please supply a CSV file name', file=sys.stderr)
        exit(1)

    # The CSV file name
    fname = sys.argv[1]

    # Ensure that the file name exists
    if not os.path.isfile(fname):
        print('File not found: `{0}`'.format(fname), file=sys.stderr)
        exit(1)
    
    (positions, votes) = parse_votes(fname)
    print(perform_stv(positions, votes))


if __name__ == '__main__':
    main()
