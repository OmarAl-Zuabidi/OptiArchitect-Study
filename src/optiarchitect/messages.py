"""
OptiArchitect bilingual message table (English / Arabic).
Single source of truth for every user-facing text (console, CLI and web app).
"""
from typing import Dict

from optiarchitect.config import COPYRIGHT, LICENSE

# ==========================================================================
#                     BILINGUAL MESSAGE TABLE (EN / AR)
# ==========================================================================
# Key prefixes:  c_ common | lp_ Part 1 | tp_ transportation | as_ assignment | nl_ Part 3
TEXT: Dict[str, Dict[str, str]] = {"en": {}, "ar": {}}
_EN, _AR = TEXT["en"], TEXT["ar"]

_EN.update({
    # ---- common -----------------------------------------------------------
    "c_ask_name": "Please enter your name [Default: Analyst]: ", "c_default_name": "Analyst",
    "c_welcome": "\nWelcome {name}! Pick a part from the menu. Tip: type ? at any prompt for help.\n",
    "c_menu_title": "MAIN MENU - choose what you want to work on",
    "c_p1_title": "[1] Part 1 | Linear Programming",
    "c_p1_sum": "Task: maximize or minimize a linear objective under linear constraints. "
                "Methods: Standard Simplex, Dual Simplex, Two-Phase Simplex, Graphical (2 variables).",
    "c_p2_title": "[2] Part 2 | Transportation & Assignment",
    "c_p2_sum": "Task: cheapest shipping plan between sources and destinations, or best one-to-one assignment. "
                "Methods: North-West Corner, Least Cost, Vogel (VAM), MODI (u-v) test, Hungarian.",
    "c_p3_title": "[3] Part 3 | Single-Variable Non-Linear Optimization",
    "c_p3_sum": "Task: minimum or maximum of f(x) on an interval, with automatic derivatives and a grid check. "
                "Methods: Golden Section, Fibonacci Search, Newton-Raphson, Secant.",
    "c_m_guide": "[4] User guide: how to use the tool and which method to choose",
    "c_m_detail": "[5] Step-by-step detail mode (shows every tableau / iteration): {state}",
    "c_m_lang": "[6] Switch language / تغيير اللغة",
    "c_m_test": "[7] Run the built-in self-test (verifies all solvers)",
    "c_m_about": "[8] About, author and licence",
    "c_m_exit": "[0] Exit",
    "c_on": "ON", "c_off": "OFF",
    "c_ask_menu": "Enter your choice [Default: 1]: ",
    "c_detail_now": "   Detail mode is now {state}.",
    "c_sub_title": "{part} - what would you like to do?",
    "c_sub_own": "[1] Solve my own problem",
    "c_sub_ex": "[2] Learn from a worked example (pre-filled data + explanation)",
    "c_sub_learn": "[3] Read about the methods of this part",
    "c_sub_back": "[0] Back to the main menu",
    "c_ask_sub": "Enter your choice [Default: 1]: ",
    "c_press_enter": "\nPress Enter to continue...",
    "c_err_number": "   [!] Invalid numeric value. Please try again (or type ? for help).",
    "c_err_integer": "   [!] An integer is required.",
    "c_err_range": "   [!] Value must be between {lo} and {hi}.",
    "c_err_choice": "   [!] Invalid choice. Valid options are: {choices}",
    "c_err_count": "   [!] Please enter exactly {k} numbers (separated by spaces).",
    "c_err_nonneg": "   [!] Values must be >= 0.",
    "c_err_total": "   [!] Total must be greater than 0.",
    "c_error": "   [X] Error: {e}",
    "c_ft_ok": "Status: Completed - solution verified.",
    "c_ft_fail": "Status: NOT verified - see messages above.",
    "c_ft": "\n" + "=" * 71 + "\n   [END OF REPORT - {part}]  {status}\n   " + COPYRIGHT + " | " + LICENSE + "\n" + "=" * 71 + "\n",
    "c_bye": "\nThank you for using OptiArchitect.   " + COPYRIGHT + " - " + LICENSE + ".",
    "c_aborted": "\nAborted.",
    "c_ex_pick": "Choose an example [Default: 1]: ",
    "c_ex_intro": "\n--- WORKED EXAMPLE: {title} ---",
    "c_ex_obs": "\n--- WHAT TO OBSERVE ---",
    "c_data": "   Problem data:",
    "c_again_hint": "(Back in the part menu: choose [1] to try your own data, or [0] to leave.)",
    "c_shape_hint": "[i] If Arabic letters look disconnected, run with --shape-ar (needs arabic-reshaper and python-bidi).",
    "c_no_sympy": "SymPy is required for Part 3 (pip install sympy).",
    # ---- self-test --------------------------------------------------------
    "c_st_hdr": "\n--- SELF-TEST: reproducing reference results ---",
    "c_st_sum": "\n   Self-test: {p}/{t} checks passed.",
    "c_st_skip": "SKIP", "c_st_pass": "PASS", "c_st_fail": "FAIL",
    # ---- help texts ("?" at a prompt) --------------------------------------
    "h_generic": "Help: type a value and press Enter. Press Enter alone to accept the default shown in [brackets].",
    "h_c_ask_menu": "Type the number printed in brackets, e.g. 1 for Part 1, then press Enter.",
    "h_c_ask_sub": "[1] enter your own data, [2] see a solved example with comments, [3] read the theory, [0] go back.",
    "h_lp_ask_obj": "1 = maximize (profit, output...), 2 = minimize (cost, waste...).",
    "h_lp_ask_n": "Number of decision variables x1..xn (the unknowns you choose). All are assumed >= 0.",
    "h_lp_ask_m": "Number of constraints (resources, requirements, balances). Do NOT count x >= 0.",
    "h_lp_ask_c": "Coefficient of this variable in the objective. Example: profit 5 per unit of x2 -> enter 5.",
    "h_lp_ask_a": "Coefficient of this variable in the current constraint. Enter 0 if it does not appear.",
    "h_lp_ask_rel": "1 = '<=' (capacity / at most), 2 = '>=' (requirement / at least), 3 = '=' (exact balance).",
    "h_lp_ask_rhs": "Right-hand side constant of the constraint (may be negative; the solver handles it).",
    "h_lp_ask_method": "1 lets the program pick the best-suited method (recommended). Choosing another one "
                       "shows whether it is valid for your model - useful for learning.",
    "h_lp_ask_plot": "The graphical method draws the feasible region and the optimum (2 variables only).",
    "h_tp_ask_kind": "1 = Transportation (ship units at minimum cost), 2 = Assignment (one item per job, min cost / max profit).",
    "h_tp_ask_m": "Number of sources (factories / warehouses) that supply goods.",
    "h_tp_ask_n": "Number of destinations (customers / markets) that demand goods.",
    "h_tp_cost_row": "Unit shipping costs from this source to every destination, separated by spaces.",
    "h_tp_ask_supply": "Units available at each source, separated by spaces (non-negative).",
    "h_tp_ask_demand": "Units required at each destination, separated by spaces (non-negative). "
                       "If totals differ, a zero-cost dummy source/destination is added automatically.",
    "h_as_ask_rows": "Number of workers / items to assign (rows of the matrix).",
    "h_as_ask_cols": "Number of jobs / machines (columns). If different from rows, dummy rows/columns of 0 are added.",
    "h_as_ask_max": "1 = the matrix holds COSTS (minimize), 2 = the matrix holds PROFITS (maximize).",
    "h_as_row": "Costs (or profits) of this worker for every job, separated by spaces.",
    "h_nl_ask_fun": "Use x as the variable. Write products explicitly (2*x). Powers: x**2 or x^2. "
                    "Functions: sin cos tan exp log sqrt abs; constants: pi, E.",
    "h_nl_ask_goal": "1 = find the minimum of f(x), 2 = find the maximum of f(x).",
    "h_nl_ask_a": "Left end of the search interval [a, b] that contains the optimum.",
    "h_nl_ask_b": "Right end of the search interval; must be greater than a.",
    "h_nl_ask_tol": "Stopping tolerance: smaller = more accurate but more iterations. Practical range 1e-12 .. 1.",
    "h_nl_ask_x0": "Newton/Secant starting guess inside [a, b]. A good guess is close to the expected optimum.",
    "h_nl_ask_x1": "Second starting point for Secant; must differ from x0 and lie inside [a, b].",
})

