pipeline {
    agent any

    environment {

        IMAGE_NAME = "192.168.0.10:31000/odoo18"
        IMAGE_TAG  = "${BUILD_NUMBER}"

        DOCKER_CREDS = "docker-registry-creds"
        ARGOCD_CREDS = "argocd-jenkins-creds"

        ARGOCD_SERVER = "argocd-server.argocd.svc.cluster.local"
        ARGOCD_APP    = "odoo18"

        GIT_REPO = "https://github.com/mhadiltt/odoo18.git"
        GIT_BRANCH = "main"
    }

    stages {

        stage('Clone Source Code') {
            steps {
                git branch: "${GIT_BRANCH}", url: "${GIT_REPO}"
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(credentialsId: DOCKER_CREDS, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
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

        stage('Deploy using ArgoCD') {
            steps {
                withCredentials([usernamePassword(credentialsId: ARGOCD_CREDS, usernameVariable: 'ARGO_USER', passwordVariable: 'ARGO_PASS')]) {
                    sh '''
                        # Login to ArgoCD
                        argocd login $ARGOCD_SERVER --username $ARGO_USER --password $ARGO_PASS --insecure

                        # Update Helm image tag in ArgoCD
                        argocd app set $ARGOCD_APP --helm-set image.tag=$IMAGE_TAG

                        # Sync application
                        argocd app sync $ARGOCD_APP
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "Odoo 18 successfully built and deployed using Jenkins + ArgoCD!"
        }
        failure {
            echo "Odoo 18 pipeline failed. Please check Jenkins logs."
        }
    }
}
