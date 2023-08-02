#!/usr/bin/env python3

# Copyright (C) 2022 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3, as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import marionette_driver
import sys

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: {} pid version'.format(sys.argv[0]))
        sys.exit(1)

    pid = int(sys.argv[1])
    version = sys.argv[2]

    print('runtime version: {}'.format(version))

    marionette = marionette_driver.marionette.Marionette()
    marionette.start_session()
    print('session capabilities: {}'
          .format(json.dumps(marionette.session_capabilities, indent=2)))
    assert(marionette.session_capabilities['moz:processID'] == pid)
    assert(marionette.session_capabilities['moz:headless'])
    assert(marionette.session_capabilities['browserName'] == 'firefox')
    assert(marionette.session_capabilities['browserVersion'] in version)

    marionette.navigate('about:support')
    versionbox = \
        marionette.find_element(marionette_driver.by.By.ID, 'version-box')
    marionette_driver.wait.Wait(marionette).until(
        lambda m:
        len(versionbox.text) > 0 and version.endswith(versionbox.text))
    print('about:support version: {}'.format(versionbox.text))

    distributionidbox = \
        marionette.find_element(
            marionette_driver.by.By.ID, 'distributionid-box')
    marionette_driver.wait.Wait(marionette).until(
        lambda m: distributionidbox.text == 'canonical-002')
    print('about:support distribution ID: {}'.format(distributionidbox.text))
