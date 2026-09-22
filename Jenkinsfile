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

        stage('Fetch Tags') {
            steps {
                bat 'git fetch --tags --force'
            }
        }

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

                    def tagStatus = bat(
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

                    def commit = bat(
                        script: "git rev-list -n 1 v${params.VERSION}",
                        returnStdout: true
                    ).trim()

                    echo "Selected commit: ${commit}"
                }
            }
        }

        stage('Build Docker Image') {
            steps {

                bat "docker build -t retail-app:${params.VERSION} ."

                echo "Built image: retail-app:${params.VERSION}"
            }
        }

        stage('Record Previous Image') {
            steps {
                script {

                    def result = bat(
                        script: 'docker ps --filter "name=retail-app" --format "{{.Image}}"',
                        returnStdout: true
                    ).trim()

                    env.OLD_IMAGE = result

                    echo "Previous image: ${env.OLD_IMAGE}"
                }
            }
        }

        stage('Start New Version') {
            steps {

                bat "docker rm -f retail-app-new 2>nul || exit /b 0"

                bat "docker run -d --name retail-app-new -p 8081:8081 retail-app:${params.VERSION}"

                echo "Started new version: retail-app:${params.VERSION}"
            }
        }

        stage('Health Check') {
            steps {
                script {

                    sleep 5

                    def status = bat(
                        script: 'docker inspect -f "{{.State.Health.Status}}" retail-app-new',
                        returnStdout: true
                    ).trim()

                    echo "Health status: ${status}"

                    if (!status.contains('healthy')) {
                        error('Health check failed')
                    }

                    echo "Health check passed"
                }
            }
        }

        stage('Complete Deployment') {
            steps {
                script {

                    bat 'docker rm -f retail-app 2>nul || exit /b 0'

                    bat 'docker rename retail-app-new retail-app'

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

                bat 'docker rm -f retail-app-new 2>nul || exit /b 0'

                if (env.OLD_IMAGE?.trim()) {

                    bat "docker run -d --name retail-app -p 8081:8081 ${env.OLD_IMAGE}"

                    echo "Restored old version: ${env.OLD_IMAGE}"
                }

                echo "FINAL STATE: ROLLBACK REQUIRED"
            }
        }
    }
}