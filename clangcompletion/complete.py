
import os
import subprocess
import re
import configuration

from xml.dom.minidom import parseString

re_package = re.compile ("package (?P<packagename>(\w+.)*\w+);")

def get_packages (origdoc):
    match = re_package.search (origdoc)
    if match != None:
        return match.group ("packagename")
    else:
        return None


def make_word (abbr, type):
    word = abbr
    if type != "":
        if type.find ('->') != -1:
            # function
            args = type.replace (" ->", ",").replace (" : ", ":")  
            last = args.rfind (",")
            returntype = args[last + 2:]
            args = args[:last]
            word += " (" + args + ") : " + returntype
        else:
            word += " : " + type
    return word


def get_program_output (fullpath, origdoc, offset):
    command = "clang -w -fsyntax-only -Xclang -code-completion-at=" + fullpath + ":" + offset + " " + fullpath
    proc = subprocess.Popen(command,
                        shell=True,
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        )
    out = proc.communicate()
    print command
    str = out[0]
    begin = str.find ("COMPLETION")
    if begin != -1:
        str = str[begin:]

    result = None
    try:
        if proc.returncode == 0:
            list=str.split("\n")
            result = []
            for item in list:
                dict = {}
                vals = item.split(": ")
                dict["abbr"] = vals[1].strip()
                if len(vals) > 1:
                    dict["type"] = vals[2]
                else:
                    dict["type"] = ""
                dict["word"] = make_word (dict["abbr"], dict["type"])
                result.append (dict)
        else:
            result = "Error : " + str
    except Exception, e:
        print e

    return result

def clang_complete (fileloc, origdoc, offset):
    package = get_packages (origdoc)
    fullpath = fileloc.replace ("file://", "")
    dirname = os.path.dirname (fullpath)
    filename = os.path.basename (fullpath)
    #FIXME: add a clever method for using makefiles! take a look at gccsense ;)
    return get_program_output (fullpath, origdoc, offset)