_AR.update({
    # ---- common -----------------------------------------------------------
    "c_ask_name": "يرجى إدخال الاسم [الافتراضي: المحلل]: ", "c_default_name": "المحلل",
    "c_welcome": "\nأهلاً بك {name}! اختر جزءاً من القائمة. تلميح: اكتب ? عند أي سؤال لعرض المساعدة.\n",
    "c_menu_title": "القائمة الرئيسية - اختر ما تريد العمل عليه",
    "c_p1_title": "[1] الجزء الأول | البرمجة الخطية",
    "c_p1_sum": "المهمة: تعظيم أو تصغير دالة هدف خطية تحت قيود خطية. "
                "الطرق: السيمبلكس القياسي، السيمبلكس الثنائي، طريقة المرحلتين، الطريقة البيانية (متغيران).",
    "c_p2_title": "[2] الجزء الثاني | مسائل النقل والتخصيص",
    "c_p2_sum": "المهمة: أرخص خطة نقل بين المصادر والمقاصد، أو أفضل تخصيص واحد لواحد. "
                "الطرق: الركن الشمالي الغربي، أدنى تكلفة، فوغل (VAM)، اختبار MODI (u-v)، الطريقة المجرية.",
    "c_p3_title": "[3] الجزء الثالث | التحسين غير الخطي أحادي المتغير",
    "c_p3_sum": "المهمة: إيجاد أصغر أو أكبر قيمة للدالة f(x) على فترة، مع مشتقات تلقائية وفحص بالشبكة. "
                "الطرق: القسم الذهبي، فيبوناتشي، نيوتن-رافسون، القاطع.",
    "c_m_guide": "[4] دليل المستخدم: كيف تستخدم الأداة وكيف تختار الطريقة",
    "c_m_detail": "[5] وضع التفصيل خطوة بخطوة (يعرض كل جدول / تكرار): {state}",
    "c_m_lang": "[6] تغيير اللغة / Switch language",
    "c_m_test": "[7] تشغيل الاختبار الذاتي (يتحقق من جميع المحلّلات)",
    "c_m_about": "[8] حول البرنامج والمطوّر والترخيص",
    "c_m_exit": "[0] خروج",
    "c_on": "مفعّل", "c_off": "معطّل",
    "c_ask_menu": "أدخل اختيارك [الافتراضي: 1]: ",
    "c_detail_now": "   وضع التفصيل الآن: {state}.",
    "c_sub_title": "{part} - ماذا تريد أن تفعل؟",
    "c_sub_own": "[1] حل مسألتي الخاصة",
    "c_sub_ex": "[2] التعلّم من مثال محلول (بيانات جاهزة + شرح)",
    "c_sub_learn": "[3] قراءة شرح طرق هذا الجزء",
    "c_sub_back": "[0] العودة إلى القائمة الرئيسية",
    "c_ask_sub": "أدخل اختيارك [الافتراضي: 1]: ",
    "c_press_enter": "\nاضغط Enter للمتابعة...",
    "c_err_number": "   [!] قيمة رقمية غير صالحة. حاول مرة أخرى (أو اكتب ? للمساعدة).",
    "c_err_integer": "   [!] يجب إدخال عدد صحيح.",
    "c_err_range": "   [!] يجب أن تكون القيمة بين {lo} و {hi}.",
    "c_err_choice": "   [!] خيار غير صالح. الخيارات المتاحة: {choices}",
    "c_err_count": "   [!] يرجى إدخال {k} أرقام بالضبط (مفصولة بفراغات).",
    "c_err_nonneg": "   [!] يجب أن تكون القيم >= 0.",
    "c_err_total": "   [!] يجب أن يكون المجموع أكبر من 0.",
    "c_error": "   [X] خطأ: {e}",
    "c_ft_ok": "الحالة: اكتمل التنفيذ - تم التحقق من الحل.",
    "c_ft_fail": "الحالة: لم يُتحقق من الحل - راجع الرسائل أعلاه.",
    "c_ft": "\n" + "=" * 71 + "\n   [نهاية التقرير - {part}]  {status}\n   " + COPYRIGHT + " | " + LICENSE + "\n" + "=" * 71 + "\n",
    "c_bye": "\nشكراً لاستخدامك OptiArchitect.   " + COPYRIGHT + " - " + LICENSE + ".",
    "c_aborted": "\nتم الإلغاء.",
    "c_ex_pick": "اختر مثالاً [الافتراضي: 1]: ",
    "c_ex_intro": "\n--- مثال محلول: {title} ---",
    "c_ex_obs": "\n--- ما الذي يجب أن تلاحظه ---",
    "c_data": "   بيانات المسألة:",
    "c_again_hint": "(أنت الآن في قائمة الجزء: اختر [1] لتجربة بياناتك الخاصة أو [0] للخروج.)",
    "c_shape_hint": "[i] إذا ظهرت الحروف العربية منفصلة فشغّل البرنامج مع الخيار --shape-ar (يتطلب arabic-reshaper و python-bidi).",
    "c_no_sympy": "مكتبة SymPy مطلوبة للجزء الثالث (pip install sympy).",
    # ---- self-test --------------------------------------------------------
    "c_st_hdr": "\n--- الاختبار الذاتي: إعادة إنتاج النتائج المرجعية ---",
    "c_st_sum": "\n   الاختبار الذاتي: نجح {p} من {t} فحصاً.",
    "c_st_skip": "تخطّي", "c_st_pass": "نجح", "c_st_fail": "فشل",
    # ---- help texts ---------------------------------------------------------
    "h_generic": "مساعدة: اكتب القيمة ثم Enter. اضغط Enter وحدها لقبول القيمة الافتراضية الظاهرة بين [الأقواس].",
    "h_c_ask_menu": "اكتب الرقم الظاهر بين الأقواس، مثلاً 1 للجزء الأول، ثم اضغط Enter.",
    "h_c_ask_sub": "[1] أدخل بياناتك، [2] شاهد مثالاً محلولاً مع التعليق، [3] اقرأ النظرية، [0] رجوع.",
    "h_lp_ask_obj": "1 = تعظيم (ربح، إنتاج...)، 2 = تصغير (تكلفة، هدر...).",
    "h_lp_ask_n": "عدد متغيرات القرار x1..xn (المجاهيل التي تختارها). كلها تُفترض >= 0.",
    "h_lp_ask_m": "عدد القيود (موارد، متطلبات، موازنات). لا تحسب شروط x >= 0.",
    "h_lp_ask_c": "معامل هذا المتغير في دالة الهدف. مثال: ربح 5 لكل وحدة من x2 -> أدخل 5.",
    "h_lp_ask_a": "معامل هذا المتغير في القيد الحالي. أدخل 0 إذا لم يظهر في القيد.",
    "h_lp_ask_rel": "1 = '<=' (سعة / حد أعلى)، 2 = '>=' (متطلب / حد أدنى)، 3 = '=' (توازن تام).",
    "h_lp_ask_rhs": "الثابت في الطرف الأيمن للقيد (قد يكون سالباً؛ المحلّل يتعامل معه).",
    "h_lp_ask_method": "الخيار 1 يترك للبرنامج اختيار أنسب طريقة (موصى به). اختيار طريقة أخرى "
                       "يُظهر هل هي صالحة لنموذجك - مفيد للتعلّم.",
    "h_lp_ask_plot": "الطريقة البيانية ترسم منطقة الحلول الممكنة والحل الأمثل (لمتغيرين فقط).",
    "h_tp_ask_kind": "1 = نقل (شحن وحدات بأقل تكلفة)، 2 = تخصيص (عنصر واحد لكل وظيفة، أدنى تكلفة / أعلى ربح).",
    "h_tp_ask_m": "عدد المصادر (مصانع / مخازن) التي توفّر البضاعة.",
    "h_tp_ask_n": "عدد المقاصد (عملاء / أسواق) التي تطلب البضاعة.",
    "h_tp_cost_row": "تكاليف نقل الوحدة من هذا المصدر إلى كل مقصد، مفصولة بفراغات.",
    "h_tp_ask_supply": "الوحدات المتاحة في كل مصدر، مفصولة بفراغات (غير سالبة).",
    "h_tp_ask_demand": "الوحدات المطلوبة في كل مقصد، مفصولة بفراغات (غير سالبة). "
                       "إذا اختلف المجموعان يُضاف مصدر/مقصد وهمي بتكلفة صفر تلقائياً.",
    "h_as_ask_rows": "عدد العمال / العناصر المراد تخصيصها (صفوف المصفوفة).",
    "h_as_ask_cols": "عدد الوظائف / الآلات (الأعمدة). إذا اختلف عن الصفوف تُضاف صفوف/أعمدة وهمية بقيمة 0.",
    "h_as_ask_max": "1 = المصفوفة تحوي تكاليف (تصغير)، 2 = المصفوفة تحوي أرباحاً (تعظيم).",
    "h_as_row": "تكاليف (أو أرباح) هذا العامل لكل وظيفة، مفصولة بفراغات.",
    "h_nl_ask_fun": "استخدم x كمتغير. اكتب الضرب صراحة (2*x). القوى: x**2 أو x^2. "
                    "الدوال: sin cos tan exp log sqrt abs؛ الثوابت: pi, E.",
    "h_nl_ask_goal": "1 = إيجاد أصغر قيمة للدالة، 2 = إيجاد أكبر قيمة للدالة.",
    "h_nl_ask_a": "الطرف الأيسر لفترة البحث [a, b] التي تحوي القيمة المثلى.",
    "h_nl_ask_b": "الطرف الأيمن لفترة البحث؛ يجب أن يكون أكبر من a.",
    "h_nl_ask_tol": "تفاوت التوقف: كلما صغر زادت الدقة وزادت التكرارات. المدى العملي 1e-12 .. 1.",
    "h_nl_ask_x0": "تخمين بداية لنيوتن/القاطع داخل [a, b]. الأفضل أن يكون قريباً من النهاية المتوقعة.",
    "h_nl_ask_x1": "النقطة الثانية للقاطع؛ يجب أن تختلف عن x0 وتقع داخل [a, b].",
})

