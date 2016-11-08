#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Extracts email addresses from one or more plain text files.
#
# Notes:
# - Does not save to file (pipe the output to a file if you want it saved).
# - Does not check for duplicates (which can easily be done in the terminal).
#
# (c) 2013  Dennis Ideler <ideler.dennis@gmail.com>

import re
import csv
# import ipdb as pdb
regex = re.compile(("([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`"
                    "{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|"
                    "\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)"))


def file_to_str(filename):
    """Returns the contents of filename as a string."""
    with open(filename) as f:
        # Case is lowered to prevent regex mismatches.
        return f.read().lower()


def get_emails(s):
    """Returns an iterator of matched emails found in string s."""
    # Removing lines that start with '//' because the regular expression
    # mistakenly matches patterns like 'http://foo@bar.com' as '//foo@bar.com'.
    return (email[0]
            for email in re.findall(regex, s)
            if not email[0].startswith('//'))

if __name__ == '__main__':
    # pdb.set_trace()
    input_file_name = 'stackoverflow-users.csv'
    output_file_name = 'stackoverflow-users-email.csv'
    with open(input_file_name) as csvfile:
        stack_user_reader = csv.reader(csvfile, delimiter=',')
        with open(output_file_name, 'w') as csvoutput:
            writer = csv.writer(csvoutput,
                                lineterminator='\n',
                                delimiter=',')
            for row in stack_user_reader:
                for email in get_emails(str(row[7])):
                    row.append(email)
                writer.writerow(row)
    print("Arquivo {0} gerado com sucesso!".format(output_file_name))
