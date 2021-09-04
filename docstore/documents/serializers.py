from ..accounts.models import Account


def serialize_document(document):
    return {
        'id': document.code,
        'name': document.name,
        'content': document.content,
        'account': Account.encode(document.account_id),
        'created': document.created,
        'modified': document.modified,
        'deleted': document.deleted,
    }
