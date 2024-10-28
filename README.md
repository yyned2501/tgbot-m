docker-compose.yml
```docker-compose.yml
services:
  tgbot-m:
    image: yyned2501/git-python:3.12
    container_name: tgbot-m
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./sessions:/app/sessions
    environment:
      - TZ=Asia/Shanghai
      - GIT_REMOTE=https://github.com/yyned2501/tgbot-m.git
      - GIT_BRANCH=master
      - SUPERVISOR_USERNAME=admin
      - SUPERVISOR_PASSWORD=admin
    network_mode: bridge
    working_dir: /app
    ports:
      - 8880:5001 #supervisor管理端口
    tty: true
```
启动后
