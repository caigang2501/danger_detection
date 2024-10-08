import sys,os,socket
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flask import Flask
from appname.views import danger_dtc

def create_app():
    app = Flask(__name__)

    # 注册 Blueprint
    app.register_blueprint(danger_dtc.bp)

    return app

if __name__ == "__main__":
    if 'WINDOWS' in socket.gethostname():
        create_app().run(debug=True)
    else:
        create_app().run()