# ------------------------------ PART 1 : LP ---------------------------------
_EN.update({
    "lp_name": "OptiArchitect - Part 1: Linear Programming",
    "lp_title": "\n=== PART 1 | LINEAR PROGRAMMING ===",
    "lp_ask_obj": "\nSelect objective type (1 for MAX, 2 for MIN) [Default: 1]: ",
    "lp_ask_n": "Enter number of decision variables (N >= 1) [Default: 2]: ",
    "lp_ask_m": "Enter number of constraints (M >= 1) [Default: 2]: ",
    "lp_hdr_obj": "\n--- Objective function coefficients ---",
    "lp_ask_c": "  {name}, enter coefficient of x{j} in Z: ",
    "lp_hdr_con": "\n--- Constraints setup ---", "lp_con_no": "Constraint #{i}:",
    "lp_ask_a": "  Coefficient of x{j}: ",
    "lp_ask_rel": "  Relation (1 for <=, 2 for >=, 3 for =): ",
    "lp_ask_rhs": "  Right-hand side (RHS) value: ",
    "lp_echo": "\n--- YOUR MODEL (check it before solving) ---",
    "lp_rep_title": "ACADEMIC DIAGNOSIS & METHOD ROUTING REPORT",
    "lp_rep_welcome": "Welcome {name}, the model was analysed:",
    "lp_rep_summary": " * Variables: {n} | Constraints: {m} | Objective: {obj}",
    "lp_rec": " * Recommended method: {method}",
    "lp_rep_reason": " * Reason: {reason}",
    "lp_applic": "\n Applicability of each method to THIS model:",
    "lp_ap_ok": "[APPLICABLE]", "lp_ap_no": "[BYPASSED]",
    "lp_m_standard": "Standard Simplex", "lp_m_dual": "Dual Simplex", "lp_m_two_phase": "Two-Phase Simplex",
    "lp_r_std_ok": "all rows are '<=' with RHS >= 0, so the slack basis is already feasible.",
    "lp_r_std_no": "needs all rows '<=' and RHS >= 0 (you have '>=', '=' or a negative RHS).",
    "lp_r_dual_ok": "no '=' rows and the Z row is already optimal, only feasibility must be repaired.",
    "lp_r_dual_eq": "needs a model without '=' rows.",
    "lp_r_dual_c": "needs an optimal-looking Z row at the start (maximize form: all c <= 0, e.g. MIN with c >= 0).",
    "lp_r_tp": "always valid; artificial variables are removed in Phase I.",
    "lp_cmp_note": " * Note: Big-M would also work but needs a huge penalty constant M that can cause numerical "
                   "trouble; Two-Phase avoids it.",
    "lp_ask_method": "\nChoose method (1 = automatic/recommended, 2 = Standard, 3 = Dual, 4 = Two-Phase) [Default: 1]: ",
    "lp_forced_bad": "   [!] {method} cannot start on this model. Reason: {why}\n       The recommended method is used instead.",
    "lp_press_enter": "\nPress Enter to start solving...",
    "lp_running": "\n>>> Running: {method}",
    "lp_st_optimal": "Status: OPTIMAL",
    "lp_st_infeasible": "Status: INFEASIBLE - no point satisfies all constraints.",
    "lp_st_unbounded": "Status: UNBOUNDED - the objective improves without limit.",
    "lp_st_iteration_limit": "Status: ITERATION LIMIT reached - result is NOT reliable.",
    "lp_sum_title": "RESULTS ({name})",
    "lp_obj_val": "Optimal objective value (Z) = {z:.6f}", "lp_iters": "Iterations: {k}",
    "lp_viol": "Max constraint violation (independent check): {v:.2e}",
    "lp_ask_plot": "\nDraw the graphical solution (feasible region + optimum)? (Y/n): ",
    "lp_plot_skip": "   (Graphical method needs exactly 2 variables - skipped.)",
    "lp_plot_title": "Feasible Region - {name}",
    "lp_plot_missing": "   [!] matplotlib is not installed (pip install matplotlib) - plot skipped.",
    "lp_plot_saved": "   [i] No interactive display available: figure saved to {path}",
    "lp_trace_note": "   [Tableau legend] Basic = basic variable of each row; Z row negative entries mean Z can still improve.",
    # worked examples
    "lp_ex_menu": "Worked examples:\n  [1] Production plan (MAX, all '<=')           -> Standard Simplex + graph\n"
                  "  [2] Diet / cost problem (MIN, '>=' rows)      -> Dual Simplex\n"
                  "  [3] Exact balance with an '=' row             -> Two-Phase Simplex",
    "lp_ex1_t": "Production plan - Standard Simplex",
    "lp_ex1_s": "A workshop earns 3 per unit of x1 and 5 per unit of x2. Machine capacities: x1 <= 4, 2*x2 <= 12, "
                "3*x1 + 2*x2 <= 18.",
    "lp_ex1_o": " 1. Every row is '<=' with RHS >= 0, so the slack variables form a feasible start: Standard Simplex.\n"
                " 2. Show detail mode (menu 5) to watch the tableaus: x2 enters first (most negative Z entry), then x1.\n"
                " 3. Optimum x = (2, 6), Z = 36. In the graph it is the corner where constraints 2 and 3 meet.",
    "lp_ex2_t": "Diet / cost problem - Dual Simplex",
    "lp_ex2_s": "Minimize cost 2*x1 + 3*x2 while meeting requirements x1 + x2 >= 4 and x1 + 3*x2 >= 6.",
    "lp_ex2_o": " 1. '>=' rows give a negative RHS after conversion, so the origin is NOT feasible.\n"
                " 2. But the Z row is already optimal (all costs >= 0): Dual Simplex repairs feasibility directly, no artificial variables.\n"
                " 3. Optimum x = (3, 1), Z = 9.",
    "lp_ex3_t": "Exact balance - Two-Phase Simplex",
    "lp_ex3_s": "Maximize 3*x1 + 2*x2 where x1 + x2 = 4 (exact production quota) and x1 <= 3.",
    "lp_ex3_o": " 1. The '=' row has no slack variable, so no basic feasible start exists: Phase I adds an artificial variable.\n"
                " 2. Phase I drives the artificial variable to 0 (otherwise the model is INFEASIBLE), Phase II optimizes Z.\n"
                " 3. Optimum x = (3, 1), Z = 11.",
    "lp_learn": """
PART 1 - LINEAR PROGRAMMING (LP)
Model:  maximize / minimize  c.x   subject to  A x (<=, >=, =) b ,  x >= 0.

1) STANDARD (PRIMAL) SIMPLEX
   Use when : every row is '<=' and every RHS >= 0 (slack variables give a feasible start).
   Idea     : walk from corner to neighbouring corner of the feasible region, improving Z each time.
   Steps    : (1) add one slack variable per row;
              (2) entering variable = most negative entry of the Z row;
              (3) leaving row = minimum ratio RHS / (positive column entries);
              (4) pivot; (5) stop when the Z row has no negative entry.
   Reading  : no positive entry in the entering column => UNBOUNDED.

2) DUAL SIMPLEX
   Use when : no '=' rows and the Z row is already optimal, but some RHS is negative
              (typical for MIN problems with '>=' rows).
   Idea     : keep optimality, repair feasibility.
   Steps    : (1) leaving row = most negative RHS; (2) entering column = minimum of |Z_j / a_rj| over
              the negative entries of that row; (3) pivot; (4) stop when all RHS >= 0.
   Reading  : no negative entry in the leaving row => INFEASIBLE.

3) TWO-PHASE SIMPLEX
   Use when : '=' rows are present or no easy feasible start exists.
   Phase I  : add artificial variables and minimize their sum. A positive minimum => INFEASIBLE.
   Phase II : remove the artificials and optimize the real objective from the feasible basis found.
   Benefit  : no huge constant M (unlike Big-M).

4) GRAPHICAL METHOD (2 variables)
   Draw each constraint line, shade the feasible region, slide the objective line (dashed): the
   optimum sits at a corner of the region.

SPECIAL OUTCOMES: INFEASIBLE (empty region), UNBOUNDED (Z improves forever), alternative optima
(a zero in the Z row of a non-basic variable at the end).
""",
})
_AR.update({
    "lp_name": "OptiArchitect - الجزء الأول: البرمجة الخطية",
    "lp_title": "\n=== الجزء الأول | البرمجة الخطية ===",
    "lp_ask_obj": "\nاختر نوع دالة الهدف (1 لـ MAX، 2 لـ MIN) [الافتراضي: 1]: ",
    "lp_ask_n": "أدخل عدد متغيرات القرار (N >= 1) [الافتراضي: 2]: ",
    "lp_ask_m": "أدخل عدد القيود (M >= 1) [الافتراضي: 2]: ",
    "lp_hdr_obj": "\n--- معاملات دالة الهدف ---",
    "lp_ask_c": "  {name}، أدخل معامل x{j} في Z: ",
    "lp_hdr_con": "\n--- إدخال القيود ---", "lp_con_no": "القيد رقم #{i}:",
    "lp_ask_a": "  معامل x{j}: ",
    "lp_ask_rel": "  نوع العلاقة (1 لـ <=، 2 لـ >=، 3 لـ =): ",
    "lp_ask_rhs": "  قيمة الطرف الأيمن (RHS): ",
    "lp_echo": "\n--- نموذجك (راجعه قبل الحل) ---",
    "lp_rep_title": "تقرير التشخيص الأكاديمي وتوجيه الحل",
    "lp_rep_welcome": "أهلاً بك {name}، تم تحليل النموذج:",
    "lp_rep_summary": " * عدد المتغيرات: {n} | عدد القيود: {m} | دالة الهدف: {obj}",
    "lp_rec": " * الطريقة الموصى بها: {method}",
    "lp_rep_reason": " * السبب: {reason}",
    "lp_applic": "\n صلاحية كل طريقة لهذا النموذج:",
    "lp_ap_ok": "[صالحة]", "lp_ap_no": "[مستبعدة]",
    "lp_m_standard": "السيمبلكس القياسي", "lp_m_dual": "السيمبلكس الثنائي", "lp_m_two_phase": "طريقة المرحلتين",
    "lp_r_std_ok": "جميع القيود (<=) والطرف الأيمن غير سالب، فالأساس الابتدائي (المتغيرات الراكدة) مقبول.",
    "lp_r_std_no": "تتطلب أن تكون كل القيود (<=) وأن يكون الطرف الأيمن >= 0 (لديك >= أو = أو طرف أيمن سالب).",
    "lp_r_dual_ok": "لا توجد قيود مساواة وصف Z مثالي مسبقاً، فيكفي إصلاح الإمكانية فقط.",
    "lp_r_dual_eq": "تتطلب نموذجاً بلا قيود مساواة.",
    "lp_r_dual_c": "تتطلب صف Z مثالياً من البداية (بصيغة التعظيم: كل المعاملات c <= 0، مثل MIN بمعاملات >= 0).",
    "lp_r_tp": "صالحة دائماً؛ وتُزال المتغيرات الاصطناعية في المرحلة الأولى.",
    "lp_cmp_note": " * ملاحظة: طريقة M الكبرى ممكنة أيضاً لكنها تحتاج ثابتاً عقابياً ضخماً M قد يسبب مشكلات عددية؛ "
                   "وطريقة المرحلتين تتجنب ذلك.",
    "lp_ask_method": "\nاختر الطريقة (1 = تلقائي/موصى به، 2 = قياسي، 3 = ثنائي، 4 = مرحلتان) [الافتراضي: 1]: ",
    "lp_forced_bad": "   [!] لا يمكن بدء {method} على هذا النموذج. السبب: {why}\n       سيُستخدم الأسلوب الموصى به بدلاً منها.",
    "lp_press_enter": "\nاضغط Enter لبدء الحل...",
    "lp_running": "\n>>> جارٍ التشغيل: {method}",
    "lp_st_optimal": "الحالة: حل أمثل",
    "lp_st_infeasible": "الحالة: غير ممكنة - لا توجد نقطة تحقق جميع القيود.",
    "lp_st_unbounded": "الحالة: غير محدودة - تتحسن دالة الهدف بلا حدود.",
    "lp_st_iteration_limit": "الحالة: بلغ الحد الأقصى للتكرارات - النتيجة غير موثوقة.",
    "lp_sum_title": "النتائج ({name})",
    "lp_obj_val": "القيمة المثلى لدالة الهدف (Z) = {z:.6f}", "lp_iters": "عدد التكرارات: {k}",
    "lp_viol": "أقصى انتهاك للقيود (فحص مستقل): {v:.2e}",
    "lp_ask_plot": "\nهل ترسم الحل البياني (منطقة الحلول الممكنة + الحل الأمثل)؟ (Y/n): ",
    "lp_plot_skip": "   (الطريقة البيانية تتطلب متغيرين بالضبط - تم التخطي.)",
    "lp_plot_title": "منطقة الحلول الممكنة - {name}",
    "lp_plot_missing": "   [!] مكتبة matplotlib غير مثبتة (pip install matplotlib) - تم تخطي الرسم.",
    "lp_plot_saved": "   [i] لا توجد شاشة تفاعلية: حُفظ الرسم في {path}",
    "lp_trace_note": "   [دليل الجدول] Basic = المتغير الأساسي في كل صف؛ القيم السالبة في صف Z تعني أن Z قابلة للتحسين.",
    "lp_ex_menu": "أمثلة محلولة:\n  [1] خطة إنتاج (MAX، كل القيود <=)            -> السيمبلكس القياسي + رسم\n"
                  "  [2] مسألة غذاء / تكلفة (MIN، قيود >=)         -> السيمبلكس الثنائي\n"
                  "  [3] توازن تام بقيد مساواة                      -> طريقة المرحلتين",
    "lp_ex1_t": "خطة إنتاج - السيمبلكس القياسي",
    "lp_ex1_s": "ورشة تربح 3 لكل وحدة من x1 و5 لكل وحدة من x2. سعات الآلات: x1 <= 4، 2*x2 <= 12، "
                "3*x1 + 2*x2 <= 18.",
    "lp_ex1_o": " 1. كل القيود (<=) والطرف الأيمن >= 0، فالمتغيرات الراكدة تعطي بداية ممكنة: السيمبلكس القياسي.\n"
                " 2. فعّل وضع التفصيل (القائمة 5) لترى الجداول: يدخل x2 أولاً (أكبر سالب في صف Z) ثم x1.\n"
                " 3. الحل الأمثل x = (2, 6) و Z = 36، وهو في الرسم الركن الذي يلتقي فيه القيدان 2 و3.",
    "lp_ex2_t": "مسألة غذاء / تكلفة - السيمبلكس الثنائي",
    "lp_ex2_s": "صغّر التكلفة 2*x1 + 3*x2 مع تحقيق المتطلبات x1 + x2 >= 4 و x1 + 3*x2 >= 6.",
    "lp_ex2_o": " 1. قيود (>=) تعطي طرفاً أيمن سالباً بعد التحويل، فنقطة الأصل غير ممكنة.\n"
                " 2. لكن صف Z مثالي مسبقاً (كل التكاليف >= 0): يصلح السيمبلكس الثنائي الإمكانية مباشرة دون متغيرات اصطناعية.\n"
                " 3. الحل الأمثل x = (3, 1) و Z = 9.",
    "lp_ex3_t": "توازن تام - طريقة المرحلتين",
    "lp_ex3_s": "عظّم 3*x1 + 2*x2 حيث x1 + x2 = 4 (حصة إنتاج محددة تماماً) و x1 <= 3.",
    "lp_ex3_o": " 1. قيد المساواة بلا متغير راكد فلا يوجد أساس ابتدائي ممكن: تضيف المرحلة الأولى متغيراً اصطناعياً.\n"
                " 2. تخفّض المرحلة الأولى المتغير الاصطناعي إلى 0 (وإلا فالنموذج غير ممكن) ثم تحسّن المرحلة الثانية Z.\n"
                " 3. الحل الأمثل x = (3, 1) و Z = 11.",
    "lp_learn": """
الجزء الأول - البرمجة الخطية (LP)
النموذج:  تعظيم / تصغير  c.x   تحت القيود  A x (<=, >=, =) b ،  x >= 0.

1) السيمبلكس القياسي (الأولي)
   متى: كل القيود (<=) وكل الأطراف اليمنى >= 0 (المتغيرات الراكدة تعطي بداية ممكنة).
   الفكرة: الانتقال من ركن إلى ركن مجاور في منطقة الحلول مع تحسين Z في كل مرة.
   الخطوات: (1) أضف متغيراً راكداً لكل قيد؛
            (2) المتغير الداخل = أكبر قيمة سالبة في صف Z؛
            (3) الصف الخارج = أصغر نسبة RHS / (عناصر العمود الموجبة)؛
            (4) أجرِ عملية المحور؛ (5) توقف حين لا توجد قيمة سالبة في صف Z.
   القراءة: إذا لم يوجد عنصر موجب في العمود الداخل => المسألة غير محدودة.

2) السيمبلكس الثنائي
   متى: لا توجد قيود مساواة وصف Z مثالي مسبقاً لكن بعض الأطراف اليمنى سالبة
        (شائع في مسائل MIN ذات قيود >=).
   الفكرة: نحافظ على الأمثلية ونصلح الإمكانية.
   الخطوات: (1) الصف الخارج = أكثر طرف أيمن سالباً؛ (2) العمود الداخل = أصغر |Z_j / a_rj| بين
            العناصر السالبة في ذلك الصف؛ (3) المحور؛ (4) توقف حين تصبح كل RHS >= 0.
   القراءة: إذا لم يوجد عنصر سالب في الصف الخارج => المسألة غير ممكنة.

3) طريقة المرحلتين
   متى: وجود قيود مساواة أو غياب بداية ممكنة سهلة.
   المرحلة الأولى: أضف متغيرات اصطناعية وصغّر مجموعها. إن بقي موجباً => المسألة غير ممكنة.
   المرحلة الثانية: احذف الاصطناعية وحسّن دالة الهدف الحقيقية انطلاقاً من الأساس الممكن.
   الميزة: لا تحتاج ثابتاً ضخماً M (بخلاف طريقة M الكبرى).

4) الطريقة البيانية (متغيران)
   ارسم خط كل قيد، ظلّل منطقة الحلول الممكنة، وحرّك خط دالة الهدف (المتقطع): الحل الأمثل يقع عند ركن.

حالات خاصة: غير ممكنة (منطقة فارغة)، غير محدودة (Z تتحسن بلا نهاية)، حلول مثلى بديلة
(وجود صفر في صف Z لمتغير غير أساسي عند النهاية).
""",
})

