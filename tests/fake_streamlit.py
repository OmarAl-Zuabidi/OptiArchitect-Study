"""Minimal in-memory stand-in for streamlit so the apps can be exercised without a browser.

``run(scenario)`` executes ``optiarchitect/app.py`` once (used by the original smoke tests).
``Session`` keeps one session_state across several script runs (a multi-page flow such as the study),
re-running the script after ``st.rerun()`` exactly like Streamlit does.
"""
import contextlib
import os
import runpy
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)
APP_PATH = os.path.join(SRC, "optiarchitect", "app.py")
STUDY_PATH = os.path.join(SRC, "optiarchitect", "study", "app_study.py")
ADMIN_PATH = os.path.join(SRC, "optiarchitect", "study", "admin.py")

TEXT_OK = {"en": "Completed - solution verified", "ar": "تم التحقق من الحل"}


class Rerun(Exception):
    pass


class Stop(Exception):
    pass


class SS(dict):
    __getattr__ = dict.get

    def __setattr__(self, k, v):
        self[k] = v


class Fake(types.ModuleType):
    def __init__(self, session_state=None):
        super().__init__("streamlit")
        self.session_state = session_state if session_state is not None else SS()
        self.out = []
        self.pressed = set()
        self.editors = {}
        self.query_params = {}
        self.sidebar = self
        self._form = None
        self.column_config = types.SimpleNamespace(
            SelectboxColumn=lambda *a, **k: ("sel", a, k), NumberColumn=lambda *a, **k: ("num", a, k))

    # ---- context-manager behaviour of the object returned by st.columns / st.sidebar
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def _w(self, *a):
        self.out.append(" ".join(str(x) for x in a))

    # ---- output
    def set_page_config(self, **k): pass
    def markdown(self, t, **k): self._w(t)
    def header(self, t, **k): self._w("#", t)
    def title(self, t, **k): self._w("#", t)
    def subheader(self, t, **k): self._w("##", t)
    def caption(self, t, **k): self._w(t)
    def info(self, t, **k): self._w("[info]", t)
    def success(self, t, **k): self._w("[success]", t)
    def warning(self, t, **k): self._w("[warning]", t)
    def error(self, t, **k): self._w("[error]", t)
    def divider(self): pass
    def code(self, t, **k): self._w(t)
    def table(self, df): self._w(df.to_string())
    def dataframe(self, df, **k): self._w("<DATAFRAME>", len(df))
    def json(self, obj, **k): self._w("<JSON>", obj)
    def metric(self, label, value, **k): self._w("<METRIC>", label, value)
    def pyplot(self, fig, **k): self._w("<PYPLOT>")
    def write(self, *a): pass
    def progress(self, v, **k): pass
    def download_button(self, label, data, **k): self._w("<DL>", k.get("file_name"))

    def stop(self):
        raise Stop()

    def rerun(self):
        raise Rerun()

    @contextlib.contextmanager
    def spinner(self, *a, **k): yield

    @contextlib.contextmanager
    def expander(self, label, **k):
        self._w("<EXP>", label)
        yield

    @contextlib.contextmanager
    def container(self, **k): yield

    @contextlib.contextmanager
    def form(self, key, **k):
        self._form = key
        yield
        self._form = None

    def form_submit_button(self, label, **k):
        return self._form in self.pressed

    def columns(self, n):
        n = n if isinstance(n, int) else len(n)
        return [self for _ in range(n)]

    # ---- widgets: the value is session_state[key] when present, else the widget default
    def _get(self, key, default):
        if key is None:
            return default
        if key not in self.session_state:
            self.session_state[key] = default
        return self.session_state[key]

    def radio(self, label, options, key=None, format_func=str, index=0, **k):
        for o in options:
            format_func(o)
        return self._get(key, None if index is None else options[index])

    def selectbox(self, label, options, key=None, format_func=str, index=0, **k):
        for o in options:
            format_func(o)
        return self._get(key, None if index is None else options[index])

    def multiselect(self, label, options, key=None, format_func=str, **k):
        for o in options:
            format_func(o)
        return self._get(key, [])

    def checkbox(self, label, value=False, key=None, **k): return self._get(key, value)
    def text_input(self, label, value="", key=None, **k): return self._get(key, value)
    def text_area(self, label, value="", key=None, **k): return self._get(key, value)

    def number_input(self, label, min_value=None, max_value=None, value=None, step=None, key=None, **k):
        return self._get(key, value)

    def data_editor(self, df, key=None, **k): return self.editors.get(key, df)

    def button(self, label, key=None, on_click=None, args=(), disabled=False, **k):
        hit = key in self.pressed and not disabled
        if hit and on_click:
            on_click(*args)
        return hit


def _install(fake):
    sys.modules["streamlit"] = fake
    comp = types.ModuleType("streamlit.components")
    v1 = types.ModuleType("streamlit.components.v1")
    v1.html = lambda body, **k: fake._w("<COMPONENT-HTML>", len(body))
    comp.v1 = v1
    fake.components = comp
    sys.modules["streamlit.components"] = comp
    sys.modules["streamlit.components.v1"] = v1
    # modules that did `import streamlit as st` must be re-imported against the new fake
    pkg = sys.modules.get("optiarchitect")
    for name in list(sys.modules):
        if name == "optiarchitect.app" or name.startswith("optiarchitect.study"):
            del sys.modules[name]
    if pkg is not None:
        for attr in ("app", "study"):
            if hasattr(pkg, attr):
                delattr(pkg, attr)


def run(scenario):
    """Run optiarchitect/app.py once with a fresh session."""
    fake = Fake(SS(scenario.get("state", {})))
    fake.pressed = set(scenario.get("pressed", ()))
    fake.editors = scenario.get("editors", {})
    _install(fake)
    runpy.run_path(APP_PATH, run_name="__main__")
    return fake


class Session:
    """One browser session: session_state survives across runs of the script."""

    def __init__(self, path=STUDY_PATH, state=None):
        self.path = path
        self.state = SS(state or {})
        self.last = None

    def run(self, pressed=(), set_state=None, max_reruns=8):
        if set_state:
            self.state.update(set_state)
        for _ in range(max_reruns):
            fake = Fake(self.state)
            fake.pressed = set(pressed)
            _install(fake)
            self.last = fake
            try:
                runpy.run_path(self.path, run_name="__main__")
                return fake
            except Rerun:
                pressed = ()                   # a rerun is not another click
                continue
            except Stop:
                return fake
        raise RuntimeError("too many reruns")

    @property
    def text(self):
        return "\n".join(self.last.out) if self.last else ""
