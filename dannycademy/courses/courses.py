import os

from flask import Blueprint, render_template, request, abort, redirect, url_for, flash
from flask_login import login_required, current_user

from dannycademy import db, app
from dannycademy.forms import UpdateCourseSettings
from dannycademy.main.main import urlCoursePics
from dannycademy.models import Course, Chapter, Exercise
from dannycademy.users.users import save_picture

courses = Blueprint('courses', __name__)


@courses.route('/edit', methods=['GET', 'POST'])
@login_required
def editCourse():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")

    id = request.args.get("courseId")
    current_course = Course.query.filter_by(id=id).first()

    if current_course is None:
        abort(404)

    form = UpdateCourseSettings()
    if form.validate_on_submit():
        if form.thumbnail.data:
            picture_file = save_picture(form.thumbnail.data, urlCoursePics, (500, 500))
            oldImg = current_course.thumbnail
            current_course.thumbnail = picture_file
            if oldImg != "default.jpg":
                os.remove(os.path.join(app.root_path, 'templates', urlCoursePics, oldImg))
        current_course.title = form.title.data
        db.session.commit()
    elif request.method == 'GET':
        form.title.data = current_course.title

    # chapters = Chapter.query.filter_by(course_id=id).order_by(Chapter.orderIndex.asc())
    items = Chapter.query.filter_by(course_id=id).all() + Exercise.query.filter_by(course_id=id).all()
    items.sort(key=lambda x: x.orderIndex)

    return render_template('editCourse.html', course=current_course, image_path=urlCoursePics, form=form,
                           items=items, Exercise=Exercise, Chapter=Chapter, isinstance=isinstance)

@courses.route('/publishCourse')
@login_required
def publishCourse():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")
    courseId = request.args.get("courseId")
    action = request.args.get("action")
    current_course = Course.query.filter_by(id=courseId).first()

    if action == "publish":
        current_course.published = True
        flash(
            f'Course "{current_course.title}" has been published. make sure to publish its chapters and exercises individually',
            'success')

    elif action == "unpublish":
        current_course.published = False
        # for chapter in Chapter.query.filter_by(course_id=courseId):
        #     chapter.published = False

        items = Chapter.query.filter_by(course_id=courseId).all() + Exercise.query.filter_by(course_id=courseId).all()
        items.sort(key=lambda x: x.orderIndex)
        for item in items:
            item.published = False

        flash(f'Course "{current_course.title}" and all of its chapters and exercises have been unpublished', 'success')
    else:
        abort(404)
    db.session.commit()
    return redirect(url_for("main.teach"))


@courses.route('/addCourse')
@login_required
def addCourse():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")
    myCourse = Course(title="enter course name here", author=current_user)
    db.session.add(myCourse)
    db.session.commit()
    return redirect("/edit?courseId=" + str(Course.query.all()[-1].id))  # get request


@courses.route('/viewCourse')
def viewCourse():
    courseId = request.args.get("courseId")
    current_course = Course.query.filter_by(id=courseId).first()
    if current_course is None or (
            not current_course.published and (not current_user.is_authenticated or current_user.role != "teacher")):
        abort(404)
    items = Chapter.query.filter_by(course_id=courseId).all() + Exercise.query.filter_by(course_id=courseId).all()
    items.sort(key=lambda x: x.orderIndex)
    # return render_template("viewCourse.html", course=current_course, image_path=urlCoursePics, chapters=chapters)
    return render_template('view-course.html', course=current_course, image_path=urlCoursePics,
                           items=items, Exercise=Exercise, Chapter=Chapter, isinstance=isinstance)


@courses.route('/deleteCourse', methods=['GET', 'POST'])
@login_required
def deleteCourse():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")
    id = request.args.get("courseId")
    current_course = Course.query.filter_by(id=id).first()

    if current_course is None:
        abort(404)

    if request.method == "POST":
        db.session.delete(current_course)
        db.session.commit()
        return redirect(url_for("main.teach"))
    else:
        return render_template("delete-course.html", course=current_course)
