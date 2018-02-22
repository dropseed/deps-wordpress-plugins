import os
import json
from subprocess import run

from utils import write_json_to_temp_file


def act():
    # An actor will always be given a set of "input" data, so that it knows what
    # exactly it is supposed to update. That JSON data will be stored in a file
    # at /dependencies/input_data.json for you to load.
    with open('/dependencies/input_data.json', 'r') as f:
        data = json.load(f)

    run(['deps', 'branch'], check=True)

    for manifest_path, manifest_data in data.get('manifests', {}).items():
        for dependency_name, updated_dependency_data in manifest_data['updated']['dependencies'].items():
            installed = manifest_data['current']['dependencies'][dependency_name]['constraint']
            version_to_update_to = updated_dependency_data['constraint']

            plugin_dir_path = os.path.join(manifest_path, dependency_name)

            run(['rm', '-r', plugin_dir_path], check=True)
            run(f'curl https://downloads.wordpress.org/plugin/{dependency_name}.{version_to_update_to}.zip > {dependency_name}.zip', shell=True, check=True)
            run(['unzip', f'{dependency_name}.zip', '-d', os.path.dirname(plugin_dir_path)], check=True)
            run(['rm', f'{dependency_name}.zip'], check=True)

            run(['deps', 'commit', '-m', 'Update {} from {} to {}'.format(dependency_name, installed, version_to_update_to), plugin_dir_path], check=True)

    run(['deps', 'pullrequest', write_json_to_temp_file(data)], check=True)
