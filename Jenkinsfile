pipeline {
  agent {
    kubernetes {
      defaultContainer 'docker'
      yaml """
apiVersion: v1
kind: Pod
spec:
  tolerations:
    - key: "node-role.kubernetes.io/control-plane"
      operator: "Exists"
      effect: "NoSchedule"

  securityContext:
    runAsUser: 0

  containers:
    - name: docker
      image: docker:24.0.6-dind
      securityContext:
        privileged: true
      env:
        - name: DOCKER_TLS_CERTDIR
          value: ""
      args:
        - "--insecure-registry=192.168.0.10:31000"
      resources:
        requests:
          ephemeral-storage: "50Gi"
        limits:
          ephemeral-storage: "50Gi"
      tty: true

    - name: jnlp
      image: jenkins/inbound-agent:latest
      resources:
        requests:
          ephemeral-storage: "2Gi"
        limits:
          ephemeral-storage: "2Gi"
      tty: true
"""
    }
  }

  environment {
    IMAGE_NAME = "192.168.0.10:31000/odoo18"
    IMAGE_TAG  = "${BUILD_NUMBER}"
    DOCKER_CRED_ID = "DOCKER_CREDS"
    HELM_RELEASE = "odoo"
    HELM_NAMESPACE = "odoo"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Docker Login') {
      steps {
        container('docker') {
          withCredentials([usernamePassword(credentialsId: DOCKER_CRED_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh 'echo "$DOCKER_PASS" | docker login http://192.168.0.10:31000 -u "$DOCKER_USER" --password-stdin'
          }
        }
      }
    }

    stage('Build Image') {
      steps {
        container('docker') {
          sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG .'
        }
      }
    }

    stage('Push Image') {
      steps {
        container('docker') {
          sh 'docker push $IMAGE_NAME:$IMAGE_TAG'
        }
      }
    }

    stage('Deploy with Helm') {
      steps {
        container('docker') {
          sh '''
            cd helm
            helm upgrade --install $HELM_RELEASE . \
              --namespace $HELM_NAMESPACE \
              --set image.repository=$IMAGE_NAME \
              --set image.tag=$IMAGE_TAG
          '''
        }
      }
    }
  }
}
