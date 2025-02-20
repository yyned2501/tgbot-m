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
      - 8880:9001 #supervisor管理端口
    tty: true
  redis:
    image: redis:latest
    container_name: redis
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data
    network_mode: bridge
```

首次启动后,可以进入config文件夹修改setting和launch

启动后 进宿主机控制台 `docker exec -it tgbot-m python login.py` 登录成功后可以正常运行。
