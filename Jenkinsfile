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
            defaultValue: '1.0.1',
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

        stage('Check Git') {
            steps {
                bat 'where git'
                bat 'git --version'
            }
        }

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

                        error(
                            'Production deployment requires CONFIRM_PROD = YES'
                        )
                    }

                    if (!params.VERSION?.trim()) {
                        error('VERSION is required')
                    }

                    def tagStatus = bat(
                        script: "git rev-parse --verify refs/tags/v${params.VERSION}",
                        returnStatus: true
                    )

                    if (tagStatus != 0) {
                        error(
                            "Version v${params.VERSION} does not exist"
                        )
                    }

                    echo "================================="
                    echo "DEPLOYMENT CONFIGURATION"
                    echo "================================="
                    echo "Action      : ${params.DEPLOYMENT_ACTION}"
                    echo "Environment : ${params.ENVIRONMENT}"
                    echo "Version     : ${params.VERSION}"
                    echo "Git Tag     : v${params.VERSION}"
                    echo "================================="
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
            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                bat """
                    docker build -t retail-app:${params.VERSION} .
                """

                echo "Built image: retail-app:${params.VERSION}"
            }
        }

        stage('Verify Docker Image') {
            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                bat """
                    docker image inspect retail-app:${params.VERSION}
                """

                echo "Docker image exists"
            }
        }

        stage('Record Previous Image') {
            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    def oldImage = bat(
                        script: """
                            docker ps --filter "name=retail-app" --format "{{.Image}}"
                        """,
                        returnStdout: true
                    ).trim()

                    env.OLD_IMAGE = oldImage

                    echo "Previous image: ${env.OLD_IMAGE}"
                }
            }
        }

        stage('Start New Version') {
            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                bat """
                    docker rm -f retail-app-new >nul 2>&1 || exit /b 0
                """

                bat """
                    docker run -d ^
                    --name retail-app-new ^
                    -p 8094:8081 ^
                    retail-app:${params.VERSION}
                """

                echo "Started new version"
            }
        }

        stage('Health Check') {
            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    sleep 5

                    def status = bat(
                        script: """
                            docker inspect -f "{{.State.Health.Status}}" retail-app-new
                        """,
                        returnStdout: true
                    ).trim()

                    echo "Health status: ${status}"

                    if (status != 'healthy') {

                        error(
                            "Health check failed. Status: ${status}"
                        )
                    }
                }
            }
        }

        stage('Complete Deployment') {
            when {
                expression {
                    params.DEPLOYMENT_ACTION == 'DEPLOY'
                }
            }

            steps {

                script {

                    bat """
                        docker rm -f retail-app >nul 2>&1 || exit /b 0
                    """

                    bat """
                        docker rename retail-app-new retail-app
                    """

                    echo "================================="
                    echo "DEPLOYMENT SUCCESSFUL"
                    echo "================================="
                    echo "Old image : ${env.OLD_IMAGE}"
                    echo "New image : retail-app:${params.VERSION}"
                    echo "================================="
                }
            }
        }
    }

    post {

        failure {

            script {

                echo "Deployment failed. Starting automatic rollback..."

                bat """
                    docker rm -f retail-app-new >nul 2>&1 || exit /b 0
                """

                if (env.OLD_IMAGE?.trim()) {

                    bat """
                        docker rm -f retail-app >nul 2>&1 || exit /b 0
                    """

                    bat """
                        docker run -d ^
                        --name retail-app ^
                        -p 8094:8081 ^
                        ${env.OLD_IMAGE}
                    """

                    echo "Restored old image: ${env.OLD_IMAGE}"

                } else {

                    echo "No previous image found. Nothing to restore."
                }

                echo "FINAL STATE: ROLLBACK REQUIRED"
            }
        }

        success {

            echo "FINAL STATE: DEPLOYMENT SUCCESSFUL"
        }
    }
}