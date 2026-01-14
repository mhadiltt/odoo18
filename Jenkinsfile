pipeline {
  agent {
    kubernetes {
      defaultContainer 'kaniko'
      yaml """
apiVersion: v1
kind: Pod
spec:
  serviceAccountName: jenkins
  containers:
  - name: kaniko
    image: gcr.io/kaniko-project/executor:latest
    command:
    - /busybox/cat
    tty: true
    volumeMounts:
    - name: docker-config
      mountPath: /kaniko/.docker

  - name: helm
    image: alpine/helm:3.14.0
    command:
    - cat
    tty: true

  volumes:
  - name: docker-config
    secret:
      secretName: docker-regcred
"""
    }
  }

  environment {
    IMAGE_NAME = "192.168.0.10:31000/odoo18"
    IMAGE_TAG  = "${BUILD_NUMBER}"
    HELM_RELEASE = "odoo"
    HELM_NAMESPACE = "odoo"
  }

  stages {

    stage('Clone Source Code') {
      steps {
        checkout scm
      }
    }

    stage('Build & Push Image (Kaniko)') {
      steps {
        container('kaniko') {
          sh '''
            /kaniko/executor \
              --dockerfile=Dockerfile \
              --context=$WORKSPACE \
              --destination=$IMAGE_NAME:$IMAGE_TAG \
              --insecure \
              --skip-tls-verify
          '''
        }
      }
    }

    stage('Deploy using Helm') {
      steps {
        container('helm') {
          sh '''
            cd helm
            helm upgrade --install $HELM_RELEASE . \
              --namespace $HELM_NAMESPACE \
              --create-namespace \
              --set image.repository=$IMAGE_NAME \
              --set image.tag=$IMAGE_TAG \
              --set image.pullPolicy=Always
          '''
        }
      }
    }
  }

  post {
    success {
      echo "Odoo 18 successfully built with Kaniko and deployed using Helm!"
    }
    failure {
      echo "Odoo 18 pipeline failed. Please check Jenkins logs."
    }
  }
}
