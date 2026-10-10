import re
import logging
from jinja2.sandbox import SandboxedEnvironment, SecurityError
from jinja2.exceptions import TemplateSyntaxError, UndefinedError

logger = logging.getLogger(__name__)

UNSAFE_ATTRIBUTES = frozenset(
    [
        "__class__",
        "__mro__",
        "__subclasses__",
        "__globals__",
        "__builtins__",
        "__dict__",
        "__doc__",
        "__name__",
        "__module__",
        "__import__",
        "__code__",
        "__func__",
        "__self__",
        "__getattribute__",
        "__setattr__",
        "__delattr__",
        "__reduce__",
        "__reduce_ex__",
        "__getstate__",
        "__setstate__",
        "_TemplateReference__context",
        "_get_default_module",
        "environment",
        "request",
        "application",
        "config",
        "g",
        "session",
        "current_app",
        "lipsum",
        "cycler",
        "joiner",
        "namespace",
        "range",
        "dict",
        "list",
        "tuple",
        "set",
        "frozenset",
        "type",
        "object",
        "eval",
        "exec",
        "compile",
        "open",
        "file",
        "input",
        "raw_input",
        "reload",
        "__import__",
    ]
)

SAFE_MAGIC_METHODS = frozenset(
    [
        "__add__",
        "__sub__",
        "__mul__",
        "__truediv__",
        "__floordiv__",
        "__mod__",
        "__pow__",
        "__and__",
        "__or__",
        "__xor__",
        "__lt__",
        "__le__",
        "__eq__",
        "__ne__",
        "__gt__",
        "__ge__",
        "__len__",
        "__contains__",
        "__iter__",
        "__getitem__",
        "__str__",
        "__repr__",
        "__int__",
        "__float__",
        "__bool__",
        "__neg__",
        "__pos__",
    ]
)


class SSTISandbox(SandboxedEnvironment):
    def is_safe_attribute(self, obj, attr, value):
        if attr in UNSAFE_ATTRIBUTES:
            return False
        if attr.startswith("_") and attr.endswith("_"):
            return attr in SAFE_MAGIC_METHODS
        if attr.startswith("_"):
            return False
        return super().is_safe_attribute(obj, attr, value)

    def __init__(self):
        super().__init__()
        from src.jinja_funcs.jinja_filters import JinjaFilters

        self.filters["_ae"] = JinjaFilters.ae

    def render(self, template_string: str, context: dict = None) -> str:
        if not re.search(r"\{\{.*?\}\}|\{%.*?%\}", template_string):
            return template_string

        try:
            template = self.from_string(template_string)
            context = context or {}
            result = template.render(context)
            return str(result)

        except (TemplateSyntaxError, UndefinedError, SecurityError) as e:
            logger.warning(f"SSTI error: {e}")
            return template_string
        except Exception as e:
            logger.warning(f"SSTI sandbox error: {e}")
            return template_string


ssti_sandbox = SSTISandbox()
