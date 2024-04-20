import requests as rq
import hashlib, json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
def login(username, password) -> str:
    loginUrl = "https://222.20.126.100:50188/api/login"
    password = hashlib.md5(password.encode()).hexdigest()
    headers = {
        'Authorization': 'Basic YmFpaG9uZ3NvZnQ6YmFpaG9uZ3NvZnQ=',
        'User-Agent': user_agent
    }
    res = rq.post(url=loginUrl, data={'username': username, 'password': password}, verify=False, headers=headers)
    if res.status_code == 200:
        res = json.loads(res.text)
        if res.get('status') == 500:
            raise Exception("登录失败: " + res.get('msg'))
        token = res.get('access_token')
        return token
    else:
        raise Exception("Login failed: " + res.text)

def get_all_courses(token) -> list:
    url = 'https://222.20.126.100:50188/api/course/info?level=1&pageIndex=1'
    headers = {
        'Authorization': 'Bearer ' + token,
        'User-Agent': user_agent,
    }
    res = rq.get(url, headers=headers, verify=False)
    if res.status_code == 200:
        res = json.loads(res.text)
        data = res['data']['data']
        courses = []
        for course in data:
            courses.append({
                'id': course['auto_id'],
                'name': course['course_name']
            })
        return get_course_chapters(token, courses)
    else:
        raise Exception("Get courses failed: " + res.text)

def get_course_chapters(token, courses) -> list:
    url = 'https://222.20.126.100:50188/api/course/chapter?courseId='

    headers = {
        'Authorization': 'Bearer ' + token,
        'User-Agent': user_agent,
    }

    for course in courses:
        res = rq.get(url + str(course['id']), headers=headers, verify=False)
        if res.status_code == 200:
            res = json.loads(res.text)
            data = res['data']['chapters']
            chapters = []
            for chapter in data:
                chapters.append({
                    'id': chapter['auto_id'],
                    'name': chapter['chapter_name'],
                    "is_complete": chapter["is_complete"]
                })
            course['chapters'] = chapters

        else:
            raise Exception("Get chapters failed: " + res.text)
    return courses

def get_exercises(token, chapter_id) -> list:
    url = 'https://222.20.126.100:50188/api/course/learningInfo?chapterId='
    headers = {
        'Authorization': 'Bearer ' + token,
        'User-Agent': user_agent,
    }
    res = rq.get(url + str(chapter_id), headers=headers, verify=False)
    if res.status_code == 200:
        res = json.loads(res.text)
        data = res['data']['exercises']
        questions = []
        for question in data:
           q = {
               "id": question["auto_id"],
               "info": question["question_answer_info"],
           }
           # 获取题目选项
           right_options = []
           childrens = question["childrens"]
           for child in childrens:
              if child["isanswers"]:
                 right_options.append(child["option"])

           q["right_options"] = right_options
           questions.append(q)
        return questions
    else:
        raise Exception("Get exercises failed: " + res.text)

def submit_answers(token, chapter_id, answers):
    url = "https://222.20.126.100:50188/api/course/submit-answers"
    headers = {
        'Authorization': 'Bearer ' + token,
        'User-Agent': user_agent,
    }
    data = {
        "answers": [],
        'chapterId': chapter_id
    }

    for answer in answers:
        data["answers"].append({
            "question_id": answer["id"],
            "student_option": str.join(",", answer["right_options"])
        })
    res = rq.post(url, headers=headers, data=json.dumps(data), verify=False)
    if res.status_code == 200:
        # 校验答案
        res = json.loads(res.text)
        answers = res["data"]["answers"]
        for answer in answers:
            if not answer["isRight"]:
                raise Exception("Submit answers failed: " + res.text)
        print("做题成功")
    else:
        raise Exception("Submit answers failed: " + res.text)
def pritty_print_courses(courses):
    for course in courses:
        print("id: " + str(course['id']) + "\tname: " + course['name'])
        for chapter in course['chapters']:
            print('\t' + "id: " + str(chapter['id']) + "\tname: " + chapter['name'] + "\tcompleted: " + str(chapter["is_complete"]))

def pritty_print_exercises(exercises):
    for exercise in exercises:
        # 如果info最后有换行符，这里会有一个空行, 所以要去掉
        if exercise["info"][-1] == "\n":
            exercise["info"] = exercise["info"][:-1]
        print("Question: " + exercise["info"])
        print("Answer: " + str.join(",", exercise["right_options"]))