# ------------------------ PART 2 : TRANSPORT & ASSIGNMENT ---------------------
_EN.update({
    "tp_name": "OptiArchitect - Part 2: Transportation & Assignment",
    "tp_title": "\n=== PART 2 | TRANSPORTATION & ASSIGNMENT ===",
    "tp_ask_kind": "Select problem type:\n  1. Transportation problem\n  2. Assignment problem\nEnter choice (1 or 2) [Default: 1]: ",
    "tp_hdr": "\n" + "-" * 55 + "\n   Transportation Problem Data Input\n" + "-" * 55,
    "tp_ask_m": "Enter number of Sources (m) [Default: 3]: ",
    "tp_ask_n": "Enter number of Destinations (n) [Default: 3]: ",
    "tp_cost_hdr": "\nEnter Cost Matrix ({m}x{n}) [one row per line, numbers separated by spaces]:",
    "tp_cost_row": "Row {i}: ",
    "tp_ask_supply": "\nEnter Supply Vector (length {m}): ",
    "tp_ask_demand": "Enter Demand Vector (length {n}): ",
    "tp_bal_source": "\n   [!] Unbalanced: Supply = {ts:g} < Demand = {td:g}. A dummy SOURCE (S*) with supply {d:g} and cost 0 was added.",
    "tp_bal_destination": "\n   [!] Unbalanced: Supply = {ts:g} > Demand = {td:g}. A dummy DESTINATION (D*) with demand {d:g} and cost 0 was added.",
    "tp_bal_ok": "\n   Balanced problem: total supply = total demand = {ts:g}.",
    "tp_rep": "Technical Method Analysis Report ({name})",
    "tp_sec_ibfs": "\n--- [1] INITIAL BASIC FEASIBLE SOLUTION (IBFS) METHODS ---",
    "tp_t_nw": "\n1. North-West Corner Rule (NWCR):", "tp_n_nw": "   [Note] Ignores shipping costs entirely - fast but usually far from optimal.",
    "tp_t_lc": "\n2. Least Cost Method (LCM):", "tp_n_lc": "   [Note] Greedy: cheapest available cell first.",
    "tp_t_vam": "\n3. Vogel's Approximation Method (VAM):", "tp_n_vam": "   [Note] Uses penalty (opportunity) costs to avoid expensive cells; usually the best start.",
    "tp_s_nw": "Allocated {q:g} units to cell ({i},{j}).",
    "tp_s_lc": "Min cost {c:g} at ({i},{j}). Allocated {q:g} units.",
    "tp_s_vam": "Penalty {p} -> cell ({i},{j}) [cost {c:g}]. Allocated {q:g} units.",
    "tp_forced": "forced (single option)",
    "tp_tot": "   --> Total Cost ({m}) = {c:.4f}",
    "tp_alloc_hdr": "   Allocation matrix:",
    "tp_sec_opt": "\n--- [2] OPTIMALITY TEST AND IMPROVEMENT (MODI / u-v METHOD) ---",
    "tp_note_modi": "   [Note] u_i + v_j = c_ij on basic cells; Delta_ij = c_ij - (u_i + v_j) on the others. "
                    "A negative Delta means the plan can be improved by shipping along that cell.",
    "tp_start": "   Starting point: {m} (cost {c:.4f}, the cheapest IBFS).",
    "tp_degen": "   [!] Degenerate basis: {k} zero-valued basic cell(s) were added to complete the m+n-1 spanning tree.",
    "tp_it_line": "   Iteration {k}: enter ({i},{j}) with Delta={d:g}; shift theta={t:g}; leave ({a},{b}); cost -> {c:.4f}",
    "tp_loop": "      closed loop: {loop}",
    "tp_uv": "      u = {u}\n      v = {v}",
    "tp_delta_hdr": "      Net evaluation matrix Delta:",
    "tp_optimal": "   [V] OPTIMAL: all Delta_ij >= 0 after {k} iteration(s).",
    "tp_limit": "   [X] Iteration limit reached - result is NOT guaranteed optimal.",
    "tp_alt": "   [i] Some non-basic Delta_ij = 0: alternative optimal solutions exist.",
    "tp_final_hdr": "\n--- [3] OPTIMAL TRANSPORTATION PLAN ---",
    "tp_final_cost": "   --> Minimum Total Cost = {c:.4f}",
    "tp_check": "   Feasibility check (max residual of supply/demand): {r:.2e}",
    "tp_unmet": "   Unmet demand at destination D{j}: {q:g} units (shipped from the dummy source).",
    "tp_unused": "   Unused supply at source S{i}: {q:g} units (sent to the dummy destination).",
    "as_hdr": "\n" + "-" * 55 + "\n   Assignment Problem Data Input\n" + "-" * 55,
    "as_ask_rows": "Enter number of Workers/Items (Rows) [Default: 3]: ",
    "as_ask_cols": "Enter number of Jobs/Machines (Cols) [Default: 3]: ",
    "as_ask_max": "Objective (1 = minimize cost, 2 = maximize profit) [Default: 1]: ",
    "as_rep": "Technical Execution Report for Assignment ({name})",
    "as_pad": "   [!] Non-square matrix ({r}x{c}): padded with zero dummy rows/columns.",
    "as_h_title": "\nMethod: Hungarian Algorithm",
    "as_h_note": "   [Note] Row/column reduction, then adjustments using a minimum line cover until n independent zeros exist.",
    "as_h_row": "\n   Step 1 - subtract row minimums:", "as_h_col": "\n   Step 2 - subtract column minimums:",
    "as_h_adj": "\n   Iteration {k}: only {a} independent zeros (< n). Adjust by min uncovered value {d:g}:",
    "as_h_done": "\n   {n} independent zeros found -> optimal assignment.",
    "as_res_hdr": "\n   --> Optimal Assignments:",
    "as_res_row": "       Item {i} -> Job {j} (value = {c:g})",
    "as_res_dummy": "       Item {i} -> dummy job (no real assignment)",
    "as_res_free": "       Job {j} is left unassigned",
    "as_tot_min": "   --> Total Minimum Assignment Cost = {c:.4f}",
    "as_tot_max": "   --> Total Maximum Assignment Profit = {c:.4f}",
    "tp_ex_menu": "Worked examples:\n  [1] Balanced transportation (3 sources, 4 destinations)\n"
                  "  [2] Unbalanced transportation (dummy destination)\n"
                  "  [3] Assignment, minimize cost (4 x 4)\n"
                  "  [4] Assignment, maximize profit (3 workers, 4 jobs: non-square)",
    "tp_ex1_t": "Balanced transportation", "tp_ex2_t": "Unbalanced transportation",
    "tp_ex3_t": "Assignment (min cost)", "tp_ex4_t": "Assignment (max profit, non-square)",
    "tp_ex1_s": "Three factories supply 40, 30 and 40 units; four markets demand 15, 5, 45 and 45 units. "
                "Total supply = total demand = 110.",
    "tp_ex1_o": " 1. Compare the three initial plans: North-West (1005) ignores costs; Least Cost and Vogel both reach 700.\n"
                " 2. 700 is NOT optimal: MODI finds negative Delta values and improves the plan in two iterations to 650.\n"
                " 3. When every Delta >= 0 the plan is optimal. Turn on detail mode (menu 5) to see each closed loop.",
    "tp_ex2_s": "Supply 20, 30, 25 (total 75) but demand only 10, 25, 15, 10 (total 60).",
    "tp_ex2_o": " 1. Supply exceeds demand, so a dummy destination D* with demand 15 and cost 0 is added.\n"
                " 2. Units sent to D* are simply NOT shipped: the report lists the unused supply per source.",
    "tp_ex3_s": "Four workers, four jobs; the matrix holds the cost of each worker on each job.",
    "tp_ex3_o": " 1. Row reduction then column reduction create zeros; if fewer than 4 independent zeros exist the matrix is adjusted.\n"
                " 2. Optimal assignment is read from independent zeros; the total is computed on the ORIGINAL costs.",
    "tp_ex4_s": "Three workers, four jobs; the matrix holds profits. A dummy worker row of zeros is added.",
    "tp_ex4_o": " 1. Maximization is converted to minimization by subtracting every value from the largest one.\n"
                " 2. One job stays unassigned (matched to the dummy worker); the total profit uses the original values.",
    "tp_learn": """
PART 2 - TRANSPORTATION AND ASSIGNMENT

TRANSPORTATION: ship goods from m sources (supply S_i) to n destinations (demand D_j) at unit cost c_ij
so that total cost is minimal. If total supply != total demand, a zero-cost dummy source/destination
balances the problem.

Step A - initial basic feasible solution (IBFS)
 1) NORTH-WEST CORNER : start at the top-left cell, ship as much as possible, move right/down. Ignores costs.
 2) LEAST COST        : repeatedly use the cheapest cell that still has supply and demand.
 3) VOGEL (VAM)       : for every row/column compute the penalty = (2nd cheapest) - (cheapest); serve the cheapest
                        cell of the line with the biggest penalty. Usually the best starting point.

Step B - optimality test and improvement (MODI / u-v)
   Solve u_i + v_j = c_ij on basic cells (u_1 = 0); compute Delta_ij = c_ij - u_i - v_j for empty cells.
   If every Delta >= 0 the plan is optimal. Otherwise choose the most negative Delta, build the closed loop
   (+ / - alternately), shift theta = smallest '-' allocation, and repeat.
   Degeneracy: if fewer than m+n-1 cells are basic, zero-valued basic cells are added.
   A zero Delta on an empty cell means ALTERNATIVE optimal plans exist.

ASSIGNMENT (one worker per job): HUNGARIAN ALGORITHM
   (1) subtract each row minimum; (2) subtract each column minimum; (3) find the maximum set of independent zeros;
   (4) if fewer than n, cover all zeros with the minimum number of lines, subtract the smallest uncovered
   value from uncovered cells and add it at line intersections; repeat. Maximization: replace each value by
   (max - value). Non-square: pad with zero dummy rows/columns.
""",
})
_AR.update({
    "tp_name": "OptiArchitect - الجزء الثاني: النقل والتخصيص",
    "tp_title": "\n=== الجزء الثاني | مسائل النقل والتخصيص ===",
    "tp_ask_kind": "اختر نوع المسألة:\n  1. مسألة نقل\n  2. مسألة تخصيص / تعيين\nأدخل اختيارك (1 أو 2) [الافتراضي: 1]: ",
    "tp_hdr": "\n" + "-" * 55 + "\n   إدخال بيانات مسألة النقل\n" + "-" * 55,
    "tp_ask_m": "أدخل عدد المصادر (m) [الافتراضي: 3]: ",
    "tp_ask_n": "أدخل عدد المقاصد (n) [الافتراضي: 3]: ",
    "tp_cost_hdr": "\nأدخل مصفوفة التكاليف ({m}x{n}) [صف في كل سطر، أرقام مفصولة بفراغات]:",
    "tp_cost_row": "الصف {i}: ",
    "tp_ask_supply": "\nأدخل متجه العرض (الطول {m}): ",
    "tp_ask_demand": "أدخل متجه الطلب (الطول {n}): ",
    "tp_bal_source": "\n   [!] مسألة غير متوازنة: العرض = {ts:g} < الطلب = {td:g}. أُضيف مصدر وهمي (S*) بعرض {d:g} وتكلفة 0.",
    "tp_bal_destination": "\n   [!] مسألة غير متوازنة: العرض = {ts:g} > الطلب = {td:g}. أُضيف مقصد وهمي (D*) بطلب {d:g} وتكلفة 0.",
    "tp_bal_ok": "\n   مسألة متوازنة: إجمالي العرض = إجمالي الطلب = {ts:g}.",
    "tp_rep": "تقرير التحليل الفني لطرق النقل ({name})",
    "tp_sec_ibfs": "\n--- [1] طرق إيجاد الحل الممكن الأولي (IBFS) ---",
    "tp_t_nw": "\n1. طريقة الركن الشمالي الغربي:", "tp_n_nw": "   [ملاحظة] تتجاهل التكاليف نهائياً - سريعة لكنها غالباً بعيدة عن الأمثل.",
    "tp_t_lc": "\n2. طريقة أدنى تكلفة:", "tp_n_lc": "   [ملاحظة] جشعة: تختار الخلية الأرخص المتاحة أولاً.",
    "tp_t_vam": "\n3. طريقة فوغل التقريبية (VAM):", "tp_n_vam": "   [ملاحظة] تستخدم الغرامات (تكلفة الفرصة) لتجنب الخلايا المكلفة؛ وغالباً تعطي أفضل بداية.",
    "tp_s_nw": "تخصيص {q:g} وحدة في الخلية ({i},{j}).",
    "tp_s_lc": "أدنى تكلفة {c:g} في الخلية ({i},{j}). تخصيص {q:g} وحدة.",
    "tp_s_vam": "الغرامة {p} -> الخلية ({i},{j}) [تكلفة {c:g}]. تخصيص {q:g} وحدة.",
    "tp_forced": "إجباري (خيار وحيد)",
    "tp_tot": "   --> إجمالي التكلفة ({m}) = {c:.4f}",
    "tp_alloc_hdr": "   مصفوفة التخصيص:",
    "tp_sec_opt": "\n--- [2] اختبار الأمثلية والتحسين (طريقة MODI / u-v) ---",
    "tp_note_modi": "   [ملاحظة] u_i + v_j = c_ij في الخلايا الأساسية؛ و Delta_ij = c_ij - (u_i + v_j) في بقية الخلايا. "
                    "القيمة السالبة تعني إمكانية تحسين الخطة بالشحن عبر تلك الخلية.",
    "tp_start": "   نقطة البداية: {m} (التكلفة {c:.4f}، وهي أرخص حل أولي).",
    "tp_degen": "   [!] أساس منحل: أُضيفت {k} خلية أساسية صفرية لإكمال الشجرة الممتدة m+n-1.",
    "tp_it_line": "   التكرار {k}: دخول ({i},{j}) بـ Delta={d:g}؛ النقل theta={t:g}؛ خروج ({a},{b})؛ التكلفة -> {c:.4f}",
    "tp_loop": "      الحلقة المغلقة: {loop}",
    "tp_uv": "      u = {u}\n      v = {v}",
    "tp_delta_hdr": "      مصفوفة التقييم الصافي Delta:",
    "tp_optimal": "   [V] حل أمثل: كل Delta_ij >= 0 بعد {k} تكرار.",
    "tp_limit": "   [X] بلغ الحد الأقصى للتكرارات - الأمثلية غير مضمونة.",
    "tp_alt": "   [i] بعض قيم Delta_ij غير الأساسية = 0: توجد حلول مثلى بديلة.",
    "tp_final_hdr": "\n--- [3] خطة النقل المثلى ---",
    "tp_final_cost": "   --> أدنى تكلفة إجمالية = {c:.4f}",
    "tp_check": "   فحص الإمكانية (أقصى انحراف عن العرض/الطلب): {r:.2e}",
    "tp_unmet": "   طلب غير ملبّى في المقصد D{j}: {q:g} وحدة (من المصدر الوهمي).",
    "tp_unused": "   عرض غير مستخدم في المصدر S{i}: {q:g} وحدة (إلى المقصد الوهمي).",
    "as_hdr": "\n" + "-" * 55 + "\n   إدخال بيانات مسألة التخصيص / التعيين\n" + "-" * 55,
    "as_ask_rows": "أدخل عدد العمال/العناصر (الصفوف) [الافتراضي: 3]: ",
    "as_ask_cols": "أدخل عدد الوظائف/الآلات (الأعمدة) [الافتراضي: 3]: ",
    "as_ask_max": "الهدف (1 = تصغير التكلفة، 2 = تعظيم الربح) [الافتراضي: 1]: ",
    "as_rep": "تقرير تنفيذ مسألة التخصيص ({name})",
    "as_pad": "   [!] المصفوفة غير مربعة ({r}x{c}): أُضيفت صفوف/أعمدة وهمية بقيمة 0.",
    "as_h_title": "\nطريقة الحل: الخوارزمية المجرية",
    "as_h_note": "   [ملاحظة] اختزال الصفوف والأعمدة ثم تعديلات بخطوط تغطية دنيا حتى وجود n أصفار مستقلة.",
    "as_h_row": "\n   الخطوة 1 - طرح أدنى قيمة في كل صف:", "as_h_col": "\n   الخطوة 2 - طرح أدنى قيمة في كل عمود:",
    "as_h_adj": "\n   التكرار {k}: يوجد {a} أصفار مستقلة فقط (< n). تعديل بأصغر قيمة غير مغطاة {d:g}:",
    "as_h_done": "\n   تم إيجاد {n} أصفار مستقلة -> التخصيص أمثل.",
    "as_res_hdr": "\n   --> التخصيص الأمثل:",
    "as_res_row": "       العنصر {i} -> الوظيفة {j} (القيمة = {c:g})",
    "as_res_dummy": "       العنصر {i} -> وظيفة وهمية (لا تخصيص فعلي)",
    "as_res_free": "       الوظيفة {j} بلا تخصيص",
    "as_tot_min": "   --> إجمالي أدنى تكلفة تخصيص = {c:.4f}",
    "as_tot_max": "   --> إجمالي أعلى ربح تخصيص = {c:.4f}",
    "tp_ex_menu": "أمثلة محلولة:\n  [1] نقل متوازن (3 مصادر، 4 مقاصد)\n"
                  "  [2] نقل غير متوازن (مقصد وهمي)\n"
                  "  [3] تخصيص بتصغير التكلفة (4 × 4)\n"
                  "  [4] تخصيص بتعظيم الربح (3 عمال، 4 وظائف: مصفوفة غير مربعة)",
    "tp_ex1_t": "نقل متوازن", "tp_ex2_t": "نقل غير متوازن",
    "tp_ex3_t": "تخصيص (أدنى تكلفة)", "tp_ex4_t": "تخصيص (أعلى ربح، غير مربع)",
    "tp_ex1_s": "ثلاثة مصانع تعرض 40 و30 و40 وحدة؛ وأربعة أسواق تطلب 15 و5 و45 و45 وحدة. "
                "إجمالي العرض = إجمالي الطلب = 110.",
    "tp_ex1_o": " 1. قارن الخطط الأولية الثلاث: الركن الشمالي الغربي (1005) يتجاهل التكاليف؛ وأدنى تكلفة وفوغل يبلغان 700 معاً.\n"
                " 2. القيمة 700 ليست مثلى: يجد MODI قيم Delta سالبة ويحسّن الخطة في تكرارين إلى 650.\n"
                " 3. حين تكون كل Delta >= 0 تكون الخطة مثلى. فعّل وضع التفصيل (القائمة 5) لترى كل حلقة مغلقة.",
    "tp_ex2_s": "العرض 20 و30 و25 (المجموع 75) بينما الطلب 10 و25 و15 و10 (المجموع 60) فقط.",
    "tp_ex2_o": " 1. العرض يفوق الطلب، فيُضاف مقصد وهمي D* بطلب 15 وتكلفة 0.\n"
                " 2. الوحدات المرسلة إلى D* لا تُشحن فعلياً: يعرض التقرير العرض غير المستخدم لكل مصدر.",
    "tp_ex3_s": "أربعة عمال وأربع وظائف؛ المصفوفة تحوي تكلفة كل عامل على كل وظيفة.",
    "tp_ex3_o": " 1. اختزال الصفوف ثم الأعمدة يولّد أصفاراً؛ وإن وُجد أقل من 4 أصفار مستقلة تُعدَّل المصفوفة.\n"
                " 2. يُقرأ التخصيص الأمثل من الأصفار المستقلة، ويُحسب الإجمالي على التكاليف الأصلية.",
    "tp_ex4_s": "ثلاثة عمال وأربع وظائف؛ المصفوفة تحوي أرباحاً. يُضاف صف عامل وهمي من أصفار.",
    "tp_ex4_o": " 1. يتحول التعظيم إلى تصغير بطرح كل قيمة من أكبر قيمة.\n"
                " 2. تبقى وظيفة بلا تخصيص (تُقرن بالعامل الوهمي)؛ ويُحسب إجمالي الربح بالقيم الأصلية.",
    "tp_learn": """
الجزء الثاني - مسائل النقل والتخصيص

مسألة النقل: شحن البضاعة من m مصدراً (العرض S_i) إلى n مقصداً (الطلب D_j) بتكلفة الوحدة c_ij
بحيث تكون التكلفة الإجمالية أصغر ما يمكن. إذا اختلف إجمالي العرض عن إجمالي الطلب يُضاف مصدر/مقصد
وهمي بتكلفة صفر لموازنة المسألة.

الخطوة أ - إيجاد الحل الممكن الأولي (IBFS)
 1) الركن الشمالي الغربي: ابدأ من الخلية العليا اليسرى (حسب اتجاه الجدول)، اشحن أكبر كمية ممكنة وتحرك يميناً/لأسفل. تتجاهل التكاليف.
 2) أدنى تكلفة: استخدم مراراً أرخص خلية ما زال فيها عرض وطلب.
 3) فوغل (VAM): لكل صف/عمود احسب الغرامة = (ثاني أرخص) - (أرخص)؛ واخدم أرخص خلية في الخط ذي الغرامة الأكبر.
    غالباً تعطي أفضل نقطة بداية.

الخطوة ب - اختبار الأمثلية والتحسين (MODI / u-v)
   حل u_i + v_j = c_ij للخلايا الأساسية (u_1 = 0)؛ ثم احسب Delta_ij = c_ij - u_i - v_j للخلايا الفارغة.
   إذا كانت كل Delta >= 0 فالخطة مثلى. وإلا اختر أكبر Delta سالبة، وابنِ الحلقة المغلقة
   (+ / - بالتناوب)، وانقل theta = أصغر كمية في خلايا (-)، وكرر.
   الانحلال: إذا كانت الخلايا الأساسية أقل من m+n-1 تُضاف خلايا أساسية بقيمة صفر.
   وجود Delta = 0 في خلية فارغة يعني وجود خطط مثلى بديلة.

التخصيص (عامل واحد لكل وظيفة): الخوارزمية المجرية
   (1) اطرح أصغر قيمة في كل صف؛ (2) اطرح أصغر قيمة في كل عمود؛ (3) جد أكبر مجموعة أصفار مستقلة؛
   (4) إن كانت أقل من n غطِّ كل الأصفار بأقل عدد من الخطوط، واطرح أصغر قيمة غير مغطاة من الخلايا
   غير المغطاة وأضفها عند تقاطع الخطوط، ثم كرر. للتعظيم: استبدل كل قيمة بـ (الأكبر - القيمة).
   المصفوفة غير المربعة: تُكمَّل بصفوف/أعمدة وهمية من أصفار.
""",
})

