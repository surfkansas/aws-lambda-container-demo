account_number=$(aws sts get-caller-identity --output text --query 'Account')
region=sa-east-1
ecr_repository_name='test-lambda-ecr'
date_tag=$(date +%s)

ecr_url=$account_number.dkr.ecr.$region.amazonaws.com/$ecr_repository_name:build-$date_tag

docker build -t test-lambda-ecr .

docker tag test-lambda-ecr $ecr_url

aws ecr get-login-password --region $region | docker login --username AWS --password-stdin $account_number.dkr.ecr.$region.amazonaws.com

docker push $ecr_url

echo
echo $ecr_url


