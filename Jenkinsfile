pipeline {
    agent any
    
    environment {
        // Use Python virtual environment
        VENV = 'venv'
        PYTHON_VERSION = '3.11.0'  // Specify desired Python version
        CONDA_HOME = "${WORKSPACE}/python_install/miniconda3"
        PATH = "${CONDA_HOME}/bin:${PATH}"
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
                                
                                # Create local installation directory
                                mkdir -p ${WORKSPACE}/python_install
                                cd ${WORKSPACE}/python_install
                                
                                # Download and install Miniconda (includes Python)
                                wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
                                bash miniconda.sh -b -p ${WORKSPACE}/python_install/miniconda3
                                
                                # Add to PATH
                                export PATH="${WORKSPACE}/python_install/miniconda3/bin:$PATH"
                                
                                # Install required packages
                                conda install -y python=3.11 pip
                            else
                                echo "Python3 found:"
                                python3 --version
                            fi
                            
                            # Ensure pip is available
                            if ! command -v pip3 &> /dev/null; then
                                curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                                python3 get-pip.py --user
                            fi
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
                                # Initialize conda
                                eval "\$(${CONDA_HOME}/bin/conda 'shell.bash' 'hook')"
                                
                                # Create and activate conda environment
                                conda create -y -p "${WORKSPACE}/${VENV}" python=3.11
                                conda activate "${WORKSPACE}/${VENV}"
                                
                                # Install requirements
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
                                eval "\$(${CONDA_HOME}/bin/conda 'shell.bash' 'hook')"
                                conda activate "${WORKSPACE}/${VENV}"
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
                    sh """
                        eval "\$(${CONDA_HOME}/bin/conda 'shell.bash' 'hook')"
                        conda deactivate
                        conda env remove -p "${WORKSPACE}/${VENV}" -y
                        rm -rf "${WORKSPACE}/python_install"
                    """
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
