# (c) 2012, Zettar Inc.
# Written by Chin Fang <fangchin@zettar.com>
#
# This file is part of Ansible
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#

'''
This module is for enhancing ansible's inventory parsing capability such
that it can deal with hostnames specified using a simple pattern in the
form of [beg:end], example: [1:5] where if beg is not specified, it
defaults to 0.

If beg is given and is left-zero-padded, e.g. '001', it is taken as a
formatting hint when the range is expanded. e.g. [001:010] is to be
expanded into 001, 002 ...009, 010.

Note that when beg is specified with left zero padding, then the length of
end must be the same as that of beg, else a exception is raised.
'''

from ansible import errors

def expand_hostname_range(line):
    '''
    A helper function that expands a given line that contains a pattern
    specified in top docstring, and returns a list that consists of the
    expanded version.

    The '[' and ']' characters are used to maintain the pseudo-code
    appearance. They are replaced in this function with '|' to ease
    string splitting.

    References: http://ansible.github.com/patterns.html#hosts-and-groups
    '''

    # A hostname such as db[1:6]-node is considered to consists
    # three parts:
    # head: 'db'
    # nrange: [1:6]; range() is a built-in. Can't use the name
    # tail: '-node'

    start_group = line.find("[")
    separator = line.find(":")
    if separator == -1:
        separator = line.find("-")
    end_group = line.find("]")
    if not (start_group != -1 and end_group != -1 and separator != -1 and
            start_group < separator < end_group):
        return [line]

    head = line[:start_group]
    beg = line[start_group + 1:separator]
    end = line[separator + 1:end_group]
    tail = line[end_group + 1:]
    if not beg:
        beg = "0"
    if not end:
        raise errors.AnsibleError("host range end value missing")
    if beg[0] == '0' and len(beg) > 1:
        rlen = len(beg) # range length formatting hint
    else:
        rlen = None
    if rlen > 1 and rlen != len(end):
        raise errors.AnsibleError("host range format incorrectly specified!")

    all_hosts = []
    for _ in range(int(beg), int(end)+1):
        if rlen:
            rseq = str(_).zfill(rlen) # range sequence
        else:
            rseq = str(_)
        hname = ''.join((head, rseq, tail))
        all_hosts.append(hname)

    return all_hosts
