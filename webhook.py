from flask import Flask, request, abort
#from discordBot import 

app = Flask(__name__)

@app.route("/announcement", methods=["POST"])
def annnouncement():
    if request.method == "POST":
        print(request.json)
        return "success", 200
    else:
        abort(400)

@app.route("/gallery")
def gallery():
    return "Hello!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050)