# ------------------------------ PART 3 : NLP --------------------------------
_EN.update({
    "nl_name": "OptiArchitect - Part 3: Non-Linear Optimization",
    "nl_title": "\n=== PART 3 | SINGLE-VARIABLE NON-LINEAR OPTIMIZATION ===",
    "nl_ask_fun": "Enter f(x) [variable x; ^ or **; sin cos tan exp log sqrt abs pi E] [Default: (x-2)**2+1]: ",
    "nl_default_fun": "(x-2)**2+1",
    "nl_ask_goal": "Goal (1 = minimize, 2 = maximize) [Default: 1]: ",
    "nl_ask_a": "Interval start a [Default: 0]: ", "nl_ask_b": "Interval end b [Default: 5]: ",
    "nl_ask_tol": "Tolerance (1e-12 .. 1) [Default: 1e-6]: ",
    "nl_ask_x0": "Starting point x0 for Newton/Secant [Default: midpoint]: ",
    "nl_ask_x1": "Second point x1 for Secant [Default: x0 + 10% of the interval]: ",
    "nl_err_expr": "   [X] Invalid expression: {e}",
    "nl_err_interval": "   [!] b must be greater than a.",
    "nl_err_inside": "   [!] Both points must lie inside [a, b] and they must differ.",
    "nl_rep": "Technical Analysis Report ({name})",
    "nl_fun": "   f(x)   = {t}", "nl_d1": "   f'(x)  = {t}", "nl_d2": "   f''(x) = {t}",
    "nl_numeric": "   [!] Some derivatives are not smooth/symbolic: finite differences are used (less accurate).",
    "nl_sec_diag": "\n--- [1] APPLICABILITY ANALYSIS ---",
    "nl_applicable": "[APPLICABLE]", "nl_caution": "[CAUTION]", "nl_bypassed": "[BYPASSED]",
    "nl_m_golden": "Golden Section", "nl_m_fibonacci": "Fibonacci Search", "nl_m_newton": "Newton-Raphson", "nl_m_secant": "Secant",
    "uni_unimodal": "single valley detected on [a, b] (sampling test, a heuristic - not a proof).",
    "uni_monotone": "monotone on [a, b]: the minimum is at an endpoint.",
    "uni_flat": "function is constant on [a, b] (every point is optimal).",
    "uni_multimodal": "several local minima/maxima detected: bracketing may return only a local optimum.",
    "uni_domain": "f(x) is undefined at some sample points of [a, b]: bracketing cannot be used.",
    "newton_ok": "f''(x0) = {v:.6g} > 0.",
    "newton_curv": "f''(x0) = {v:.6g} <= 0: Newton would be attracted to a maximum/inflection; choose another x0.",
    "deriv_fail": "derivative cannot be evaluated at the starting point(s).",
    "secant_ok": "two distinct starting points with defined f'.",
    "secant_same": "x0 and x1 must be different.",
    "nl_sec_res": "\n--- [2] RESULTS ---",
    "nl_res": "{m}: x* = {x:.8g} | f(x*) = {fx:.8g} | iterations = {it} | evaluations = {ev}",
    "nl_status": "   status: {s}",
    "st_converged": "CONVERGED", "st_max_iter": "ITERATION LIMIT - not converged",
    "st_zero_curvature": "FAILED - zero curvature (f'' ~ 0)",
    "st_not_minimum": "STOPPED at a stationary point that is NOT a minimum",
    "st_left_interval": "FAILED - iterate left [a, b]", "st_diverged": "FAILED - diverged",
    "st_domain_error": "FAILED - function undefined along the way",
    "n_precision": "   note: tol is below the attainable accuracy (~{limit:.1e}); digits beyond that are noise.",
    "n_endpoint": "   note: the optimum is at the boundary of [a, b].",
    "n_fib_n": "   note: Fibonacci N = {n} evaluations chosen from the tolerance.",
    "n_maximum": "   note: f''(x*) < 0 - this is a local MAXIMUM of the minimized function.",
    "n_inflection": "   note: f''(x*) ~ 0 - inflection/undetermined point, not a verified minimum.",
    "n_zero_curvature": "   note: Newton/Secant step is undefined here.",
    "n_left_interval": "   note: the next iterate {x:.6g} is outside [a, b].",
    "n_diverged": "   note: |x| became huge.", "n_domain": "   note: f or a derivative is undefined near the iterate.",
    "nl_table": "      iteration table:",
    "nl_sec_ver": "\n--- [3] VERIFICATION ---",
    "nl_grid": "   Reference grid scan (2001 points): x ~ {x:.6g}, f ~ {fx:.8g}",
    "nl_best": "   Best converged result: {m} -> x* = {x:.8g}, f(x*) = {fx:.8g}",
    "nl_agree": "   [V] The best result agrees with the grid scan.",
    "nl_worse": "   [X] The grid scan found a better value than the best method result: the function may be multimodal; results are local.",
    "nl_none": "   [X] No method converged.",
    "nl_ex_menu": "Worked examples:\n  [1] f(x) = (x-2)^2 + 1 on [0, 5], minimize           -> all four methods agree\n"
                  "  [2] f(x) = x*exp(-x) on [0, 5], MAXIMIZE            -> maximization via sign change\n"
                  "  [3] f(x) = x^4 - 3x^3 + 2 on [0, 3], minimize       -> Newton is bypassed (f'' = 0 at x0)",
    "nl_ex1_t": "Parabola", "nl_ex2_t": "Maximization", "nl_ex3_t": "Why a method can be bypassed",
    "nl_ex1_s": "Minimize f(x) = (x-2)^2 + 1 on [0, 5] with tolerance 1e-6.",
    "nl_ex1_o": " 1. A single valley is detected, so Golden Section and Fibonacci are applicable; f'' > 0 so Newton/Secant also work.\n"
                " 2. Compare the number of evaluations: Fibonacci uses the fewest bracketing evaluations; Newton needs very few iterations.\n"
                " 3. All results agree with the independent grid scan: x* = 2, f(x*) = 1.",
    "nl_ex2_s": "Maximize f(x) = x*exp(-x) on [0, 5] (starting points x0 = 0.5, x1 = 0.8).",
    "nl_ex2_o": " 1. Maximizing f is the same as minimizing -f; the program does this automatically and reports the ORIGINAL f.\n"
                " 2. Expected optimum: x* = 1, f(x*) = 0.3679.",
    "nl_ex3_s": "Minimize f(x) = x^4 - 3x^3 + 2 on [0, 3] with starting points x0 = 1.5 (the midpoint) and x1 = 2.0.",
    "nl_ex3_o": " 1. At x0 = 1.5 we get f''(x0) = 12x^2 - 18x = 0: the Newton step would divide by zero, so Newton is [BYPASSED].\n"
                " 2. Bracketing methods and Secant do not need f'' at the start and find x* = 2.25.\n"
                " 3. Lesson: always check the applicability report before trusting a derivative-based method.\n"
                " 4. Try your own problem with x1 = 1.8: the first Secant jump leaves [0, 3] and the method reports FAILED -\n"
                "    starting points matter for derivative-based methods.",
    "nl_learn": """
PART 3 - SINGLE-VARIABLE NON-LINEAR OPTIMIZATION
Goal: find x* in [a, b] that minimizes f(x) (a maximum is found by minimizing -f).

BRACKETING METHODS (no derivatives; need a UNIMODAL function = one valley on [a, b])
 1) GOLDEN SECTION : keep two interior points at the golden ratio (0.618); each step discards the part of the
                     interval that cannot contain the minimum and reuses one old evaluation. The interval shrinks
                     by 0.618 per evaluation.
 2) FIBONACCI      : like Golden Section but the ratios come from Fibonacci numbers; for a fixed number N of
                     evaluations it gives the smallest possible final interval, so N is chosen from the tolerance.

DERIVATIVE METHODS (fast, but need a good starting point and smoothness)
 3) NEWTON-RAPHSON : solves f'(x) = 0 using  x_new = x - f'(x) / f''(x).  Quadratic convergence near the answer.
                     Danger: f'' <= 0 at the start leads to a maximum/inflection; f'' ~ 0 breaks the step.
 4) SECANT         : like Newton but replaces f'' by the slope between the last two values of f'; needs two
                     starting points and no second derivative.

Safety nets in this tool: formulas are validated before evaluation, derivatives are computed symbolically,
the stationary point is classified with f'' (minimum / maximum / inflection), and the best result is compared
with an independent grid scan of 2001 points. Sampling can only SUGGEST unimodality, never prove it.
""",
})
_AR.update({
    "nl_name": "OptiArchitect - الجزء الثالث: التحسين غير الخطي",
    "nl_title": "\n=== الجزء الثالث | التحسين غير الخطي أحادي المتغير ===",
    "nl_ask_fun": "أدخل f(x) [المتغير x؛ ^ أو **؛ sin cos tan exp log sqrt abs pi E] [الافتراضي: (x-2)**2+1]: ",
    "nl_default_fun": "(x-2)**2+1",
    "nl_ask_goal": "الهدف (1 = تصغير، 2 = تعظيم) [الافتراضي: 1]: ",
    "nl_ask_a": "بداية الفترة a [الافتراضي: 0]: ", "nl_ask_b": "نهاية الفترة b [الافتراضي: 5]: ",
    "nl_ask_tol": "التفاوت المسموح (1e-12 .. 1) [الافتراضي: 1e-6]: ",
    "nl_ask_x0": "نقطة البداية x0 لنيوتن/القاطع [الافتراضي: منتصف الفترة]: ",
    "nl_ask_x1": "النقطة الثانية x1 للقاطع [الافتراضي: x0 + 10% من الفترة]: ",
    "nl_err_expr": "   [X] تعبير غير صالح: {e}",
    "nl_err_interval": "   [!] يجب أن تكون b أكبر من a.",
    "nl_err_inside": "   [!] يجب أن تقع النقطتان داخل [a, b] وأن تختلفا.",
    "nl_rep": "تقرير التحليل الفني ({name})",
    "nl_fun": "   f(x)   = {t}", "nl_d1": "   f'(x)  = {t}", "nl_d2": "   f''(x) = {t}",
    "nl_numeric": "   [!] بعض المشتقات غير ملساء/غير رمزية: استُخدمت الفروق المنتهية (دقة أقل).",
    "nl_sec_diag": "\n--- [1] تحليل قابلية التطبيق ---",
    "nl_applicable": "[صالحة]", "nl_caution": "[بحذر]", "nl_bypassed": "[مستبعدة]",
    "nl_m_golden": "القسم الذهبي", "nl_m_fibonacci": "بحث فيبوناتشي", "nl_m_newton": "نيوتن-رافسون", "nl_m_secant": "القاطع",
    "uni_unimodal": "وادٍ واحد على [a, b] (اختبار بالعينات: استدلال وليس برهاناً).",
    "uni_monotone": "الدالة رتيبة على [a, b]: الحد الأدنى عند أحد الطرفين.",
    "uni_flat": "الدالة ثابتة على [a, b] (كل نقطة مثلى).",
    "uni_multimodal": "رُصدت عدة نهايات صغرى/عظمى محلية: قد تُرجع طرق الحصر حلاً محلياً فقط.",
    "uni_domain": "الدالة غير معرّفة عند بعض نقاط العينة في [a, b]: لا يمكن استخدام طرق الحصر.",
    "newton_ok": "f''(x0) = {v:.6g} > 0.",
    "newton_curv": "f''(x0) = {v:.6g} <= 0: ستنجذب طريقة نيوتن إلى نهاية عظمى/نقطة انعطاف؛ اختر x0 آخر.",
    "deriv_fail": "تعذّر حساب المشتقة عند نقطة (نقاط) البداية.",
    "secant_ok": "نقطتا بداية مختلفتان و f' معرّفة.",
    "secant_same": "يجب أن تختلف x0 عن x1.",
    "nl_sec_res": "\n--- [2] النتائج ---",
    "nl_res": "{m}: x* = {x:.8g} | f(x*) = {fx:.8g} | التكرارات = {it} | التقييمات = {ev}",
    "nl_status": "   الحالة: {s}",
    "st_converged": "تقارب", "st_max_iter": "بلغ حد التكرارات - لم يتقارب",
    "st_zero_curvature": "فشل - انحناء صفري (f'' ~ 0)",
    "st_not_minimum": "توقف عند نقطة ثابتة ليست نهاية صغرى",
    "st_left_interval": "فشل - خرجت النقطة من [a, b]", "st_diverged": "فشل - تباعد",
    "st_domain_error": "فشل - الدالة غير معرّفة أثناء الحساب",
    "n_precision": "   ملاحظة: التفاوت أقل من الدقة الممكنة (~{limit:.1e})؛ ما بعد ذلك ضجيج عددي.",
    "n_endpoint": "   ملاحظة: القيمة المثلى عند حدّ الفترة [a, b].",
    "n_fib_n": "   ملاحظة: عدد تقييمات فيبوناتشي N = {n} اختير من التفاوت.",
    "n_maximum": "   ملاحظة: f''(x*) < 0 - هذه نهاية عظمى محلية للدالة المصغَّرة.",
    "n_inflection": "   ملاحظة: f''(x*) ~ 0 - نقطة انعطاف/غير محسومة وليست نهاية صغرى مؤكدة.",
    "n_zero_curvature": "   ملاحظة: خطوة نيوتن/القاطع غير معرّفة هنا.",
    "n_left_interval": "   ملاحظة: النقطة التالية {x:.6g} خارج [a, b].",
    "n_diverged": "   ملاحظة: أصبحت |x| ضخمة.", "n_domain": "   ملاحظة: الدالة أو مشتقتها غير معرّفة قرب النقطة.",
    "nl_table": "      جدول التكرارات:",
    "nl_sec_ver": "\n--- [3] التحقق ---",
    "nl_grid": "   مسح مرجعي بالشبكة (2001 نقطة): x ~ {x:.6g}، f ~ {fx:.8g}",
    "nl_best": "   أفضل نتيجة متقاربة: {m} -> x* = {x:.8g}، f(x*) = {fx:.8g}",
    "nl_agree": "   [V] أفضل نتيجة تتفق مع المسح بالشبكة.",
    "nl_worse": "   [X] وجد المسح قيمة أفضل من أفضل نتيجة للطرق: قد تكون الدالة متعددة النهايات؛ النتائج محلية.",
    "nl_none": "   [X] لم تتقارب أي طريقة.",
    "nl_ex_menu": "أمثلة محلولة:\n  [1] f(x) = (x-2)^2 + 1 على [0, 5]، تصغير           -> الطرق الأربع تتفق\n"
                  "  [2] f(x) = x*exp(-x) على [0, 5]، تعظيم              -> التعظيم بتغيير الإشارة\n"
                  "  [3] f(x) = x^4 - 3x^3 + 2 على [0, 3]، تصغير       -> استبعاد نيوتن (f'' = 0 عند x0)",
    "nl_ex1_t": "قطع مكافئ", "nl_ex2_t": "تعظيم", "nl_ex3_t": "لماذا قد تُستبعد طريقة",
    "nl_ex1_s": "صغّر f(x) = (x-2)^2 + 1 على [0, 5] بتفاوت 1e-6.",
    "nl_ex1_o": " 1. رُصد وادٍ واحد فطريقتا القسم الذهبي وفيبوناتشي صالحتان؛ و f'' > 0 فنيوتن والقاطع صالحتان أيضاً.\n"
                " 2. قارن عدد التقييمات: فيبوناتشي أقل طرق الحصر تقييماً؛ ونيوتن يحتاج تكرارات قليلة جداً.\n"
                " 3. كل النتائج تتفق مع المسح المستقل بالشبكة: x* = 2 و f(x*) = 1.",
    "nl_ex2_s": "عظّم f(x) = x*exp(-x) على [0, 5] (نقطتا البداية x0 = 0.5 و x1 = 0.8).",
    "nl_ex2_o": " 1. تعظيم f يعادل تصغير -f؛ يفعل البرنامج ذلك تلقائياً ويعرض قيمة f الأصلية.\n"
                " 2. الحل المتوقع: x* = 1 و f(x*) = 0.3679.",
    "nl_ex3_s": "صغّر f(x) = x^4 - 3x^3 + 2 على [0, 3] بنقطتي البداية x0 = 1.5 (المنتصف) و x1 = 2.0.",
    "nl_ex3_o": " 1. عند x0 = 1.5 نجد f''(x0) = 12x^2 - 18x = 0: خطوة نيوتن تقسم على صفر، لذا تُستبعد [مستبعدة].\n"
                " 2. طرق الحصر والقاطع لا تحتاج f'' عند البداية وتجد x* = 2.25.\n"
                " 3. الدرس: افحص تقرير قابلية التطبيق دائماً قبل الوثوق بطريقة تعتمد على المشتقات.\n"
                " 4. جرّب مسألتك الخاصة بـ x1 = 1.8: القفزة الأولى للقاطع تخرج من [0, 3] فتُبلِّغ الطريقة عن الفشل -\n"
                "    فنقاط البداية مهمة في الطرق المعتمدة على المشتقات.",
    "nl_learn": """
الجزء الثالث - التحسين غير الخطي أحادي المتغير
الهدف: إيجاد x* في [a, b] يجعل f(x) أصغر ما يمكن (ولإيجاد القيمة العظمى نصغّر -f).

طرق الحصر (بلا مشتقات؛ تتطلب دالة أحادية المنوال = وادياً واحداً على [a, b])
 1) القسم الذهبي: نبقي نقطتين داخليتين بنسبة الذهب (0.618)؛ وكل خطوة تستبعد الجزء الذي لا يمكن أن يحوي
                  الحد الأدنى وتعيد استخدام أحد التقييمات القديمة. تتقلص الفترة بمعامل 0.618 لكل تقييم.
 2) فيبوناتشي: كالقسم الذهبي لكن النسب مأخوذة من أعداد فيبوناتشي؛ ولعدد ثابت N من التقييمات تعطي أصغر
                فترة نهائية ممكنة، ولذلك يُختار N من التفاوت المطلوب.

الطرق المعتمدة على المشتقات (سريعة لكنها تحتاج بداية جيدة ودالة ملساء)
 3) نيوتن-رافسون: تحل f'(x) = 0 بالعلاقة  x_new = x - f'(x) / f''(x). تقارب تربيعي قرب الحل.
                   الخطر: f'' <= 0 عند البداية يقود إلى نهاية عظمى/نقطة انعطاف؛ و f'' ~ 0 تُفشل الخطوة.
 4) القاطع: كنيوتن لكنها تستبدل f'' بميل المستقيم بين آخر قيمتين لـ f'؛ تحتاج نقطتي بداية
             ولا تحتاج مشتقة ثانية.

شبكات الأمان في هذه الأداة: تُفحص الصيغة قبل تقييمها، وتُحسب المشتقات رمزياً، وتُصنَّف النقطة الثابتة
بواسطة f'' (صغرى / عظمى / انعطاف)، وتُقارن أفضل نتيجة بمسح مستقل بالشبكة (2001 نقطة).
أخذ العينات يمكنه أن يوحي بأحادية المنوال فقط ولا يبرهنها.
""",
})

