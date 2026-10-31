pipeline {
	agent any

	environment {
        IMAGE_NAME = "sivapprakash1634/library-management"
    }

	stages {
		stage('Checkout') {
			steps {
				checkout scm
			}
		}

		stage('Docker build') {
			steps {
				sh '''
                    docker build -t $IMAGE_NAME:v1 .
                '''
			}
		}
        stage('Docker login') {
            steps{
                withCredentials([
                    usernamePassword(
                        credentialsId: 'dockerhub-cred',
                        usernameVariable: 'DOCKER_USERNAME',
                        passwordVariable: 'DOCKER_PASSWORD'
                    )
                ]){
                    sh '''
                        set +x
                        echo $DOCKER_PASSWORD | docker login -u $DOCKER_USERNAME --password-stdin
                    '''
                }
            }
        }
        stage('Docker push') {
            steps{
                sh '''
                    docker push $IMAGE_NAME:v1
                '''
            }
        }
        stage('Docker run') {
            steps{
                sh '''
                    docker run -d --name library-management -p 9000:8000 $IMAGE_NAME:v1
                '''
            }
        }
	}

	post {
		success {
			echo 'Pipeline finished.'
		}
        failure {
            echo 'Pipeline failed.'
        }
        always {
            sh 'docker logout || true'
        }
	}
}