# dictmsgr

Dict Messenger inspired by Robot Operation System, publish topic by setting item to a dict-like `Context` object. Callback subscription can be registered to be used in a single thread. The callback function should have signature `callback(ctx, msg)` and will be called when `Context.__setitem__()` is fired. This dict is designed to function like a project-wide globals() that you can read&write. '/' is used to specify multi-level nested dict keys.

`pip install dictmsgr`