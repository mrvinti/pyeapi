#
# Copyright (c) 2015, Arista Networks, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
#   Neither the name of Arista Networks nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL ARISTA NETWORKS
# BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
# BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
"""Module for working with the global system in EOS

This module provides an API for working with the global system settings
in EOS.   It provides the following class implementations:

    * System -- Configures global system settings

System Attributes:
    hostname (string): The hostname of the node as configured in the
        running-configuration.

"""

import re

from pyeapi.api import Entity

class System(Entity):
    """The System class implements global config for the node

    Global configuration settings include those thaat identify the node
    and provide node level configuration such as hostname
    """

    def get(self):
        """Returns the system configuration abstraction

        The System resource returns the following:

            * hostname (str): The hostname value

        Returns:
            dict: Represents the node's system configuration
        """
        commands = list()
        commands.append('show ip route')
        commands.append('show hostname')

        try:
            result = self.node.enable(commands, encoding='text')
            ip_route = result[0]['result']['output']
            hostname = result[1]['result']['output']
        except:
            try:
                commands = list()
                commands.append('show ip route')
                commands.append('show running-config | grep hostname')
                result = self.node.enable(commands, encoding='text')
                ip_route = result[0]['result']['output']
                hostname = result[1]['result']['output']
            except:
                return None

        resource = dict()
        resource.update(self._parse_hostname(hostname))
        resource.update(self._parse_iprouting(ip_route))
        return resource

    def _parse_hostname(self, config):
        """Parses the global config and returns the hostname value

        Returns:
            dict: The configured value for hostname.  The returned dict
                object is intended to be merged into the resource dict
        """
        value = 'localhost'
        print config
        match = re.search(r'^hostname:?\s(\S+)\n', config, re.M | re.I)
        if match:
            value = match.group(1)
        value = str(value).strip()
        return dict(hostname=value)

    def _parse_iprouting(self, config):
        """Parses the global config and returns the ip routing value

        Returns:
            dict: The configure value for ip routing.  The returned dict
                object is intendd to be merged into the resource dict
        """
        value = 'IP routing not enabled' not in config
        return dict(iprouting=value)

    def set_hostname(self, value=None, default=False):
        """Configures the global system hostname setting

        EosVersion:
            4.13.7M

        Args:
            value (str): The hostname value
            default (bool): Controls use of the default keyword

        Returns:
            bool: True if the commands are completed successfully
        """
        cmd = self.command_builder('hostname', value=value, default=default)
        return self.configure(cmd)

    def set_iprouting(self, value=None, default=False):
        """Configures the state of global ip routing

        EosVersion:
            4.13.7M

        Args:
            value(bool): True if ip routing should be enabled or False if
                ip routing should be disabled

            default (bool): Controls the use of the default keyword

        Returns:
            bool: True if the commands completed successfully otherwise False
        """
        cmd = self.command_builder('ip routing', value=value, default=default)
        return self.configure(cmd)


def instance(api):
    """Returns an instance of System
    """
    return System(api)
