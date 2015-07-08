# Copyright (C) 2015 Red Hat, All rights reserved.
# AUTHORS: William Temple <wtemple@redhat.com>
#
# This library is a component of Project Atomic.
#
#    Project Atomic is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License as
#    published by the Free Software Foundation; either version 2 of
#    the License, or (at your option) any later version.
#
#    Project Atomic is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Project Atomic; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
#    02110-1301 USA.
#

"""Atomic Verify Module"""

import os
import docker

import util

_HAS_IMAGE_SCANNER = False
try:
    import image_scanner_client as scan
    _HAS_IMAGE_SCANNER = True
except ImportError:
    pass


class VerifyError(Exception):
    """Generic error verifying a container."""
    def __init__(self, val):
        self.val = val

    def __str__(self):
        return str(self.val)


class Verify:
    """
    A base class for container image verification
    """
    def __init__(self, *args, **kwargs):
        if 'all' in kwargs and kwargs['all']:
            self.verifyAll = True
        else:
            self.to_verify = args

    def start(self):
        """
        Begin validation.
        """
        raise NotImplementedError('Verify subclass does not implement start() '
                                  'method.')


class DockerVerify(Verify):
    """
    Verification for Docker images.
    """
    def __init__(self, *args, **kwargs):
        Verify.__init__(self, *args, **kwargs)
        self.c = docker.Client()
        self.images = []
        for ident in self.to_verify:
            m = util.image_by_name(ident)
            if len(m) != 1:
                raise VerifyError('No unique match for identifier "{}".'
                                  ''.format(ident))
            self.images.append(self.c.inspect_image(m[0]['Id']))

    def _prninfo(self, idata):
        """
        Prints image information. Accepts a dictionary with the following
        keys: 'Name', 'Release', 'Vendor', 'Version' and optionally
        'Authoritative_Registry'.
        """
        util.write('\tBased on : ')
        util.writeln('"{0}" {1}-{2} ({3})'.format(idata['Name'],
                                                  idata['Version'],
                                                  idata['Release'],
                                                  idata['Vendor']))
        if 'Authoritative_Registry' in idata:
            util.writeln('\tRegistry : {}'.format(
                idata['Authoritative_Registry']))

    def _label_info(self, iinfo):
        """
        Returns topmost labeled image information in descendence list for
        iinfo
        """
        labels = {}
        try:
            labels = iinfo['Config']['Labels']
            if not labels and iinfo['Parent']:
                return self._label_info(self.c.inspect_image(iinfo['Parent']))
            else:
                sufficient_info = 'Name' in labels and 'Version' in labels \
                                                   and 'Release' in labels \
                                                   and 'Vendor' in labels
                if sufficient_info:
                    return labels 
        except TypeError:
            # This only happens if iinfo['Config'] is None
            pass
        except KeyError:
            # No such key 'Config' in iinfo, 'Labels' in iinfo['Config'],
            # or 'Parent' in iinfo...
            pass
        return {}

    def start(self):
        """
        Begin validation of docker images.
        """
        for i in self.images:
            util.write('Verifying: {}...\t'.format(i['Id'][0:12]))
            idata = self._label_info(i)
            if idata:
                self.verifyImage(idata)
                self._prninfo(idata)
            else:
                util.writeln('SKIPPED')
                util.writeln('\tThis image has no vendor information.')


    def verifyImage(self, iinfo):
        """
        Verifies a single Docker image.
        """
        util.writeln('OKAY')
