pipeline {
  agent {
    kubernetes {
      defaultContainer 'builder'
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
    - name: builder
      image: alpine:3.20
      tty: true
      securityContext:
        privileged: true
      env:
        - name: DOCKER_TLS_CERTDIR
          value: ""
      command:
        - sh
        - -c
        - |
          apk add --no-cache docker-cli curl bash git
          curl -fsSL https://get.helm.sh/helm-v3.14.4-linux-amd64.tar.gz | tar -xz
          mv linux-amd64/helm /usr/local/bin/helm

          dockerd-entrypoint.sh \
            --host=unix:///var/run/docker.sock \
            --host=tcp://0.0.0.0:2375 \
            --insecure-registry=192.168.0.10:31000 &

          sleep infinity
      resources:
        requests:
          ephemeral-storage: "10Gi"
        limits:
          ephemeral-storage: "20Gi"
      volumeMounts:
        - name: docker-graph
          mountPath: /var/lib/docker

    - name: jnlp
      image: jenkins/inbound-agent:latest
      tty: true

  volumes:
    - name: docker-graph
      emptyDir: {}
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
        container('builder') {
          withCredentials([usernamePassword(credentialsId: DOCKER_CRED_ID, usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
            sh 'echo "$DOCKER_PASS" | docker login http://192.168.0.10:31000 -u "$DOCKER_USER" --password-stdin'
          }
        }
      }
    }

    stage('Build Image') {
      steps {
        container('builder') {
          sh 'docker build -t $IMAGE_NAME:$IMAGE_TAG .'
        }
      }
    }

    stage('Push Image') {
      steps {
        container('builder') {
          sh 'docker push $IMAGE_NAME:$IMAGE_TAG'
        }
      }
    }

    stage('Deploy with Helm') {
      steps {
        container('builder') {
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
