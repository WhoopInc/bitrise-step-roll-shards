import os
import requests
import json
import sys

def abort(build, base_url, app_slug, request_headers):
    payload = json.dumps({
        'abort_reason': 'Automatically aborted via Rolling Builds.',
        'skip_notifications': True
    })
    abort_builds_url = 'https://{}/apps/{}/builds/{}/abort'.format(base_url, app_slug, build['slug'])
    request = requests.post(abort_builds_url, payload, headers=request_headers)
    if request.status_code != 200:
        print('Unable to abort workflow {}'.format(build['triggered_workflow']))
        print('Response: {}'.format(request.text))
        return False
    else:
        print('Successfully aborted workflow {} with slug {}'.format(build['triggered_workflow'], build['slug']))
        return True
def check_vars(env_vars):
    for var in env_vars:
        if not var:
            print('{} is empty, exiting.'.format(var))
            sys.exit(1)

def main():
    rolled_build_slugs_list = []
    print('Retrieving env variables')
    workflow_names = os.environ.get('workflow_names')
    token = os.environ.get('token')
    base_url = os.environ.get('base_url')
    app_slug = os.environ.get('app_slug')
    build_slug = os.environ.get('build_slug')
    branch = os.environ.get('branch')
    env_vars = [branch, build_slug, app_slug, base_url, token]
    check_vars(token)

    running_builds_url = 'https://{}/apps/{}/builds?sort_by=created_at&branch={}&status=0'.format(base_url, app_slug, branch)
    print('URL: {}'.format(running_builds_url))

    request_headers = {
        'Authorization': token,
        'accept': 'application/json'
    }
    request = requests.get(running_builds_url, headers=request_headers)
    response = request.json()

    running_builds = response['data']
    num_builds = response['paging']
    print('Found {} running builds!'.format(num_builds['total_item_count']))
    for build in running_builds:
        if build['slug'] != build_slug and build['triggered_workflow'] in workflow_names:
            print("Build {} should be rolled, attempting abort".format(build['triggered_workflow']))
            abort_successful = abort(build, base_url, app_slug, request_headers)
            if abort_successful:
                rolled_build_slugs_list.append(build['slug'])
        else:
            print("Build {} not eligible to be rolled, skipping".format(build['triggered_workflow']))
    rolled_build_slugs = '\n'.join(rolled_build_slugs_list)
    # List of rolled builds is persisted as an env var for the rest of the build
    return rolled_build_slugs

if __name__ == '__main__':
    main()