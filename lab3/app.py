from flask import Flask, render_template, request, redirect, make_response
import pyodbc
import io
from xhtml2pdf import pisa
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

app = Flask(__name__)
username = None

# 连接数据库
conn_str = 'DRIVER={MySQL ODBC 8.0 Unicode Driver};SERVER=localhost:3306;DATABASE=db_lab3;UID=root;PWD=nwj_ustc;'
conn = pyodbc.connect(conn_str)

# 编码
sex = ('', '男', '女')
teacher_title = ('', '博士后', '助教', '讲师', '副教授', '特任教授', '教授', '助理研究员', '特任副研究员', '副研究员',
                 '特任研究员', '研究员')
paper_type = ('', 'full paper', 'short paper', 'poster paper', 'demo paper')
paper_level = ('', 'CCF-A', 'CCF-B', 'CCF-C', '中文CCF-A', '中文CCF-B', '无级别')
paper_corr = ('否', '是')
proj_type = ('', '国家级', '省部级', '市厅级', '企业合作', '其他类型')
course_semester = ('', '春季学期', '夏季学期', '秋季学期')
course_property = ('', '本科生课程', '研究生课程')


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def has_empty_value(dictionary):
    for value in dictionary.values():
        if value is None or value == "":
            return True
    return False


@app.route('/')
def start():  # put application's code here
    return redirect('/login')


@app.route('/login', methods=['GET', 'POST'])
def login():
    global username
    # 登录操作
    # request 包可以拿到浏览器传给服务器的所有数据
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == 'root' and password == 'root':
            print(username, password)
            # 登录成功之后应该跳转到管理页面
            return redirect('/admin')
        else:
            print(username, password)
            login_msg = '用户名或密码错误，请重试'
            return render_template('login.html', login_msg=login_msg, username=username)

    return render_template('login.html', username=username)


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        queryId = request.form.get('queryId')
        queryStart = request.form.get('queryStart')
        queryEnd = request.form.get('queryEnd')
        if queryId == "" or queryStart == "" or queryEnd == "":
            admin_msg = '输入不能为空，请重试'
            return render_template('admin.html', admin_msg=admin_msg, username=username)
        if "'" in queryId:
            admin_msg = '输入中不得有英文单引号，请重试'
            return render_template('admin.html', admin_msg=admin_msg, username=username)
        if int(queryStart) > int(queryEnd):
            admin_msg = '起始年份不得晚于终止年份，请重试'
            return render_template('admin.html', admin_msg=admin_msg, username=username)
        if int(queryStart) <= 1800 or int(queryEnd) <= 1800:
            admin_msg = '年份不得早于1800，请重试'
            return render_template('admin.html', admin_msg=admin_msg, username=username)
        # 执行查询操作，获取结果数据，这里假设你将结果存储在students变量中
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teacher WHERE id='{}'".format(queryId))
        teacher_info = cursor.fetchall()
        if len(teacher_info) == 0:
            admin_msg = '输入工号不存在，请检查'
            return render_template('admin.html', admin_msg=admin_msg, username=username)
        cursor.execute("SELECT course_id, name, teach_hours, year, semester FROM course, course_teach WHERE " \
                       "teacher_id='{}' AND course_id=id AND year BETWEEN '{}' AND '{}'"
                       .format(queryId, queryStart, queryEnd))
        course_info = cursor.fetchall()
        cursor.execute(
            "SELECT id, name, publish_source, publish_year, type, level, ranking, correspond FROM paper, publication WHERE " \
            "teacher_id='{}' AND paper_id=id AND YEAR(publish_year) BETWEEN '{}' AND '{}'"
            .format(queryId, queryStart, queryEnd))
        paper_info = cursor.fetchall()
        cursor.execute(
            "SELECT id, name, source, type, expenditure, start_year, finish_year, ranking, expense FROM " \
            "proj_undertake, project WHERE teacher_id='{}' AND proj_id=id AND (start_year<='{}' OR finish_year>='{}')"
            .format(queryId, queryEnd, queryStart))
        proj_info = cursor.fetchall()
        return render_template('export_template.html', teacher_info=teacher_info, course_info=course_info,
                               paper_info=paper_info, proj_info=proj_info, queryStart=queryStart, queryEnd=queryEnd,
                               sex=sex, title=teacher_title, paper_type=paper_type, paper_level=paper_level,
                               paper_corr=paper_corr, proj_type=proj_type, course_semester=course_semester,
                               course_property=course_property)

        # # 渲染HTML模板并传递查询结果数据
        # html = render_template('export_template.html', teacher_info=teacher_info, course_info=course_info,
        #                        paper_info=paper_info, proj_info=proj_info, queryStart=queryStart,
        #                        queryEnd=queryEnd,
        #                        sex=sex, title=teacher_title, paper_type=paper_type,
        #                        paper_level=paper_level,
        #                        paper_corr=paper_corr, proj_type=proj_type, course_semester=course_semester,
        #                        course_property=course_property)
        # # 创建一个字节流对象
        # result = io.BytesIO()
        #
        # # 注册 TrueType 字体
        # pdfmetrics.registerFont(TTFont('SimSun', 'SimSun.ttf'))
        #
        # # 使用 pisa 从 HTML 生成 PDF
        # pisa.CreatePDF(html, dest=result, font_config={'embeddedFonts': True, 'fontname': 'SimSun'})
        #
        # # 从字节流中获取 PDF 数据
        # pdf = result.getvalue()
        # result.close()
        #
        # # 返回 PDF 文件给用户进行下载
        # response = make_response(pdf)
        # response.headers['Content-Type'] = 'application/pdf'
        # response.headers['Content-Disposition'] = f'attachment; filename={queryId}.pdf'
        # return response

    return render_template('admin.html', username=username)


def render_teacher_table(table_content):
    # print(table_content)
    return render_template('root/teacher_table.html', table_content=table_content, sex=sex, title=teacher_title)


@app.route('/root/teachers', methods=['GET'])
def teachers():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM teacher")
    teachers = cursor.fetchall()
    cursor.close()
    teacher_table = render_teacher_table(teachers)
    # print('ok')
    return render_template('root/teachers.html', teacher_table=teacher_table, username=username)


