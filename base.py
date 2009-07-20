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


class MatchError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class ActionError(Exception):

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


