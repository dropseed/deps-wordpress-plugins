import os
import json
from subprocess import run


def act():
    # An actor will always be given a set of "input" data, so that it knows what
    # exactly it is supposed to update. That JSON data will be stored in a file
    # at /dependencies/input_data.json for you to load.
    with open('/dependencies/input_data.json', 'r') as f:
        data = json.load(f)

    # TODO `pullrequest start` could do this, take care of safe branch names, naming consistency, etc.
    branch_name = 'deps/update-job-{}'.format(os.getenv('JOB_ID'))
    run(['git', 'checkout', os.getenv('GIT_SHA')], check=True)
    run(['git', 'checkout', '-b', branch_name], check=True)

    for manifest_path, manifest_data in data.get('manifests', {}).items():
        for dependency_name, updated_dependency_data in manifest_data['updated']['dependencies'].items():
            installed = manifest_data['current']['dependencies'][dependency_name]['constraint']
            version_to_update_to = updated_dependency_data['constraint']

            plugin_dir_path = os.path.join(manifest_path, dependency_name)

            run(['rm', '-r', plugin_dir_path], check=True)
            run(f'curl https://downloads.wordpress.org/plugin/{dependency_name}.{version_to_update_to}.zip > {dependency_name}.zip', shell=True, check=True)
            run(['unzip', f'{dependency_name}.zip', '-d', os.path.dirname(plugin_dir_path)], check=True)
            run(['rm', f'{dependency_name}.zip'], check=True)

            run(['git', 'add', plugin_dir_path], check=True)
            run(['git', 'commit', '-m', 'Update {} from {} to {}'.format(dependency_name, installed, version_to_update_to)], check=True)

    if os.getenv('DEPENDENCIES_ENV') != 'test':
        # TODO have pullrequest do this too?
        run(['git', 'push', '--set-upstream', 'origin', branch_name], check=True)

    # Shell out to `pullrequest` to make the actual pull request.
    #    It will automatically use the existing env variables and JSON schema
    #    to submit a pull request, or simulate one a test mode.
    run(
        [
            'pullrequest',
            '--branch', branch_name,
            '--dependencies-json', json.dumps(data),
        ],
        check=True
    )
