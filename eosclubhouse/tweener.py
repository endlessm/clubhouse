from itertools import filterfalse


from eosclubhouse.easefunctions import EaseFunctions


class Tween:

    class TweenParameters:
        def __init__(self, target, ease_function=EaseFunctions.linear,
                     start=None, end=None, duration=1000, current_time=0):
            if start is None:
                start = {}
            if end is None:
                end = {}
            self.target = target
            self.ease_function = ease_function
            self.start = start
            self.end = end
            self.duration = duration
            self.current_time = current_time

    class TweenCallback:
        def __init__(self, func, args=None, kwargs=None):
            self.func = func
            self.args = args or []
            self.kwargs = kwargs or {}

        def call(self):
            self.func(*self.args, **self.kwargs)

    def __init__(self, target):
        self._target = target
        self._last_state = target
        self._queue = []
        self._queue_index = 0

    def _get_properties(self, target, props):
        return {p: (getattr(target, p) if hasattr(target, p) else v) for p, v in props.items()}

    def _set_properties(self, target, start, end, factor):
        for p, v_end in end.items():
            if not hasattr(target, p):
                continue
            v_start = start.get(p, 0)
            val = v_start + (v_end - v_start) * factor
            setattr(target, p, val)

    def to(self, props, duration, ease_function=EaseFunctions.linear):
        params = {
            'target': self._target,
            'ease_function': ease_function,
            'duration': duration
        }

        if isinstance(self._last_state, dict):
            params['start'] = self._last_state
        else:
            params['start'] = self._get_properties(self._last_state, props)

        params['end'] = props
        self._last_state = props
        self._queue.append(self.TweenParameters(**params))
        return self

    def wait(self, duration):
        self._queue.append(self.TweenParameters(self._target, duration=duration))
        return self

    def then(self, func, args=None, kwargs=None):
        self._queue.append(self.TweenCallback(func, args, kwargs))
        return self

    def update(self, delta_time):
        if not len(self._queue):
            return True

        params = self._queue[0]

        if isinstance(params, self.TweenCallback):
            params.call()
            self._queue.pop(0)
            return self.update(delta_time)

        params.current_time += delta_time

        factor = 1
        if params.current_time < params.duration:
            factor = params.ease_function(params.current_time / params.duration)

        self._set_properties(params.target, params.start, params.end, factor)

        if params.current_time >= params.duration:
            if params == self._queue[-1]:
                return True
            else:
                self._queue.pop(0)

        return False


class Tweener:
    _tweens = []

    @classmethod
    def add(class_, target):
        tween = Tween(target)
        class_._tweens.append(tween)
        return tween

    @classmethod
    def update(class_, delta_time):
        class_._tweens[:] = filterfalse(lambda tween: tween.update(delta_time),
                                        class_._tweens)
