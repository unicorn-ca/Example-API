# Example-API

An example API that can be deployed against the Unicorn Pipeline.

## Specifications
We leverage CodeBuild and serverless (sls) in order to build and deploy a simple
API.

The Code is cloned to CodeCommit where the Unicorn Pipeline begins deploying it.

## Editing
There are two build files `serverless.yml` and `buildspec.build.yaml`.

Buildspec is used to define the build process for AWS CodeBuild. This currently
includes some hacks to format the serverless output into a fashion that fits
into the deployed pipeline. We aim to fix this by the next iteration.

Serverless is a typical serverless configuration file. Not that a `deploymentBucket` should **not** be defined as this will cause a build to fail.