@app.route('/get_table_data', methods=['POST'])
def get_table_data():
    # print(request.form)
    # req_dict = request.form.to_dict()
    if 'teacherQuery' in request.form:
        # 是 teacher 查询
        # print(request.form)
        queryId = request.form.get('queryId')
        queryName = request.form.get('queryName')
        querySex = request.form.get('querySex')
        queryTitle = request.form.get('queryTitle')
        sqlCommand = "SELECT * FROM teacher WHERE 1=1"
        if queryId != '' and "'" not in queryId:
            sqlCommand += " and id LIKE '%{}%'".format(queryId)
        if queryName != '' and "'" not in queryName:
            sqlCommand += " and name LIKE '%{}%'".format(queryName)
        if querySex != '...':
            sqlCommand += " and sex={}".format(sex.index(querySex))
        if queryTitle != '...':
            sqlCommand += " and title={}".format(teacher_title.index(queryTitle))
        # print(sqlCommand)
        cursor = conn.cursor()
        cursor.execute(sqlCommand)
        queryTeachers = cursor.fetchall()
        cursor.close()
        return render_teacher_table(queryTeachers)
    elif 'teacherCreateNew' in request.form:
        # 是 teacher 新建
        print(request.form)
        queryId = request.form.get('queryId')
        queryName = request.form.get('queryName')
        querySex = request.form.get('querySex')
        queryTitle = request.form.get('queryTitle')
        # 空id
        if queryId == '' or queryName == '' or querySex == "" or queryTitle == "":
            return 'ERROR: 输入不得为空'
        # SQL injection
        if "'" in queryId or "'" in queryName:
            return 'ERROR: 输入中不得有英文单引号'
        # 查是否有相同id
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM teacher WHERE id='{}'".format(queryId))
        res = cursor.fetchall()
        if len(res) != 0:
            return 'ERROR: 教师 ID 已存在'
        # 正常插入
        sqlCommand = "INSERT INTO teacher (id, name, sex, title) VALUES ('{}','{}',{},{})" \
            .format(queryId, queryName, sex.index(querySex), teacher_title.index(queryTitle))
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        cursor.execute("SELECT * FROM teacher")
        queryTeachers = cursor.fetchall()
        cursor.close()
        return render_teacher_table(queryTeachers)
    elif 'courseQuery' in request.form:
        # 是 course 查询
        print(request.form)
        queryId = request.form.get('queryId')
        queryName = request.form.get('queryName')
        queryTime = request.form.get('queryTime')
        queryProperty = request.form.get('queryProperty')
        sqlCommand = "SELECT * FROM course WHERE 1=1"
        if queryId != '' and "'" not in queryId:
            sqlCommand += " and id LIKE '%{}%'".format(queryId)
        if queryName != '' and "'" not in queryName:
            sqlCommand += " and name LIKE '%{}%'".format(queryName)
        if queryTime != '':
            sqlCommand += " and hours={}".format(queryTime)
        if queryProperty != '...':
            sqlCommand += " and property={}".format(course_property.index(queryProperty))
        print(sqlCommand)
        cursor = conn.cursor()
        cursor.execute(sqlCommand)
        queryCourses = cursor.fetchall()
        cursor.close()
        return render_course_table(queryCourses)
    elif 'courseCreateNew' in request.form:
        # 是 course 新建
        print(request.form)
        queryId = request.form.get('queryId')
        queryName = request.form.get('queryName')
        queryTime = request.form.get('queryTime')
        queryProperty = request.form.get('queryProperty')
        # 空id
        if queryId == '' or queryName == "" or queryTime == "" or queryProperty == "":
            return 'ERROR: 输入不得为空'
        # SQL injection
        if "'" in queryId or "'" in queryName:
            return 'ERROR: 输入中不得有英文单引号'
        # 查是否有相同id
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM course WHERE id='{}'".format(queryId))
        res = cursor.fetchall()
        if len(res) != 0:
            return 'ERROR: 课程 ID 已存在'
        # 学时必须是正整数
        if int(queryTime) <= 0:
            return 'ERROR: 学时必须是正整数'
        # 正常插入
        sqlCommand = "INSERT INTO course (id, name, hours, property) VALUES ('{}','{}',{},{})" \
            .format(queryId, queryName, queryTime, course_property.index(queryProperty))
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        cursor.execute("SELECT * FROM course")
        queryCourses = cursor.fetchall()
        cursor.close()
        return render_course_table(queryCourses)
    elif 'projectQuery' in request.form:
        # 是 project 查询
        print(request.form)
        queryId = request.form.get('queryId')
        queryName = request.form.get('queryName')
        querySource = request.form.get('querySource')
        queryType = request.form.get('queryType')
        queryExpenditure = request.form.get('queryExpenditure')
        queryStart_year = request.form.get('queryStart_year')
        queryFinish_year = request.form.get('queryFinish_year')
        sqlCommand = "SELECT * FROM project WHERE 1=1"
        if queryId != '' and "'" not in queryId:
            sqlCommand += " and id LIKE '%{}%'".format(queryId)
        if queryName != '' and "'" not in queryName:
            sqlCommand += " and name LIKE '%{}%'".format(queryName)
        if querySource != '' and "'" not in querySource:
            sqlCommand += " and source LIKE '%{}%'".format(querySource)
        if queryType != '...':
            sqlCommand += " and type={}".format(proj_type.index(queryType))
        if queryExpenditure != '':
            sqlCommand += " and expenditure='{}'".format(queryExpenditure)
        if queryStart_year != '':
            sqlCommand += " and start_year>={}".format(queryStart_year)
        if queryFinish_year != '':
            sqlCommand += " and finish_year<={}".format(queryFinish_year)
        print(sqlCommand)
        cursor = conn.cursor()
        cursor.execute(sqlCommand)
        queryProjects = cursor.fetchall()
        cursor.close()
        return render_project_table(queryProjects)
    elif 'projectCreateNew' in request.form:
        # 是 project 新建
        print(request.form)
        queryId = request.form.get('queryId')
        queryName = request.form.get('queryName')
        querySource = request.form.get('querySource')
        queryType = request.form.get('queryType')
        queryExpenditure = request.form.get('queryExpenditure')
        queryStart_year = request.form.get('queryStart_year')
        queryFinish_year = request.form.get('queryFinish_year')
        # 空id
        if queryId == '' or queryName == '' or querySource == '' or queryType == '' \
                or queryExpenditure == '' or queryStart_year == '' or queryFinish_year == '':
            return 'ERROR: 输入不得为空'
        # SQL injection
        if "'" in queryId or "'" in queryName or "'" in querySource:
            return 'ERROR: 输入中不得有英文单引号'
        if not is_float(queryExpenditure) or float(queryExpenditure) <= 0:
            return 'ERROR: 总经费必须是大于0的整数或小数'
        if int(queryStart_year) < 1958 or int(queryFinish_year) < 1958:
            return 'ERROR: 项目年份必须是1958年之后'
        if int(queryStart_year) > int(queryFinish_year):
            return 'ERROR: 项目开始年份不得晚于结束年份'
        # 查是否有相同id
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM project WHERE id='{}'".format(queryId))
        res = cursor.fetchall()
        if len(res) != 0:
            return 'ERROR: 项目 ID 已存在'
        # 正常插入
        sqlCommand = "INSERT INTO project (id, name, source, type, expenditure, start_year, finish_year) " \
                     "VALUES ('{}','{}','{}',{},{},{},{})" \
            .format(queryId, queryName, querySource, proj_type.index(queryType), queryExpenditure, queryStart_year,
                    queryFinish_year)
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        cursor.execute("SELECT * FROM project")
        queryProjects = cursor.fetchall()
        cursor.close()
        return render_project_table(queryProjects)
    elif 'paperQuery' in request.form:
        # 是 paper 查询
        print(request.form)
        queryId = request.form.get('queryId')
        queryName = request.form.get('queryName')
        querySource = request.form.get('querySource')
        queryYear = request.form.get('queryYear')
        queryType = request.form.get('queryType')
        queryLevel = request.form.get('queryLevel')
        queryAuthor = request.form.get('queryAuthor')
        sql_query = "select id, name, publish_source, publish_year, type, level, authors, corr_author " \
                    "from paper, (select paper_id, group_concat(new_name order by ranking) as authors from ( " \
                    "select paper_id, concat(name, '(', ranking, ')') as new_name, ranking from publication, teacher where teacher_id=id " \
                    ") temp group by paper_id) temp1," \
                    "(select paper_id, group_concat(name) as corr_author from publication left outer join teacher " \
                    "on teacher_id=id and correspond=1 group by paper_id) temp2 " \
                    "where id=temp1.paper_id and id=temp2.paper_id"
        # 创建临时视图
        cursor = conn.cursor()
        cursor.execute("DROP VIEW IF EXISTS paper_view")
        conn.commit()
        sql_create_view = "CREATE VIEW paper_view AS " + sql_query
        cursor.execute(sql_create_view)
        conn.commit()
        sqlCommand = "SELECT * FROM paper_view WHERE 1=1"
        if queryId != '' and "'" not in queryId:
            sqlCommand += " and id='{}'".format(queryId)
        if queryName != '' and "'" not in queryName:
            sqlCommand += " and name LIKE '%{}%'".format(queryName)
        if querySource != '' and "'" not in querySource:
            sqlCommand += " and publish_source LIKE '%{}%'".format(querySource)
        if queryYear != '':
            sqlCommand += " and publish_year='{}'".format(queryYear)
        if queryType != '...':
            sqlCommand += " and type={}".format(paper_type.index(queryType))
        if queryLevel != '...':
            sqlCommand += " and level={}".format(paper_level.index(queryLevel))
        if queryAuthor != '' and "'" not in queryAuthor:
            sqlCommand += " and authors LIKE '%{}%'".format(queryAuthor)
        print(sqlCommand)
        cursor = conn.cursor()
        cursor.execute(sqlCommand)
        queryPapers = cursor.fetchall()
        cursor.close()
        return render_paper_table(queryPapers)
    elif 'paperCreateNew' in request.form:
        # 是 paper 新建
        print(request.form)
        createId = request.form.get('createId')
        createName = request.form.get('createName')
        createPublish_source = request.form.get('createPublish_source')
        createPublish_year = request.form.get('createPublish_year')
        createType = request.form.get('createType')
        createLevel = request.form.get('createLevel')
        createAuthor = request.form.get('createAuthor')
        createRanking = request.form.get('createRanking')
        createCorrespond = request.form.get('createCorrespond')
        # 空id
        if createId == '' or createName == '' or createPublish_source == '' or createPublish_year == '' \
                or createType == '' or createLevel == '' or createAuthor == '' or createRanking == '' \
                or createCorrespond == '':
            return 'ERROR: 输入不得为空'
        # SQL injection
        if "'" in createId or "'" in createName or "'" in createPublish_source or "'" in createAuthor:
            return 'ERROR: 输入中不得有英文单引号'
        if int(createId) <= 0:
            return 'ERROR: 论文号必须为正整数'
        if int(createRanking) <= 0:
            return 'ERROR: 排名必须是正整数'
        # 查是否有相同id
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM paper WHERE id='{}'".format(createId))
        res = cursor.fetchall()
        if len(res) != 0:
            return 'ERROR: 论文 ID 已存在'

        # 判断作者是否存在以及重名
        cursor.execute(
            "SELECT * FROM teacher WHERE id='{}' OR name LIKE '%{}%'".format(createAuthor, createAuthor))
        res = cursor.fetchall()
        if len(res) == 0:
            return 'ERROR: 论文作者不存在'
        elif len(res) > 1:
            ret_str = 'ERROR: 重名引发歧义，请输入工号\n参考信息:\n'
            for item in res:
                ret_str += f'{item[0]}, {item[1]}, {sex[item[2]]}, {teacher_title[item[3]]}\n'
            # print(ret_str)
            return ret_str

        # 正常插入
        sqlCommand = "INSERT INTO paper (id, name, publish_source, publish_year, type, level) " \
                     "VALUES ({},'{}','{}','{}',{},{})" \
            .format(createId, createName, createPublish_source, createPublish_year, paper_type.index(createType),
                    paper_level.index(createLevel))
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        sqlCommand = "INSERT INTO publication (teacher_id, paper_id, ranking, correspond) VALUES ('{}',{},{},{})".format(
            res[0][0], createId, createRanking, paper_corr.index(createCorrespond))
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        sql_query = "select id, name, publish_source, publish_year, type, level, authors, corr_author " \
                    "from paper, (select paper_id, group_concat(new_name order by ranking) as authors from ( " \
                    "select paper_id, concat(name, '(', ranking, ')') as new_name, ranking from publication, teacher where teacher_id=id " \
                    ") temp group by paper_id) temp1, " \
                    "(select paper_id, group_concat(name) as corr_author from publication left outer join teacher " \
                    "on teacher_id=id and correspond=1 group by paper_id) temp2 " \
                    "where id=temp1.paper_id and id=temp2.paper_id "
        cursor.execute(sql_query)
        queryPaper_Teacher = cursor.fetchall()
        cursor.close()
        return render_paper_table(queryPaper_Teacher)
    elif 'projectTakeQuery' in request.form:
        # 是 projectTake 查询
        print(request.form)
        queryId = request.form.get('queryId')
        queryName = request.form.get('queryName')
        querySource = request.form.get('querySource')
        queryType = request.form.get('queryType')
        queryExpenditure = request.form.get('queryExpenditure')
        queryStart_year = request.form.get('queryStart_year')
        queryFinish_year = request.form.get('queryFinish_year')
        queryApplicant = request.form.get('queryApplicant')
        sql_query = "select id, name, source, type, expenditure, now_expend, start_year, finish_year, applicants " \
                    "from project, (select proj_id, group_concat(new_name order by ranking) as applicants from ( " \
                    "select proj_id, concat(name, '(', ranking, ')') as new_name, ranking from proj_undertake, teacher where teacher_id=id " \
                    ") temp group by proj_id) temp1, " \
                    "(select proj_id, round(sum(IFNULL(expense, 0)), 2) as now_expend from proj_undertake group by proj_id) temp2 " \
                    "where id=temp1.proj_id and id=temp2.proj_id"
        # 创建临时视图
        cursor = conn.cursor()
        cursor.execute("DROP VIEW IF EXISTS projectTake_view")
        conn.commit()
        sql_create_view = "CREATE VIEW projectTake_view AS " + sql_query
        cursor.execute(sql_create_view)
        conn.commit()
        sqlCommand = "SELECT * FROM projectTake_view WHERE 1=1"
        if queryId != '' and "'" not in queryId:
            sqlCommand += " and id LIKE '%{}%'".format(queryId)
        if queryName != '' and "'" not in queryName:
            sqlCommand += " and name LIKE '%{}%'".format(queryName)
        if querySource != '' and "'" not in querySource:
            sqlCommand += " and source LIKE '%{}%'".format(querySource)
        if queryType != '...':
            sqlCommand += " and type={}".format(proj_type.index(queryType))
        if queryExpenditure != '':
            sqlCommand += " and expenditure='{}'".format(queryExpenditure)
        if queryStart_year != '':
            sqlCommand += " and start_year>={}".format(queryStart_year)
        if queryFinish_year != '':
            sqlCommand += " and finish_year<={}".format(queryFinish_year)
        if queryApplicant != '' and "'" not in queryApplicant:
            sqlCommand += " and applicants LIKE '%{}%'".format(queryApplicant)
        print(sqlCommand)
        cursor = conn.cursor()
        cursor.execute(sqlCommand)
        queryProjectTake = cursor.fetchall()
        cursor.close()
        return render_projectTake_table(queryProjectTake)
    elif 'projectTakeCreateNew' in request.form:
        # 是 projectTake 新建
        print(request.form)
        createId = request.form.get('createId')
        createName = request.form.get('createName')
        createSource = request.form.get('createSource')
        createType = request.form.get('createType')
        createExpenditure = request.form.get('createExpenditure')
        createStart_year = request.form.get('createStart_year')
        createFinish_year = request.form.get('createFinish_year')
        createApplicant = request.form.get('createApplicant')
        createRanking = request.form.get('createRanking')
        createExpense = request.form.get('createExpense')
        # 空id
        if createId == '' or createName == '' or createSource == '' or createType == '' \
                or createExpenditure == '' or createStart_year == '' or createFinish_year == '' or createApplicant == '' \
                or createRanking == '' or createExpense == '':
            return 'ERROR: 输入不得为空'
        if "'" in createId or "'" in createName or "'" in createSource or "'" in createApplicant:
            return 'ERROR: 输入中不得有英文单引号'
        if not is_float(createExpenditure) or not is_float(createExpense) or float(createExpenditure) <= 0 or float(
                createExpense) <= 0:
            return 'ERROR: 总经费和承担经费必须为大于0的整数或小数'
        if int(createStart_year) < 1958 or int(createFinish_year) < 1958:
            return 'ERROR: 项目年份必须在1958年以后'
        if int(createStart_year) > int(createFinish_year):
            return 'ERROR: 项目开始年份不得晚于结束年份'
        if int(createRanking) <= 0:
            return 'ERROR: 排名必须为正整数'
        # 查是否有相同id
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM project WHERE id='{}'".format(createId))
        res = cursor.fetchall()
        if len(res) != 0:
            return 'ERROR: 项目 ID 已存在'

        # 判断教师是否存在以及重名
        cursor.execute(
            "SELECT * FROM teacher WHERE id='{}' OR name LIKE '%{}%'".format(createApplicant, createApplicant))
        res = cursor.fetchall()
        if len(res) == 0:
            return 'ERROR: 教师不存在'
        elif len(res) > 1:
            ret_str = 'ERROR: 重名引发歧义，请输入工号\n参考信息:\n'
            for item in res:
                ret_str += f'{item[0]}, {item[1]}, {sex[item[2]]}, {teacher_title[item[3]]}\n'
            # print(ret_str)
            return ret_str

        # 查承担经费是否超过项目总经费
        if createExpenditure < createExpense:
            return f'ERROR: 承担经费超过总经费！目前承担经费上限：{createExpenditure}'

        # 正常插入
        sqlCommand = "INSERT INTO project (id, name, source, type, expenditure, start_year, finish_year) " \
                     "VALUES ('{}','{}','{}',{},{},{},{})" \
            .format(createId, createName, createSource, proj_type.index(createType), createExpenditure,
                    createStart_year, createFinish_year)
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        sqlCommand = "INSERT INTO proj_undertake (teacher_id, proj_id, ranking, expense) VALUES ('{}','{}',{},{})" \
            .format(res[0][0], createId, createRanking, createExpense)
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        sql_query = "select id, name, source, type, expenditure, now_expend, start_year, finish_year, applicants " \
                    "from project, (select proj_id, group_concat(new_name order by ranking) as applicants from ( " \
                    "select proj_id, concat(name, '(', ranking, ')') as new_name, ranking from proj_undertake, teacher where teacher_id=id " \
                    ") temp group by proj_id) temp1, " \
                    "(select proj_id, round(sum(IFNULL(expense, 0)), 2) as now_expend from proj_undertake group by proj_id) temp2 " \
                    "where id=temp1.proj_id and id=temp2.proj_id"
        cursor.execute(sql_query)
        queryProj_Undertake = cursor.fetchall()
        cursor.close()
        return render_projectTake_table(queryProj_Undertake)
    elif 'courseTeachQuery' in request.form:
        # 是 courseTeach 查询
        print(request.form)
        queryId = request.form.get('queryId')
        queryName = request.form.get('queryName')
        queryHours = request.form.get('queryHours')
        queryProperty = request.form.get('queryProperty')
        queryYear = request.form.get('queryYear')
        querySemester = request.form.get('querySemester')
        queryLecturers = request.form.get('queryLecturers')
        sql_query = "select id, name, hours, now_hours, property, year, semester, lecturers, concat(id, ',', year, ',', semester) as PK " \
                    "from course, (select course_id, group_concat(new_name) as lecturers, year, semester from ( " \
                    "select course_id, concat(name, '(', teach_hours, ')') as new_name, year, semester from course_teach, teacher where teacher_id=id " \
                    ") temp group by course_id, year, semester) temp1, " \
                    "(select course_id, year as year2, semester as semester2, sum(IFNULL(teach_hours, 0)) as now_hours from course_teach group by course_id, year, semester) temp2 " \
                    "where id=temp1.course_id and id=temp2.course_id and temp1.year=temp2.year2 and temp1.semester=temp2.semester2"
        # 创建临时视图
        cursor = conn.cursor()
        cursor.execute("DROP VIEW IF EXISTS courseTeach_view")
        conn.commit()
        sql_create_view = "CREATE VIEW courseTeach_view AS " + sql_query
        cursor.execute(sql_create_view)
        conn.commit()
        sqlCommand = "SELECT * FROM courseTeach_view WHERE 1=1"
        if queryId != '' and "'" not in queryId:
            sqlCommand += " and id LIKE '%{}%'".format(queryId)
        if queryName != '' and "'" not in queryName:
            sqlCommand += " and name LIKE '%{}%'".format(queryName)
        if queryHours != '':
            sqlCommand += " and hours='{}'".format(queryHours)
        if queryProperty != '...':
            sqlCommand += " and property={}".format(course_property.index(queryProperty))
        if queryYear != '':
            sqlCommand += " and year='{}'".format(queryYear)
        if querySemester != '...':
            sqlCommand += " and semester={}".format(course_semester.index(querySemester))
        if queryLecturers != '' and "'" not in queryLecturers:
            sqlCommand += " and lecturers LIKE '%{}%'".format(queryLecturers)
        print(sqlCommand)
        cursor = conn.cursor()
        cursor.execute(sqlCommand)
        queryCourseTeach = cursor.fetchall()
        cursor.close()
        return render_courseTeach_table(queryCourseTeach)
    elif 'courseTeachCreateNew' in request.form:
        # 是 projectTake 新建
        print(request.form)
        createIDorName = request.form.get('createIDorName')
        createYear = request.form.get('createYear')
        createSemester = request.form.get('createSemester')
        createLecturer = request.form.get('createLecturer')
        createTeach_hours = request.form.get('createTeach_hours')
        # 空id/Name
        if createIDorName == '' or createYear == '' or createSemester == '' or createLecturer == '' \
                or createTeach_hours == '':
            return 'ERROR: 输入不得为空'
        if "'" in createIDorName or "'" in createLecturer:
            return 'ERROR: 输入中不得有英文单引号'
        if int(createYear) < 1958:
            return 'ERROR: 开课年份必须在1958年以后'
        if int(createTeach_hours) <= 0:
            return 'ERROR: 主讲学时必须为正整数'
        # 判断课程是否存在以及重名
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM course WHERE id='{}' OR name LIKE '%{}%'".format(createIDorName, createIDorName))
        res_course = cursor.fetchall()
        if len(res_course) == 0:
            return 'ERROR: 课程不存在！若想新建课程，请到“课程信息”页面操作'
        elif len(res_course) > 1:
            ret_str = 'ERROR: 课程重名引发歧义，请输入课程号\n参考信息:\n'
            for item in res_course:
                ret_str += f'{item[0]}, {item[1]}, {item[2]}, {course_property[item[3]]}\n'
            # print(ret_str)
            return ret_str

        # 判断该学年课程是否存在
        cursor.execute("SELECT * FROM course_teach WHERE course_id='{}' AND year='{}' AND semester='{}'"
                       .format(res_course[0][0], createYear, course_semester.index(createSemester)))
        res1 = cursor.fetchall()
        if len(res1) >= 1:
            return 'ERROR: 当前学年课程已存在！请通过编辑操作添加授课教师！'

        # 判断教师是否存在以及重名
        cursor.execute("SELECT * FROM teacher WHERE id='{}' OR name LIKE '%{}%'".format(createLecturer, createLecturer))
        res_teacher = cursor.fetchall()
        if len(res_teacher) == 0:
            return 'ERROR: 教师不存在'
        elif len(res_teacher) > 1:
            ret_str = 'ERROR: 教师重名引发歧义，请输入工号\n参考信息:\n'
            for item in res_teacher:
                ret_str += f'{item[0]}, {item[1]}, {sex[item[2]]}, {teacher_title[item[3]]}\n'
            # print(ret_str)
            return ret_str

        # 查主讲学时是否超过课程总学时
        cursor.execute("SELECT hours FROM course WHERE id='{}'".format(res_course[0][0]))
        tot_hour = cursor.fetchall()
        if int(createTeach_hours) > int(tot_hour[0][0]):
            return f'ERROR: 主讲学时超过课程总学时！主讲学时上限：{int(tot_hour[0][0])}'

        # 正常插入
        sqlCommand = "INSERT INTO course_teach (teacher_id, course_id, year, semester, teach_hours) VALUES ('{}','{}',{},{},{})" \
            .format(res_teacher[0][0], res_course[0][0], createYear, course_semester.index(createSemester),
                    createTeach_hours)
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        sql_query = "select id, name, hours, now_hours, property, year, semester, lecturers, concat(id, ',', year, ',', semester) as PK " \
                    "from course, (select course_id, group_concat(new_name) as lecturers, year, semester from ( " \
                    "select course_id, concat(name, '(', teach_hours, ')') as new_name, year, semester from course_teach, teacher where teacher_id=id " \
                    ") temp group by course_id, year, semester) temp1, " \
                    "(select course_id, year as year2, semester as semester2, sum(IFNULL(teach_hours, 0)) as now_hours from course_teach group by course_id, year, semester) temp2 " \
                    "where id=temp1.course_id and id=temp2.course_id and temp1.year=temp2.year2 and temp1.semester=temp2.semester2"
        cursor.execute(sql_query)
        queryCourseTeach = cursor.fetchall()
        cursor.close()
        return render_courseTeach_table(queryCourseTeach)
    return render_course_table(None)


