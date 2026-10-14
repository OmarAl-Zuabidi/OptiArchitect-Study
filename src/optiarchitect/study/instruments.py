"""
Questionnaire instruments of the student study (English and Arabic).

Design (see docs/study.md for the rationale and the limitations):

* **Pre-use questionnaire**: consent, participant and course information, status in the subject, prior
  tools, a 9-item *self-rated confidence* block, difficulties experienced, and expectations.
* **Post-use questionnaire**: how the tool was used, the *same* 9 confidence items (so that the change can
  be computed for every student), the System Usability Scale (SUS; Brooke, 1996), perceived-usefulness items
  adapted from the Technology Acceptance Model (Davis, 1989), feature ratings, difficulties the tool helped
  with, overall evaluation, problems met, and one optional free-text comment.

Every answer except the optional comment is a choice. Values stored in the reports are language-neutral
(integers for scales, short codes for choices), so Arabic and English participants can be analysed together.
The Arabic wording is a working translation by the developer; it has not been psychometrically validated.
"""
from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class Choice:
    value: str
    en: str
    ar: str


@dataclass(frozen=True)
class Item:
    id: str
    kind: str                 # "text" | "single" | "multi" | "likert" | "checkbox" | "long_text"
    en: str
    ar: str
    choices: Tuple[Choice, ...] = ()
    scale: str = ""           # key of SCALES for kind == "likert"
    required: bool = True
    exclusive: str = ""       # value that cannot be combined with others (multi)
    max_chars: int = 120


@dataclass(frozen=True)
class Section:
    id: str
    en: str
    ar: str
    items: Tuple[Item, ...]
    intro_en: str = ""
    intro_ar: str = ""


def CH(*rows) -> Tuple[Choice, ...]:
    return tuple(Choice(*r) for r in rows)


# --------------------------------------------------------------------------------------------- scales
# value -> (English, Arabic); the integer is what is stored and analysed
SCALES: Dict[str, Tuple[Tuple[int, str, str], ...]] = {
    "agree5": ((1, "Strongly disagree", "أعارض بشدة"), (2, "Disagree", "أعارض"), (3, "Neutral", "محايد"),
               (4, "Agree", "أوافق"), (5, "Strongly agree", "أوافق بشدة")),
    "confidence5": ((1, "Not at all confident", "غير واثق إطلاقًا"), (2, "Slightly confident", "واثق قليلًا"),
                    (3, "Moderately confident", "واثق إلى حد ما"), (4, "Confident", "واثق"),
                    (5, "Very confident", "واثق جدًا")),
    "helpful4": ((0, "Did not use it", "لم أستخدمها"), (1, "Not helpful", "غير مفيدة"),
                 (2, "Somewhat helpful", "مفيدة إلى حد ما"), (3, "Very helpful", "مفيدة جدًا")),
    "likelihood5": ((1, "Definitely not", "بالتأكيد لا"), (2, "Probably not", "على الأرجح لا"),
                    (3, "Not sure", "لست متأكدًا"), (4, "Probably yes", "على الأرجح نعم"),
                    (5, "Definitely yes", "بالتأكيد نعم")),
    "rating5": ((1, "1 - Poor", "1 - ضعيف"), (2, "2 - Fair", "2 - مقبول"), (3, "3 - Good", "3 - جيد"),
                (4, "4 - Very good", "4 - جيد جدًا"), (5, "5 - Excellent", "5 - ممتاز")),
    "recommend11": tuple((i, str(i), str(i)) for i in range(11)),
}


def scale_label(scale: str, value: int, lang: str) -> str:
    for v, en, ar in SCALES[scale]:
        if v == value:
            return ar if lang == "ar" else en
    return str(value)


