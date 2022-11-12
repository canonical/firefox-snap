#!/usr/bin/env python3

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
    v = marionette.find_element(marionette_driver.by.By.ID, 'version-box').text
    print('about:support version: {}'.format(v))
    assert(version.endswith(v))
    d = marionette.find_element(marionette_driver.by.By.ID,
                                'distributionid-box').text
    print('about:support distribution ID: {}'.format(d))
    assert(d == 'canonical-002')
