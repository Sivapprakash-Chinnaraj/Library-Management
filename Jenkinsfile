pipeline {
	agent any

	environment {
        IMAGE_NAME = "sivapprakash1634/library-management"
        CONTAINER_NAME = "library-management"
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
                    docker build -t $IMAGE_NAME .
                '''
			}
		}
        stage('Docker login') {
            steps{
                withCredentials([
                    usernamePassword(
                        credentialsId: 'Library-Management-Cred',
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
                    docker push $IMAGE_NAME
                '''
            }
        }
        stage('Docker run') {
            steps{
                sh '''
                    docker rm -f $CONTAINER_NAME || true
                    docker run -d --name $CONTAINER_NAME -p 6969:8000 $IMAGE_NAME
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
