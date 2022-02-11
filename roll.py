import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

rolled_build_slugs_list = []

print('Retrieving env variables')
workflow_names = os.environ.get('workflow_names')
token = os.environ.get('token')
base_url = os.environ.get('base_url')
app_slug = os.environ.get('app_slug')
build_slug = os.environ.get('build_slug')
branch = os.environ.get('branch')

running_builds_url = 'https://{}/apps/{}/builds?sort_by=created_at&branch={}&status=0'.format(base_url, app_slug, branch)
print('URL: {}'.format(running_builds_url))

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 502, 503, 504],
    method_whitelist=['GET'],
    raise_on_status=True,
    backoff_factor= 2
)
adapter = HTTPAdapter(max_retries=retry_strategy)
http = requests.Session()
http.mount('https://', adapter)
request_headers = {'Authorization': token}

def abort(build):
    payload = {
        'abort_reason': 'Automatically aborted via Rolling Builds.',
        'abort_with_success': 'true',
        'skip_notifications': 'true'
    }
    abort_builds_url = 'https://{}/apps/{}/builds/{}/abort'.format(base_url, app_slug, build.slug)
    request = http.post(abort_builds_url, payload, request_headers)
    if request.status_code != 200:
        print('Unable to abort workflow {}'.format(build.triggered_workflow))
        print('Response: {}'.format(request.text))
    else:
        print('Successfully aborted workflow {}'.format(build.triggered_workflow))
        rolled_build_slugs_list.append(build.slug)

def main():
    request = http.get(running_builds_url, request_headers)
    response = request.json()

    running_builds = response.data
    num_builds = response.paging
    print('Found {} running builds!'.format(num_builds.total_item_count))
    for build in running_builds:
        if build.slug != build_slug and build.triggered_workflow in workflow_names:
            print("Build {} should be rolled, attempting abort".format(build.triggered_workflow))
            abort(build)
        else:
            print("Build {} not eligible to be rolled, skipping".format(build.triggered_workflow))
    rolled_build_slugs = '\n'.join(rolled_build_slugs_list)
    return rolled_build_slugs


if __name__ == '__main__':
    main()