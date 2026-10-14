"""Study settings: defaults that can be overridden with environment variables (no code edits needed)."""
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Optional

from optiarchitect.config import AUTHOR

CONSENT_VERSION = "1.0"


def _int(env: Mapping[str, str], key: str, default: int) -> int:
    try:
        return int(env.get(key, default))
    except (TypeError, ValueError):
        return default


@dataclass
class StudySettings:
    title: str = "Evaluation of OptiArchitect as a learning tool for operations research"
    title_ar: str = "تقييم أداة OptiArchitect بوصفها وسيلة تعلّم لبحوث العمليات"
    researcher: str = AUTHOR
    email: str = "OmarAl-Zuabidi@proton.me"
    institution: str = "Al-Nahrain University"
    ethics_ref: str = ""                  # shown on the consent page only when set
    data_dir: Path = Path("study_data")   # relative to the folder from which the study is started
    min_problems: int = 1                 # problems a participant must run before the post-questionnaire
    admin_password: str = ""              # empty -> the admin application refuses to start
    smtp_host: str = ""                   # optional e-mail copy of every completed report
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = ""
    smtp_to: str = ""
    smtp_ssl: bool = False                # True: implicit TLS (port 465); False: STARTTLS

    @classmethod
    def from_env(cls, env: Optional[Mapping[str, str]] = None) -> "StudySettings":
        e = os.environ if env is None else env
        d = cls()
        g = lambda k, default="": e.get(k, default)  # noqa: E731
        return cls(
            title=g("OPTIARCHITECT_STUDY_TITLE", d.title), title_ar=g("OPTIARCHITECT_STUDY_TITLE_AR", d.title_ar),
            researcher=g("OPTIARCHITECT_RESEARCHER", d.researcher), email=g("OPTIARCHITECT_RESEARCHER_EMAIL", d.email),
            institution=g("OPTIARCHITECT_INSTITUTION", d.institution), ethics_ref=g("OPTIARCHITECT_ETHICS_REF"),
            data_dir=Path(g("OPTIARCHITECT_STUDY_DIR", str(d.data_dir))),
            min_problems=max(0, _int(e, "OPTIARCHITECT_MIN_PROBLEMS", d.min_problems)),
            admin_password=g("OPTIARCHITECT_ADMIN_PASSWORD"),
            smtp_host=g("OPTIARCHITECT_SMTP_HOST"), smtp_port=_int(e, "OPTIARCHITECT_SMTP_PORT", d.smtp_port),
            smtp_user=g("OPTIARCHITECT_SMTP_USER"), smtp_password=g("OPTIARCHITECT_SMTP_PASSWORD"),
            smtp_from=g("OPTIARCHITECT_SMTP_FROM"), smtp_to=g("OPTIARCHITECT_SMTP_TO"),
            smtp_ssl=g("OPTIARCHITECT_SMTP_SSL", "").lower() in ("1", "true", "yes"),
        )

    @property
    def email_enabled(self) -> bool:
        return bool(self.smtp_host and (self.smtp_to or self.email))
