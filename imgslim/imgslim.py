#!/usr/bin/env python

import os

def whoiam ():
    import pwd
    return pwd.getpwuid(os.getuid()).pw_name

def ios_simulator_directory ():
    return "/Users/{username}/Library/Application Support/iPhone Simulator/".format(username = whoiam())

def ios_find_app(dir):
    ents = os.listdir(dir)
    import stat
    for ent in ents:
        if ent.endswith(".app"):
            full = dir + "/" + ent + "/"
            st = os.stat(full)
            if stat.S_ISDIR(st[stat.ST_MODE]):
                return (ent[:-4], full)
    return None

def ios_version_selection ():
    dirs = os.listdir(ios_simulator_directory())
    blacks = [".DS_Store", "Library"]
    for each in blacks:
        try: dirs.remove(each)
        except: pass
    for i in range(len(dirs)):
        print "%d: " %i + dirs[i]
    selection = int(raw_input("select: "))
    if selection >= len(dirs):
        raise OverflowError
    return dirs[selection]

def ios_app_selection (ver):
    path = ios_simulator_directory() + ver + "/Applications/"
    dirs = os.listdir(path)
    apps = []
    sysapps = ["WebViewService", "StoreKitUIService", "Web", "MobileSafari", "WebContentAnalysisUI", "DDActionsService"]
    for dir in dirs:
        dir = path + dir
        app = ios_find_app(dir)
        if app and app[0] not in sysapps:
            apps.append(app)
    for i in range(len(apps)):
        print "%d: " %i + apps[i][0]
    selection = int(raw_input("select: "))
    if (selection >= len(apps)):
        raise OverflowError
    return apps[selection]

def ios_app_strings(binary):
    all = os.popen("strings '{path}'".format(path=binary)).read().split('\n')
    from collections import OrderedDict
    all = OrderedDict.fromkeys(all).keys()
    import re
    rex = re.compile(r"^[a-zA-Z0-9\\-\\._%]+$")
    rex_wild = re.compile(r"%[0-9]*[d]")
    wilds = []
    simples = []
    for each in all:
        if rex.match(each):
            if (rex_wild.search(each)):
                wilds.append(each)
            else:
                simples.append(each)
    return (set(simples), set(wilds))

def ios_wild_strings2regex(strs):
    rxs = []
    import re
    rx = re.compile(r"(%[0-9]*[d])")
    for each in strs:
        each = "^" + rx.sub('[0-9]+', each)
        print each
        rxs.append(re.compile(each))
    return rxs

def ios_img_fullmatch(fn, strs):
    return fn in strs

def ios_img_namematch(fn, strs):    
    str, ext = os.path.splitext(fn)
    if str.find("_highlight"):
        str = str.replace("_highlight", "")
    #print str
    if str in strs:
        return True
    if str.find("@") != -1:
        pstr = str[:str.find("@")]
        #print pstr
        if pstr in strs:
            return True
        pstr = pstr + ext
        #print pstr
        if pstr in strs:
            return True
    return False

def ios_img_used(res, strs, result=None):    
    print "used processing " + res
    if result is None: 
        result = {}
    for each in os.listdir(res):
        current = res + "/" + each
        if os.path.isdir(current):
            ios_img_used(current, strs, result)
        elif os.path.isfile(current):            
            if ios_img_fullmatch(each, strs) or ios_img_namematch(each, strs):
                result[each] = (current)
    return result

def ios_img_used_wild(res, strs, result=None):
    print "used wild processing " + res
    if result is None:
        result = {}
    for each in os.listdir(res):
        current = res + "/" + each
        if os.path.isdir(current):
            ios_img_used_wild(current, strs, result)
        elif os.path.isfile(current):
            for rx in strs:
                if rx.search(each):
                    result[each] = (current)
    return result

def ios_img_unused(res, useds, result=None):
    print "unused processing " + res
    if result is None:
        result = {}
    for each in os.listdir(res):
        current = res + "/" + each
        if (os.path.isdir(current)):
            ios_img_unused(current, useds, result)
        elif os.path.isfile(current):
            if each not in useds:
                result[each] = (current)
    return result

imgsexts = [".png", ".gif", ".jpg", ".bmp"]

if __name__ == "__main__":
    print "Imgslim for iOS app"
    print "select version:"
    ver = ios_version_selection()
    app = ios_app_selection(ver)
    strs = ios_app_strings(app[1] + app[0])
    import sys
    if len(sys.argv) > 1:
        resdir = sys.argv[2]
    else:
        resdir = os.getcwd()
    useds = ios_img_used(resdir, strs[0])
    ios_img_used_wild(resdir, ios_wild_strings2regex(strs[1]), useds)
    unuseds = ios_img_unused(resdir, useds)
    print """command:
    \t0, list used resources
    \t1, list unused resources
    \t2, dereference all unused images
    \t9, remove all unused images"""
    cmd = int(raw_input("command: "))
    if cmd == 0:
        bytesize = 0
        for k in useds:
            print k
            path = useds[k]
            st = os.stat(path)
            bytesize += st.st_size
        print "byte size : {bs} KB".format(bs=bytesize/1024)
    if cmd == 1:
        bytesize = 0
        for k in unuseds:
            print k
            path = unuseds[k]
            st = os.stat(path)
            bytesize += st.st_size
        print "byte size : {bs} KB".format(bs=bytesize/1024)
    if cmd == 2:
        prjpath = "/".join(resdir.split("/")[:-2]) + "/" + app[0] + ".xcodeproj/project.pbxproj"
        prjpath2 = prjpath + "~"
        f2 = open(prjpath2, 'w')
        with open(prjpath) as f:
            for line in f:
                found = False
                for k in unuseds:
                    str, ext = os.path.splitext(k)
                    if ext in imgsexts:
                        if line.find(k) != -1:
                            found = True
                            break
                if not found:
                    f2.write(line)
        f2.close()
        import shutil
        shutil.move(prjpath2, prjpath)
    if cmd == 9:
        ok = raw_input("confirm to remove all unused images? [y/n]")
        if ok == "y":
            for k in unuseds:
                str, ext = os.path.splitext(k)
                if ext in imgsexts:
                    path = unuseds[k]
                    print "removing " + path
                    os.unlink(path)
