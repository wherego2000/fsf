#!/usr/bin/env python
#
# Author: Jamie Ford
# Description: Parses mach-o files using the Macholibre library by Aaron Stevens
# Returns various metadata about the file
# Date: 09/08/2016
'''
   Copyright 2016 BroEZ

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
'''
import sys
from macholibre import macholibre
from StringIO import StringIO
import os
from tempfile import mkstemp

def META_MACHO(s, buff):
    tmpfd, tmpfile = mkstemp()
    tmpf = os.fdopen(tmpfd, 'wb')

    try:
        #Writing the buffer to a temp file
        tmpf.write(buff)
        tmpf.close()
        dictionary = macholibre.parse(tmpfile)
    finally:
        #Remove it to save space
        os.remove(tmpfile)

    if dictionary.has_key('name'):
        #The name doesn't make sense with the temp file
        dictionary.pop('name')

    # META_BASIC_INFO already hs this informaton
    if dictionary.has_key('hashes'):
        dictionary.pop('hashes')
    if dictionary.has_key('size'):
        dictionary.pop('size')

    #Macholibre either has macho or universal
    if dictionary.has_key('macho'):
        popMachoKeys(dictionary['macho'])
        dictionary['Universal'] = False
        dictionary['machos'] = [dictionary.pop('macho')]

    elif dictionary.has_key('universal'):
        #Universal has embedded machos
        if dictionary['universal'].has_key('machos'):
            dictionary['Universal'] = True
            dictionary['machos'] = []
            for macho in dictionary['universal']['machos']:
                popMachoKeys(macho)
                dictionary['machos'].append(macho)
            dictionary.pop('universal')



    return dictionary

def popMachoKeys(macho):
    #Keys to keep to prevent too much printout
    keepKeys = ['filetype', 'signature', 'flags', 'offset', 'cputype', 'minos', 'size', 'dylibs', 'subtype']
    for key in macho.keys():
        if (key not in keepKeys):
            macho.pop(key)


if __name__ == '__main__':
    print(META_MACHO(None, sys.stdin.read()))
