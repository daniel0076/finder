#!/usr/bin/env python

import logging
import os
from os import path
import copy

import Config
import Includer
import Compiler

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    sourcePool = [
            Config.System.JAVA_POOL,
            Config.System.JAVA_GRAPHIC,
            Config.System.JAVA_TELECOMM ,
            Config.System.JAVA_TELEPHONY,
            Config.System.JAVA_MEDIA    ,
            Config.System.JAVA_LOCATION ,
        ]
    out = path.join(Config.Path.OUT, Config.System.VERSION, "java")
    if not os.path.exists(out):
        os.mkdir(out)

    files = Includer.absjoin(Config.Path.OUT, Config.System.VERSION, "Parcel_list")

    # load used creator files
    imports = set()
    with open(files, "r") as ffd:
        pkgs = ffd.read().split("\n")
    for pkg in pkgs:
        if  pkg.find(".") > 0:
            imports.add(pkg)

    # empty set
    solvedPkgs = set()
    while len(imports) > 0:
        logger.info("dependency: []".format(", ".join(imports)))
        toSolve = copy.copy(imports)

        for pkg in toSolve:
            solvedPkgs.add(pkg)
            imports.remove(pkg)

            # find built-in library but not find not solve
            if  pkg.split(".")[0] == "java":
                logger.info("builtin lib: {}".format(pkg))
                continue

            for source in sourcePool:
                file = Includer.pkg2path(source, pkg)
                if  os.path.isfile(file):
                    break
            else:
                logger.warn("Unknown file: {}".format(file))
                continue


            targetFile = path.join(out, path.relpath(file, source)).replace(".java", ".py")
            targetDir = path.dirname(targetFile)
            
            if  os.path.isfile(targetFile):
                continue

            logger.info("<<<NEW FILE>>> # {}".format(file))

            compiler = Compiler.Compiler()
            result = compiler.compilePackage(source, file)

            newDiscover = compiler.imports - solvedPkgs
            if  len(newDiscover) > 0:
                logger.info("new discover: {}".format(", ".join(newDiscover)))
                imports = imports.union(newDiscover)


            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
                
            with open(targetFile, "w") as targetFd:
                targetFd.write(result)

    for root, dirs, files in os.walk(out):
        init = path.join(root, "__init__.py")
        with open(init, 'w'):
            os.utime(init, None)
