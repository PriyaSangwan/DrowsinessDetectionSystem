from flask import Flask, render_template, Response,jsonify
from camera import Video
from threading import Thread

app = Flask(__name__)
app_not_done=True
@app.route('/')
def index():
    return render_template('desc.html')

def gen(camera):
    # thread=Thread(target=camera.get_frame)
    # thread.daemon=True
    # thread.start()
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type:  image/jpeg\r\n\r\n' + frame +
               b'\r\n\r\n')
@app.route('/update')
def update():
    return jsonify(var=v.get_var())


@app.route('/video')
def video():
    return Response(gen(v),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == "__main__":
    v = Video('camera_thread')
    v.daemon = True
    v.start()
    app.run(debug=True)
    v.join()
