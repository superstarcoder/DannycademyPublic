from urllib.parse import unquote

from flask import Blueprint, request, render_template, abort, redirect, flash
from flask_login import current_user, login_required

from dannycademy import db
from dannycademy.forms import UpdateExerciseForm
from dannycademy.models import Course, Chapter, Exercise

from urllib import parse

exercises = Blueprint('exercises', __name__)


@exercises.route('/addExercise')
@login_required
def addExercise():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")
    id = request.args.get("courseId")
    current_course = Course.query.filter_by(id=id).first()

    if current_course is None:
        abort(404)

    # figure out the orderIndex:
    # f = Chapter.query.filter_by(course_id=id).order_by(Chapter.orderIndex.asc()).all()
    items = Chapter.query.filter_by(course_id=id).all() + Exercise.query.filter_by(course_id=id).all()
    items.sort(key=lambda x: x.orderIndex)

    # print("f is: " + str(f))
    if items:
        lastIndex = items[-1].orderIndex
    else:
        lastIndex = 1

    myExercise = Exercise(title="enter exercise name here", course_id=id, orderIndex=lastIndex + 1)
    db.session.add(myExercise)
    db.session.commit()
    # return redirect(f"/editChapter?courseId={id}&chapterId={str(myChapter.query.all()[-1].id)}")  # get request
    return redirect("edit?courseId=" + str(id))


@exercises.route('/deleteExercise')
@login_required
def deleteExercise():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")

    exerciseId = request.args.get("exerciseId")
    courseId = request.args.get("courseId")
    current_exercise = Exercise.query.filter_by(id=exerciseId).first()
    current_course = Course.query.filter_by(id=courseId).first()

    if current_exercise is None or current_course is None:
        abort(404)

    db.session.delete(current_exercise)
    db.session.commit()

    return redirect("edit?courseId=" + str(courseId))


@exercises.route('/publishExercise')
@login_required
def publishExercise():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")

    exerciseId = request.args.get("exerciseId")
    courseId = request.args.get("courseId")
    action = request.args.get("action")
    current_exercise = Exercise.query.filter_by(id=exerciseId).first()
    current_course = Course.query.filter_by(id=courseId).first()

    if current_exercise is None or current_course is None:
        abort(404)

    if action == "publish":
        if not current_course.published:
            flash(f'Error. Please publish the course before publishing the exercise', 'danger')
            return redirect("edit?courseId=" + str(current_course.id))
        current_exercise.published = True
    elif action == "unpublish":
        current_exercise.published = False
    else:
        abort(404)
    db.session.commit()
    flash(f'Exercise {current_exercise.title} has been {action}ed', 'success')
    return redirect("edit?courseId=" + str(current_course.id))


@exercises.route('/editExercise', methods=['GET', 'POST'])
@login_required
def editExercise():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")

    exerciseId = request.args.get("exerciseId")
    courseId = request.args.get("courseId")
    current_exercise = Exercise.query.filter_by(id=exerciseId).first()
    current_course = Course.query.filter_by(id=courseId).first()

    if current_exercise is None or current_course is None:
        abort(404)
    form = UpdateExerciseForm()

    if request.method == "POST":
        current_exercise.title = form.title.data
        current_exercise.content = form.content.data
        current_exercise.checker = unquote(form.checker.data)
        db.session.commit()
    else:
        form.title.data = current_exercise.title
        form.content.data = current_exercise.content
        form.checker.data = current_exercise.checker

    form.checker.data = unquote(form.checker.data)
    return render_template("edit-exercise.html", exercise=current_exercise, course=current_course, form=form)


@exercises.route('/moveExercise')
@login_required
def moveExercise():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")

    courseId = request.args.get("courseId")
    exerciseId = request.args.get("exerciseId")
    action = request.args.get("action")
    current_course = Course.query.filter_by(id=courseId).first()
    current_exercise = Exercise.query.filter_by(id=exerciseId).first()
    # chapters = Chapter.query.filter_by(course_id=courseId).order_by(Chapter.orderIndex.asc()).all()
    items = Chapter.query.filter_by(course_id=courseId).all() + Exercise.query.filter_by(course_id=courseId).all()
    items.sort(key=lambda x: x.orderIndex)
    i = items.index(current_exercise)

    # if list is too small
    if len(items) <= 1:
        return redirect("/edit?courseId=" + courseId)

    if action == "up":
        if i == 0:
            return redirect("/edit?courseId=" + courseId)
        else:
            temp = items[i].orderIndex
            items[i].orderIndex = items[i - 1].orderIndex
            items[i - 1].orderIndex = temp
            db.session.commit()
            return redirect("/edit?courseId=" + courseId)
    elif action == "down":
        if i == len(items) - 1:
            return redirect("/edit?courseId=" + courseId)
        else:
            temp = items[i].orderIndex
            items[i].orderIndex = items[i + 1].orderIndex
            items[i + 1].orderIndex = temp
            db.session.commit()
            return redirect("/edit?courseId=" + courseId)
    else:
        abort(404)
