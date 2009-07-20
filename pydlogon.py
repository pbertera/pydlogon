#!/usr/bin/python
# vi:si:et:sw=4:sts=4:ts=4
# -*- coding: UTF-8 -*-
# -*- Mode: Python -*-
#
# Copyright (C) 2006 Bertera Pietro <pietro@bertera.it>

# This file may be distributed and/or modified under the terms of
# the GNU General Public License version 2 as published by
# the Free Software Foundation.
# This file is distributed without any warranty; without even the implied
# warranty of merchantability or fitness for a particular purpose.

import optparse, sys, logging, os

from parser import ParseMatchError, ParseMatch
from base import MatchError, ActionError


# Execution
if __name__ == '__main__':
    
    class MakeLogonOptionParser (optparse.OptionParser):
        def check_required (self, opt):
            option = self.get_option(opt)
            if getattr(self.values, option.dest) is None:
                self.error("%s option not supplied" % option)
   
    parser = MakeLogonOptionParser("usage: %prog [options]")
    parser.add_option('-U', '--session-user', type="string", help="session username (%U samba var)")
    parser.add_option('-u', '--user', type="string", help="username of the current service (%u samba var)")
    parser.add_option('-G', '--session-group', type="string", help="primary group of %U (%G samba var)")
    parser.add_option('-g', '--group', type="string", help="primary group name of %u (%g samba var)")
    parser.add_option('-m', '--machine', type="string", help="the NetBIOS name of the client machine (%m samba var)")
    parser.add_option('-I', '--client-address', type="string", help="the NetBIOS name of the client machine (%m samba var)")
    parser.add_option('-a', '--arch', type="string", help="the  architecture  of  the remote machine (%a samba var)")
    parser.add_option('-l', '--log', type="string", help="log file")
    parser.add_option('-d', '--debug', action="store_true", default=False, help="enable debugging")
    parser.add_option('-o', '--out-script', type="string", help="file to create with logon script")
    parser.add_option('-c', '--config', type="string", help="config file")
    
    (options,args)=parser.parse_args()

    #Loggind end debugging code

    if options.log != None:
        logfile = options.log
    else:
        logfile = ''

    debug = options.debug

    logger = logging.getLogger('pydlogon')

    if logfile:
        hdlr = logging.FileHandler(logfile)
    else:
        hdlr = logging.StreamHandler()

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)

    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    
    logger.info("options: %s" % " ".join([str(d) for d in sys.argv[1:]]))
    
    try:
        parser.check_required('-o')    
        parser.check_required('-c')    

    except Exception, e:
        logger.error("%s") % e
        sys.exit(-1)

    if not os.path.isfile(options.config):
        logger.error("File %s not exist" % options.config)
        sys.exit(-1)

    logger.info("Loading configuration.")
    match = ParseMatch(options)
    try:
        match.load()
        bind_list = match.bind_list

        for bind in bind_list:
            logger.debug('Checking bind statement: \'%s\' with action \'%s\'' %
                    (bind, bind.action))
    
            if bind.check(options):
                    logger.info('Bind statement %s matched all Match\'s' % bind)
                    logger.info("Action: %s" % bind.action)
                    bind.action.run_actions()
            else: 
                logger.debug('Bind statement %s did not match all acls' % bind)

    except (ParseMatchError, MatchError, ActionError), err:
        logger.error(str(err))
        sys.exit(1)

    sys.exit(-1)

