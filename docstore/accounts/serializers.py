from .models import Account


def serialize_account(account):
    return {
        'id': account.code,
        'name': account.name,
        'created': account.created,
        'modified': account.modified,
        'deleted': account.deleted,
    }


def serialize_token(token):
    return {
        'id': token.code,
        'uuid': token.uuid,
        'account': Account.encode(token.account_id),
        'created': token.created,
        'modified': token.modified,
        'deleted': token.deleted,
    }
