from pyelasticsearch.exceptions import ElasticHttpNotFoundError
from pyelasticsearch import ElasticSearch

from aleph.utils import dict_merge
from aleph.settings import ELASTICSEARCH_URL

es = ElasticSearch(ELASTICSEARCH_URL)

def merge_document(index, doc_type, doc_data, doc_id):

    try:
        es.refresh(index)
    except Exception as e:
        raise IOError("Error updating ES index %s (%s)" % (index, e))

    original_document = {}

    # Try to get current data if available
    try:
        original_document = es.get(index, doc_type, doc_id)['_source']
    except ElasticHttpNotFoundError as e:
        pass # not found, proceed
    except Exception as e:
        raise e 

    if len(original_document) == 0 :
        return es.index(index, doc_type, doc_data, id=doc_id)

    # Merge and index
    merged_document = dict_merge(original_document, doc_data)

    return es.index(index, doc_type, merged_document, id=doc_id)