# --------------------------------------------------------------------------------------------- shared lists
DIFFICULTIES = CH(
    ("arithmetic_errors", "Arithmetic mistakes in long hand calculations", "أخطاء حسابية في الحسابات اليدوية الطويلة"),
    ("choose_method", "Knowing which method to use", "معرفة الطريقة المناسبة للاستخدام"),
    ("why_steps", "Understanding why each step is done", "فهم سبب كل خطوة"),
    ("special_cases", "Special cases (degeneracy, ties, infeasible or unbounded problems)",
     "الحالات الخاصة (التحلل، التعادل، المسائل غير الممكنة أو غير المحدودة)"),
    ("interpret", "Interpreting the final result", "تفسير النتيجة النهائية"),
    ("formulate", "Formulating a word problem as a mathematical model", "صياغة المسألة الكلامية كنموذج رياضي"),
    ("no_feedback", "No way to check my answer or get quick feedback", "عدم وجود وسيلة للتحقق من إجابتي أو الحصول على تغذية راجعة سريعة"),
    ("language", "Study material is not in my preferred language", "المادة الدراسية ليست بلغتي المفضلة"),
    ("time", "Not enough time to practise", "ضيق الوقت للتدرّب"),
    ("math_background", "Gaps in the required mathematics (algebra, matrices)", "ضعف في الرياضيات المطلوبة (الجبر، المصفوفات)"),
)
NONE_OF_THESE = Choice("none", "None of these", "لا شيء مما سبق")

CONFIDENCE_ITEMS = (
    ("formulate_lp", "Formulating a problem as a linear programming model", "صياغة مسألة كنموذج برمجة خطية"),
    ("simplex_steps", "Carrying out the simplex method step by step", "تنفيذ طريقة السمبلكس خطوة بخطوة"),
    ("choose_variant", "Deciding whether the standard, dual or two-phase simplex applies",
     "تحديد ما إذا كانت السمبلكس القياسية أو الثنائية أو ذات المرحلتين هي المناسبة"),
    ("initial_transport", "Building an initial solution of a transportation problem (North-West Corner, Least Cost, Vogel)",
     "إيجاد الحل الابتدائي لمسألة نقل (الركن الشمالي الغربي، أقل تكلفة، فوجل)"),
    ("modi", "Testing and improving a transportation solution with the MODI method",
     "اختبار حل مسألة النقل وتحسينه بطريقة MODI"),
    ("hungarian", "Solving an assignment problem with the Hungarian method", "حل مسألة تخصيص بالطريقة الهنغارية"),
    ("search_1d", "Choosing and applying a one-variable search method (golden section, Newton, secant)",
     "اختيار طريقة بحث لمتغير واحد وتطبيقها (النسبة الذهبية، نيوتن، القاطع)"),
    ("verify_answer", "Checking that my final answer is correct", "التحقق من صحة إجابتي النهائية"),
    ("interpret_status", "Interpreting infeasible, unbounded or degenerate outcomes",
     "تفسير النتائج غير الممكنة أو غير المحدودة أو المتحللة"),
)
CONFIDENCE_IDS = tuple(f"conf_{k}" for k, _, _ in CONFIDENCE_ITEMS)


def confidence_section(when: str) -> Section:
    ar_intro = ("كيف تقيّم ثقتك الحالية في كل مهمة من المهام التالية؟" if when == "pre"
                else "بعد استخدام الأداة، كيف تقيّم ثقتك الحالية في كل مهمة من المهام التالية؟")
    en_intro = ("How confident are you **today** in each of the following tasks?" if when == "pre"
                else "**Now, after using the tool**, how confident are you in each of the following tasks?")
    return Section("confidence", "Your confidence in the subject", "ثقتك في المادة",
                   tuple(Item(f"conf_{k}", "likert", en, ar, scale="confidence5") for k, en, ar in CONFIDENCE_ITEMS),
                   en_intro, ar_intro)


