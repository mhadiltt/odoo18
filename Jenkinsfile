pipeline {
  agent {
    kubernetes {
      namespace 'odoo'
      defaultContainer 'docker'
      yaml """
apiVersion: v1
kind: Pod
spec:
  nodeSelector:
    kubernetes.io/hostname: node1-132

  tolerations:
    - key: "node-role.kubernetes.io/control-plane"
      operator: "Exists"
      effect: "NoSchedule"

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
      tty: true

    - name: argocd
      image: argoproj/argocd:latest
      securityContext:
        runAsUser: 0
      command: ["/bin/sh"]
      args: ["-c", "sleep infinity"]
      tty: true

    - name: jnlp
      image: jenkins/inbound-agent:latest
      tty: true
"""
    }
  }

  environment {
    IMAGE_NAME = "192.168.0.10:31000/odoo18"
    IMAGE_TAG  = "${BUILD_NUMBER}"
    DOCKER_CRED_ID = "DOCKER_CREDS"
    ARGOCD_SERVER = "argocd-server.admin.svc"
    ARGOCD_APP_NAME = "odoo18"
    ARGOCD_CREDS = "ARGOCD_CREDS"
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Docker Login') {
      steps {
        container('docker') {
          withCredentials([usernamePassword(credentialsId: DOCKER_CRED_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh '''
              echo "$DOCKER_PASS" | docker login http://192.168.0.10:31000 \
              -u "$DOCKER_USER" --password-stdin
            '''
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

    stage('ArgoCD Sync') {
      steps {
        container('argocd') {
          withCredentials([usernamePassword(credentialsId: ARGOCD_CREDS, usernameVariable: 'ARGOCD_USER', passwordVariable: 'ARGOCD_PASS')]) {
            sh '''
              set -e

              echo "Logging into ArgoCD..."
              echo y | argocd login $ARGOCD_SERVER \
                --username $ARGOCD_USER \
                --password $ARGOCD_PASS \
                --insecure \
                --plaintext \
                --grpc-web

              echo "Updating Helm image tag for Odoo..."
              argocd app set $ARGOCD_APP_NAME \
                --helm-set image.repository=192.168.0.10:31000/odoo18 \
                --helm-set image.tag=$IMAGE_TAG

              echo "Syncing ArgoCD application..."
              argocd app sync $ARGOCD_APP_NAME --prune

              echo "Waiting for application to become healthy..."
              argocd app wait $ARGOCD_APP_NAME --health --timeout 300
            '''
          }
        }
      }
    }
  }

  post {
    success {
      echo "Odoo 18 CI/CD completed successfully!"
    }
    failure {
      echo "Odoo 18 pipeline failed."
    }
  }
}
