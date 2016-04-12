#!/usr/bin/env python2.7
"""
Collect IInterface java source in android framework
move from ANDROID TO _IINTERFACE directory
"""

import Config
import logging
import fnmatch
import shutil
import os
import re

logger = logging.getLogger(__name__)

def fileWalker(travelPath, excludePattern, includePattern):

    includes = r'|'.join( [fnmatch.translate(x) for x in includePattern ])
    excludes = r'|'.join( [fnmatch.translate(x) for x in excludePattern ]) or r'$.'

    result = []
    for root, dirs, files in os.walk(travelPath ):
        dirs[:] = [d for d in dirs if not re.match(excludes, d)]    # filter excluded folders 
        dirs[:] = [os.path.join(root, d) for d in dirs]

        files = [ f for f in files if re.match(includes, f)] # filter satisfied file 
        files = [os.path.join(root, f) for f in files]

        result += files
    return result

def recursiveCopy(source, target, excludePattern, includePattern):
    for file in fileWalker(source, excludePattern, includePattern):
        if "*Native.java" in includePattern:
            with open(file, "r") as fd:
                buf = fd.read()
                if buf.find("descriptor") > 0:
                    t_file = file.split("/")[-1]
                    shutil.copyfile(file, os.path.join(target, t_file))
                    logger.info(" o {}".format(t_file))
        else:
            with open(file, "r") as fd:
                buf = fd.read()
                if re.search("extends (android.os.)?IInterface[^>]",buf) and (buf.find("descriptor") > 0 or buf.find("Stub") > 0):
                    t_file = file.split("/")[-1]
                    shutil.copyfile(file, os.path.join(target, t_file))
                    logger.info(" o {}".format(t_file))


if __name__ == '__main__':
    logging.basicConfig(level = logging.DEBUG)

    excludePattern = ['.git', 'vnc']

    framework = Config.System.FRAMEWORK
    aidl      = Config.System.AIDL_CACHE
    core      = Config.System.JAVA_POOL
    interface = Config.Path._IINTERFACE
    native    = Config.Path._NATIVE_STUB
    if not os.path.exists(interface):
        os.makedirs(interface)

    if not os.path.exists(native):
        os.makedirs(native)

    logger.info("Collecting system level interface: ")
    recursiveCopy(framework, interface, excludePattern, ["I*.java"])
                
    logger.info("Collecting AIDL interface: ")
    recursiveCopy(aidl, interface, excludePattern, ["*.java"])

    logger.info("Collecting Native interface: ")
    recursiveCopy(core, native, excludePattern, ["*Native.java"])
    

