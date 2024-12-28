pipeline {
    agent any
    
    environment {
        // Use Python virtual environment
        VENV = 'venv'
    }
    
    stages {
        stage('Setup Python Virtual Environment') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            python -m venv ${VENV}
                            . ${VENV}/bin/activate
                            pip install -r requirements.txt
                        """
                    } else {
                        bat """
                            python -m venv ${VENV}
                            ${VENV}\\Scripts\\activate.bat
                            pip install -r requirements.txt
                        """
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh """
                            . ${VENV}/bin/activate
                            python run_tests.py
                        """
                    } else {
                        bat """
                            ${VENV}\\Scripts\\activate.bat
                            python run_tests.py
                        """
                    }
                }
            }
        }
    }
    
    post {
        always {
            // Clean up virtual environment
            cleanWs()
        }
        success {
            echo 'All tests passed successfully!'
        }
        failure {
            echo 'Tests failed! Check the test results for details.'
        }
    }
}