@app.route('/delete_one', methods=['POST'])
def delete_one():
    # del_id 是一个字典
    del_id = request.get_json()
    print(del_id)
    cursor = conn.cursor()
    if 'teacher_id' in del_id:
        cursor.execute("DELETE FROM teacher WHERE id='{}'".format(del_id['teacher_id']))
        conn.commit()
    elif 'course_id' in del_id:
        cursor.execute("DELETE FROM course WHERE id='{}'".format(del_id['course_id']))
        conn.commit()
    elif 'project_id' in del_id:
        cursor.execute("DELETE FROM project WHERE id='{}'".format(del_id['project_id']))
        conn.commit()
    elif 'paper_id' in del_id:
        cursor.execute("DELETE FROM paper WHERE id={}".format(del_id['paper_id']))
        conn.commit()
    elif 'author_id' in del_id:
        cursor.execute("DELETE FROM publication WHERE teacher_id='{}' AND paper_id={}"
                       .format(del_id['author_id'], del_id['rel_paper_id']))
        conn.commit()
    elif 'applicant_id' in del_id:
        cursor.execute("DELETE FROM proj_undertake WHERE teacher_id='{}' AND proj_id='{}'"
                       .format(del_id['applicant_id'], del_id['rel_proj_id']))
        conn.commit()
    elif 'clear_applicant_id' in del_id:
        cursor.execute("DELETE FROM proj_undertake WHERE proj_id='{}'".format(del_id['clear_applicant_id']))
        conn.commit()
    elif 'lecturer_id' in del_id:
        course_id_, course_year_, course_semester_ = del_id['rel_PK'].split(',')
        cursor.execute(
            "DELETE FROM course_teach WHERE teacher_id='{}' AND course_id='{}' AND year='{}' AND semester='{}'"
            .format(del_id['lecturer_id'], course_id_, course_year_, course_semester_))
    elif 'remove_lecture_pk' in del_id:
        course_id_, course_year_, course_semester_ = del_id['remove_lecture_pk'].split(',')
        cursor.execute(
            "DELETE FROM course_teach WHERE course_id='{}' AND year='{}' AND semester='{}'"
            .format(course_id_, course_year_, course_semester_))

    cursor.close()
    return 'ok'


