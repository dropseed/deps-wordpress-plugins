import re
import os
import json
import sys
import logging

import requests


def collect():
    plugins_path = sys.argv[1]
    plugins_contents = os.listdir(plugins_path)
    plugin_directories = [x for x in plugins_contents if os.path.isdir(os.path.join(plugins_path, x))]

    collected_plugins = {}

    for plugin in plugin_directories:

        print(f'Collecting {plugin}')

        plugin_path = os.path.join(plugins_path, plugin)

        # look in all root php files for the "Version: x" to detect installed version
        plugin_root_files = os.listdir(plugin_path)
        plugin_root_paths = [os.path.join(plugin_path, x) for x in plugin_root_files]
        plugin_root_file_paths = [x for x in plugin_root_paths if not os.path.isdir(x) and x[-4:] == '.php']

        installed_version = None
        for path in plugin_root_file_paths:
            with open(path, 'rb') as f:
                contents = f.read()
                version_match = re.search(b'^\s*\**\s*Version:\s*(.*)\s*$', contents, re.MULTILINE)
                if version_match:
                    installed_version = version_match.groups(0)[0]
                    break

        if not installed_version:
            raise Exception(f'Could not detect installed version of {plugin}')

        installed_version = installed_version.decode('utf-8').strip()

        try:
            response = requests.get(f'https://api.wordpress.org/plugins/info/1.0/{plugin}.json')
            available = response.json().get('versions', {}).keys()
        except Exception:
            logging.error(f'Unable to find available versions of {plugin} in API.')
            available = [installed_version]

        collected_plugins[plugin] = {
            'constraint': installed_version,
            'available': [{'name': x} for x in available],
            'source': 'wordpress-plugin',
        }

    schema_output = json.dumps({
        'manifests': {
            os.path.relpath(os.path.abspath(plugins_path), '/repo'): {
                'current': {
                    'dependencies': collected_plugins
                }
            }
        }
    })
    print(f'<Dependencies>{schema_output}</Dependencies>')
