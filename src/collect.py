import re
import os
import sys
import logging
import json
from subprocess import run

import requests


def get_plugin_version(plugin_path):
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
                installed_version = version_match.groups(0)[0].decode('utf-8').strip()
                break

    return installed_version


def collect(input_path, output_path):
    plugins_path = input_path
    plugins_contents = os.listdir(plugins_path)
    plugin_directories = [x for x in plugins_contents if os.path.isdir(os.path.join(plugins_path, x))]

    current_plugins = {}
    updated_plugins = {}

    for plugin in plugin_directories:

        print(f'Collecting {plugin}')

        plugin_path = os.path.join(plugins_path, plugin)
        installed_version = get_plugin_version(plugin_path)

        if not installed_version:
            raise Exception(f'Could not detect installed version of {plugin}')

        try:
            response = requests.get(f'https://api.wordpress.org/plugins/info/1.0/{plugin}.json')
            response.raise_for_status()
            latest = response.json()["version"]
        except Exception:
            logging.error(f'Unable to find latest version of {plugin} in API.')
            latest = None

        current_plugins[plugin] = {
            'constraint': installed_version,
            'source': 'wordpress-plugin',
        }

        if latest and latest != installed_version:
            updated_plugins[plugin] = {
                'constraint': latest,
                'source': 'wordpress-plugin',
            }

    output = {
        'manifests': {
            plugins_path: {
                'current': {
                    'dependencies': current_plugins,
                },
                'updated': {
                    'dependencies': updated_plugins,
                },
            }
        }
    }

    with open(output_path, "w+") as f:
        json.dump(output, f)


if __name__ == "__main__":
    collect(sys.argv[1], sys.argv[2])