@app.route('/change_one', methods=['POST'])
def change_one():
    new_info = request.form.to_dict()
    # print(new_info)
    if has_empty_value(new_info):
        return 'ERROR: 输入不得为空'
    check_info = "".join(new_info)
    if "'" in check_info:
        return 'ERROR: 输入中不得有英文单引号'
    cursor = conn.cursor()
    if 'Sex' in new_info:
        # 是教师表
        cursor.execute("UPDATE teacher SET name='{}', sex={}, title={} WHERE id='{}'"
                       .format(new_info['Name'], sex.index(new_info['Sex']), teacher_title.index(new_info['Title']),
                               new_info['Id']))
    elif 'Property' in new_info:
        # 是课程表
        if int(new_info['Time']) <= 0:
            return 'ERROR: 学时必须是正整数'
        cursor.execute("UPDATE course SET name='{}', hours={}, property={} WHERE id='{}'"
                       .format(new_info['Name'], new_info['Time'], course_property.index(new_info['Property']),
                               new_info['Id']))
    elif 'Expenditure' in new_info:
        # 是项目表
        print(f'debug: new_info={new_info}')
        if not is_float(new_info['Expenditure']) or float(new_info['Expenditure']) <= 0:
            return 'ERROR: 总经费必须是大于0的整数或小数'
        if int(new_info['Start_year']) < 1958 or int(new_info['Finish_year']) < 1958:
            return 'ERROR: 项目年份必须在1958年以后'
        if int(new_info['Start_year']) > int(new_info['Finish_year']):
            return 'ERROR: 项目开始年份不得晚于结束年份'
        cursor.execute(
            "UPDATE project SET name='{}', source='{}', type={}, expenditure={}, start_year={}, finish_year={} WHERE id='{}'"
            .format(new_info['Name'], new_info['Source'], proj_type.index(new_info['Type']), new_info['Expenditure'],
                    new_info['Start_year'], new_info['Finish_year'], new_info['Id']))
    elif 'Level' in new_info:
        # 是论文表
        cursor.execute(
            "UPDATE paper SET name='{}', publish_source='{}', publish_year='{}', type={}, level={} WHERE id={}"
            .format(new_info['Name'], new_info['Publish_source'], new_info['Publish_year'],
                    paper_type.index(new_info['Type']), paper_level.index(new_info['Level']), new_info['Id']))
    conn.commit()
    cursor.close()
    return 'ok'


