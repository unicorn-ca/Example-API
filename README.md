# Example-API

An example API that can be deployed against the Unicorn Pipeline.

## Specifications
We leverage CodeBuild and serverless (sls) in order to build and deploy a simple
API.

To package and create Lambda function definitions, we do `sls package`.
We later just use these definitions in `json` format, to deploy from CodeDeploy by providing this json artifact.

The Code is cloned to CodeCommit where the Unicorn Pipeline begins deploying it.

## Editing
There are two build files `serverless.yml` and `buildspec.build.yaml`.

Buildspec is used to define the build process for AWS CodeBuild. This currently
includes some hacks to format the serverless output into a fashion that fits
into the deployed pipeline. We aim to fix this by the next iteration.

Serverless is a typical serverless configuration file. Not that a `deploymentBucket` should **not** be defined as this will cause a build to fail.

`handler.py` contains the Python APIs that `serverless` creates Lambda functions from. The API currently supports Server Side Request Forgery (SSRF), JSON Web Token (JWT) and SQL Injection (SQLi).
