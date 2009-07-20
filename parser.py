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

import re, logging, grp, os
from IPy import IP
from base import MatchError, ActionError

logger = logging.getLogger("pydlogon")

class MatchError(Exception):
    """
    Error that might happen inside any type of Match class.
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ParseMatchError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class ActionContainer(object):
    def __init__ (self, name, out_script):
        if not name:
            raise ActionError("Name is empty")
        self.name = name
        self.actions = []
        self.logon_file_name = out_script
        try:
            self.logon_file = open(self.logon_file_name, 'w')
            self.logon_file.close()
        except Exception, e:
            logger.error("error Initializin file %s: %s" % (self.logon_file, e))


    def add(self, action):
        self.actions.append(action)
    
    def __str__(self):
        return "%s: %s" % (self.name,  "".join([str(d) for d in self.actions]))

    def run_actions(self):
        try:
            self.logon_file = open(self.logon_file_name, 'a')
        except Exception, e:
            logger.error("error opening file %s: %s" % (self.logon_file, e))
        
        for action in self.actions:
            logger.debug("Running action %s: %s" % (action.action, action.text))

            if action.action == "exec":
                logger.debug("writing %s to logon file: %s" % (action.text, self.logon_file_name))
                    
                try:
                    self.logon_file.write( "%s\n" % action.text)
                except Exception, e:
                    logger.error("error writing logon file %s: %s" % (self.logon_file_name, e))
                
            elif action.action == "file":
                try:
                    r_file = open(action.text, 'r')
                except Exception, e:
                    logger.error("error reading file %s" % action.text)
                    return
                for line in  r_file.readlines():
                    self.logon_file.write( "%s" % line)

            elif action.action == "server_exec":
                logger.info("executing %s command" % action.text)
                ret = os.system(action.text)
                logger.info("command returned %d" % ret)

            else:
                raise ActionError("Action %s: not valid" % action.action)

        self.logon_file.close()
                
        
class Action(object):
    def __init__ (self, action, text):
        
        if not text:
            raise ActionError("Text is empty")

        if not action:
            raise ActionError("Action is empty")
        
        self.action = action
        self.text = text

    def __str__(self):
        return "%s -> %s" % (self.action, "".join([str(d) for d in self.text]))


class Match(object):
    """
    This wraps Match types objects.
    """

    def __init__(self, name):
        if not name:
            raise MatchError("Name is empty")

        self.name = name
        self.data = []

    def add(self, match):
        self.data.append(match)

    def __str__(self):
        return self.name

    def check(self, vars):
        for match in self.data:
            if match.check(vars):
                return True
        return False

    def content(self):
        return " ".join(["'%s' -> '%s'" % (str(d), str(d._value)) for d in self.data])


class Bind(object):

    def __init__(self, action=None):
        self.action = action
        self.match_list = []

    def add_match(self, match, negate=False):

        logger.debug("Adding MATCH '%s': '%s'" % (match, match.content()))

        self.match_list.append([match, negate])

    def check(self, vars):
        for match, negate in self.match_list:
            if match.check(vars):
                if negate:
                    return False
            else:
                if not negate:
                    return False

        return True

    def __str__(self):
        s = ""
        for match, negate in self.match_list:
            if s:
                s = s + " "

            if negate:
                s = s + "!" + str(match)
            else:
                s = s + str(match)

        return s

class MatchBase(object):
    def __str__(self):
        return "%s" % self._value

class MatchUser(MatchBase):
    def __init__(self, value):
        self._value = value

    def check(self, vars):
        logger.debug("Checking if user is %s" % self._value)
        if vars.user == self._value:
            return True

        return False

class MatchGroup(MatchBase):
    def __init__(self, value):
        self._value = value

    def check(self, vars):
        logger.debug("Checking if group is %s" % self._value)
        if vars.group == self._value:
            logger.debug("Matched")
            return True

        return False

class MatchSessionUser(MatchBase):
    def __init__(self, value):
        self._value = value

    def check(self, vars):
        logger.debug("Checking if session user is %s" % self._value)
        if vars.session_user == self._value:
            logger.debug("Matched")
            return True

        return False

class MatchSessionGroup(MatchBase):
    def __init__(self, value):
        self._value = value

    def check(self, vars):
        logger.debug("Checking if session group is %s" % self._value)
        if vars.session_group == self._value:
            logger.debug("Matched")
            return True

        return False

class MatchMachine(MatchBase):
    def __init__(self, value):
        self._value = value

    def check(self, vars):
        logger.debug("Checking if machine is %s" % self._value)
        if vars.machine == self._value:
            logger.debug("Matched")
            return True

        return False

class MatchIPAddress(MatchBase):
    def __init__(self, value):
        """
        Example of MATCH 'client_address':
        match machine client_address 192.168.0.10
        match net1 client_address 192.168.1.0/24
        match net2 client_address 192.168.2.0/255.255.255.0
        match net3 client_address 192.168.3.0-192.168.3.255
        """
        try:
            self._value = IP(value)
        except ValueError:
            logger.error("Invalid value for MATCH client_address: '%s'" % value)
            raise MatchError("Invalid value for MATCH client_address: '%s'" % value)


    def check(self, vars):
        client_address = IP(vars.client_address)
        logger.debug("Checking if client address is %s" % self._value)

        if client_address in self._value:
            logger.debug("Matched")
            return True

        return False

class MatchArch(MatchBase):
    """
    Example of MATCH 'arch':
    match arch old_pc Win95
    """
    def __init__(self, value):
        self._value = value

    def check(self, vars):
        logger.debug("Checking if architecture is %s" % self._value)
        if vars.arch == self._value:
            logger.debug("Matched")
            return True

        return False

class MatchUserInGroup(MatchBase):
    """
    Example of MATCH 'user_in_group':
    match Domain user_in_group Domain
    """
    def __init__(self, value):
        self._value = value

    def check(self, vars):
        logger.debug("Checking if user %s is in %s group" % (vars.user, self._value))
        if vars.user in grp.getgrnam(self._value)[3]:
            logger.debug("Matched")
            return True

        return False

class MatchUserInGroupId(MatchBase):
    """
    Example of MATCH 'user_in_group_id':
    match Domain user_in_group_id 500
    """
    def __init__(self, value):
        self._value = value

    def check(self, vars):
        logger.debug("Checking if user %s is in %s gid" % (vars.user, self._value))
        if vars.user in grp.getgrgid(self._value)[3]:
            logger.debug("Matched")
            return True

        return False

class MatchSessionUserInGroup(MatchBase):
    def __init__(self, value):
        self._value = value

    def check(self, vars):
        logger.debug("Checking if session user %s is in %s group" % (vars.session_user, self._value))
        if vars.session_user in grp.getgrnam(self._value)[3]:
            logger.debug("Matched")
            return True

        return False

class MatchSessionUserInGroupId(MatchBase):
    def __init__(self, value):
        self._value = value

    def check(self, vars):
        logger.debug("Checking if session user %s is in %s gid" % (vars.session_user, self._value))
        if vars.session_user in grp.getgrgid(self._value)[3]:
            logger.debug("Matched")
            return True

        return False


class MatchAll(MatchBase):
    """
    Always True
    """
    def __init__(self, value):
        self._value = value
    
    def check(self, vars):
        logger.debug("Checking All")
        logger.debug("Matched")
        return True


MATCH_CLASSES = {   'user': MatchUser,
                    'group': MatchGroup,
                    'session_group': MatchSessionGroup,
                    'session_user': MatchSessionUser,
                    'machine': MatchMachine,
                    'client_address': MatchIPAddress,
                    'arch': MatchArch,
                    'all': MatchAll,
                    'user_in_group': MatchUserInGroup,
                    'user_in_group_id': MatchUserInGroupId,
                    'session_user_in_group': MatchSessionUserInGroup,
                    'session_user_in_group_id': MatchSessionUserInGroupId,
                }


class ParseMatch(object):
    
    counter = 0

    def __init__(self, options):
        self.out_script = options.out_script
        self.config = options.config

    def load_match(self, name, match_class, value):

        logger.debug("Loading MATCH %s: '%s' -> '%s'" % (name, match_class, value))

        if match_class in MATCH_CLASSES:
            match_class = MATCH_CLASSES[match_class]
        else:
            raise ParseMatchError("Invalid MATCH class '%s'. Line #%d." % (match_class, self.counter))

        if name in self.match_list:
            logger.debug("Adding to %s: '%s'" % (name, value))
            self.match_list[name].add(match_class(value))
        else:
            logger.debug("Creating %s: -> '%s'" % (name, value))
            match = Match(name)
            match.add(match_class(value))
            self.match_list[name] = match

    def load_action(self, name, action, text):
        logger.debug("Loading ACTION %s: '%s' -> '%s'" % (name, action, text))

        if not name in self.action_list:
            action_container =  ActionContainer(name, self.out_script)
            action_container.add(Action(action, text))
            self.action_list[name] = action_container
        else: 
            self.action_list[name].add(Action(action, text))
    
    def load_bind(self, matchs, action_name):

        if action_name in self.action_list:
            bind = Bind(action=self.action_list[action_name])
            logger.debug("Loading BIND statement: %s -> %s" % (matchs, action_name))
        else:
            raise ParseMatchError("Action '%s' does not exist. Line #%d." % (action_name, self.counter))

        for match in matchs:
            negate = False
            m = re.match("^(!)?(.*)", match)
            match_name = m.group(2)
            if m.group(1):
                negate = True

            if match_name not in self.match_list:
                raise ParseMatchError("MATCH '%s' does not exist. Line #%d." % (match_name, self.counter))

            bind.add_match(self.match_list[match_name], negate)

        self.bind_list.append(bind)

    def load(self):

        self.match_list = {}
        self.action_list = {}
        self.bind_list = []

        try:
            #TODO: change filename
            match_file = open(self.config, 'r')
        except IOError, err:
            #TODO: change filename
            raise ParseMatchError("Unable to open %s configuration file" % "config.match")

        for raw_line in match_file:
            self.counter = self.counter + 1

            if re.match("^#.*", raw_line):
                continue
           
            line = raw_line.strip('\n').split()
 
            if not line:
                continue

            if line[0] == "match":
                if line[2] == "all":
                    line.append("")

                self.load_match(line[1], line[2], " ".join([str(s) for s in line[3:]]))

            if line[0] == "action":
                self.load_action(line[1], line[2], " ".join([str(s) for s in line[3:]]))
            if line[0] == "bind":
                if len(line) > 2:
                    self.load_bind(line[1:-1], line[-1])
                else:
                    raise ParseMatchError("Invalid syntax for 'bind'. Line #%d" % self.counter)


