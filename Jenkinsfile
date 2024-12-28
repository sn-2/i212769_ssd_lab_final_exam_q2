pipeline {
    agent any
    
    environment {
        // Use Python virtual environment
        VENV = 'venv'
        PYTHON_VERSION = '3.11.0'  // Specify desired Python version
    }
    
    stages {
        stage('Check/Install Python') {
            steps {
                script {
                    if (isUnix()) {
                        // Linux environment
                        sh '''
                            if ! command -v python3 &> /dev/null; then
                                echo "Python not found. Installing Python..."
                                if command -v apt &> /dev/null; then
                                    # Debian/Ubuntu
                                    sudo apt-get update
                                    sudo apt-get install -y python3 python3-pip python3-venv
                                elif command -v yum &> /dev/null; then
                                    # CentOS/RHEL
                                    sudo yum update -y
                                    sudo yum install -y python3 python3-pip
                                else
                                    echo "Unsupported package manager"
                                    exit 1
                                fi
                            fi
                            python3 --version
                        '''
                    } else {
                        // Windows environment
                        bat '''
                            where python > nul 2>&1
                            if %errorlevel% neq 0 (
                                echo Python not found. Installing Python...
                                curl -o python_installer.exe https://www.python.org/ftp/python/%PYTHON_VERSION%/python-%PYTHON_VERSION%-amd64.exe
                                python_installer.exe /quiet InstallAllUsers=1 PrependPath=1
                                del python_installer.exe
                            )
                            python --version
                        '''
                    }
                }
            }
        }
        stage('Setup Python Virtual Environment') {
            steps {
                script {
                    try {
                        if (isUnix()) {
                            sh """
                                # Ensure pip and venv are available
                                python3 -m ensurepip --upgrade || true
                                python3 -m pip install --upgrade pip
                                python3 -m pip install virtualenv
                                
                                # Create and activate virtual environment
                                python3 -m venv ${VENV}
                                . ${VENV}/bin/activate
                                pip install --no-cache-dir -r requirements.txt
                            """
                        } else {
                            bat """
                                :: Ensure pip and venv are available
                                python -m ensurepip --upgrade
                                python -m pip install --upgrade pip
                                python -m pip install virtualenv
                                
                                :: Create and activate virtual environment
                                python -m venv ${VENV}
                                call ${VENV}\\Scripts\\activate.bat
                                pip install --no-cache-dir -r requirements.txt
                            """
                        }
                    } catch (Exception e) {
                        error "Failed to setup Python environment: ${e.message}"
                    }
                }
            }
        }
        
        stage('Run Tests') {
            steps {
                script {
                    try {
                        if (isUnix()) {
                            sh """
                                . ${VENV}/bin/activate
                                python run_tests.py
                            """
                        } else {
                            bat """
                                call ${VENV}\\Scripts\\activate.bat
                                python run_tests.py
                                if %errorlevel% neq 0 exit /b %errorlevel%
                            """
                        }
                    } catch (Exception e) {
                        error "Test execution failed: ${e.message}"
                    }
                }
            }
        }
    }
    
    post {
        always {
            script {
                // Clean up virtual environment
                if (isUnix()) {
                    sh "rm -rf ${VENV}"
                } else {
                    bat "rmdir /s /q ${VENV}"
                }
                cleanWs()
            }
        }
        success {
            echo 'All tests passed successfully!'
        }
        failure {
            echo 'Tests failed! Check the test results for details.'
            error 'Test execution failed'
        }
    }
}
