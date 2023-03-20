from flask import Flask, render_template, request, jsonify
import requests 
import json
import secrets
import os 

def jsongen(url):
    headers = {"X-Signature-Version": "web2","X-Signature": secrets.token_hex(32)}
    res = requests.get(url, headers=headers)
    y = json.loads(res.text)
    return y

def getlink(data):
    api = "https://api.cloud.altbalaji.com/media/"
    for x in data.split(" "):
        if "https://www.altbalaji.com/show" in x:
            id = x.split("/")[-1]
            return api+"series/"+id+"/seasons"
        elif "https://www.altbalaji.com/media/" in x:
            id = x.split("/")[-1]
            return api+"videos/"+id
       
def result(data):
    link = getlink(data)
    if "series" in link: # type: ignore
        jsonlink = jsongen(link)
        seasonlink = f"{link}/{str(jsonlink['seasons'][0]['id'])}/episodes?limit={str(jsonlink['seasons'][0]['episode_count'] + 10)}&order=asc"
        jsonseason = jsongen(seasonlink)
        episodesdata = []
        for x in jsonseason['episodes']:
            ep = {'id' : x['id'], 'title' : x['titles']['default'],}
            for s in x['streams']['web']:
                try:
                    if s['drm']['type'] == "widevine-dash":
                        ep.update({'stream' : s['src']})
                except:
                    pass
            episodesdata.append(ep)
        return episodesdata
    else:
        jsonlink = jsongen(link)
        videodata = {'id': jsonlink['id'],'title':jsonlink['titles']['default'],}
        for s in jsonlink['streams']['web']:
            try:
                if s['drm']['type'] == "widevine-dash":
                    videodata.update({'stream' : s['src']})
            except:
                pass
        return [videodata]

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['link']
        data = result(url)
        return render_template('cards.html', data = data)
    else:
        return render_template('index.html')



@app.route('/url',methods = ['GET'])
def url():
    link = request.args.get("u")
    data = result(link)
    return data,200

@app.route('/play',methods=['GET'])
def play():
    url = request.args.get("u")
    return render_template('results.html', url=url)

@app.route('/log',methods=["GET"])
def log():
    ip = request.args.get("ip")
    route = request.args.get("r")
    token = os.environ.get("TOKEN")
    chat = os.environ.get("CHAT")
    url = f"http://ip-api.com/json/{ip}"
    data = "mxplayer"+ "\n" + route + "\n" + str(jsongen(url))
    posturl = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat}&text={data}"
    requests.get(posturl)
    return "success!`" 


if __name__ == '__main__':
    app.run(debug=True, port=6000)