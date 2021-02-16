from urllib.parse import unquote

from flask import Blueprint, request, render_template, abort, redirect, flash
from flask_login import current_user, login_required

from dannycademy import db
from dannycademy.forms import UpdateChapterForm
from dannycademy.models import Course, Chapter, Exercise

chapters = Blueprint('chapters', __name__)


@chapters.route('/viewChapter')
def viewChapter():
    courseId = request.args.get("courseId")
    chapterId = request.args.get("chapterId")
    current_course = Course.query.filter_by(id=courseId).first()
    current_chapter = Chapter.query.filter_by(id=chapterId).first()

    if current_course is None or current_chapter is None or (
            (not current_course.published or not current_chapter.published) and (
            not current_user.is_authenticated or current_user.role != "teacher")):
        abort(404)
    # chapters = Chapter.query.filter_by(course_id=courseId)
    return render_template("view-chapter.html", course=current_course, chapter=current_chapter)


@chapters.route('/publishChapter')
@login_required
def publishChapter():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")

    chapterId = request.args.get("chapterId")
    courseId = request.args.get("courseId")
    action = request.args.get("action")
    current_chapter = Chapter.query.filter_by(id=chapterId).first()
    current_course = Course.query.filter_by(id=courseId).first()

    if current_chapter is None or current_course is None:
        abort(404)

    if action == "publish":
        if not current_course.published:
            flash(f'Error. Please publish the course before publishing the chapter', 'danger')
            return redirect("edit?courseId=" + str(current_course.id))
        current_chapter.published = True
    elif action == "unpublish":
        current_chapter.published = False
    else:
        abort(404)
    db.session.commit()
    flash(f'Chapter {current_chapter.title} has been {action}ed', 'success')
    return redirect("edit?courseId=" + str(current_course.id))


@chapters.route('/editChapter', methods=['GET', 'POST'])
@login_required
def editChapter():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")

    chapterId = request.args.get("chapterId")
    courseId = request.args.get("courseId")
    current_chapter = Chapter.query.filter_by(id=chapterId).first()
    current_course = Course.query.filter_by(id=courseId).first()

    if current_chapter is None or current_course is None:
        abort(404)
    form = UpdateChapterForm()

    if request.method == "POST":
        current_chapter.title = form.title.data
        db.session.commit()
    else:
        form.title.data = current_chapter.title

    print("debug2: " + current_chapter.content)
    return render_template("edit-chapter.html", chapter=current_chapter, course=current_course, form=form)


@chapters.route('/addChapter')
@login_required
def addChapter():
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

    if items:
        lastIndex = items[-1].orderIndex
    else:
        lastIndex = 1

    myChapter = Chapter(title="enter chapter name here", course_id=id, orderIndex=lastIndex + 1)
    db.session.add(myChapter)
    db.session.commit()
    # return redirect(f"/editChapter?courseId={id}&chapterId={str(myChapter.query.all()[-1].id)}")  # get request
    return redirect("edit?courseId=" + str(id))


@chapters.route('/deleteChapter')
@login_required
def deleteChapter():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")

    chapterId = request.args.get("chapterId")
    courseId = request.args.get("courseId")
    current_chapter = Chapter.query.filter_by(id=chapterId).first()
    current_course = Course.query.filter_by(id=courseId).first()

    if current_chapter is None or current_course is None:
        abort(404)

    db.session.delete(current_chapter)
    db.session.commit()

    return redirect("edit?courseId=" + str(courseId))


@chapters.route('/moveChapter')
@login_required
def moveChapter():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")

    courseId = request.args.get("courseId")
    chapterId = request.args.get("chapterId")
    action = request.args.get("action")
    current_course = Course.query.filter_by(id=courseId).first()
    current_chapter = Chapter.query.filter_by(id=chapterId).first()
    items = Chapter.query.filter_by(course_id=courseId).all() + Exercise.query.filter_by(course_id=courseId).all()
    items.sort(key=lambda x: x.orderIndex)
    i = items.index(current_chapter)

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



@chapters.route('/saveContent')
@login_required
def saveContent():
    if current_user.role != "teacher":
        return render_template("need-to-be-a-teacher.html")
    content = unquote(request.args.get("content"))
    print("debug: " + content)
    chapterId = request.args.get("chapterId")
    courseId = request.args.get("courseId")

    current_chapter = Chapter.query.filter_by(id=chapterId).first()
    current_course = Course.query.filter_by(id=courseId).first()

    if current_chapter is None or current_course is None:
        abort(404)

    current_chapter.content = content
    db.session.commit()
    return redirect(f"/editChapter?chapterId={chapterId}&courseId={courseId}")
