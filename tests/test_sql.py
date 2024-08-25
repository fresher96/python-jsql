import jsql

def mock_execute_sql(engine, query, params):
    class ResultProxy:
        def keys(self):
            return ['engine', 'query', 'params']
        def __iter__(self):
            return iter([[engine, query, params]])
    return ResultProxy()
jsql.execute_sql = mock_execute_sql

def logparams_decorator(fn):
    import functools
    @functools.wraps(fn)
    def inner(engine, template, params):
        template = template.replace('HOOKPARAMS', '/* pod=xyz */')
        template = template.replace('COMMENTS', '')
        return fn(engine, template, params)
    return inner

engine = object()


def test_sqlhook(monkeypatch):
    monkeypatch.setattr(jsql, jsql.sql_inner.__name__, logparams_decorator(jsql.sql_inner))
    # jsql.sql_inner = logparams_decorator(jsql.sql_inner)
    ret = jsql.sql(engine, 'SELECT 1 FROM tbl WHERE 1=1 HOOKPARAMS').dict()
    assert ret['query'] == 'SELECT 1 FROM tbl WHERE 1=1 /* pod=xyz */'


def test_sql():
    ret = jsql.sql(engine, 'SELECT 1 FROM tbl {% if customer %}WHERE customer=:customer{% endif %} COMMENTS', customer='abc').dict()
    assert ret['engine'] == engine
    assert ret['query'] == 'SELECT 1 FROM tbl WHERE customer=:customer COMMENTS'
    assert ret['params']['customer'] == 'abc'

