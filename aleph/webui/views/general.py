from flask.ext.login import login_required, current_user
from flask import Blueprint, render_template

from aleph.constants import SAMPLE_STATUS_NEW, SAMPLE_STATUS_PROCESSING, SAMPLE_STATUS_PROCESSED
from aleph.datastore import es
from aleph.webui.views.samples import update_submissions
from aleph.webui.models import Submission

mod = Blueprint('general', __name__) 

@mod.route('/')
@mod.route('/index')
@login_required
def index():

    # Overall Counts
    sample_count = {
        'total': es.count(),
        'new':  es.count('status:%d' % SAMPLE_STATUS_NEW),
        'processing':  es.count('status:%d' % SAMPLE_STATUS_PROCESSING),
        'ready':  es.count('status:%d' % SAMPLE_STATUS_PROCESSED),
    }

    # Latest submissions
    update_submissions(current_user.id)
    submissions = current_user.submissions.order_by(Submission.timestamp.desc()).limit(15).all()
    submission_samples = {}

    for item in submissions:
        if item.sample_uuid:
            submission_samples[item.sample_uuid] = es.get(item.sample_uuid)

    # Latest samples
    es_samples = es.all(size=15)
    samples = []

    for s in es_samples['hits']['hits']:
        samples.append(s['_source'])

    return render_template('general/index.html', sample_count=sample_count, submissions=submissions, submission_samples=submission_samples, samples=samples)
