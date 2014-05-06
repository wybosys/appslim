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
    tmp = []
    import re
    rex = re.compile(r"^[a-zA-Z0-9\\-\\._]+$")
    for each in all:
        if rex.match(each):
            tmp.append(each)
    all = tmp
    print all

if __name__ == "__main__":
    print "Imgslim for iOS app"
    print "select version:"
    ver = ios_version_selection()
    app = ios_app_selection(ver)
    strs = ios_app_strings(app[1] + app[0])