# --------------------------------------------------------------------------------------------- PRE questionnaire
CONSENT_ITEMS = (
    Item("consent_read", "checkbox", "I have read the study information above and I understand it.",
         "لقد قرأتُ معلومات الدراسة أعلاه وفهمتُها."),
    Item("consent_adult", "checkbox", "I am 18 years old or older.", "عمري 18 سنة أو أكثر."),
    Item("consent_voluntary", "checkbox",
         "I take part voluntarily and I know that I can withdraw at any time without giving a reason.",
         "أشارك طوعًا، وأعلم أن بإمكاني الانسحاب في أي وقت دون إبداء سبب."),
    Item("consent_data", "checkbox",
         "I agree that my answers and the problems I solve in the tool are recorded and used for this research.",
         "أوافق على تسجيل إجاباتي والمسائل التي أحلّها في الأداة واستخدامها لأغراض هذا البحث."),
)

PRE_SECTIONS = (
    Section("consent", "Consent", "الموافقة", CONSENT_ITEMS),
    Section("profile", "About you and your course", "معلومات عنك وعن مقررك",
            (
                Item("full_name", "text", "Full name", "الاسم الكامل"),
                Item("university", "text", "University", "الجامعة"),
                Item("college", "text", "College / faculty", "الكلية"),
                Item("department", "text", "Department", "القسم"),
                Item("course", "text", "Course / module name", "اسم المادة أو المقرر الدراسي"),
                Item("instructor", "text", "Course instructor's name", "اسم أستاذ المادة"),
                Item("level", "single", "Your academic level", "مستواك الدراسي",
                     CH(("y1", "First year", "السنة الأولى"), ("y2", "Second year", "السنة الثانية"),
                        ("y3", "Third year", "السنة الثالثة"), ("y4", "Fourth year", "السنة الرابعة"),
                        ("y5", "Fifth year or above", "السنة الخامسة فأعلى"), ("pg", "Postgraduate", "دراسات عليا"))),
            ),
            "These details are used only to describe the participants and are never shown to other students.",
            "تُستخدم هذه البيانات لوصف المشاركين فقط، ولا تُعرض على الطلبة الآخرين."),
    Section("status", "Your situation in the subject", "وضعك في المادة",
            (
                Item("course_status", "single", "What is your status in this subject?", "ما وضعك في هذه المادة؟",
                     CH(("enrolled_now", "I am currently studying it", "أدرسها حاليًا"),
                        ("completed_before", "I studied it in a previous term", "درستُها في فصل سابق"),
                        ("self_study", "I am not enrolled; I study it on my own", "غير مسجّل فيها؛ أدرسها ذاتيًا"))),
                Item("topics_studied", "multi", "Which topics have you already studied? (select all that apply)",
                     "ما المواضيع التي سبق أن درستها؟ (اختر كل ما ينطبق)",
                     CH(("lp", "Linear programming and the simplex method", "البرمجة الخطية وطريقة السمبلكس"),
                        ("transport", "Transportation problems", "مسائل النقل"),
                        ("assignment", "Assignment problems (Hungarian method)", "مسائل التخصيص (الطريقة الهنغارية)"),
                        ("nlp", "One-variable non-linear optimization", "التحسين غير الخطي بمتغير واحد"),
                        ("none", "None of these", "لا شيء مما سبق")), exclusive="none"),
                Item("standing", "single", "How would you describe your current standing in this subject?",
                     "كيف تصف مستواك الحالي في هذه المادة؟",
                     CH(("excellent", "Excellent", "ممتاز"), ("good", "Good", "جيد"), ("average", "Average", "متوسط"),
                        ("below", "Below average", "دون المتوسط"), ("unsure", "I do not know yet", "لا أعرف بعد"))),
                Item("study_hours", "single", "About how many hours per week do you study this subject outside class?",
                     "كم ساعة أسبوعيًا تقريبًا تدرس هذه المادة خارج المحاضرات؟",
                     CH(("lt1", "Less than 1 hour", "أقل من ساعة"), ("h1_2", "1 to 2 hours", "من ساعة إلى ساعتين"),
                        ("h3_5", "3 to 5 hours", "من 3 إلى 5 ساعات"), ("gt5", "More than 5 hours", "أكثر من 5 ساعات"))),
                Item("tools_before", "multi", "Which tools have you used before to solve this kind of problem? (select all that apply)",
                     "ما الأدوات التي استخدمتها سابقًا لحل هذا النوع من المسائل؟ (اختر كل ما ينطبق)",
                     CH(("hand", "Hand calculation only", "الحل اليدوي فقط"),
                        ("excel", "Excel Solver or spreadsheets", "Excel Solver أو الجداول الإلكترونية"),
                        ("matlab_python", "MATLAB, Python or R", "MATLAB أو Python أو R"),
                        ("online", "Online calculators or websites", "حاسبات أو مواقع على الإنترنت"),
                        ("other", "Other software", "برامج أخرى")), exclusive="hand"),
                Item("computing_comfort", "single", "How comfortable are you with using computer software for coursework?",
                     "ما مدى ارتياحك لاستخدام البرامج الحاسوبية في دراستك؟",
                     CH(("very", "Very comfortable", "مرتاح جدًا"), ("fairly", "Fairly comfortable", "مرتاح إلى حد ما"),
                        ("little", "A little uncomfortable", "غير مرتاح قليلًا"), ("not", "Not comfortable", "غير مرتاح"))),
                Item("device", "single", "Which device are you using now?", "ما الجهاز الذي تستخدمه الآن؟",
                     CH(("phone", "Phone", "هاتف"), ("tablet", "Tablet", "جهاز لوحي"), ("laptop", "Laptop", "حاسوب محمول"),
                        ("desktop", "Desktop computer", "حاسوب مكتبي"))),
                Item("preferred_language", "single", "In which language do you prefer to study this subject?",
                     "بأي لغة تفضّل دراسة هذه المادة؟",
                     CH(("arabic", "Arabic", "العربية"), ("english", "English", "الإنجليزية"),
                        ("both", "Both equally", "كلتاهما بالتساوي"))),
            )),
    confidence_section("pre"),
    Section("difficulties", "Difficulties you face", "الصعوبات التي تواجهها",
            (
                Item("difficulties", "multi", "Which of these difficulties do you face in this subject? (select all that apply)",
                     "أي من الصعوبات التالية تواجهها في هذه المادة؟ (اختر كل ما ينطبق)",
                     DIFFICULTIES + (NONE_OF_THESE,), exclusive="none"),
                Item("top_difficulty", "single", "Which ONE is the most serious for you?", "وما أخطرها بالنسبة لك (اختر واحدة فقط)؟",
                     DIFFICULTIES + (NONE_OF_THESE,)),
                Item("check_answers", "single", "How do you usually check that your answers are correct?",
                     "كيف تتحقق عادةً من صحة إجاباتك؟",
                     CH(("none", "I do not check them", "لا أتحقق منها"),
                        ("classmates", "I compare with classmates", "أقارنها مع زملائي"),
                        ("instructor", "I ask the instructor or assistant", "أسأل الأستاذ أو المساعد"),
                        ("textbook", "I compare with textbook solutions", "أقارنها بحلول الكتاب"),
                        ("software", "I use software", "أستخدم برنامجًا"))),
                Item("expect_help", "likert", "I expect step-by-step solutions to help me understand the methods.",
                     "أتوقع أن تساعدني الحلول خطوة بخطوة على فهم الطرق.", scale="agree5"),
            )),
)

