#!/bin/bash
set -e

# Cargar las variables del .env
export $(grep -v '^#' .env | xargs)

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$ECR_REPO"

echo "🔑 Logueando en AWS ECR con profile $AWS_PROFILE ..."
AWS_PROFILE=$AWS_PROFILE aws ecr get-login-password --region $AWS_REGION \
    | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com

echo "🏷️  Taggeando imagen: $LOCAL_IMAGE -> $ECR_URI:latest ..."
docker tag $LOCAL_IMAGE:latest $ECR_URI:latest

echo "📤 Pusheando imagen a $ECR_URI ..."
docker push $ECR_URI:latest

echo "✅ Imagen publicada correctamente en ECR"
