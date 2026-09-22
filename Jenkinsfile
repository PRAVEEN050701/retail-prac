pipeline {
    agent any

    parameters {
        choice(
            name: 'DEPLOYMENT_ACTION',
            choices: ['DEPLOY', 'ROLLBACK'],
            description: 'What should Jenkins do?'
        )

        choice(
            name: 'ENVIRONMENT',
            choices: ['UAT', 'PRODUCTION'],
            description: 'Where should we deploy?'
        )

        string(
            name: 'VERSION',
            description: 'Version to deploy'
        )

        choice(
            name: 'CONFIRM_PROD',
            choices: ['NO', 'YES'],
            description: 'Confirm production deployment'
        )
    }

    environment {
        OLD_IMAGE = ''
    }

    stages {

        stage('Validate') {
            steps {
                script {
                    if (params.ENVIRONMENT == 'PRODUCTION' &&
                        params.CONFIRM_PROD != 'YES') {
                        error('Production deployment requires CONFIRM_PROD = YES')
                    }

                    if (!params.VERSION?.trim()) {
                        error('VERSION is required')
                    }

                    def tagStatus = sh(
                        script: "git rev-parse --verify refs/tags/v${params.VERSION}",
                        returnStatus: true
                    )

                    if (tagStatus != 0) {
                        error("Version v${params.VERSION} does not exist")
                    }

                    echo "Action: ${params.DEPLOYMENT_ACTION}"
                    echo "Environment: ${params.ENVIRONMENT}"
                    echo "Version: ${params.VERSION}"
                    echo "Production confirmation: ${params.CONFIRM_PROD}"
                    echo "Git tag v${params.VERSION} exists"
                }
            }
        }

        stage('Identify Commit') {
            steps {
                script {
                    def commit = sh(
                        script: "git rev-list -n 1 v${params.VERSION}",
                        returnStdout: true
                    ).trim()

                    echo "Selected commit: ${commit}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t retail-app:${params.VERSION} ."
                echo "Built image: retail-app:${params.VERSION}"
            }
        }

        stage('Record Previous Image') {
            steps {
                script {
                    env.OLD_IMAGE = sh(
                        script: "docker ps --filter name=retail-app --format '{{.Image}}'",
                        returnStdout: true
                    ).trim()

                    echo "Previous production image: ${env.OLD_IMAGE}"
                }
            }
        }

        stage('Start New Version') {
            steps {
                sh "docker run -d --name retail-app-new -p 8081:8081 retail-app:${params.VERSION}"
                echo "Started new version: retail-app:${params.VERSION}"
            }
        }

        stage('Health Check') {
            steps {
                script {
                    sleep 5

                    def status = sh(
                        script: "docker inspect -f '{{.State.Health.Status}}' retail-app-new",
                        returnStdout: true
                    ).trim()

                    echo "Health status: ${status}"

                    if (status != 'healthy') {
                        error('Health check failed')
                    }
                }
            }
        }

        stage('Complete Deployment') {
            steps {
                script {
                    sh "docker stop retail-app || true"
                    sh "docker rm retail-app || true"

                    sh "docker rename retail-app-new retail-app"

                    echo "Old version: ${env.OLD_IMAGE}"
                    echo "New version: retail-app:${params.VERSION}"
                    echo "FINAL STATE: DEPLOYMENT SUCCESSFUL"
                }
            }
        }
    }

    post {
        failure {
            script {
                echo "Deployment failed. Starting automatic rollback..."

                sh "docker stop retail-app-new || true"
                sh "docker rm retail-app-new || true"

                if (env.OLD_IMAGE?.trim()) {
                    sh "docker run -d --name retail-app -p 8081:8081 ${env.OLD_IMAGE}"
                    echo "Restored old version: ${env.OLD_IMAGE}"
                }

                echo "FINAL STATE: ROLLBACK REQUIRED"
            }
        }
    }
}