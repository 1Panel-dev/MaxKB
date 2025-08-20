# 安装单个包
pip install --target /opt/maxkb-data/maxkb-python-packages numpy

# 安装多个包
pip install --target /opt/maxkb-data/maxkb-python-packages numpy pandas requests scikit-learn

# 从requirements.txt安装
pip install --target /opt/maxkb-data/maxkb-python-packages -r requirements.txt



# 查看已安装的包
ls -la /opt/maxkb-data/maxkb-python-packages/

# 重启容器测试持久化
docker restart gs-backend


现在当您更新容器版本时：
停止旧容器：docker stop gs-backend
运行新版本部署脚本：./deploy-interactive.sh
依赖自动保留：所有在 /opt/maxkb-data/maxkb-python-packages 中的依赖包会自动挂载到新容器