from contextvars import ContextVar


class ContextObj:
    def __setattr__(self, name, value):
        self.__dict__[name] = value

    def __getattr__(self, name):
        try:
            return self.__dict__[name]
        except KeyError:
            raise AttributeError(f"'ContextObj' object has no attribute '{name}'")


class ContextVarProxy:
    def __init__(self, context_var: ContextVar):
        self._context_var = context_var

    def __getattr__(self, name):
        context = self._context_var.get()
        if context is None:
            raise AttributeError('Context is not initialized.')
        return getattr(context, name)

    def __setattr__(self, name, value):
        if name == '_context_var':
            super().__setattr__(name, value)
        else:
            context = self._context_var.get()
            if context is None:
                raise AttributeError('Context is not initialized.')
            setattr(context, name, value)
