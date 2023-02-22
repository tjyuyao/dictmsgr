from typing import Dict, List, Callable, Any
from collections.abc import Mapping

class Context(dict):

    def __init__(self, *args, **kwargs) -> None:
        self._subscriptions:Dict[str, List[Callable[[Context, Any], None]]] = dict()
        self.root = None
        self.update(*args, **kwargs)

    def subscribe(self, topic, callback):
        self_dict, topic = self.split_topic(topic)
        self_dict._subscriptions.setdefault(topic, [])
        self_dict._subscriptions[topic].append(callback)
    
    def __setitem__(self, topic:str, msg):
        self_dict, topic = self.split_topic(topic)
        if self_dict is self:
            dict.__setitem__(self_dict, topic, msg)
            if isinstance(msg, Context):
                if msg.root is not None:
                    raise RuntimeError("Nested context can not be reassigned.")
                msg.root = self.root or self
            if topic in self._subscriptions:
                for callback in self._subscriptions[topic]:
                    callback(self.root or self, msg)
        else:
            self_dict[topic] = msg
    
    def __getitem__(self, topic:str):
        self_dict, topic = self.split_topic(topic, create_mode=False)
        return dict.__getitem__(self_dict, topic)

    def __delitem__(self, topic):
        self_dict, topic = self.split_topic(topic, create_mode=False)
        dict.__delitem__(self_dict, topic)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            if isinstance(v, dict) and not isinstance(v, Context):
                v = Context(v)
            self[k] = v

    def split_topic(self, topic, create_mode=True):
        self_dict = self
        if '/' in topic:
            nested_topics = topic.split('/')
            for nested_topic in nested_topics[:-1]:
                if create_mode: self_dict.setdefault(nested_topic, Context())
                self_dict = self_dict[nested_topic]
            topic = nested_topics[-1]
        return self_dict, topic


from unittest import TestCase, main

class TestContext(TestCase):

    def test_type(self):
        assert issubclass(Context, dict)
        assert issubclass(Context, Mapping)

    def test_coverage(self):
        ctx = Context({"global_iters":0, "batch": {"img": "img_val"}, })

        def on_global_iters(ctx, msg):
            assert msg == ctx['global_iters']
        ctx.subscribe("global_iters", on_global_iters)
        ctx['global_iters'] += 1

        def on_batch_gt(ctx, msg):
            assert msg == "gt_val"
        ctx.subscribe("batch/gt", on_batch_gt)
        ctx['batch']['gt'] = "gt_val"

        def on_batch_img_metas(ctx, msg):
            assert msg == "misc"
        ctx.subscribe("batch/img_metas", on_batch_img_metas)
        ctx['batch/img_metas'] = "misc"

        def on_multi_level_assign(ctx, msg):
            assert msg == "misc"
        ctx.subscribe("batch/multi/level/assign", on_multi_level_assign)
        ctx['batch/multi/level/assign'] = "misc"

        c1 = Context()
        c2 = Context()
        c3 = Context()
        c1['c2'] = c2
        with self.assertRaises(RuntimeError):
            c3['c2'] = c2

        del ctx['batch/multi/level']
        with self.assertRaises(KeyError):
            ctx['batch/multi/level/assign']
        
        # from print_torch import pt
        # pt(ctx)

if __name__ == "__main__":
    main()

__version__ = "0.1"
__all__ = ["Context",]