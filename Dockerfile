FROM danger_dtc_env1

WORKDIR /danger_detection

COPY . .
# pip install 

EXPOSE 5000

ENV FLASK_APP=appname.app.py

CMD ["flask", "run", "--host=0.0.0.0"]

# scp D:\workspace\hb_projects\danger_detection\main.py user@10.83.190.141:caigang/danger_detection/main.py R8z@6cDY
# docker build -t danger_detection .
# docker save -o danger_detection.tar danger_detection
# scp danger_env.tar user@10.83.190.141:caigang/ 
# docker load -i danger_detection.tar
# unzip /tmp/danger_detection.zip -d /gcph/pythonData/

# docker run -d -p 8088:5000  --name mydanger_detection danger_detection
# docker run
#    -d -p 8088:5000
#    -v /tmp/python_logs:/danger_detection/example/output
#    --name mydanger_detection danger_detection
#    --network gp_network

# docker run -it -p 5010:5000 danger_detection bash
# docker exec -it mydanger_detection /bin/sh            进入容器
# exit or ctrl+d                                    退出
