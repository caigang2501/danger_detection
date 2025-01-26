echo "正在复制"
mv /home/user/caigang/danger_detection/models /home/user/caigang/models
rm -rf /home/user/caigang/danger_detection
unzip /home/user/caigang/danger_detection.zip -d /home/user/caigang/danger_detection/
mkdir /home/user/caigang/danger_detection/data
mv /home/user/caigang/models /home/user/caigang/danger_detection/models

echo "正在删除"
cid=$(docker ps | grep mydanger_detection | awk '{print $1}')
if [ -n "$cid" ]; then
  docker stop "$cid"
else
  echo "No container found for mydanger_detection."
fi
docker rm "${cid}"
docker rmi danger_detection

echo "构建并启动"
docker build -t danger_detection /home/user/caigang/danger_detection/
docker run -d -p 8088:5000 -v /home/user/caigang/data:/danger_detection/data --name mydanger_detection danger_detection
echo "完成!!!"

# chmod +x /home/user/caigang/danger_detection.sh

