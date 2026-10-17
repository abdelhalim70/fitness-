#!/usr/bin/env python3
"""
Builds the Arabic page (ar/index.html) from the English page (index.html).

    python3 tools/build-ar.py

Why a generator: both pages keep exactly the same structure, so a layout or
code change made in index.html reaches the Arabic page automatically. Only the
text below needs translating.

When you change English text in index.html, the matching entry below no longer
matches; the script stops and lists it. Update the English (left) side, and the
Arabic (right) side, then run it again.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
OUT = ROOT / "ar" / "index.html"

NAME_AR = "عبد الحليم بنحدي"

# --- Structural changes: language, direction, assets, fonts, hero photo -----------------
STRUCTURE = [
    ('<html lang="en">', '<html lang="ar" dir="rtl">'),
    ('<link rel="canonical" href="https://www.your-domain.com/" />',
     '<link rel="canonical" href="https://www.your-domain.com/ar/" />'),
    ('<meta property="og:url" content="https://www.your-domain.com/" />',
     '<meta property="og:url" content="https://www.your-domain.com/ar/" />\n  <meta property="og:locale" content="ar_AE" />'),
    ('og-image-en.jpg', 'og-image-ar.jpg'),  # link-preview image (og:image, twitter:image, structured data)
    ('family=Bebas+Neue&family=Inter:wght@400;500;600;700&display=swap',
     'family=Bebas+Neue&family=Cairo:wght@400;600;700;800&display=swap'),
    # Arabic hero: high-kick photo (coach on the left, so the right-aligned text doesn't cover him)
    ('<link rel="preload" as="image" href="assets/img/coach-battle-ropes.jpg" />',
     '<link rel="preload" as="image" href="assets/img/coach-high-kick.jpg" />'),
    ('''          src="assets/img/coach-battle-ropes.jpg"
          alt="Abdelhalim Benhaddi doing battle-rope conditioning next to a heavy bag"
          width="1280" height="1280"''',
     f'''          src="assets/img/coach-high-kick.jpg"
          alt="{NAME_AR} يسدد ركلة دائرية عالية على كيس الملاكمة"
          width="1280" height="1110"'''),
    ('"description": "Private boxing, martial arts and fitness coaching in Abu Dhabi.",',
     '"description": "تدريب خاص في الملاكمة والفنون القتالية واللياقة البدنية في أبوظبي.",'),
    ('"url": "https://www.your-domain.com/",', '"url": "https://www.your-domain.com/ar/",'),
    # Language switch points back to English
    ('<a href="ar/" class="lang-switch" hreflang="ar" lang="ar" aria-label="النسخة العربية">عربي</a>',
     '<a href="../" class="lang-switch" hreflang="en" lang="en" aria-label="English version">English</a>'),
    ('<a href="ar/" class="mobile-menu__lang" hreflang="ar" lang="ar">عربي · النسخة العربية</a>',
     '<a href="../" class="mobile-menu__lang" hreflang="en" lang="en">English version</a>'),
    ('<input type="hidden" name="language" value="en" />', '<input type="hidden" name="language" value="ar" />'),
    # Phone numbers must stay left-to-right inside Arabic text
    ('<a href="tel:+212655911650">', '<a href="tel:+212655911650" dir="ltr">'),
    ('q=Abu+Dhabi,UAE&output=embed', 'q=Abu+Dhabi,UAE&hl=ar&output=embed'),
    # Photo viewer arrows point the other way in right-to-left
    ('aria-label="Previous photo">&#8249;</button>', 'aria-label="الصورة السابقة">&#8250;</button>'),
    ('aria-label="Next photo">&#8250;</button>', 'aria-label="الصورة التالية">&#8249;</button>'),
]

# --- Text: (English as it appears in index.html, Arabic) ----------------------------------
TEXT = [
    # <head>
    ("<title>Abdelhalim Benhaddi | Boxing, Martial Arts & Personal Trainer in Abu Dhabi</title>",
     f"<title>{NAME_AR} | مدرب ملاكمة وفنون قتالية ولياقة بدنية في أبوظبي</title>"),
    ('content="Private boxing, martial arts and fitness coaching in Abu Dhabi with a national karate champion and Les Mills certified instructor. 1-to-1 sessions, weight loss, beginners, small groups and online programs. Book your free intro session."',
     'content="تدريب خاص في الملاكمة والفنون القتالية واللياقة البدنية في أبوظبي مع بطل وطني في الكاراتيه ومدرب معتمد من Les Mills. حصص فردية، خسارة الوزن، المبتدئون، المجموعات الصغيرة والبرامج أونلاين. احجز حصتك التعريفية المجانية."'),
    ('content="boxing coach Abu Dhabi, personal trainer Abu Dhabi, karate coach Abu Dhabi, private boxing lessons, kickboxing, weight loss coaching, fitness coach UAE"',
     'content="مدرب ملاكمة أبوظبي, مدرب شخصي أبوظبي, مدرب كاراتيه أبوظبي, دروس ملاكمة خاصة, كيك بوكسينغ, خسارة الوزن, مدرب لياقة الإمارات"'),
    ('<meta name="author" content="Abdelhalim Benhaddi" />', f'<meta name="author" content="{NAME_AR}" />'),
    ('content="Train like a fighter. Transform your body. | Abdelhalim Benhaddi"', f'content="تدرّب كالمقاتل. غيّر جسدك. | {NAME_AR}"'),
    ('content="Private boxing, martial arts & fitness coaching in Abu Dhabi. Book your free intro session."',
     'content="تدريب خاص في الملاكمة والفنون القتالية واللياقة البدنية في أبوظبي. احجز حصتك التعريفية المجانية."'),

    # Header & menus
    (">Skip to content</a>", ">تخطَّ إلى المحتوى</a>"),
    ('aria-label="Abdelhalim Benhaddi – home"', f'aria-label="{NAME_AR} – الرئيسية"'),
    ('<span class="logo__name">Abdelhalim Benhaddi</span>', f'<span class="logo__name">{NAME_AR}</span>'),
    ('aria-label="Main navigation"', 'aria-label="القائمة الرئيسية"'),
    (">About</a>", ">من أنا</a>"),
    (">Services</a>", ">الخدمات</a>"),
    (">Pricing</a>", ">الأسعار</a>"),
    (">Gallery</a>", ">المعرض</a>"),
    (">FAQ</a>", ">الأسئلة الشائعة</a>"),
    (">Contact</a>", ">تواصل</a>"),
    (">Book now</a>", ">احجز الآن</a>"),
    ('aria-label="Open menu"', 'aria-label="فتح القائمة"'),
    (">Book a free intro session</a>", ">احجز حصة تعريفية مجانية</a>"),

    # Hero
    (">Boxing & fitness coach · Abu Dhabi</span>", ">مدرب ملاكمة ولياقة بدنية · أبوظبي</span>"),
    ('Train like a fighter. <span class="accent">Transform</span> your body.',
     'تدرّب كالمقاتل. <span class="accent">غيّر</span> جسدك.'),
    ("""          1-to-1 boxing and fitness coaching built around your goals, your level and your schedule.
          Burn fat, build real strength and gain the confidence of a fighter. No experience needed.""",
     """          تدريب فردي في الملاكمة واللياقة البدنية مصمَّم حول أهدافك ومستواك وجدولك.
          احرق الدهون، ابنِ قوة حقيقية واكتسب ثقة المقاتل. لا تحتاج إلى أي خبرة سابقة."""),
    (">Book a free session</a>", ">احجز حصة مجانية</a>"),
    (">See pricing</a>", ">اطّلع على الأسعار</a>"),
    ('<div class="stat__label">Years coaching</div>', '<div class="stat__label">سنوات من التدريب</div>'),
    ('<div class="stat__label">National karate champion</div>', '<div class="stat__label">بطل وطني في الكاراتيه</div>'),
    ('<div class="stat__label">Combat disciplines</div>', '<div class="stat__label">رياضات قتالية</div>'),

    # About
    ('alt="Abdelhalim Benhaddi performing a cable crossover in the gym"', f'alt="{NAME_AR} يؤدي تمرين الكابل كروس أوفر في الصالة"'),
    ('8+ years<small>coaching athletes & clients</small>', '+8 سنوات<small>في تدريب الرياضيين والعملاء</small>'),
    (">About the coach</span>", ">عن المدرب</span>"),
    ('From the ring <span class="accent">to your corner</span>', 'من الحلبة <span class="accent">إلى جانبك</span>'),
    ("""            Combat sports shaped me. I became Moroccan National Kumite Champion in 2011, earned my 1st Dan black belt
            in karate, then competed in boxing with Mouloudia Marrakech Boxing Club and in national kickboxing and
            Muay Thai finals. The discipline I learned on the mat and in the ring is what I now pass on to my clients.""",
     """            الرياضات القتالية هي التي صنعتني. أصبحت بطل المغرب الوطني في الكوميتيه عام 2011، ونلت الحزام الأسود
            دان أول في الكاراتيه، ثم نافست في الملاكمة مع نادي المولودية المراكشية للملاكمة، وفي النهائيات الوطنية
            للكيك بوكسينغ والمواي تاي. الانضباط الذي تعلّمته على البساط وفي الحلبة هو ما أنقله اليوم إلى عملائي."""),
    ("""            For 8+ years I've coached everyone from international guests at Fairmont Marrakech to student-athletes
            at UM6P and members as Head Coach at Alpha Forme Fitness Club. Now I bring that experience to Abu Dhabi:
            fighter-style training that is smart, intense and always adapted to you, in English, Arabic or French.""",
     """            على مدى أكثر من 8 سنوات درّبت الجميع: من النزلاء الدوليين في فيرمونت مراكش، إلى الطلاب الرياضيين في
            جامعة محمد السادس متعددة التخصصات التقنية (UM6P)، وأعضاء نادي Alpha Forme حيث عملت مدرباً رئيسياً.
            واليوم أنقل هذه الخبرة إلى أبوظبي: تدريب بأسلوب المقاتلين، ذكي ومكثّف ومصمَّم لك دائماً، بالعربية أو الإنجليزية أو الفرنسية."""),
    ("<h3>Fight background</h3><p>2× National Karate Champion · 1st Dan black belt · competitive boxer, kickboxing & Muay Thai.</p>",
     "<h3>الخلفية القتالية</h3><p>بطل وطني في الكاراتيه مرتين · حزام أسود دان أول · ملاكم منافس، كيك بوكسينغ ومواي تاي.</p>"),
    ("<h3>Certified</h3><p>Les Mills BODYPUMP™ & RPM™ instructor · Aerobics & Fitness Level 1 · First Aid & CPR.</p>",
     "<h3>شهادات معتمدة</h3><p>مدرب Les Mills BODYPUMP™ و RPM™ · شهادة الأيروبيك واللياقة المستوى 1 · الإسعافات الأولية والإنعاش القلبي الرئوي.</p>"),
    ("<h3>Elite experience</h3><p>Fairmont Marrakech · UM6P athletics · Head Coach at Alpha Forme.</p>",
     "<h3>خبرة رفيعة</h3><p>فيرمونت مراكش · رياضة جامعة UM6P · مدرب رئيسي في Alpha Forme.</p>"),
    ("<h3>Nutrition</h3><p>Certified in sports nutrition to support your results outside the gym.</p>",
     "<h3>التغذية</h3><p>حاصل على شهادة في التغذية الرياضية لدعم نتائجك خارج الصالة.</p>"),
    ("""            "Discipline beats motivation. I'll give you the plan, the technique and the push. You bring the consistency.
            Together, we get results that last.\"""",
     """            «الانضباط يتفوّق على الحماس. سأمنحك الخطة والتقنية والدفعة، وأنت تلتزم بالاستمرار.
            معاً نحقق نتائج تدوم.»"""),
    (">Train with me</a>", ">تدرّب معي</a>"),

    # Services
    (">Services</span>", ">الخدمات</span>"),
    ('Coaching that <span class="accent">fits your goal</span>', 'تدريب <span class="accent">يناسب هدفك</span>'),
    ("Whatever your starting point, there's a program designed to get you to the next level, safely and fast.",
     "أياً كانت نقطة انطلاقك، هناك برنامج مصمَّم لينقلك إلى المستوى التالي، بأمان وبسرعة."),
    ("<h3>Private 1-to-1 coaching</h3>", "<h3>التدريب الخاص الفردي</h3>"),
    ("<p>100% focused on you. The fastest way to learn to fight properly and transform your body.</p>",
     "<p>تركيز كامل عليك. أسرع طريقة لتتعلّم القتال بشكل صحيح وتغيّر جسدك.</p>"),
    ("<li>Boxing, karate & kickboxing technique</li>", "<li>تقنيات الملاكمة والكاراتيه والكيك بوكسينغ</li>"),
    ("<li>Pad work & fight conditioning</li>", "<li>التدريب على الميتس واللياقة القتالية</li>"),
    ("<li>Strength, mobility & injury prevention</li>", "<li>القوة والمرونة والوقاية من الإصابات</li>"),
    ("<h3>Fitness & weight loss</h3>", "<h3>اللياقة وخسارة الوزن</h3>"),
    ("<p>Burn fat, tone up and boost your energy with high-intensity training and simple nutrition habits.</p>",
     "<p>احرق الدهون، شُدّ جسمك وارفع طاقتك بتمارين عالية الكثافة وعادات غذائية بسيطة.</p>"),
    ("<li>Fat-burning boxing & HIIT circuits</li>", "<li>دوائر حرق الدهون بالملاكمة وتمارين HIIT</li>"),
    ("<li>Progress tracking every month</li>", "<li>متابعة التقدّم كل شهر</li>"),
    ("<li>Realistic nutrition guidance</li>", "<li>إرشادات غذائية واقعية</li>"),
    ("<h3>Boxing for beginners</h3>", "<h3>الملاكمة للمبتدئين</h3>"),
    ("<p>Never thrown a punch? Perfect. Learn the fundamentals step by step in a safe, no-ego environment.</p>",
     "<p>لم تسدّد لكمة من قبل؟ ممتاز. تعلّم الأساسيات خطوة بخطوة في بيئة آمنة وبعيدة عن الاستعراض.</p>"),
    ("<li>Stance, footwork & defence</li>", "<li>الوقفة وحركة القدمين والدفاع</li>"),
    ("<li>Basic combinations</li>", "<li>التركيبات الأساسية</li>"),
    ("<li>No sparring unless you want it</li>", "<li>بدون نزال إلا إذا أردت ذلك</li>"),
    ("<h3>Small group sessions</h3>", "<h3>حصص المجموعات الصغيرة</h3>"),
    ("<p>Train with friends, family or colleagues (2–6 people). Led by a Les Mills certified group instructor.</p>",
     "<p>تدرّب مع أصدقائك أو عائلتك أو زملائك (2–6 أشخاص)، بقيادة مدرب جماعي معتمد من Les Mills.</p>"),
    ("<li>Duo & team sessions</li>", "<li>حصص ثنائية وجماعية</li>"),
    ("<li>Corporate team-building</li>", "<li>أنشطة بناء الفريق للشركات</li>"),
    ("<li>Boxing, HIIT & functional training</li>", "<li>الملاكمة وHIIT والتدريب الوظيفي</li>"),
    ("<h3>Online coaching</h3>", "<h3>التدريب أونلاين</h3>"),
    ("<p>A personalised program in your pocket. Train anywhere with video guidance and weekly check-ins.</p>",
     "<p>برنامج مخصّص في جيبك. تدرّب في أي مكان مع توجيه بالفيديو ومتابعة أسبوعية.</p>"),
    ("<li>Custom training plan</li>", "<li>خطة تدريب مخصّصة</li>"),
    ("<li>Video technique feedback</li>", "<li>ملاحظات على التقنية عبر الفيديو</li>"),
    ("<li>Weekly WhatsApp check-in</li>", "<li>متابعة أسبوعية على واتساب</li>"),
    ("<h3>Not sure where to start?</h3>", "<h3>لا تعرف من أين تبدأ؟</h3>"),
    ("<p>Book a free 30-minute intro session. We'll assess your level, talk goals and build your plan. Zero commitment.</p>",
     "<p>احجز حصة تعريفية مجانية لمدة 30 دقيقة. نقيّم مستواك، نناقش أهدافك ونبني خطتك. دون أي التزام.</p>"),

    # Signature group classes
    ("<span>Boxing</span><span>Kickboxing</span><span>HIIT</span><span>Karate</span><span>Push your limits</span>",
     "<span>ملاكمة</span><span>كيك بوكسينغ</span><span>HIIT</span><span>كاراتيه</span><span>تجاوز حدودك</span>"),
    ('alt="Abdelhalim Benhaddi on an indoor cycling bike in a spin studio"', f'alt="{NAME_AR} على دراجة التمارين الداخلية في استوديو السبينينغ"'),
    ('</svg>Les Mills certified instructor</span>', '</svg>مدرب معتمد من Les Mills</span>'),
    ('Ride hard. <span class="accent">Lift strong.</span>', 'دوّس بقوة. <span class="accent">ارفع بثقة.</span>'),
    ("""              Two of the world's best-known group workouts, coached with fighter energy. Pick your class and see how it hits.""",
     """              اثنان من أشهر التمارين الجماعية في العالم، بطاقة المقاتلين. اختر حصتك واكتشف كيف تعمل."""),
    ('aria-label="Group classes"', 'aria-label="الحصص الجماعية"'),
    ("<strong>RPM™</strong><span>Indoor cycling</span>", "<strong>RPM™</strong><span>دراجات داخلية</span>"),
    ("<strong>BODYPUMP™</strong><span>Barbell strength</span>", "<strong>BODYPUMP™</strong><span>قوة بالبار</span>"),
    ("<p>A music-driven ride through hills, sprints and flats. Serious cardio, low impact on your joints, and you control the resistance.</p>",
     "<p>رحلة على إيقاع الموسيقى بين الصعود والسرعات والطرق المستوية. كارديو قوي، تأثير خفيف على المفاصل، وأنت من يتحكم في المقاومة.</p>"),
    ("<li><strong>45</strong><span>minutes</span></li>", "<li><strong>45</strong><span>دقيقة</span></li>"),
    ("<li><strong>Cardio</strong><span>focus</span></li>", "<li><strong>كارديو</strong><span>التركيز</span></li>"),
    ("<li><strong>All</strong><span>levels</span></li>", "<li><strong>كل</strong><span>المستويات</span></li>"),
    ("<figcaption>Intensity across a typical ride</figcaption>", "<figcaption>الشدّة خلال حصة نموذجية</figcaption>"),
    ("<li>Warm-up</li><li>Pace</li><li>Hills</li><li>Intervals</li><li>Mountain climb</li><li>Cool-down</li>",
     "<li>الإحماء</li><li>الإيقاع</li><li>التلال</li><li>الفترات</li><li>صعود الجبل</li><li>التهدئة</li>"),
    ("<p>The original barbell class: light to moderate weights, high reps, every major muscle group. Get lean and strong.</p>",
     "<p>حصة البار الأصلية: أوزان خفيفة إلى متوسطة، تكرارات عالية، وكل المجموعات العضلية الرئيسية. جسم مشدود وقوي.</p>"),
    ("<li><strong>60</strong><span>minutes</span></li>", "<li><strong>60</strong><span>دقيقة</span></li>"),
    ("<li><strong>10</strong><span>tracks</span></li>", "<li><strong>10</strong><span>مقاطع</span></li>"),
    ("<figcaption>Track by track</figcaption>", "<figcaption>مقطعاً بمقطع</figcaption>"),
    ("<li>Warm-up</li><li>Squats</li><li>Chest</li><li>Back</li><li>Triceps</li>",
     "<li>الإحماء</li><li>القرفصاء</li><li>الصدر</li><li>الظهر</li><li>الترايسبس</li>"),
    ("<li>Biceps</li><li>Lunges</li><li>Shoulders</li><li>Core</li><li>Cool-down</li>",
     "<li>البايسبس</li><li>الطعنات</li><li>الأكتاف</li><li>عضلات الجذع</li><li>التهدئة</li>"),
    (">Book a group class</a>", ">احجز حصة جماعية</a>"),
    ("<p>For small groups, corporate teams, hotels and gyms across Abu Dhabi.</p>",
     "<p>للمجموعات الصغيرة وفرق الشركات والفنادق والصالات الرياضية في جميع أنحاء أبوظبي.</p>"),

    # Pricing
    (">Pricing & subscriptions</span>", ">الأسعار والاشتراكات</span>"),
    ('Invest in <span class="accent">yourself</span>', 'استثمر <span class="accent">في نفسك</span>'),
    ("Simple, transparent pricing. No hidden fees. Commit for 3 months and save.",
     "أسعار بسيطة وواضحة. بلا رسوم خفية. التزم لمدة 3 أشهر ووفّر."),
    ('aria-label="Billing period"', 'aria-label="فترة الدفع"'),
    ('aria-pressed="true">Monthly</button>', 'aria-pressed="true">شهري</button>'),
    ('aria-pressed="false">3 months <span class="save">-10%</span>', 'aria-pressed="false">3 أشهر <span class="save">وفّر 10%</span>'),
    ('<h3 class="plan__name">Single session</h3>', '<h3 class="plan__name">حصة واحدة</h3>'),
    ("Try a full private session or train whenever it suits you.", "جرّب حصة خاصة كاملة أو تدرّب متى ما ناسبك."),
    ('data-monthly="AED 300" data-quarterly="AED 825">AED 300<', 'data-monthly="300 درهم" data-quarterly="825 درهم">300 درهم<'),
    ('data-monthly="/ session" data-quarterly="/ pack of 3">/ session<', 'data-monthly="/ للحصة" data-quarterly="/ باقة 3 حصص">/ للحصة<'),
    ('data-monthly="Pay as you go" data-quarterly="3-session pack · save AED 75">Pay as you go<',
     'data-monthly="ادفع حسب الحصة" data-quarterly="باقة 3 حصص · وفّر 75 درهم">ادفع حسب الحصة<'),
    ("</svg>60-min private session</li>", "</svg>حصة خاصة لمدة 60 دقيقة</li>"),
    ("</svg>Boxing, conditioning or strength</li>", "</svg>ملاكمة أو لياقة أو قوة</li>"),
    ("</svg>Gloves & equipment provided</li>", "</svg>القفازات والمعدات متوفرة</li>"),
    ("</svg>No commitment</li>", "</svg>بدون التزام</li>"),
    (">Book a session</a>", ">احجز حصة</a>"),
    ('<span class="plan__badge">Most popular</span>', '<span class="plan__badge">الأكثر طلباً</span>'),
    ('<h3 class="plan__name">Fighter plan</h3>', '<h3 class="plan__name">خطة المقاتل</h3>'),
    ("The sweet spot for real, visible transformation.", "التوازن المثالي لتحوّل حقيقي وواضح."),
    ('data-monthly="AED 2,000" data-quarterly="AED 1,800">AED 2,000<', 'data-monthly="2,000 درهم" data-quarterly="1,800 درهم">2,000 درهم<'),
    ('<span class="plan__period">/ month</span>', '<span class="plan__period">/ شهرياً</span>'),
    ('data-monthly="AED 250 per session" data-quarterly="Billed AED 5,400 every 3 months · save AED 600">AED 250 per session<',
     'data-monthly="250 درهم للحصة" data-quarterly="5,400 درهم كل 3 أشهر · وفّر 600 درهم">250 درهم للحصة<'),
    ("</svg>8 private sessions / month</li>", "</svg>8 حصص خاصة شهرياً</li>"),
    ("</svg>Personalised training plan</li>", "</svg>خطة تدريب مخصّصة</li>"),
    ("</svg>Monthly progress check-in</li>", "</svg>مراجعة شهرية للتقدّم</li>"),
    ("</svg>Home workouts between sessions</li>", "</svg>تمارين منزلية بين الحصص</li>"),
    ("</svg>Priority booking</li>", "</svg>أولوية في الحجز</li>"),
    (">Subscribe</a>", ">اشترك</a>"),
    ('<h3 class="plan__name">Champion plan</h3>', '<h3 class="plan__name">خطة البطل</h3>'),
    ("All-in coaching for maximum results, in and out of the gym.", "تدريب شامل لأقصى النتائج، داخل الصالة وخارجها."),
    ('data-monthly="AED 3,500" data-quarterly="AED 3,150">AED 3,500<', 'data-monthly="3,500 درهم" data-quarterly="3,150 درهم">3,500 درهم<'),
    ('data-monthly="Full support, 7 days a week" data-quarterly="Billed AED 9,450 every 3 months · save AED 1,050">Full support, 7 days a week<',
     'data-monthly="دعم كامل 7 أيام في الأسبوع" data-quarterly="9,450 درهم كل 3 أشهر · وفّر 1,050 درهم">دعم كامل 7 أيام في الأسبوع<'),
    ("</svg>Unlimited private sessions</li>", "</svg>حصص خاصة غير محدودة</li>"),
    ("</svg>Personalised nutrition guidance</li>", "</svg>إرشادات غذائية مخصّصة</li>"),
    ("</svg>WhatsApp follow-up, 7 days a week</li>", "</svg>متابعة على واتساب 7 أيام في الأسبوع</li>"),
    ("</svg>Body composition tracking</li>", "</svg>قياس تكوين الجسم</li>"),
    ("</svg>Online program for travel weeks</li>", "</svg>برنامج أونلاين لأسابيع السفر</li>"),
    ("""          Secure payment by card via Stripe. Cancel monthly plans anytime with 7 days' notice.
          Not sure? <a href="#contact" data-plan="Free intro session">Start with a free intro session →</a>""",
     """          دفع آمن بالبطاقة عبر Stripe. يمكنك إلغاء الخطط الشهرية في أي وقت بإشعار مسبق لمدة 7 أيام.
          غير متأكد؟ <a href="#contact" data-plan="Free intro session">ابدأ بحصة تعريفية مجانية ←</a>"""),

    # How it works
    (">How it works</span>", ">كيف نعمل</span>"),
    ('3 steps to <span class="accent">your best shape</span>', '3 خطوات نحو <span class="accent">أفضل نسخة منك</span>'),
    ("<h3>Book your intro session</h3>", "<h3>احجز حصتك التعريفية</h3>"),
    ("<p>Free, 30 minutes, no pressure. We meet, talk about your goals and test your current level.</p>",
     "<p>مجانية، 30 دقيقة، دون أي ضغط. نلتقي ونتحدث عن أهدافك ونختبر مستواك الحالي.</p>"),
    ("<h3>Get your personalised plan</h3>", "<h3>احصل على خطتك المخصّصة</h3>"),
    ("<p>I build a training (and nutrition) plan around your body, your schedule and your target.</p>",
     "<p>أبني لك خطة تدريب (وتغذية) تناسب جسمك وجدولك وهدفك.</p>"),
    ("<h3>Train & see results</h3>", "<h3>تدرّب وشاهد النتائج</h3>"),
    ("<p>We put in the work together. You track your progress every month and feel the difference within weeks.</p>",
     "<p>نعمل معاً بجدّ. تتابع تقدّمك كل شهر وتشعر بالفرق خلال أسابيع.</p>"),
    (">Start now, it's free</a>", ">ابدأ الآن، مجاناً</a>"),

    # Gallery
    (">Gallery</span>", ">المعرض</span>"),
    ('Inside the <span class="accent">training</span>', 'من داخل <span class="accent">التدريب</span>'),
    ('aria-label="View larger: ', 'aria-label="عرض بحجم أكبر: '),
    ("Abdelhalim Benhaddi throwing a high roundhouse kick at a heavy bag", f"{NAME_AR} يسدد ركلة دائرية عالية على كيس الملاكمة"),
    ("Abdelhalim Benhaddi showing his physique in the studio mirror", f"{NAME_AR} يستعرض لياقته البدنية أمام مرآة الاستوديو"),
    ("Abdelhalim Benhaddi demonstrating a core crunch on a mat in the studio", f"{NAME_AR} يؤدي تمرين البطن على البساط في الاستوديو"),
    ("Abdelhalim Benhaddi doing battle-rope conditioning in the gym", f"{NAME_AR} يتدرّب بالحبال القتالية في الصالة"),
    ('<strong>Follow the journey</strong><span style="color:var(--muted)">Daily training clips, tips and client wins on Instagram.</span>',
     '<strong>تابع الرحلة</strong><span style="color:var(--muted)">مقاطع تدريب يومية ونصائح وإنجازات العملاء على إنستغرام.</span>'),

    # FAQ
    (">FAQ</span>", ">الأسئلة الشائعة</span>"),
    ('Questions? <span class="accent">Answered.</span>', 'لديك أسئلة؟ <span class="accent">إليك الإجابات.</span>'),
    (">What happens during the first session?<", ">ماذا يحدث في الحصة الأولى؟<"),
    ("<p>Your free intro session lasts about 30 minutes. We talk about your goals, health history and schedule, then do a light movement and fitness assessment and a taste of boxing. You leave with a clear recommendation, with no obligation to sign up.</p>",
     "<p>تستغرق حصتك التعريفية المجانية نحو 30 دقيقة. نتحدث عن أهدافك وتاريخك الصحي وجدولك، ثم نُجري تقييماً خفيفاً للحركة واللياقة مع تجربة أولى للملاكمة. تغادر بتوصية واضحة، دون أي التزام بالاشتراك.</p>"),
    (">What equipment do I need?<", ">ما المعدات التي أحتاجها؟<"),
    ("<p>Just comfortable sportswear, trainers, a water bottle and a towel. Gloves, wraps, pads and all training equipment are provided. If you get hooked, I'll help you choose your own gear.</p>",
     "<p>فقط ملابس رياضية مريحة، حذاء رياضي، قارورة ماء ومنشفة. القفازات والأربطة والميتس وجميع معدات التدريب متوفرة. وإذا أحببت الرياضة، سأساعدك في اختيار معداتك الخاصة.</p>"),
    (">I'm a complete beginner. Is this for me?<", ">أنا مبتدئ تماماً. هل هذا مناسب لي؟<"),
    ("<p>Absolutely. Most of my clients had never boxed before. Every session is adapted to your level and fitness. There's no sparring or contact unless you ask for it. You'll progress at your own pace, safely.</p>",
     "<p>بالتأكيد. معظم عملائي لم يمارسوا الملاكمة من قبل. كل حصة مصمَّمة حسب مستواك ولياقتك، ولا يوجد نزال أو احتكاك إلا إذا طلبت ذلك. ستتقدّم بالسرعة التي تناسبك، وبأمان.</p>"),
    (">What is your cancellation policy?<", ">ما هي سياسة الإلغاء؟<"),
    ("<p>You can reschedule or cancel any session free of charge up to 24 hours in advance. Late cancellations count as a completed session. Monthly plans can be cancelled anytime with 7 days' notice; 3-month plans run for their full term.</p>",
     "<p>يمكنك إعادة جدولة أي حصة أو إلغاؤها مجاناً قبل 24 ساعة على الأقل. الإلغاء المتأخر يُحتسب كحصة منجزة. يمكن إلغاء الخطط الشهرية في أي وقت بإشعار مسبق لمدة 7 أيام، أما خطط الأشهر الثلاثة فتستمر حتى نهاية مدتها.</p>"),
    (">Where do sessions take place?<", ">أين تُقام الحصص؟<"),
    ("<p>I coach across Abu Dhabi: at your home or villa, your building or hotel gym, your office, or outdoors at the Corniche and local parks. Online coaching works from anywhere. Sessions are available in English, Arabic or French.</p>",
     "<p>أدرّب في جميع أنحاء أبوظبي: في منزلك أو فيلتك، في صالة البناية أو الفندق، في مكتبك، أو في الهواء الطلق على الكورنيش والحدائق القريبة. والتدريب أونلاين متاح من أي مكان. الحصص متوفرة بالعربية أو الإنجليزية أو الفرنسية.</p>"),
    (">How fast will I see results?<", ">متى سأرى النتائج؟<"),
    ("<p>Most clients feel more energy and better stamina within 2–3 weeks, and see visible changes in 6–8 weeks with 2 sessions a week and the right nutrition. Consistency is the key, and I'll keep you consistent.</p>",
     "<p>يشعر معظم العملاء بطاقة أكبر وتحمّل أفضل خلال 2–3 أسابيع، ويرون تغييرات واضحة خلال 6–8 أسابيع مع حصتين أسبوعياً وتغذية صحيحة. الاستمرارية هي المفتاح، وسأساعدك على الاستمرار.</p>"),

    # Contact / booking form
    (">Book now</span>", ">احجز الآن</span>"),
    ('Your first session <span class="accent">is on me</span>', 'حصتك الأولى <span class="accent">على حسابي</span>'),
    ("Fill in the form and I'll get back to you within 24 hours. Prefer to chat? Message me on WhatsApp.",
     "املأ النموذج وسأردّ عليك خلال 24 ساعة. تفضّل المحادثة؟ راسلني على واتساب."),
    ("<label>Don't fill this in: ", "<label>لا تملأ هذا الحقل: "),
    ('>Full name *</label>', '>الاسم الكامل *</label>'),
    ('placeholder="Your name"', 'placeholder="اسمك"'),
    ('>Phone / WhatsApp *</label>', '>الهاتف / واتساب *</label>'),
    ('>Email *</label>', '>البريد الإلكتروني *</label>'),
    ('>Main goal *</label>', '>الهدف الرئيسي *</label>'),
    ('disabled selected>Choose your goal</option>', 'disabled selected>اختر هدفك</option>'),
    ('>Preferred plan</label>', '>الخطة المفضّلة</label>'),
    ('>Message</label>', '>رسالتك</label>'),
    ('placeholder="Tell me about your experience, availability, injuries…"', 'placeholder="حدّثني عن خبرتك وأوقاتك المتاحة وأي إصابات…"'),
    ('<span>I agree that my data is used to contact me about my request. See the <a href="privacy.html">privacy policy</a>. *</span>',
     '<span>أوافق على استخدام بياناتي للتواصل معي بخصوص طلبي. اطّلع على <a href="privacy.html">سياسة الخصوصية</a> (بالإنجليزية). *</span>'),
    ('>Book my free session</button>', '>احجز حصتي المجانية</button>'),
    ("                WhatsApp me\n", "                راسلني على واتساب\n"),
    ('title="Map of Abu Dhabi, the coaching area"', 'title="خريطة أبوظبي، منطقة التدريب"'),
    ("<h3>Opening hours</h3>", "<h3>ساعات العمل</h3>"),
    ("<span>Monday – Friday</span>", "<span>الاثنين – الجمعة</span>"),
    ("<span>Saturday</span>", "<span>السبت</span>"),
    ("<span>Sunday</span><span>Closed</span>", "<span>الأحد</span><span>مغلق</span>"),
    ("<h3>Find me</h3>", "<h3>أين تجدني</h3>"),
    (">Abu Dhabi, UAE · home, hotel & outdoor sessions</p>", ">أبوظبي، الإمارات · حصص في المنزل والفندق وفي الهواء الطلق</p>"),
    ('aria-label="Instagram"', 'aria-label="إنستغرام"'),

    # Final band & footer
    (">Your fight starts today</h2>", ">معركتك تبدأ اليوم</h2>"),
    (">Spots are limited each month to guarantee quality coaching. Claim your free intro session now.</p>",
     ">الأماكن محدودة كل شهر لضمان جودة التدريب. احجز حصتك التعريفية المجانية الآن.</p>"),
    (">Start now</a>", ">ابدأ الآن</a>"),
    ("<p>Private boxing, martial arts & fitness coaching in Abu Dhabi. Train like a fighter, live like a champion.</p>",
     "<p>تدريب خاص في الملاكمة والفنون القتالية واللياقة البدنية في أبوظبي. تدرّب كالمقاتل، وعِش كالبطل.</p>"),
    ("<h4>Explore</h4>", "<h4>استكشف</h4>"),
    ("<h4>Support</h4>", "<h4>الدعم</h4>"),
    ("<h4>Contact</h4>", "<h4>تواصل</h4>"),
    (">Free intro session</a>", ">حصة تعريفية مجانية</a>"),
    (">Abu Dhabi, UAE</a>", ">أبوظبي، الإمارات</a>"),
    ("Abdelhalim Benhaddi Coaching. All rights reserved.", f"تدريب {NAME_AR}. جميع الحقوق محفوظة."),
    (">Privacy policy</a>", ">سياسة الخصوصية</a>"),
    (">Legal notice</a>", ">الإشعار القانوني</a>"),
    (">Terms of sale</a>", ">شروط البيع</a>"),
    (">Cookie settings</button>", ">إعدادات ملفات تعريف الارتباط</button>"),

    # Ask A2B chat
    ('<span class="chat-fab__label">Ask A2B</span>', '<span class="chat-fab__label">اسأل A2B</span>'),
    ('<strong id="chat-title">Ask A2B</strong>', '<strong id="chat-title">اسأل A2B</strong>'),
    ("<span>AI assistant · replies instantly</span>", "<span>مساعد ذكي · يرد فوراً</span>"),
    ('aria-label="Close chat"', 'aria-label="إغلاق المحادثة"'),
    ("Hi! I'm Abdelhalim's AI assistant. Ask me about training, plans and prices, in English, Arabic or French. 👊",
     "مرحباً! أنا المساعد الذكي لعبد الحليم. اسألني عن التدريب والخطط والأسعار، بالعربية أو الإنجليزية أو الفرنسية. 👊"),
    ('<button type="button">Which plan is right for me?</button>', '<button type="button">ما الخطة المناسبة لي؟</button>'),
    ("<button type=\"button\">I'm a total beginner</button>", '<button type="button">أنا مبتدئ تماماً</button>'),
    ('<button type="button">What happens in the free session?</button>', '<button type="button">ماذا يحدث في الحصة المجانية؟</button>'),
    # The 4th chip (Where do sessions take place?) is translated by the FAQ entry with the same text.
    ('class="visually-hidden">Your message</label>', 'class="visually-hidden">رسالتك</label>'),
    ('placeholder="Type your question…"', 'placeholder="اكتب سؤالك…"'),
    ('class="chat__send" aria-label="Send"', 'class="chat__send" aria-label="إرسال"'),
    ("""AI can make mistakes and doesn't give medical advice. Chats are processed by Anthropic. <a href="privacy.html#ai">Privacy</a>""",
     """قد يخطئ المساعد الذكي ولا يقدّم نصائح طبية. تتم معالجة المحادثات بواسطة Anthropic. <a href="privacy.html#ai">الخصوصية</a>"""),

    # Photo viewer, WhatsApp button, cookie banner
    ('aria-label="Photo viewer"', 'aria-label="عارض الصور"'),
    ('aria-label="Close">&times;</button>', 'aria-label="إغلاق">&times;</button>'),
    ('aria-label="Chat on WhatsApp"', 'aria-label="تحدّث معي على واتساب"'),
    ('aria-label="Cookie consent"', 'aria-label="الموافقة على ملفات تعريف الارتباط"'),
    ('🍪 This site uses essential cookies and, with your consent, analytics cookies to improve your experience. <a href="privacy.html#cookies">Learn more</a>',
     '🍪 يستخدم هذا الموقع ملفات تعريف الارتباط الأساسية، وبموافقتك، ملفات تحليلية لتحسين تجربتك. <a href="privacy.html#cookies">اعرف المزيد</a>'),
    ('data-cookie="accept">Accept all</button>', 'data-cookie="accept">قبول الكل</button>'),
    ('data-cookie="reject">Essential only</button>', 'data-cookie="reject">الأساسية فقط</button>'),
]

