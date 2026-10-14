"""Interface texts of the study pages (English / Arabic). The questionnaires themselves are in instruments.py."""
from optiarchitect.study.settings import StudySettings

T = {
    "en": dict(
        lang_label="Language / اللغة",
        thanks_title="Thank you for volunteering!",
        thanks=("Thank you for taking part in this study. Your experience will help us improve **OptiArchitect** and "
                "understand how interactive tools can support the learning of operations research. It takes about "
                "**15 to 20 minutes** in total."),
        info_title="About the study (please read before you start)",
        info_purpose="**Purpose.** To evaluate whether an interactive tool that shows every step of the classical operations research algorithms helps students understand them.",
        info_steps="**What you will do.** (1) Answer a short questionnaire; (2) use the tool to run at least **{n}** problem(s) - a worked example or your own; (3) answer a second questionnaire about your experience.",
        info_data="**Data collected.** Your name, university, college, department, course and instructor's name; your questionnaire answers; and the problems you run in the tool together with the results the tool produced.",
        info_use="**Use of the data.** Only for this research and for improving the tool. Results are reported in aggregate; no individual is identified in any publication.",
        info_conf="**Confidentiality.** Your data are stored on the research team's computer or server. They are not shown to other students, and are not shared with your instructor or university.",
        info_vol="**Voluntary participation.** You may withdraw at any time with the *Withdraw* button in the sidebar (your data are then deleted). Each questionnaire is saved when you submit it; if you close the page before the end, you may ask the researcher to delete what was saved.",
        info_contact="**Contact.** {researcher}, {institution} - {email}.",
        info_ethics="Ethics approval reference: {ref}.",
        required_note="Questions marked with * are required.",
        pre_title="Questionnaire before using the tool",
        pre_submit="Continue to the tool",
        post_title="Questionnaire after using the tool",
        post_intro="Thank you for trying the tool. Please answer the following questions about your experience. Your honest opinion is what helps most.",
        post_submit="Submit and finish",
        step="Step {i} of {n}",
        steps=("Questionnaire 1", "Use the tool", "Questionnaire 2"),
        errors_head="Please complete all required questions ({n} missing or invalid):",
        err_exclusive="Select \"None of these\" on its own: {q}",
        err_text="This answer cannot be empty",
        sidebar_title="Study session",
        sidebar_code="Participant code",
        sidebar_count="Problems run: **{n}**",
        sidebar_need="Run at least **{m}** problem(s) before the evaluation (a worked example is enough).",
        finish="Finish and evaluate the tool",
        withdraw_title="Withdraw from the study",
        withdraw_confirm="I want to withdraw and delete my data",
        withdraw_button="Withdraw and delete my data",
        withdrawn="You have withdrawn from the study. Your data were deleted. Thank you for your time.",
        done_title="Thank you - your answers were saved",
        done_text="Your participation is complete. You may now close this page. Your participant code is **{pid}** (quote it if you ever ask us to delete your data).",
        done_copy="Download a copy of my answers (JSON)",
        save_error="Your answers could not be saved on the server. Please download the copy below and send it to the researcher.",
    ),
    "ar": dict(
        lang_label="Language / اللغة",
        thanks_title="شكرًا لتطوعك!",
        thanks=("نشكرك على مشاركتك في هذه الدراسة. ستساعدنا تجربتك في تحسين أداة **OptiArchitect** وفي فهم كيف "
                "يمكن للأدوات التفاعلية أن تدعم تعلّم بحوث العمليات. يستغرق الأمر نحو **15 إلى 20 دقيقة** إجمالًا."),
        info_title="عن الدراسة (يُرجى القراءة قبل البدء)",
        info_purpose="**الغرض.** تقييم ما إذا كانت أداة تفاعلية تعرض كل خطوة من خوارزميات بحوث العمليات الكلاسيكية تساعد الطلبة على فهمها.",
        info_steps="**ما المطلوب منك.** (1) الإجابة عن استمارة قصيرة؛ (2) استخدام الأداة لتشغيل **{n}** مسألة على الأقل - مثال محلول أو مسألتك الخاصة؛ (3) الإجابة عن استمارة ثانية حول تجربتك.",
        info_data="**البيانات التي تُجمع.** اسمك وجامعتك وكليتك وقسمك والمقرر واسم أستاذ المادة؛ وإجاباتك عن الاستمارتين؛ والمسائل التي تشغّلها في الأداة مع النتائج التي أنتجتها الأداة.",
        info_use="**استخدام البيانات.** لأغراض هذا البحث وتحسين الأداة فقط. تُعرض النتائج مجمَّعة، ولا يُكشف عن هوية أي فرد في أي نشر علمي.",
        info_conf="**السرية.** تُحفظ بياناتك على حاسوب أو خادم الفريق البحثي. لا تُعرض على الطلبة الآخرين، ولا تُشارك مع أستاذك أو جامعتك.",
        info_vol="**المشاركة طوعية.** يمكنك الانسحاب في أي وقت بزر *الانسحاب* في الشريط الجانبي (وتُحذف بياناتك عندئذٍ). تُحفظ كل استمارة عند إرسالها؛ وإذا أغلقتَ الصفحة قبل النهاية فيمكنك أن تطلب من الباحث حذف ما حُفظ.",
        info_contact="**للتواصل.** {researcher}، {institution} - {email}.",
        info_ethics="الرقم المرجعي للموافقة الأخلاقية: {ref}.",
        required_note="الأسئلة المعلَّمة بـ * إلزامية.",
        pre_title="استمارة ما قبل استخدام الأداة",
        pre_submit="المتابعة إلى الأداة",
        post_title="استمارة ما بعد استخدام الأداة",
        post_intro="شكرًا لتجربتك الأداة. يُرجى الإجابة عن الأسئلة التالية حول تجربتك. رأيك الصريح هو ما يفيدنا أكثر.",
        post_submit="إرسال وإنهاء",
        step="الخطوة {i} من {n}",
        steps=("الاستمارة الأولى", "استخدام الأداة", "الاستمارة الثانية"),
        errors_head="يُرجى إكمال جميع الأسئلة الإلزامية (عدد الأسئلة الناقصة أو غير الصالحة: {n}):",
        err_exclusive="اختر «لا شيء مما سبق» وحده: {q}",
        err_text="لا يمكن ترك هذه الإجابة فارغة",
        sidebar_title="جلسة الدراسة",
        sidebar_code="رمز المشارك",
        sidebar_count="المسائل المشغَّلة: **{n}**",
        sidebar_need="شغّل **{m}** مسألة على الأقل قبل التقييم (يكفي مثال محلول).",
        finish="إنهاء وتقييم الأداة",
        withdraw_title="الانسحاب من الدراسة",
        withdraw_confirm="أريد الانسحاب وحذف بياناتي",
        withdraw_button="انسحاب وحذف بياناتي",
        withdrawn="لقد انسحبتَ من الدراسة وحُذفت بياناتك. شكرًا لوقتك.",
        done_title="شكرًا - تم حفظ إجاباتك",
        done_text="اكتملت مشاركتك. يمكنك الآن إغلاق هذه الصفحة. رمز مشاركتك هو **{pid}** (اذكره إذا طلبتَ يومًا حذف بياناتك).",
        done_copy="تنزيل نسخة من إجاباتي (JSON)",
        save_error="تعذّر حفظ إجاباتك على الخادم. يُرجى تنزيل النسخة أدناه وإرسالها إلى الباحث.",
    ),
}


def info_lines(lang: str, s: StudySettings) -> list:
    t = T[lang]
    lines = [t["info_purpose"], t["info_steps"].format(n=s.min_problems), t["info_data"], t["info_use"], t["info_conf"],
             t["info_vol"], t["info_contact"].format(researcher=s.researcher, institution=s.institution, email=s.email)]
    if s.ethics_ref:
        lines.append(t["info_ethics"].format(ref=s.ethics_ref))
    return lines
