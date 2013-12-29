# Copyright 2013 rsiddharth <rsiddharth@ninthfloor.org>
#
# This work is free. You can redistribute it and/or modify it under
# the terms of the Do What The Fuck You Want To Public License,
# Version 2, as published by Sam Hocevar. See the COPYING file or
# <http://www.wtfpl.net/> for more details.

import xmlrpclib as xmlrpc
from xmlrpclib import Fault

def update(table):
    """
    Generates wiki page using table and pushes it to the wiki using XML-RPC.
    """

    # Code below adapted from
    # http://moinmo.in/MoinAPI/Examples#xmlrpc.putPage.28.29

    name = raw_input("username> ")
    password = raw_input("pass> ")
    wikiurl = "http://localhost/m"
    homewiki = xmlrpc.ServerProxy(wikiurl + "?action=xmlrpc2",
                                  allow_none=True)
    auth_token = homewiki.getAuthToken(name, password)
    mc = xmlrpc.MultiCall(homewiki)
    mc.applyAuthToken(auth_token)
    pagename = "Documentation/3/DifferencesWithDebian"
    page_content = generate_wiki_page(table)
    mc.putPage(pagename, page_content)
    result = mc()

    try:
        sucess, raw = tuple(result)

        if sucess:
            print "Updated %s" % pagename
        else:
            print "Something went wrong. Please report this issue."

    except Fault:
        print "Nothing new. %s/%s was not updated" % (wikiurl,
                                                      pagename)

def generate_wiki_page(table):
    """
    Generates the wiki page using the table.

    `differences-with-debian.txt' file, used by this function,
    contains text that precedes the table.
    """

    page_content = open("src/differences-with-debian.txt", "r").read() + "\n"

    for row in table:
        page_content += row + "\n"

    return page_content
