# bitrise-step-roll-shards

---

## 🔴 This is a public repository 🔴

---
### Description
This is a Bitrise step to roll shards. The Bitrise [Rolling Builds](https://blog.bitrise.io/post/auto-cancel-builds-and-keep-rolling)
feature for PRs only rolls builds with the same workflow name and branch. Builds kicked off via the `build-router-start`
step in a rolled build are however not killed by association. This step kills all shards associated with a build as soon
as the build is rolled.

The aborted builds are aborted successfully - they thus do not count as a failure

### Prerequisites
- `workflow_names` and `token` need to be passed in to the step
    - `workflow_names` is a whitelist of workflow names to abort if running on the same branch
    - `token` is an api token required to authenticate with Bitrise. This should be a secret set in the UI
---
### Usage
- Add a step call within the desired workflow of your `bitrise.yml` to report the start of a build to dev as such:
```yaml
- git::https://github.com/WhoopInc/bitrise-step-roll-shards.git@master:
     title: Roll sharded workflows
     inputs:
        - workflow_names: |-
            Shard_1
            Shard_2
        - token: $AUTH_TOKEN
     is_always_run: true
     run_if: $BITRISE_GIT_BRANCH != 'main'
```

### Outputs
`ROLLED_BUILD_SLUGS` will contain a list of build slugs that were rolled as a result of the step