# Form choices: the value stays English (so booking emails are always in English), only the label changes
OPTIONS = {
    "Lose weight": "خسارة الوزن",
    "Learn boxing": "تعلّم الملاكمة",
    "Get fit & build stamina": "اللياقة وبناء التحمّل",
    "Build strength & muscle": "بناء القوة والعضلات",
    "Prepare for competition": "الاستعداد للمنافسات",
    "Other": "أخرى",
    "Free intro session": "حصة تعريفية مجانية",
    "Single session": "حصة واحدة",
    "Fighter plan": "خطة المقاتل",
    "Champion plan": "خطة البطل",
    "Small group sessions": "حصص المجموعات الصغيرة",
    "Online coaching": "التدريب أونلاين",
}

# Latin words that are fine to keep on the Arabic page (brand names, handles, contact details)
ALLOWED_LATIN = {"Les", "Mills", "BODYPUMP", "RPM", "UM6P", "Alpha", "Forme", "Fairmont", "HIIT",
                 "Stripe", "English", "version", "abdelhalimlife", "abdelhalimbenhaddi", "gmail", "com", "you", "email", "Anthropic"}


def apply(html, pairs, missing):
    for en, ar in pairs:
        if en not in html:
            missing.append(en)
            continue
        html = html.replace(en, ar)
    return html


