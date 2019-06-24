import os
import json
import sys
from subprocess import run
import zipfile


def act(input_path, output_path):
    # An actor will always be given a set of "input" data, so that it knows what
    # exactly it is supposed to update. That JSON data will be stored in a file
    # at /dependencies/input_data.json for you to load.
    with open(input_path, 'r') as f:
        data = json.load(f)

    for manifest_path, manifest_data in data.get('manifests', {}).items():
        for dependency_name, updated_dependency_data in manifest_data['updated']['dependencies'].items():
            version_to_update_to = updated_dependency_data['constraint']

            plugin_dir_path = os.path.join(manifest_path, dependency_name)

            run(['rm', '-r', plugin_dir_path], check=True)
            run(f'curl https://downloads.wordpress.org/plugin/{dependency_name}.{version_to_update_to}.zip > {dependency_name}.zip', shell=True, check=True)
            z = zipfile.ZipFile(f'{dependency_name}.zip', 'r')
            z.extractall(os.path.dirname(plugin_dir_path))
            z.close()
            run(['rm', f'{dependency_name}.zip'], check=True)

    with open(output_path, "w+") as f:
        json.dump(data, f)


if __name__ == "__main__":
    act(sys.argv[1], sys.argv[2])
