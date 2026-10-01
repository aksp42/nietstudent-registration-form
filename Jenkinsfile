// Declarative Jenkins Pipeline: Checkout -> Build -> Test
//
// EASY TO MODIFY:
//   * If your Jenkins machine uses "python" instead of "python3",
//     change PYTHON_CMD below.
//   * If Jenkins runs on Windows, replace each  sh  step with  bat
//     (the Build stage then needs "if exist" commands instead of the loop).

pipeline {
    agent any

    environment {
        PYTHON_CMD = 'python3'
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Checking out source code from SCM...'
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo 'Building Student Registration Project...'
                // A static HTML site has nothing to compile,
                // so "build" means: make sure every required file is present.
                sh '''
                    for f in index.html style.css script.js test.py; do
                        if [ -f "$f" ]; then
                            echo "Found: $f"
                        else
                            echo "ERROR: required file is missing: $f"
                            exit 1
                        fi
                    done
                '''
                echo 'Build stage completed. All required files are present.'
            }
        }

        stage('Test') {
            steps {
                echo 'Running automated tests...'
                sh "${PYTHON_CMD} test.py"
                echo 'Tests completed successfully.'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: The Student Registration pipeline passed.'
        }
        failure {
            echo 'FAILURE: The pipeline failed. Open the Console Output and read the line starting with the cross mark.'
        }
        always {
            echo 'Pipeline finished.'
        }
    }
}
