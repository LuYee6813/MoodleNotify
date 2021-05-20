import requests
import datetime
import time
import os
from lotify.client import Client


def moodle_notify():
    lotify = Client()
    moodleToken = os.environ.get("MOODLE_TOKEN")
    lineToken = os.environ.get("LINE_TOKEN")
    url = f"{os.environ.get('MOODLE_URL','https://moodle.ntust.edu.tw/')}webservice/rest/server.php"
    currentTime = int(time.time())
    dayTime = 86400
    GMT8 = 28800
    params = {"moodlewsrestformat": "json",
              "wsfunction": "core_webservice_get_site_info", "wstoken": moodleToken}
    userId = requests.get(url, params).json()["userid"]
    params["wsfunction"] = "core_enrol_get_users_courses"
    params["userid"] = userId
    courses = requests.get(url, params).json()
    params["wsfunction"] = "core_course_get_contents"
    params.pop("userid")
    typeParams = {"moodlewsrestformat": "json", "wstoken": moodleToken}
    for course in courses:
        params["courseid"] = course["id"]
        courseContent = requests.get(url, params).json()
        for i in courseContent:
            modules = i["modules"]
            for module in modules:
                if module.get("contents") == None:
                    continue
                for content in module["contents"]:
                    if int(content["timemodified"]) >= currentTime-dayTime:
                        lotify.send_message(
                            lineToken, f"{course['fullname']}\n{content['modplural']}: {module['name']}\nCheck it on moodle")
        # assignments notify
        typeParams["wsfunction"] = "mod_assign_get_assignments"
        typeParams["courseids[0]"] = course["id"]
        assignments = requests.get(url, typeParams).json()[
            "courses"][0]["assignments"]
        for assingment in assignments:
            if int(assingment["timemodified"]) >= currentTime-dayTime:
                dueDate = datetime.datetime.utcfromtimestamp(
                    int(assingment['duedate'])+GMT8).strftime('%Y-%m-%d %H:%M:%S')
                lotify.send_message(
                    lineToken, f"{course['fullname']}\n作業: {assingment['name']}\nDue: {dueDate}\nCheck it on moodle")
        # quiz notify
        typeParams["wsfunction"] = "mod_quiz_get_quizzes_by_courses"
        quizzes = requests.get(url, typeParams).json()["quizzes"]
        for quiz in quizzes:
            if currentTime <= int(quiz["timeclose"]) and currentTime >= int(quiz["timeopen"]):
                closeTime = datetime.datetime.utcfromtimestamp(
                    int(assingment['timeclose'])+GMT8).strftime('%Y-%m-%d %H:%M:%S')
                lotify.send_message(
                    lineToken, f"{course['fullname']}\n考試: {quiz['name']}\nClose time: {closeTime}\nCheck it on moodle")


if __name__ == "__main__":
    moodle_notify()