class LatinFinder(HTMLParser):
    """Collects visible text and user-facing attributes that still contain English words."""
    ATTRS = {"alt", "aria-label", "placeholder", "title"}

    def __init__(self):
        super().__init__()
        self.skip = 0
        self.found = []

    def check(self, text, where):
        words = set(re.findall(r"[A-Za-z]{3,}", text)) - ALLOWED_LATIN
        if words:
            self.found.append((where, text.strip()[:80]))

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.skip += 1
        for k, v in attrs:
            if k in self.ATTRS and v:
                self.check(v, f"{tag}[{k}]")
            if tag == "meta" and k == "content" and dict(attrs).get("name") in ("description", "keywords"):
                self.check(v, "meta")

    def handle_endtag(self, tag):
        if tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip and data.strip():
            self.check(data, "text")


def main():
    html = SRC.read_text(encoding="utf-8")
    missing = []
    html = apply(html, STRUCTURE, missing)
    html = apply(html, TEXT, missing)
    for value, label in OPTIONS.items():
        pattern = re.compile(rf'(<option value="{re.escape(value)}"(?: selected)?>){re.escape(value)}</option>')
        html, n = pattern.subn(rf"\g<1>{label}</option>", html)
        if not n:
            missing.append(f"<option> {value}")

    # Latin brand names with ™ inside Arabic text: isolate them so "RPM™" doesn't render as "™RPM"
    for brand in ("RPM™", "BODYPUMP™"):
        html = re.sub(rf"(?<![\w<\"=]){re.escape(brand)}", f"<bdi>{brand}</bdi>", html)

    # Paths: the Arabic page lives one folder down
    html = re.sub(r'(href|src)="(assets/|privacy\.html|site\.webmanifest)', r'\1="../\2', html)

    if missing:
        print("These English strings were not found in index.html (the text probably changed).")
        print("Update them in tools/build-ar.py, then run again:\n")
        for m in missing:
            print("  -", m[:110].replace("\n", " "))
        sys.exit(1)

    finder = LatinFinder()
    finder.feed(html)
    if finder.found:
        print("Warning: English text still on the Arabic page (add a translation if needed):")
        for where, text in finder.found:
            print(f"  - {where}: {text}")

    banner = "<!-- GENERATED from index.html by tools/build-ar.py. Do not edit by hand. -->\n"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html.replace("<!DOCTYPE html>\n", "<!DOCTYPE html>\n" + banner, 1), encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
