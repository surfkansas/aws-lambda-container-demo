
# This is the sample Lambda code. I wrote it to mimic the pattern of an 
# out-of-the-box hello world Lamba. But, since we control the bootstrap
# layer, we can write our handlers however we want.

def lambda_handler(event, context):
    
    # Logging is simple, straight from the STDOUT
    print('Logging works just like old-school Lambda')

    # I added in the ability to force an exception so that your can see
    # how the exception handling is implemented back in the bootstrap
    if 'force_exception' in event:
        raise Exception(event['force_exception'])
    
    # I cheated a bit here by included `context`. In a "vanilla" Python
    # Lambda function, the context object is not JSON serializable and
    # would result in an error. Since we control the bootstrap, our
    # `context` object is 100% under our control. We can implement
    # without it, if we want. For our example, context is just a 
    # Python dictionary of the three key header values provided from
    # the Lambda invocation API.
    return {
        'statusCode': 200,
        'body': 'Hello from ECR Lambda!!!!',
        'event': event,
        'context': context
    }
