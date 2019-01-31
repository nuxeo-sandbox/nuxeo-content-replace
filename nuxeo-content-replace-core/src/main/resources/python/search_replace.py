#
# This file is part of the LibreOffice project.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# This file incorporates work covered by the following license notice:
#
#   Licensed to the Apache Software Foundation (ASF) under one or more
#   contributor license agreements. See the NOTICE file distributed
#   with this work for additional information regarding copyright
#   ownership. The ASF licenses this file to you under the Apache
#   License, Version 2.0 (the "License"); you may not use this file
#   except in compliance with the License. You may obtain a copy of
#   the License at http://www.apache.org/licenses/LICENSE-2.0 .
#

import getopt, sys, uno

from unohelper import Base, systemPathToFileUrl, absolutize
from os import getcwd
from com.sun.star.beans import PropertyValue
from com.sun.star.beans.PropertyState import DIRECT_VALUE
from com.sun.star.uno import Exception as UnoException
from com.sun.star.io import IOException, XInputStream


def main():
    retVal = 0
    doc = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hc:o:f:s:r:x:", [
                                   "help", "connection-string="])
        url = "uno:socket,host=localhost,port=2004;urp;StarOffice.ComponentContext"
        outputPath = "/tmp/"
        search = ""
        replace = "*"
        regex = False
        for o, a in opts:
            if o in ("-h", "--help"):
                usage()
                sys.exit()
            elif o in ("-c", "--connection-string"):
                url = "uno:" + a + ";urp;StarOffice.ComponentContext"
            elif o == "-o":
                outputPath = a
            elif o == "-s":
                search = a
            elif o == "-r":
                replace = a
            elif o == "-x":
                regex = a == "true"

        if not len(args):
            usage()
            sys.exit()

        ctxLocal = uno.getComponentContext()
        smgrLocal = ctxLocal.ServiceManager

        resolver = smgrLocal.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", ctxLocal)
        ctx = resolver.resolve(url)
        smgr = ctx.ServiceManager

        desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx)

        cwd = systemPathToFileUrl(getcwd())
        inProps = PropertyValue("Hidden", 0, True, 0),
        for path in args:
            try:
                outputFile = outputPath
                fileUrl = uno.absolutize(cwd, systemPathToFileUrl(path))
                outputUrl = uno.absolutize(
                    cwd, systemPathToFileUrl(outputFile))
                doc = desktop.loadComponentFromURL(
                    fileUrl, "_blank", 0, inProps)

                if not doc:
                    raise UnoException(
                        "Could not open stream for unknown reason", None)

                srd = doc.createReplaceDescriptor()
                srd.setPropertyValue("SearchRegularExpression", regex)
                srd.setSearchString(search)
                srd.setReplaceString(replace)

                doc.replaceAll(srd)
                doc.storeToURL(outputUrl, ())
            except IOException as e:
                sys.stderr.write(
                    "Error during conversion: " + e.Message + "\n")
                retVal = 1
            except UnoException as e:
                sys.stderr.write(
                    "Error (" + repr(e.__class__) + ") during conversion: " + e.Message + "\n")
                retVal = 1
            if doc:
                doc.dispose()

    except UnoException as e:
        sys.stderr.write(
            "Error (" + repr(e.__class__) + "): " + e.Message + "\n")
        retVal = 1
    except getopt.GetoptError as e:
        sys.stderr.write(str(e) + "\n")
        usage()
        retVal = 1

    sys.exit(retVal)


def usage():
    sys.stderr.write("usage: search_replace.py --help |" +
                     " [-c <connection-string> | --connection-string=<connection-string>]" +
                     " -s <search> -r <replace> -x <regex:true|false>" +
                     " -o <outputDir> <input...>\n"
                     )


main()