@app.route('/add_one', methods=['POST'])
def add_one():
    new_info = request.form.to_dict()
    print(new_info)
    if has_empty_value(new_info):
        return 'ERROR: 输入不得为空'
    check_info = "".join(new_info)
    if "'" in check_info:
        return 'ERROR: 输入中不得有英文单引号'
    if 'addAuthorRanking' in new_info:
        # 是新增 publication
        cursor = conn.cursor()
        # 空id
        if new_info['addAuthorIDorName'] == '':
            return 'ERROR: ID/姓名不得为空'
        # 判断作者是否存在以及重名
        cursor.execute("SELECT * FROM teacher WHERE id='{}' OR name LIKE '%{}%'".format(new_info['addAuthorIDorName'],
                                                                                        new_info['addAuthorIDorName']))
        res = cursor.fetchall()
        if len(res) == 0:
            return 'ERROR: 教师不存在'
        elif len(res) > 1:
            ret_str = 'ERROR: 重名引发歧义，请输入工号\n参考信息:\n'
            for item in res:
                ret_str += f'{item[0]}, {item[1]}, {sex[item[2]]}, {teacher_title[item[3]]}\n'
            # print(ret_str)
            return ret_str
        # 查是否有相同id
        cursor.execute("SELECT * FROM publication WHERE teacher_id='{}' AND paper_id={}"
                       .format(res[0][0], new_info['rel_paper_id']))
        res2 = cursor.fetchall()
        if len(res2) != 0:
            return 'ERROR: 该作者已存在'
        # 查是否已经有通讯作者
        if new_info['addAuthorCorr'] == '是':
            cursor.execute("SELECT * FROM publication WHERE correspond=1 AND paper_id={}"
                           .format(new_info['rel_paper_id']))
            temp = cursor.fetchall()
            if len(temp) != 0:
                return 'ERROR: 通讯作者已存在'
        # 查是否有排名冲突
        if int(new_info['addAuthorRanking']) <= 0:
            return 'ERROR: 排名必须为正整数'
        cursor.execute("SELECT * FROM publication WHERE ranking={} AND paper_id={}"
                       .format(new_info['addAuthorRanking'], new_info['rel_paper_id']))
        temp = cursor.fetchall()
        if len(temp) != 0:
            return 'ERROR: 排名冲突'
        # 正常插入
        sqlCommand = "INSERT INTO publication (teacher_id, paper_id, ranking, correspond) VALUES ('{}',{},{},{})" \
            .format(res[0][0], new_info['rel_paper_id'], new_info['addAuthorRanking'],
                    paper_corr.index(new_info['addAuthorCorr']))
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        # 实时更新作者详细信息
        cursor.execute(
            "SELECT id, name, ranking, correspond FROM publication, teacher WHERE paper_id={} AND id=teacher_id ORDER BY ranking"
            .format(new_info['rel_paper_id']))
        detailAuthor = cursor.fetchall()
        cursor.close()
        return render_author_list(detailAuthor, new_info['rel_paper_id'])
    elif 'addApplicantRanking' in new_info:
        # 是新增 proj_undertake
        cursor = conn.cursor()
        # 空id
        if new_info['addApplicantIDorName'] == '':
            return 'ERROR: ID/姓名不得为空'
        # 判断参与者是否存在以及重名
        cursor.execute(
            "SELECT * FROM teacher WHERE id='{}' OR name LIKE '%{}%'".format(new_info['addApplicantIDorName'],
                                                                             new_info['addApplicantIDorName']))
        res = cursor.fetchall()
        if len(res) == 0:
            return 'ERROR: 教师不存在'
        elif len(res) > 1:
            ret_str = 'ERROR: 重名引发歧义，请输入工号\n参考信息:\n'
            for item in res:
                ret_str += f'{item[0]}, {item[1]}, {sex[item[2]]}, {teacher_title[item[3]]}\n'
            # print(ret_str)
            return ret_str
        # 查是否重复添加
        cursor.execute("SELECT * FROM proj_undertake WHERE teacher_id='{}' AND proj_id='{}'"
                       .format(res[0][0], new_info['rel_proj_id']))
        res2 = cursor.fetchall()
        if len(res2) != 0:
            return 'ERROR: 该教师已是项目参与者'
        # 查是否有排名冲突
        if int(new_info['addApplicantRanking']) <= 0:
            return 'ERROR: 排名必须为正整数'
        cursor.execute("SELECT * FROM proj_undertake WHERE ranking={} AND proj_id='{}'"
                       .format(new_info['addApplicantRanking'], new_info['rel_proj_id']))
        temp = cursor.fetchall()
        if len(temp) != 0:
            return 'ERROR: 排名冲突'
        # 查承担经费是否已经超过项目剩余经费
        if not is_float(new_info['addApplicantExpense']) or float(new_info['addApplicantExpense']) <= 0:
            return 'ERROR: 承担经费必须是大于0的整数或小数'
        cursor.execute("SELECT sum(IFNULL(expense, 0)) AS now_expend FROM proj_undertake WHERE proj_id='{}'"
                       .format(new_info['rel_proj_id']))
        now_tot = cursor.fetchall()
        if now_tot[0][0] is None:
            now_tot[0][0] = 0.0
        cursor.execute("SELECT expenditure FROM project WHERE id='{}'"
                       .format(new_info['rel_proj_id']))
        tot = cursor.fetchall()
        print(f'now_tot = {now_tot}, tot = {tot}')
        if float(now_tot[0][0]) + float(new_info['addApplicantExpense']) > float(tot[0][0]):
            return f'ERROR: 承担经费超过剩余经费！目前承担经费上限：{float(tot[0][0]) - float(now_tot[0][0])}'
        # 正常插入
        sqlCommand = "INSERT INTO proj_undertake (teacher_id, proj_id, ranking, expense) VALUES ('{}','{}',{},{})" \
            .format(res[0][0], new_info['rel_proj_id'], new_info['addApplicantRanking'],
                    new_info['addApplicantExpense'])
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        # 实时更新参与者详细信息
        cursor.execute(
            "SELECT id, name, ranking, expense FROM proj_undertake, teacher WHERE proj_id='{}' AND id=teacher_id ORDER BY ranking"
            .format(new_info['rel_proj_id']))
        detailApplicant = cursor.fetchall()
        cursor.close()
        return render_applicant_list(detailApplicant, new_info['rel_proj_id'])
    elif 'lecturerTeach_hours' in new_info:
        # 是新增 course_teach
        course_id_, course_year_, course_semester_ = new_info['rel_PK'].split(',')
        cursor = conn.cursor()
        # 空id
        if new_info['lecturerIDorName'] == '':
            return 'ERROR: ID/姓名不得为空'
        # 判断参与者是否存在以及重名
        cursor.execute("SELECT * FROM teacher WHERE id='{}' OR name LIKE '%{}%'".format(new_info['lecturerIDorName'],
                                                                                        new_info['lecturerIDorName']))
        res = cursor.fetchall()
        if len(res) == 0:
            return 'ERROR: 教师不存在'
        elif len(res) > 1:
            ret_str = 'ERROR: 重名引发歧义，请输入工号\n参考信息:\n'
            for item in res:
                ret_str += f'{item[0]}, {item[1]}, {sex[item[2]]}, {teacher_title[item[3]]}\n'
            # print(ret_str)
            return ret_str
        # 查是否重复添加
        cursor.execute(
            "SELECT * FROM course_teach WHERE teacher_id='{}' AND course_id='{}' AND year='{}' AND semester='{}'"
            .format(res[0][0], course_id_, course_year_, course_semester_))
        res2 = cursor.fetchall()
        if len(res2) != 0:
            return 'ERROR: 该教师已在授课教师中'
        # 查主讲学时是否已经超过课程剩余学时
        if int(new_info['lecturerTeach_hours']) <= 0:
            return 'ERROR: 主讲学时必须为正整数'
        cursor.execute(
            "SELECT sum(IFNULL(teach_hours, 0)) AS now_hour FROM course_teach WHERE course_id='{}' AND year='{}' AND semester='{}'"
            .format(course_id_, course_year_, course_semester_))
        now_tot = cursor.fetchall()
        if now_tot[0][0] is None:
            now_tot[0][0] = 0
        cursor.execute("SELECT hours FROM course WHERE id='{}'"
                       .format(course_id_))
        tot = cursor.fetchall()
        print(f'now_tot = {now_tot}, tot = {tot}')
        if int(now_tot[0][0]) + int(new_info['lecturerTeach_hours']) > int(tot[0][0]):
            return f'ERROR: 主讲学时超过未分配学时！目前主讲学时上限：{int(tot[0][0]) - int(now_tot[0][0])}'
        # 正常插入
        sqlCommand = "INSERT INTO course_teach (teacher_id, course_id, year, semester, teach_hours) VALUES ('{}','{}','{}','{}','{}')" \
            .format(res[0][0], course_id_, course_year_, course_semester_, new_info['lecturerTeach_hours'])
        print(sqlCommand)
        cursor.execute(sqlCommand)
        conn.commit()
        # 实时更新授课教师详细信息
        cursor.execute("SELECT id, name, teach_hours FROM course_teach, teacher WHERE course_id='{}' AND year='{}' " \
                       "AND semester='{}' AND id=teacher_id"
                       .format(course_id_, course_year_, course_semester_))
        detailLecturer = cursor.fetchall()
        cursor.close()
        return render_lecturer_list(detailLecturer, new_info['rel_PK'])

    return render_author_list(None, new_info['rel_paper_id'])