# --------------------------------------------------------------------------------------------- SUS
SUS_ITEMS = (
    ("I think that I would like to use this system frequently.", "أعتقد أنني أرغب في استخدام هذا النظام بشكل متكرر."),
    ("I found the system unnecessarily complex.", "وجدتُ النظام معقدًا دون داعٍ."),
    ("I thought the system was easy to use.", "رأيتُ أن النظام سهل الاستخدام."),
    ("I think that I would need the support of a technical person to be able to use this system.",
     "أعتقد أنني سأحتاج إلى مساعدة شخص متخصص تقنيًا لأتمكن من استخدام هذا النظام."),
    ("I found the various functions in this system were well integrated.", "وجدتُ أن الوظائف المختلفة في هذا النظام متكاملة بشكل جيد."),
    ("I thought there was too much inconsistency in this system.", "رأيتُ أن هناك تناقضًا كبيرًا في هذا النظام."),
    ("I would imagine that most people would learn to use this system very quickly.",
     "أتصور أن معظم الناس سيتعلمون استخدام هذا النظام بسرعة كبيرة."),
    ("I found the system very cumbersome to use.", "وجدتُ النظام مرهقًا جدًا في الاستخدام."),
    ("I felt very confident using the system.", "شعرتُ بثقة كبيرة أثناء استخدام النظام."),
    ("I needed to learn a lot of things before I could get going with this system.",
     "كنتُ بحاجة إلى تعلّم أشياء كثيرة قبل أن أتمكن من البدء باستخدام هذا النظام."),
)
SUS_IDS = tuple(f"sus_{i}" for i in range(1, 11))

