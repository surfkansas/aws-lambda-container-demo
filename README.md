# Container Image Lambda Sample

This repository demonstrates how to build and deploy a Lambda function that uses container images stored in AWS ECR to provide the container runtime and code.

### 1 - Create the ECR Repository

First, you should create an ECR repository in your account called `test-lambda-ecr`. This can be done either via the GUI, or by running the `create-ecr.sh` shell script from this repository.

Once the repository is created, we can run the build and publish step.

### 2 - Publish ECR Image

Once the ECR repository is in place, run the `publish-ecr.sh` shell script to build the container image from the code in `\content` and using the supplied `Dockerfile`. This image is pushed - using an epoch-derived build tag - to the ECR repository.

### 3 - Create the Lambda Function

For this step, log into you AWS account and go into the Lambda GUI in the console.

Click the `Create Function` button to begin creating a new Lambda function.  From here, you should select the `Existing Source` option.

Under `Existing Source`, select `Elastic Container Registry (ECR)` in the source selection tabs. 

Fill out the form as follows:

* Function name: **test-lambda-ecr-function**
* Docker container image from selected repository: Click the `browse images` button. From this GUI, select the `test-lambda-ecr` repository and select the image you published in the prior step.  (You can also paste in the image URL to the published image.)

At this point, you can click `Create function`, as this function does not require a VPC or any changes to IAM permissions, environment variables, or runtime compute allocation.

## Testing the Function

Once the function is fully deployed, use the console to create a test message based off of the `hello-world` example and called `basictest`.

Once this test event is created, you can use it to run a test of the function. You should see a successful run with a generic result message that looks something like this:

```json
{
  "statusCode": 200,
  "body": "Hello from ECR Lambda!!!!",
  "event": {
    "key1": "value1",
    "key2": "value2",
    "key3": "value3"
  },
  "context": {
    "request_id": "<redacted>",
    "invoked_function_arn": "arn:aws:lambda:sa-east-1:<redacted>:function:test-lambda-ecr-function",
    "trace_id": "Root=<redacted>;Parent=<redacted>;Sampled=0"
  }
}
```
