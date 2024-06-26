import course
with open("config", "r") as f:
    username = f.readline().strip()
    password = f.readline().strip()
    if not username or not password:
        print("没有配置用户名和密码")
        exit(1)

access_token = course.login(username, password)
print("access_token: ", access_token)

courses = course.get_all_courses(access_token)
course.pritty_print_courses(courses)

# needs_do = [79, 80, 247, 86, 276, 114, 115, 116, 117, 118, 119]
needs_do = []
# 先让needs_do为空, 运行一次, 看看有哪些章节, 然后输入需要做的章节id
# 然后再运行一次, 就会自动做这些章节
for do_id in needs_do:
    answers = course.get_exercises(access_token, do_id)
    course.pritty_print_exercises(answers)
    course.submit_answers(access_token, do_id, answers)
