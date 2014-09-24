from flask.ext.babel import gettext
from flask.ext.login import login_required, current_user
from flask import Blueprint, render_template, request, g, abort, flash, redirect, url_for

from werkzeug import secure_filename

from elasticsearch import TransportError
from sqlalchemy import and_

from math import ceil
import hashlib, os

from aleph.datastore import es
from aleph.utils import humansize
from aleph.webui import app
from aleph.webui.forms import SubmitSampleForm
from aleph.webui.models import Submission, User
from aleph.webui.database import db


mod = Blueprint('samples', __name__, url_prefix='/samples')

@mod.route('/')
@mod.route('/index')
@mod.route('/index/<int:page>')
@login_required
def index(page = 1):

    samples = []
    es_samples = None
    page_offset = (app.config.get('ITEMS_PER_PAGE')*(page-1))

    if 'search' in request.args:
        # @@ FIXME <- INJECTION PRONE!!!
        query = request.args['search']
        sample_count = es.count(query)
        es_samples = es.lucene_search(query, start=page_offset, size=app.config.get('ITEMS_PER_PAGE'))
    else:
        es_samples = es.all(size=app.config.get('ITEMS_PER_PAGE'), start=page_offset)
        sample_count = es.count()

    for s in es_samples['hits']['hits']:
        samples.append(s['_source'])

    page_count = int(ceil(sample_count/app.config.get('ITEMS_PER_PAGE')))
    if page_count <= 1:
        page_count = 1
    pages = range(1, page_count+1)
    return render_template('samples/index.html', sample_count=sample_count, samples=samples, pages=pages, page=page)


@mod.route('/view/<uuid>')
@login_required
def view(uuid):

    g.current_lang = 'pt'
    try:
        sample = es.get(uuid)
        xrefs = sample['xrefs']
        xrefs_objs = {}
        for relation, rel_xrefs in xrefs.iteritems():
            for xref in rel_xrefs:
                xrefs_objs[xref] = es.get(xref)

        return render_template('samples/view.html', sample=sample, xrefs_info=xrefs_objs)
    except TransportError, e:
        abort(404)

def validate_submission(form):

    if not os.access(app.config.get('SAMPLE_SUBMIT_FOLDER'), os.W_OK):
        flash(gettext('Cannot write to folder: %(folderpath)s', folderpath=app.config.get('SAMPLE_SUBMIT_FOLDER')))
        return False

    if form.sample.name not in request.files:
        flash(gettext('No file submitted.'))
        return False

    fh = request.files[form.sample.name]
    filename = secure_filename(fh.filename)
    file_data = fh.read()
    file_size = len(file_data)

    # Check size limits
    if file_size > app.config.get('SAMPLE_MAX_FILESIZE'):
        flash(gettext('Sample %(samplename)s (%(samplesize)s) is bigger than maximum file size allowed: %(maxsize)s', samplename=filename, samplesize=humansize(file_size), maxisze=humansize(app.config.get('SAMPLE_MAX_FILESIZE'))))
        return False

    if file_size < app.config.get('SAMPLE_MIN_FILESIZE'):
        flash(gettext('Sample %(samplename)s (%(samplesize)s) is smaller than minimum file size allowed: %(minsize)s', samplename=filename, samplesize=humansize(file_size), minsize=humansize(app.config.get('SAMPLE_MIN_FILESIZE'))))
        return False

    file_hash = hashlib.sha256(file_data).hexdigest()

    # Check if already submitted by this user
    exists = Submission.query.filter(and_(User.id == current_user.id, Submission.file_hash == file_hash)).first()
    if exists:
        flash(gettext('File already submitted.'))
        return False

    return True

@mod.route('/submit', methods=['GET', 'POST'])
@login_required
def submit():

    form = SubmitSampleForm()

    if form.validate_on_submit():

        if not validate_submission(form):
            return render_template('samples/submit.html', form=form)
        else:
            fh = request.files[form.sample.name]
            fh.seek(0, 0)
            file_hash = hashlib.sha256(fh.read()).hexdigest()
            filename = secure_filename(fh.filename)

            submission = Submission()
            submission.user = current_user
            submission.filename = filename
            submission.file_hash = file_hash

            db.session.add(submission)
            db.session.commit()

            fh.seek(0, 0)
            fh.save(os.path.join(app.config.get('SAMPLE_SUBMIT_FOLDER'), filename))

            flash(gettext('Sample submitted successfully'))
            return redirect(url_for('samples.submissions'))

    return render_template('samples/submit.html', form=form)

def update_submissions(user_id):
    user = User.query.get(user_id)
    pending = user.submissions.filter(Submission.sample_uuid == None).all()
    for row in pending:
        result = es.search({"hashes.sha256": row.file_hash})
        exists = ('hits' in result and result['hits']['total'] != 0)
        if exists:
            data = result['hits']['hits'][0]['_source']
            row.sample_uuid = data['uuid']
            db.session.add(row)

    db.session.commit()


@mod.route('/submissions')
@mod.route('/submissions/<int:page>/')
@login_required
def submissions(page = 1):

    update_submissions(current_user.id)

    samples = {}
    submissions = current_user.submissions.paginate(page, app.config.get('ITEMS_PER_PAGE'))
    for item in submissions.items:
        if item.sample_uuid:
            samples[item.sample_uuid] = es.get(item.sample_uuid)

    return render_template('samples/submissions.html', submissions=submissions, samples=samples)


