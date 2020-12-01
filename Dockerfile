# Build this from a small and secure base image. In production, we would also
# want to run in a non-root mode. This IS only demo-ware, though, so an 
# Alpine base image should be fine
FROM python:alpine

# Here, we copy all of our buld context from the 'content' folder. For our 
# example, we are including our code, bootstrap, and requirements file. 
# However, any of these could easily be supplied from a pre-build base 
# image.
COPY ./content .

# Here, we are installing the latest version of the modules we use in the
# example (boto3 and requests). However, we could run any other installations
# here to build the exact app stack our Lambda function needs
RUN pip install -r requirements.txt

# Rather than specifying the Lambda entrypoint in the function settings, the 
# behaviour of container-based Lambas is to use the entrypoint and command
# of the container to target the bootstrapper
CMD python3 bootstrap.py