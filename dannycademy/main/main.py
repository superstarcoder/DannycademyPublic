
from flask import render_template, send_from_directory, Blueprint, request
from dannycademy.models import Course
from dannycademy import main
from flask_login import current_user, login_required
from dannycademy import sandbox


main = Blueprint('main', __name__)

urlProfilePics = "assets/img/profile_pics"
urlCoursePics = "assets/img/courses"


@main.route('/')
@main.route('/home')
def index():
    return render_template('index.html', Course=Course, image_path=urlCoursePics)


@main.route('/courses')
def courses():
    return render_template('courses.html', Course=Course, image_path=urlCoursePics)


@main.route('/codeEditor')
def codeEditor():
    return render_template('code-editor.html')


@main.route('/about')
def about():
    return render_template('about.html')


@main.route('/teach')
@login_required
def teach():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")
    return render_template('teach.html', Courses=Course.query.filter_by(author=current_user),
                           image_path=urlCoursePics)


@main.route('/run')
def run():
    code = request.args.get("code")
    result = sandbox.run(code.encode("utf_8"))
    print("result")
    output = result["stdout"].decode("utf-8")
    error = result["stderr"].decode("utf-8")

    if result['timeout']:
        error += "your code took too long to execute"

    print("the error is:", error)
    print("the output is:", output)
    print("""
    <script>
        myConsole.setValue("%s");
    </script>
    """ % (output + error))

    return ("""
    <script>
        myConsole.setValue(String.raw`%s`);
    </script>
    """ % (output + error))


@main.route('/src-noconflict/<path:path>')
def ace(path):
    return send_from_directory('templates/src-noconflict', path)


@main.route('/assets/<path:path>')
def assets(path):
    return send_from_directory('templates/assets', path)


@main.route('/Components/<path:path>')
def Components(path):
    return send_from_directory('templates/Components', path)
