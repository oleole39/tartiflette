import requests
import json
import datetime
import os

from .. import db

class UnlistedApp(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    owner = db.Column(db.String(64), nullable=False)
    description = db.Column(db.String(256))
    updated_days_ago = db.Column(db.Integer, default=-1)

    def __repr__(self):
        return '<UnlistedApp %r>' % self.name

    def init():
        pass

    def update():

        UnlistedApp.query.delete()

        official = json.loads(requests.get("https://raw.githubusercontent.com/YunoHost/apps/master/official.json").text)
        community = json.loads(requests.get("https://raw.githubusercontent.com/YunoHost/apps/master/community.json").text)

        known_apps = set()
        known_apps = known_apps.union([os.path.basename(app["url"]) for app in official.values() ])
        known_apps = known_apps.union([os.path.basename(app["url"]) for app in community.values() ])

        apps = []

        for i in range(1,7):

            print("Page " + str(i) + " ... ")
            r = requests.get("https://api.github.com/search/repositories?q=_ynh&sort=updated&per_page=100&page="+str(i))
            assert r.status_code == 200, r.text
            j = json.loads(r.text)
            print(str(len(j["items"])) + " items ")
            for item in j["items"]:

                if str(item["size"]) == "0":
                    continue

                if not item["name"].endswith("_ynh"):
                    continue

                if item["name"] in known_apps:
                    continue

                item["name"] = item["name"].replace("_ynh", "")

                app = UnlistedApp(name=item["name"],
                                  url=item["html_url"],
                                  owner=item["owner"]["login"],
                                  description=item["description"],
                                  updated_days_ago=githubDateToDaysAgo(item["updated_at"])
                )
                db.session.add(app)

        db.session.commit()

        #apps = sorted(apps, key=lambda x: x["updated_days_ago"])

        #for app in apps:
        #    if app["updated_days_ago"] > 100:
        #        continue
        #    print(app["name"] + " ... " + app["url"] + " ... " + str(app["updated_days_ago"]))

        #with open('apps.json', 'w') as f:
        #    json.dump(apps, f)


def githubDateToDaysAgo(date):
    now = datetime.datetime.now()
    date = datetime.datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
    return (now - date).days

