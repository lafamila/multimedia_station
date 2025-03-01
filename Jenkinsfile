pipeline {
	// 어떤 젠킨스 agent가 이 파이프라인을 처리할지 설정
    agent any

    // 환경 변수들 설정
    environment {
        GITHUB_URL = 'https://github.com/lafamila/multimedia_station.git'
        GITHUB_CRED_ID = 'github-token'
        GITHUB_BRANCH = 'main'
        REPO_TAG = 'multimedia-station'
        CONTAINER_NAME = 'multimedia-station'
        DB_USER = credentials('console-db-user')
        DB_PASSWORD = credentials('console-db-password')
        DB_SCHEME = credentials('mom-db-scheme')
        DB_PORT = credentials('console-db-port')
        DB_HOST = credentials('console-db-host')
    }
    stages {
    	// 깃허브 소스코드를 가져오는 부분
        stage('Clone') {
            steps {
                echo 'Clone start'
                // git plugin을 사용하여 레포지토리 코드를 클론
                git branch: GITHUB_BRANCH, credentialsId: GITHUB_CRED_ID, url: GITHUB_URL
                sh 'ls'
                echo 'Clone end'
            }
        }

        // test용 Dockerfile(Dockerfile.test)을 빌드하고 실행한다.
        // unit test를 실행하여 테스트가 실패하면 여기서 파이프라인이 종료된다.
        // stage('Test') {
        //     steps {
        //         echo 'Test start'
        //         sh 'docker build -f Dockerfile.test -t test-image .'
        //         sh 'docker run test-image'
        //         echo 'Test end'
        //     }
        // }

        // 배포용 이미지를 빌드한다.
        // 그리고 image tag 명령어로 latest tag말고 BUILD_NUMBER tag도 달아준다.
        // BUILD_NUMBER는 젠킨스의 빌드넘버다. 등록한 파이프라인을 몇 번 실행했냐라고 보면 된다.
        stage('Build') {
            steps {
                echo 'Build start'
                sh 'docker image build -t $REPO_TAG:latest .'
                sh 'docker image tag $REPO_TAG:latest $REPO_TAG:$BUILD_NUMBER'
                echo 'Build end'
            }
        }


        // 서버에 컨테이너를 실행하여 Flask 서버를 배포한다.
        // BUILD_NUMBER가 1일 경우(파이프라인 첫 번째 실행) 컨테이너를 실행만 하고
        // BUILD_NUMBER가 1이 아니면 기존 컨테이너를 중단, 삭제한 후 실행한다.
        stage('Deploy') {
            steps {
                echo 'Deploy start'
                script{
                    try{
                        sh 'docker stop $CONTAINER_NAME'
                        sh 'docker rm $CONTAINER_NAME'
                    } catch (Exception e) {
                        echo 'No container name: $CONTAINER_NAME'
                    }

                    sh 'docker run --name $CONTAINER_NAME -d --network host -e DB_USER=$DB_USER -e DB_PASSWORD=$DB_PASSWORD -e DB_HOST=$DB_HOST -e DB_PORT=$DB_PORT -e DB_SCHEME=$DB_SCHEME -p 20021:20021 $REPO_TAG'
                }
                echo 'Deploy end'
            }
        }
    }
}