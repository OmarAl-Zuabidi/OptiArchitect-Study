"""Rendering and validation of the questionnaires with Streamlit widgets (to be used inside ``st.form``)."""
from typing import Dict, List

import streamlit as st

from optiarchitect.study import instruments as I
from optiarchitect.study.texts import T


def _q(item: I.Item, lang: str) -> str:
    return (item.ar if lang == "ar" else item.en) + (" *" if item.required else "")


def render_sections(sections, lang: str, prefix: str) -> Dict[str, object]:
    """Draw the sections and return the current answers (``None`` / ``[]`` for unanswered items)."""
    answers: Dict[str, object] = {}
    for s in sections:
        st.markdown(f"#### {s.ar if lang == 'ar' else s.en}")
        intro = s.intro_ar if lang == "ar" else s.intro_en
        if intro:
            st.markdown(intro)
        for item in s.items:
            key, label = f"{prefix}_{item.id}", _q(item, lang)
            if item.kind == "text":
                answers[item.id] = st.text_input(label, key=key, max_chars=item.max_chars).strip()
            elif item.kind == "long_text":
                answers[item.id] = st.text_area(label, key=key, max_chars=item.max_chars).strip()
            elif item.kind == "checkbox":
                answers[item.id] = st.checkbox(label, key=key)
            elif item.kind == "single":
                answers[item.id] = st.radio(label, [c.value for c in item.choices], index=None, key=key,
                                            format_func=lambda v, it=item: I.choice_label(it, v, lang))
            elif item.kind == "multi":
                answers[item.id] = list(st.multiselect(label, [c.value for c in item.choices], key=key,
                                                       format_func=lambda v, it=item: I.choice_label(it, v, lang)))
            elif item.kind == "likert":
                answers[item.id] = st.radio(label, [v for v, _, _ in I.SCALES[item.scale]], index=None, horizontal=True,
                                            key=key, format_func=lambda v, it=item: I.scale_label(it.scale, v, lang))
            else:                                                       # pragma: no cover
                raise ValueError(f"unknown item kind {item.kind!r}")
    return answers


def validate(sections, answers: Dict[str, object], lang: str) -> List[str]:
    """Return a list of problems (empty when the answers are complete and consistent)."""
    t, errors = T[lang], []
    for s in sections:
        for item in s.items:
            v = answers.get(item.id)
            q = item.ar if lang == "ar" else item.en
            if item.kind == "checkbox":
                if item.required and v is not True:
                    errors.append(q)
            elif item.kind == "multi":
                if item.required and not v:
                    errors.append(q)
                elif v and item.exclusive and item.exclusive in v and len(v) > 1:
                    errors.append(t["err_exclusive"].format(q=q))
            elif item.kind in ("text", "long_text"):
                if item.required and not (isinstance(v, str) and len(v.strip()) >= 2):
                    errors.append(f"{q} ({t['err_text']})")
            elif item.required and v is None:
                errors.append(q)
    return errors