# ------------------------------ GUIDE / ABOUT ---------------------------------
_EN.update({
    "c_guide": """
USER GUIDE
 * Navigation  : every menu takes a number; press Enter to accept the default shown in [brackets].
 * Help        : type ?  at any question to see what that question means.
 * Detail mode : menu [5] prints every simplex tableau / MODI loop / iteration table - ideal for learning.
 * Examples    : inside each part, [2] loads a pre-filled problem and explains what to observe.
 * Language    : menu [6] switches between English and Arabic at any time.
 * Results     : each answer is verified independently (constraint residuals, grid scan, supply/demand check).

WHICH PART / METHOD SHOULD I USE?
 Linear objective and linear constraints (resources, mixes, plans)  -> Part 1
     all '<=' and RHS >= 0 ......... Standard Simplex      '>=' rows with a MIN objective ... Dual Simplex
     '=' rows or unclear start ...... Two-Phase Simplex     exactly 2 variables ............. add the Graph
 Shipping goods from sources to destinations at minimum cost         -> Part 2 (Transportation)
     starting plan: Vogel (best) / Least Cost / North-West (fastest); optimality: MODI
 One worker per job, min cost or max profit                          -> Part 2 (Assignment, Hungarian)
 One unknown x and a curved function f(x) on an interval            -> Part 3
     single valley, no derivatives needed ... Golden Section / Fibonacci
     smooth f with a good starting guess ... Newton-Raphson (fast) / Secant (no f'' needed)

COMMON PITFALLS
 * Variables are always >= 0 in Parts 1-2 (add substitutions yourself if a variable may be negative).
 * Part 3 formulas: write 2*x not 2x;  x^2 or x**2 are both accepted.
 * Arabic text looks disconnected? Install arabic-reshaper + python-bidi and run with --shape-ar.
""",
    "c_about": """
OPTIARCHITECT  v{ver}
  Interactive bilingual toolkit for teaching Operations Research and Optimization.
  Part 1 Linear Programming | Part 2 Transportation & Assignment | Part 3 Non-linear optimization

  Developer : {author}
  Copyright : {copyright}
  Licence   : {license}  (free to use, copy, modify and distribute with this notice kept)
  Source    : {url}
  Citation  : Al-Zuabidi, O. A. M. (2026). OptiArchitect (Version {ver}) [Computer software]. {url}
              (see CITATION.cff in the repository for the full citation metadata)
  Python    : numpy (required) | sympy (Part 3) | matplotlib (graphs) | arabic-reshaper + python-bidi (Arabic)
""",
})
_AR.update({
    "c_guide": """
دليل المستخدم
 * التنقل      : كل قائمة تقبل رقماً؛ اضغط Enter لقبول القيمة الافتراضية الظاهرة بين [الأقواس].
 * المساعدة    : اكتب ?  عند أي سؤال لتعرف معناه.
 * وضع التفصيل : القائمة [5] تطبع كل جدول سيمبلكس / حلقة MODI / جدول تكرارات - مثالي للتعلّم.
 * الأمثلة     : داخل كل جزء، الخيار [2] يحمّل مسألة جاهزة ويشرح ما ينبغي ملاحظته.
 * اللغة       : القائمة [6] تبدّل بين العربية والإنجليزية في أي وقت.
 * النتائج     : كل جواب يُتحقق منه باستقلالية (انحراف القيود، المسح بالشبكة، فحص العرض/الطلب).

أي جزء / أي طريقة أستخدم؟
 دالة هدف خطية وقيود خطية (موارد، خلطات، خطط)                      -> الجزء الأول
     كل القيود <= والطرف الأيمن >= 0 ... السيمبلكس القياسي    قيود >= مع هدف MIN ... السيمبلكس الثنائي
     قيود = أو بداية غير واضحة ........ طريقة المرحلتين         متغيران فقط ........ أضف الرسم البياني
 نقل بضاعة من مصادر إلى مقاصد بأقل تكلفة                             -> الجزء الثاني (النقل)
     خطة البداية: فوغل (الأفضل) / أدنى تكلفة / الركن الشمالي الغربي (الأسرع)؛ والأمثلية: MODI
 عامل واحد لكل وظيفة، بأقل تكلفة أو أعلى ربح                          -> الجزء الثاني (التخصيص، المجرية)
 مجهول واحد x ودالة منحنية f(x) على فترة                             -> الجزء الثالث
     وادٍ واحد وبلا مشتقات ... القسم الذهبي / فيبوناتشي
     دالة ملساء وتخمين بداية جيد ... نيوتن-رافسون (سريع) / القاطع (بلا f'')

أخطاء شائعة
 * المتغيرات في الجزأين 1-2 دائماً >= 0 (أضف التعويضات بنفسك إن كان المتغير قد يكون سالباً).
 * صيغ الجزء الثالث: اكتب 2*x وليس 2x؛ ويقبل x^2 و x**2 معاً.
 * الحروف العربية تظهر منفصلة؟ ثبّت arabic-reshaper و python-bidi وشغّل البرنامج مع --shape-ar.
""",
    "c_about": """
OPTIARCHITECT  الإصدار {ver}
  أداة تفاعلية ثنائية اللغة لتعليم بحوث العمليات والتحسين.
  الجزء 1 البرمجة الخطية | الجزء 2 النقل والتخصيص | الجزء 3 التحسين غير الخطي

  المطوّر        : {author}
  حقوق النشر     : {copyright}
  الترخيص        : {license}  (استخدام ونسخ وتعديل وتوزيع حرّ مع الإبقاء على هذا الإشعار)
  المصدر         : {url}
  الاقتباس       : Al-Zuabidi, O. A. M. (2026). OptiArchitect (Version {ver}) [Computer software]. {url}
                   (انظر الملف CITATION.cff في المستودع لبيانات الاقتباس الكاملة)
  بايثون         : numpy (مطلوب) | sympy (الجزء 3) | matplotlib (الرسوم) | arabic-reshaper + python-bidi (العربية)
""",
})