@app.route('/get_detail', methods=['POST'])
def get_detail():
    get_id = request.get_json()
    print(get_id)
    if has_empty_value(get_id):
        return 'ERROR: 输入不得为空'
    check_get = "".join(get_id)
    if "'" in check_get:
        return 'ERROR: 输入中不得有英文单引号'
    cursor = conn.cursor()
    if 'paper_id' in get_id:
        # 查作者详细信息的
        cursor.execute(
            "SELECT id, name, ranking, correspond FROM publication, teacher WHERE paper_id={} AND id=teacher_id ORDER BY ranking"
            .format(get_id['paper_id']))
        detailAuthor = cursor.fetchall()
        cursor.close()
        return render_author_list(detailAuthor, get_id['paper_id'])
    elif 'proj_id' in get_id:
        # 查项目参与者详细信息的
        cursor.execute(
            "SELECT id, name, ranking, expense FROM proj_undertake, teacher WHERE proj_id='{}' AND id=teacher_id ORDER BY ranking"
            .format(get_id['proj_id']))
        detailApplicant = cursor.fetchall()
        cursor.close()
        return render_applicant_list(detailApplicant, get_id['proj_id'])
    elif 'lecture_PK' in get_id:
        # 查授课教师详细信息的
        course_id_, course_year_, course_semester_ = get_id['lecture_PK'].split(',')
        cursor.execute("SELECT id, name, teach_hours FROM course_teach, teacher WHERE course_id='{}' AND year='{}' " \
                       "AND semester='{}' AND id=teacher_id"
                       .format(course_id_, course_year_, course_semester_))
        detailLecturer = cursor.fetchall()
        cursor.close()
        return render_lecturer_list(detailLecturer, get_id['lecture_PK'])


