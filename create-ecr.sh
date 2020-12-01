ecr_repository_name='test-lambda-ecr'

aws ecr create-repository --repository-name $ecr_repository_name --image-scanning-configuration '{"scanOnPush":true}'
