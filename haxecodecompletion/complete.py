
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


def get_program_output (basedir, classname, fullpath, origdoc, offset, hxmlfile,package):
	#check for utf-8 with written BOM
    if ord(origdoc[0])>256:
        offset=offset+2
    os.rename (fullpath, fullpath + ".bak")
    file = open (fullpath, "w")
    file.write (origdoc)
    file.close ()
    if hxmlfile != None:
    	cls = classname
        if package != None:
            cls = package+"."+cls
        command = ["haxe", os.path.basename(hxmlfile), cls, "--display", "%s@%d" % (fullpath[len(basedir)+1:], offset)]
        #print ("haxe "+os.path.basename(hxmlfile)+" "+cls+" --display %s@%d" % (fullpath[len(basedir)+1:], offset))
    elif os.path.exists (basedir + "/compile.hxml"):
        command = ["haxe", basedir + "/compile.hxml", classname , "--display", "%s@%d" % (classname.replace (".", "/") + ".hx", offset)] 
    else:
        # TODO This should be parametrable
        command = ["haxe", "-swf-version", "9", "-swf", "/tmp/void.swf", classname, "--display" , "%s@%d" % (classname.replace (".", "/") + ".hx", offset)]

    proc = subprocess.Popen (command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=basedir)
    out = proc.communicate ()

    str = out[1]
    begin = str.find ("<list>")
    if begin != -1:
        str = str[begin:]

    already = set () # FIXME : haxe compiler outputs two times package names.
    result = None
    try:
        if proc.returncode == 0:
            xmldom = parseString (str)
            list = xmldom.getElementsByTagName ('i')
            result = []
            for item in list:
                dict = {}
                val = item.attributes["n"].value
                if val in already: continue # FIXME
                dict["abbr"] = val
                already.add (val) # FIXME
                dict["type"] = ""
                try:
                    dict["type"] = item.getElementsByTagName ('t')[0].childNodes[0].nodeValue
                except Exception, e:
                    # print e
                    pass
                dict["word"] = make_word (dict["abbr"], dict["type"])
                result.append (dict)
        else:
            result = []
            result.append({"word":"Error: "+str})
            print str
    except Exception, e:
        print e
        print str

    os.rename (fullpath + ".bak", fullpath)

    return result

def haxe_complete (fileloc, origdoc, offset):
    package = get_packages (origdoc)
    complete_path = fileloc.replace ("file://", "")
    dirname = os.path.dirname (complete_path)
    filename = os.path.basename (complete_path)
	
    classname = filename[:-3]
    
    hxmlfile = configuration.getHxmlFile()
    if hxmlfile !=None:
    	dirname = os.path.dirname(hxmlfile)

    basedir = dirname # by default
    if package != None:
        if dirname.endswith (package.replace (".", "/")):
            basedir = dirname[:-len(package.replace (".", "/"))] 
            classname = package + '.' + classname

    return get_program_output (basedir, classname, complete_path, origdoc, offset, hxmlfile,package)