def render_course_table(table_content):
    # print(table_content)
    return render_template('root/course_table.html', table_content=table_content, property=course_property)


@app.route('/root/courses')
def courses():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM course")
    courses = cursor.fetchall()
    print(courses)
    cursor.close()
    course_table = render_course_table(courses)
    return render_template('root/courses.html', course_table=course_table, username=username)


def render_project_table(table_content):
    # print(table_content)
    return render_template('root/project_table.html', table_content=table_content, proj_type=proj_type)


@app.route('/root/projects')
def projects():
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM project")
    projects = cursor.fetchall()
    # print(projects)
    cursor.close()
    project_table = render_project_table(projects)
    return render_template('root/projects.html', project_table=project_table, username=username)


def render_paper_table(table_content):
    # print(table_content)
    return render_template('root/paper_table.html', table_content=table_content, paper_type=paper_type,
                           paper_level=paper_level)


def render_author_list(list_content, rel_paper_id):
    print(list_content)
    return render_template('root/author_list.html', list_content=list_content, rel_paper_id=rel_paper_id,
                           paper_corr=paper_corr)


@app.route('/root/papers')
def papers():
    cursor = conn.cursor()
    sql_query = "select id, name, publish_source, publish_year, type, level, authors, corr_author " \
                "from paper, (select paper_id, group_concat(new_name order by ranking) as authors from ( " \
                "select paper_id, concat(name, '(', ranking, ')') as new_name, ranking from publication, teacher where teacher_id=id " \
                ") temp group by paper_id) temp1, " \
                "(select paper_id, group_concat(name) as corr_author from publication left outer join teacher " \
                "on teacher_id=id and correspond=1 group by paper_id) temp2 " \
                "where id=temp1.paper_id and id=temp2.paper_id "
    cursor.execute(sql_query)
    papers = cursor.fetchall()
    # print(papers)
    cursor.close()
    paper_table = render_paper_table(papers)
    return render_template('root/papers.html', paper_table=paper_table, username=username)


