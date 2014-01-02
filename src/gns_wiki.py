# Copyright 2013 rsiddharth <rsiddharth@ninthfloor.org>
#
# This work is free. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License,
# Version 2, as published by Sam Hocevar. See the COPYING file or
# <http://www.wtfpl.net/> for more details.

import xmlrpclib as xmlrpc
from xmlrpclib import Fault
import filecmp
import os.path as path

def get_topsecret(src_dir):
    """
    Returns the username, password & wikiurl

    They are stored in src/config/ directory in the topsecret.txt
    file.
    """

    secrets = open(path.join(src_dir,
                             "config",
                             "topsecret.txt"), "r").readlines()

    username = secrets[0].strip()
    password = secrets[1].strip()
    wikiurl  = secrets[2].strip()

    return username, password, wikiurl

def update(table, src_dir):
    """
    Generates wiki page using table and pushes it to the wiki using XML-RPC.
    """

    # Code below adapted from
    # http://moinmo.in/MoinAPI/Examples#xmlrpc.putPage.28.29

    name, password, wikiurl = get_topsecret(src_dir)
    homewiki = xmlrpc.ServerProxy(wikiurl + "?action=xmlrpc2",
                                  allow_none=True)
    auth_token = homewiki.getAuthToken(name, password)
    mc = xmlrpc.MultiCall(homewiki)
    mc.applyAuthToken(auth_token)
    pagename = "Documentation/3/DifferencesWithDebian"
    wiki_page_content, update = generate_wiki_page(table, src_dir)

    if(update):
        # Send the updated wiki page to moin wiki:
        mc.putPage(pagename, wiki_page_content)
        result = mc()

        try:
            success, raw = tuple(result)

            if success:
                print "Updated %s" % pagename
            else:
                print "Something went wrong. Please report this issue."

        except Fault, e:
            print e
    else:
        print "Nothing new! %s/%s was not updated" % (wikiurl,
                                                     pagename)

def generate_wiki_page(table, src_dir):
    """
    Generates the wiki page using the table.

    `differences-with-debian-head.txt' file, used by this function,
    contains text that precedes the table.
    """

    # generate wikipage
    diff_with_deb_head = path.join(src_dir,
                                   "wiki-files",
                                   "differences-with-debian-head.txt")
    wiki_page_content = open(diff_with_deb_head, "r").read() + "\n"

    for row in table:
        wiki_page_content += row + "\n"

    update = wiki_page_updated(wiki_page_content, src_dir)

    return wiki_page_content, update


def wiki_page_updated(wiki_page_content, src_dir):
    """
    Returns True if the wiki page is updated
    """

    # write wikipage to temp file
    temp_file = open("/tmp/diff-with-deb-tmp.txt", "w")
    temp_file.write(wiki_page_content)
    temp_file.close()

    # this file contains the wiki page last generated by the script.
    diff_with_deb = path.join(src_dir,
                              "wiki-files",
                              "differences-with-debian.txt")

    # first check if the file exists
    if(path.isfile(diff_with_deb)):
        # filecmp.cmp returns True if both the file are same.
        update = (filecmp.cmp(temp_file.name,
                              diff_with_deb, 1) == False)
    else:
        # This is the first time the page is generated,
        # so update the wiki.
        update = True

    if(update):
        update_wiki_page_locally(wiki_page_content, diff_with_deb)

    return update


def update_wiki_page_locally(wiki_page_content, filename):
    """
    Writes the wiki page locally to `filename'
    """

    wiki_file = open(filename, "w")
    wiki_file.write(wiki_page_content)
    wiki_file.close()

