pipeline {
    agent any

    environment {
        IMAGE_NAME = "192.168.0.10:31000/odoo18"
        IMAGE_TAG  = "${BUILD_NUMBER}"

        DOCKER_CRED_ID = "DOCKER_CREDS"

        GIT_REPO = "https://github.com/mhadiltt/odoo18.git"
        GIT_BRANCH = "main"

        HELM_RELEASE = "odoo"
        HELM_NAMESPACE = "odoo"
    }

    stages {

        stage('Clone Source Code') {
            steps {
                git branch: "${GIT_BRANCH}", url: "${GIT_REPO}"
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([
                    usernamePassword(
                        credentialsId: "${DOCKER_CRED_ID}",
                        usernameVariable: 'DOCKER_USER',
                        passwordVariable: 'DOCKER_PASS'
                    )
                ]) {
                    sh '''
                        echo "$DOCKER_PASS" | docker login 192.168.0.10:31000 -u "$DOCKER_USER" --password-stdin
                    '''
                }
            }
        }

        stage('Build Odoo Image') {
            steps {
                sh '''
                    docker build -t $IMAGE_NAME:$IMAGE_TAG .
                '''
            }
        }

        stage('Push Odoo Image') {
            steps {
                sh '''
                    docker push $IMAGE_NAME:$IMAGE_TAG
                '''
            }
        }

        stage('Deploy using Helm') {
            steps {
                sh '''
                    cd helm
                    helm upgrade --install $HELM_RELEASE . \
                      --namespace $HELM_NAMESPACE \
                      --set image.repository=$IMAGE_NAME \
                      --set image.tag=$IMAGE_TAG \
                      --set image.pullPolicy=Always
                '''
            }
        }
    }

    post {
        success {
            echo "Odoo 18 successfully built and deployed using Jenkins + Helm!"
        }
        failure {
            echo "Odoo 18 pipeline failed. Please check Jenkins logs."
        }
    }
}