FEATURES = (
    ("examples", "Worked examples", "الأمثلة المحلولة"),
    ("own_problem", "Solving my own problem", "حل مسألتي الخاصة"),
    ("detail_mode", "Step-by-step detail mode (tableaux, loops, iterations)", "وضع الشرح خطوة بخطوة (الجداول والحلقات والتكرارات)"),
    ("diagnosis", "The report that recommends a method and explains why", "التقرير الذي يوصي بطريقة ويشرح السبب"),
    ("verification", "The independent verification of results", "التحقق المستقل من النتائج"),
    ("graphical", "The graphical method (feasible region plot)", "الطريقة البيانية (رسم منطقة الحلول الممكنة)"),
    ("methods_text", "The descriptions of the methods", "شروحات الطرق"),
    ("language_switch", "Switching between Arabic and English", "التبديل بين العربية والإنجليزية"),
    ("user_guide", "The user guide", "دليل المستخدم"),
)

USEFULNESS = (
    ("use_understand", "Using the tool improved my understanding of the algorithms.", "استخدام الأداة حسّن فهمي للخوارزميات."),
    ("use_stepbystep", "The step-by-step display made the methods easier to follow.", "عرض الخطوات جعل الطرق أسهل في المتابعة."),
    ("use_diagnosis", "The explanation of which method applies, and why, was useful.", "كان شرح الطريقة المناسبة وسبب مناسبتها مفيدًا."),
    ("use_verification", "The independent verification of results increased my trust in my answers.",
     "التحقق المستقل من النتائج زاد ثقتي بإجاباتي."),
    ("use_time", "The tool saved me time compared with solving by hand only.", "وفّرت الأداة وقتي مقارنةً بالحل اليدوي فقط."),
    ("use_exam", "The tool would help me prepare for exams and assignments.", "ستساعدني الأداة في الاستعداد للامتحانات والواجبات."),
    ("use_language", "Having the tool in my preferred language made the material easier to follow.",
     "توفّر الأداة بلغتي المفضلة جعل المادة أسهل في المتابعة."),
    ("use_recommend", "I would recommend this tool to other students.", "سأوصي زملائي الطلبة بهذه الأداة."),
)

PROBLEMS = CH(
    ("slow", "It was slow", "كانت بطيئة"),
    ("menus", "The menus or options were confusing", "كانت القوائم أو الخيارات مربكة"),
    ("input", "Entering my problem was difficult", "كان إدخال مسألتي صعبًا"),
    ("results", "The results were hard to understand", "كان من الصعب فهم النتائج"),
    ("errors", "I met errors or unexpected behaviour", "واجهتُ أخطاء أو سلوكًا غير متوقع"),
    ("translation", "Problems with the Arabic or English text", "مشكلات في النص العربي أو الإنجليزي"),
    ("mobile", "It was hard to use on my device or screen", "كان استخدامها صعبًا على جهازي أو شاشتي"),
    ("too_many", "Too many options at once", "خيارات كثيرة جدًا دفعة واحدة"),
    ("none", "I met no problems", "لم أواجه أي مشكلات"),
)

