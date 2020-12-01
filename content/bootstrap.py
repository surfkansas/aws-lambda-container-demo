# This file is out main entrypoint for the Lambda function. It is a rudimentary Python port of the
# sample bash code supplied from Amazon in their write-up on how to implement a custom Lambda 
# runtime:
#
#   https://docs.aws.amazon.com/lambda/latest/dg/runtimes-custom.html
#
# Unlike with custom runtimes, we control the bootstrap via the container entrypoint and command,
# rather than Lambda looking for a command called `bootstrap`. We could call this `surfer_dude.py`
# and it would work fine, as long as the Dockerfile reflects the correct file.

import boto3
import os 
import requests
import sys
import traceback

# The actual Lambda code is implemented in the app.py file. By convention, we should keep the
# bootstrap and code in separate files. When creating the app, we can (and should) create any
# global shared resources as part of creating this. Note: in a production app, we need to catch
# and report errors as initializaiton errors.
import app

# This is the main loop of the Lambda function. It iteracts with the local Lambda invocation API
# to get events and handle responses.
def run_loop():
    # The AWS_LAMBDA_RUNTIME_API environment variable lets us know where the API endpoint for 
    # Lambda invocation API is located. This is a locally callable endpoint, usually something like
    # `http://localhost:9001`.
    aws_lambda_runtime_api = os.environ['AWS_LAMBDA_RUNTIME_API']

    # The main thing the bootstrap does is starts a long-running loop to handle getting events. Each loop
    # will try to get the next invocation details. This method will run until is ab-ends via an unhandled 
    # exception, or until AWS terminates the container
    while True:
        # Always clear out the request_id in each loop
        request_id = None
        try:
            # Call the invocation/next endpoint to get the details about the event. The JSON body of the event
            # is returned in the body, and the request ID (alongside other headers) are returned in the headers.
            invocation_response = requests.get(f'http://{aws_lambda_runtime_api}/2018-06-01/runtime/invocation/next')

            # Get the interesting header values from the invocation response. The most important of these is the
            # request ID which must be used for all further posts back to the invocation API.
            request_id = invocation_response.headers['Lambda-Runtime-Aws-Request-Id']
            invoked_function_arn = invocation_response.headers['Lambda-Runtime-Invoked-Function-Arn']
            trace_id = invocation_response.headers['Lambda-Runtime-Trace-Id']
            
            # Set the trace ID environment variable to allow the X-Ray SDK to implement tracing. (We aren't actually
            # using X-Ray, so this doesn't really impact our sample code.)
            os.environ['_X_AMZN_TRACE_ID'] = trace_id

            # Build a context dictionary to pass to the interesting headers to the function code
            context = {
                'request_id': request_id,
                'invoked_function_arn': invoked_function_arn,
                'trace_id': trace_id
            }

            # Pull the JSON for the event from the body of the invocation result
            event = invocation_response.json()

            # Build the URL we need to post our results to after the function is invoked.
            response_url = f'http://{aws_lambda_runtime_api}/2018-06-01/runtime/invocation/{request_id}/response'

            # Call our funciton implementation to determine our funciton results.
            result = app.lambda_handler(event, context)

            # DO NOT FORGET THIS LINE! This flushes the output so that the Lambda runtime can read all of 
            # the log entries from STDOUT stream. If you forget this, you will be missing all (or at least 
            # most) of your log messages in CloudWatch.
            sys.stdout.flush()

            # Post the results from the Lambda function as a JSON document to the response endpoint.
            requests.post(response_url, json=result)
        
        except:
            # We only need to do special handling of exceptions in cases wehere we have an active request.
            # Any exceptions that occured from non-request errors (such as timeout gettin the invocation due
            # to an empty queue) can be ignored.
            if request_id != None:
                # Wrap our error handling in a try/catch so that error handling errors don't ab-end a fucntion
                # call
                try:
                    # Create an eception response object from the exception info
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    exception_message = {
                        'errorType': exc_type.__name__, 
                        'errorMessage': str(exc_value), 
                        'stackTrace': traceback.format_exception(exc_type, exc_value, exc_traceback)
                    }

                    # Determine the error API endpoint to POST the error message to.
                    error_url = f'http://{aws_lambda_runtime_api}/2018-06-01/runtime/invocation/{request_id}/error'

                    # Again, REMEMBER TO FLUSH STDOUT or you won't get logs.
                    sys.stdout.flush()

                    # Make the POST call to the error endpoint.
                    requests.post(error_url, json=exception_message)
                except:
                    # Don't let exception reporting errors crash the runtime
                    pass

# Start the loop up when the container starts
run_loop()