def render_projectTake_table(table_content):
    # print(table_content)
    return render_template('root/projectTake_table.html', table_content=table_content, proj_type=proj_type)


def render_applicant_list(list_content, rel_proj_id):
    # print(list_content)
    return render_template('root/applicant_list.html', list_content=list_content, rel_proj_id=rel_proj_id)


@app.route('/root/projectTake')
def projectTake():
    cursor = conn.cursor()
    sql_query = "select id, name, source, type, expenditure, now_expend, start_year, finish_year, applicants " \
                "from project, (select proj_id, group_concat(new_name order by ranking) as applicants from ( " \
                "select proj_id, concat(name, '(', ranking, ')') as new_name, ranking from proj_undertake, teacher where teacher_id=id " \
                ") temp group by proj_id) temp1, " \
                "(select proj_id, round(sum(IFNULL(expense, 0)), 2) as now_expend from proj_undertake group by proj_id) temp2 " \
                "where id=temp1.proj_id and id=temp2.proj_id"
    cursor.execute(sql_query)
    projectTake = cursor.fetchall()
    # print(papers)
    cursor.close()
    projectTake_table = render_projectTake_table(projectTake)
    return render_template('root/projectTake.html', projectTake_table=projectTake_table, username=username)


def render_courseTeach_table(table_content):
    # print(table_content)
    return render_template('root/courseTeach_table.html', table_content=table_content, course_property=course_property,
                           course_semester=course_semester)


def render_lecturer_list(list_content, rel_PK):
    # print(list_content)
    return render_template('root/lecturer_list.html', list_content=list_content, rel_PK=rel_PK)


@app.route('/root/courseTeach')
def courseTeach():
    cursor = conn.cursor()
    sql_query = "select id, name, hours, now_hours, property, year, semester, lecturers, concat(id, ',', year, ',', semester) as PK " \
                "from course, (select course_id, group_concat(new_name) as lecturers, year, semester from ( " \
                "select course_id, concat(name, '(', teach_hours, ')') as new_name, year, semester from course_teach, teacher where teacher_id=id " \
                ") temp group by course_id, year, semester) temp1, " \
                "(select course_id, year as year2, semester as semester2, sum(IFNULL(teach_hours, 0)) as now_hours from course_teach group by course_id, year, semester) temp2 " \
                "where id=temp1.course_id and id=temp2.course_id and temp1.year=temp2.year2 and temp1.semester=temp2.semester2"
    cursor.execute(sql_query)
    courseTeach = cursor.fetchall()
    # print(papers)
    cursor.close()
    courseTeach_table = render_courseTeach_table(courseTeach)
    return render_template('root/courseTeach.html', courseTeach_table=courseTeach_table, username=username)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
