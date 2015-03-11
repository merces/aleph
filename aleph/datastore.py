from elasticsearch import Elasticsearch, NotFoundError

import logging

from aleph.utils import dict_merge
from aleph.settings import ELASTICSEARCH_URI, ELASTICSEARCH_INDEX, ELASTICSEARCH_DOCTYPE, ELASTICSEARCH_TRACE, LOGGING

class DataStore(object):

    es = None
    tracer = None

    def __init__(self):

        self.es = Elasticsearch(ELASTICSEARCH_URI)
        self.tracer = logging.getLogger('elasticsearch.trace')

        if ELASTICSEARCH_TRACE:
            self.tracer.setLevel(logging.DEBUG)
            self.tracer.addHandler(logging.FileHandler(LOGGING['filename']))
        else:
            self.tracer.addHandler(logging.NullHandler())

    def update(self, doc_id, partial_body):
        self.es.update(index=ELASTICSEARCH_INDEX, id=doc_id, doc_type=ELASTICSEARCH_DOCTYPE, body={'doc': partial_body })

    def setup(self):
        self.es.indices.create(index=ELASTICSEARCH_INDEX, ignore=400) # Ignore already exists

    def count(self, q=None):

        if q:
            result = self.es.count(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_DOCTYPE, q=q)
        else:
            result = self.es.count(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_DOCTYPE)
        return result['count']

    def all(self, size=10, start=0):
        try:
            result = self.es.search(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_DOCTYPE, body={
                'query': {
                    'match_all': {},
                },
                'from': start,
                'size': size,
                "sort": {
                    "timestamp": {
                        'order': 'desc'
                    },
                }
                })
        except NotFoundError:
            pass
        except Exception:
            raise

        return result


    def lucene_search(self, query, start=0, size=15):

        try:
            body = {
                "sort": {
                    "timestamp": {
                        'order': 'desc'
                    },
                }
            }
            result = self.es.search(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_DOCTYPE, q=query, from_=start, size=size, body=body)
        except NotFoundError:
            pass
        except Exception:
            raise

        return result

    def search(self, query):

        result = []

        try:
            result = self.es.search(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_DOCTYPE, body={'query': {'term': query } })
        except NotFoundError:
            pass
        except Exception:
            raise

        return result

    def save(self, doc_data, doc_id):
        return self.merge_document(ELASTICSEARCH_INDEX, ELASTICSEARCH_DOCTYPE, doc_data, doc_id)

    def get(self, doc_id):

        return self.es.get(index=ELASTICSEARCH_INDEX, doc_type=ELASTICSEARCH_DOCTYPE, id=doc_id)['_source']

    def merge_document(self, index, doc_type, doc_data, doc_id):

        try:
            self.es.indices.refresh(index)
        except Exception as e:
            raise IOError("Error updating ES index %s (%s)" % (index, e))

        original_document = {}

        # Try to get current data if available
        try:
            original_document = self.es.get(index=index, doc_type=doc_type, id=doc_id)
            if 'hits' in original_document and original_document['hits']['total'] != 0:
                original_document = original_document['_source']
            else:
                original_document = {}
        except NotFoundError as e:
            pass # not found, proceed
        except Exception as e:
            raise e 

        if len(original_document) == 0 :
            return self.es.index(index, doc_type, doc_data, id=doc_id)

        # Merge and index
        merged_document = dict_merge(original_document, doc_data)

        return self.es.index(index=index, doc_type=doc_type, body=merged_document, id=doc_id)

es = DataStore()