POST_SECTIONS = (
    Section("session", "How you used the tool", "كيف استخدمتَ الأداة",
            (
                Item("how_used", "single", "How did you use the tool?", "كيف استخدمتَ الأداة؟",
                     CH(("alone", "On my own", "بمفردي"), ("classmates", "Together with classmates", "مع زملائي"),
                        ("in_class", "In class, guided by the instructor", "داخل المحاضرة بتوجيه من الأستاذ"))),
            )),
    confidence_section("post"),
    Section("sus", "Ease of use", "سهولة الاستخدام",
            tuple(Item(f"sus_{i}", "likert", en, ar, scale="agree5") for i, (en, ar) in enumerate(SUS_ITEMS, 1)),
            "Please answer every statement about the tool you have just used.",
            "يُرجى الإجابة عن كل عبارة بخصوص الأداة التي استخدمتها للتو."),
    Section("usefulness", "Usefulness for your learning", "فائدة الأداة لتعلّمك",
            tuple(Item(k, "likert", en, ar, scale="agree5") for k, en, ar in USEFULNESS)),
    Section("features", "Features you used", "الميزات التي استخدمتها",
            tuple(Item(f"feat_{k}", "likert", en, ar, scale="helpful4") for k, en, ar in FEATURES),
            "How helpful was each feature?", "ما مدى فائدة كل ميزة؟"),
    Section("impact", "Effect on your difficulties", "أثر الأداة على صعوباتك",
            (
                Item("difficulties_helped", "multi", "Which of your difficulties did the tool help with? (select all that apply)",
                     "أي من صعوباتك ساعدتك الأداة في تجاوزها؟ (اختر كل ما ينطبق)",
                     DIFFICULTIES + (Choice("none", "None of these", "لا شيء مما سبق"),), exclusive="none"),
                Item("perceived_learning", "single", "Compared with studying without the tool, my understanding is now:",
                     "مقارنةً بالدراسة دون الأداة، أصبح فهمي الآن:",
                     CH(("much_better", "Much better", "أفضل بكثير"), ("slightly_better", "Slightly better", "أفضل قليلًا"),
                        ("same", "About the same", "كما هو تقريبًا"), ("worse", "Worse", "أسوأ"))),
            )),
    Section("overall", "Overall evaluation", "التقييم العام",
            (
                Item("overall_rating", "likert", "Overall, how would you rate the tool?", "بوجه عام، كيف تقيّم الأداة؟", scale="rating5"),
                Item("reuse", "likert", "How likely are you to use the tool again?", "ما احتمال أن تستخدم الأداة مرة أخرى؟", scale="likelihood5"),
                Item("recommend_nps", "likert",
                     "How likely are you to recommend the tool to a classmate? (0 = not at all, 10 = extremely likely)",
                     "ما احتمال أن توصي زميلًا باستخدام الأداة؟ (0 = مستبعد تمامًا، 10 = مؤكد جدًا)", scale="recommend11"),
                Item("problems", "multi", "Which problems did you meet? (select all that apply)",
                     "ما المشكلات التي واجهتها؟ (اختر كل ما ينطبق)", PROBLEMS, exclusive="none"),
                Item("comment", "long_text", "Any other comment? (optional)", "هل لديك أي ملاحظة أخرى؟ (اختياري)",
                     required=False, max_chars=1000),
            )),
)


def all_items(sections) -> Tuple[Item, ...]:
    return tuple(i for s in sections for i in s.items)


def choice_label(item: Item, value: str, lang: str = "en") -> str:
    for c in item.choices:
        if c.value == value:
            return c.ar if lang == "ar" else c.en
    return str(value)
