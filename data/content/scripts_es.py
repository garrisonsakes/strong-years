# Spanish scripts ES01–ES40 for @donchuyylupe (Don Chuy & Doña Lupe; CHARACTERS_ES.md). Written natively in Mexican-US
# Spanish, never translated line by line. Validated by tools/build_content_es.py (hooked into tools/build_content.py);
# generated output: SCRIPTS_ES.md + data/content/scripts_es.json.
#   ES01–ES25 = RUNWAY (25): the Spanish page's own runway before Años Fuertes checkout opens in Spanish. Value-first;
#               LISTA (free waitlist) is a minority CTA (7/25). No price, no "$", no membership talk.
#   ES26–ES40 = LAUNCH (15): LIBRO (starter books; cell B default = books + first founding month, then the founding
#               price monthly), UNIRME (membership only) and FAMILIA (gift). Every offer script says the characters are AI.
# Per-script pillar / format / CTA / grammar / evidence / speaker come from data/content/hooks_es.psv (row n = ESn), so
# each fact has one source. Beats: (time, speaker, spoken, on-screen text, shot). Placeholders filled by the pipeline from
# live config ({{EBOOK_PRICE}}, {{FOUNDING_PRICE}}, {{DOMAIN}}); same USD prices as the US (CANON UPDATE 2/3).
# Honesty rules: no countdowns, no "quedan pocos", no testimonials, no outcome promises, "bloqueado mientras sigas
# suscrito" (never "de por vida"), "garantía" only as "garantía de devolución de 14 días".
PAGE = "@donchuyylupe"
PA = "SET-ES-PATIO | CH-TRAIN"
PAP = "SET-ES-PATIO | CH-PATIO"
CO = "SET-ES-COCHERA | CH-TRAIN"
ESC = "SET-ES-ESCALONES | CH-CAMINAR"
CM = "SET-ES-COMEDOR | CH-TRABAJO"
CK = "SET-ES-COCINA | CH-TRABAJO"
SA = "SET-ES-SALA | CH-TRABAJO"
BA = "SET-ES-BANO | CH-TRABAJO"
RC = "SET-ES-RECAMARA | CH-NOCHE"
LK = "SET-ES-COCINA | LU-COCINA"
LT = "SET-ES-COMEDOR | LU-CARDI-ROSA"
LS = "SET-ES-SALA | LU-CARDI-AZUL"
LC = "SET-ES-BANQUETA | LU-CAMINAR"
LR = "SET-ES-RECAMARA | LU-NOCHE"
LM = "SET-ES-MERCADO | LU-CAMINAR"
DK = "SET-ES-COCINA | CH-TRABAJO + LU-COCINA"
DS = "SET-ES-SALA | CH-TRABAJO + LU-CARDI-ROSA"
DP = "SET-ES-PATIO | CH-TRAIN + LU-ENTRENA"
DC = "SET-ES-COMEDOR | CH-TRABAJO + LU-CARDI-ROSA"
DG = "SET-ES-COCHERA | CH-TRAIN + LU-CARDI-AZUL"
DB = "SET-ES-BANQUETA | CH-CAMINAR + LU-CAMINAR"

# skip lines (said verbatim; CHARACTERS_ES.md §10)
SK_MOVE = "¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero."
SK_MOVE_TU = "¿Operación reciente, mareo al pararte o dolor fuerte? Pregúntale a tu doctor primero."
SK_FOOD = "¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida."
SK_FOOD_U = "¿Usa insulina o pastillas para el azúcar, o tiene los riñones delicados? Pregúntele a su médico antes de cambiar su comida."

# free waitlist (runway only); matches the app's consent text in Spanish (FUNNEL.md §4.20)
WL = ("La lista de espera es gratis: un correo cuando abra Años Fuertes, y máximo 3 correos de lanzamiento en las 72 horas "
      "siguientes. Sin tarjeta. Te das de baja con un clic.")
# launch: membership terms (S-02, CANON UPDATE 2/3); required in every caption that mentions the membership
MEMBER = ("La membresía se renueva cada mes al mismo precio hasta que canceles. Cancela en línea cuando quieras (máximo dos "
          "pantallas). Garantía de devolución de 14 días en el cobro de la membresía, una vez por persona. Tu precio fundador "
          "queda bloqueado mientras sigas suscrito, pausas incluidas. Precio fundador abierto a todos hasta la fecha de cierre; "
          "términos completos en {{DOMAIN}}/es/terminos#fundadores.")
LIBRO = ("Los libros de inicio de Años Fuertes (PDF en español): \"Fuerza en 7 Días\" de Don Chuy + \"La Cocina Fuerte\" de "
         "Doña Lupe. {{EBOOK_PRICE}} hoy. La página te dice exactamente qué incluye antes de pagar: para la mayoría, los dos "
         "libros + tu primer mes de la Membresía Fundadora, luego {{FOUNDING_PRICE}}/mes; algunas personas ven solo los "
         "libros, {{EBOOK_PRICE}} un solo pago, no es suscripción. Los libros son tuyos para quedártelos. El enlace llega por "
         "mensaje; el pago es en nuestra tienda Shopify. " + MEMBER)
UNIRME = ("Membresía Fundadora de Años Fuertes: {{FOUNDING_PRICE}}/mes. El primer mes se cobra hoy. " + MEMBER)
GIFT = ("Regalo: 3 meses $49 o 12 meses $119, pagados por adelantado. Empieza el día que lo abren, termina a los 3 o 12 "
        "meses y nunca se renueva solo.")
# spoken offer lines (cell B default; the page states the cell the person actually gets)
SAY_LIBRO = ("{{EBOOK_PRICE}} hoy: los dos libros y su primer mes. Luego {{FOUNDING_PRICE}} al mes, se renueva cada mes, "
             "y se cancela en línea cuando quiera.")
SAY_LIBRO_TU = ("{{EBOOK_PRICE}} hoy: los dos libros y tu primer mes. Luego {{FOUNDING_PRICE}} al mes, se renueva cada mes, "
                "y cancelas en línea cuando quieras.")
TAGS_IG = ["#fuerzadespuesdelos60", "#ejercicioencasa", "#donchuyylupe"]
TAGS_K = ["#cocinamexicana", "#recetasconproteina", "#donchuyylupe"]

SCRIPTS = [
# ===================================================================== RUNWAY (ES01–ES25) =====
dict(id="ES01", title="Las cubetas del mandado", secs=44, prop="two orange sand buckets with handles", obj="cubetas", demo=True,
 beats=[
  ("0-3","CHUY","Dos cubetas de arena, diez pasos, hombros abajo. Mire lo que pasa.","DOS CUBETAS, DIEZ PASOS",f"{CO} | Chuy lifts two orange sand buckets by the handles, garage door open | eye-level medium-full"),
  ("3-11","CHUY","Párese derecho. Saque el aire al levantar. Las cubetas pegaditas a las piernas, no adelante.","Derecho · cubetas pegadas","same | side view, he stands tall with the buckets | side medium-full"),
  ("11-20","CHUY","Diez pasos despacio. Los hombros lejos de las orejas. La espalda se acomoda sola, como block bien nivelado.","10 pasos · hombros abajo","same | slow carry down the driveway and back | tracking medium-full"),
  ("20-28","CHUY","En una revisión de 121 estudios, los adultos mayores que entrenaron fuerza dos o tres veces por semana se pusieron más fuertes.","121 estudios · 2–3 por semana","same | study card inset lower-left (Liu & Latham, Cochrane 2009) | medium"),
  ("28-35","CHUY","¿Muy pesado? Media cubeta, o una sola con la otra mano en la pared. Ahí empezamos.","Fácil: media cubeta","same | Frank carries one half-full bucket, free hand on the wall | two-shot"),
  ("35-40","CHUY",SK_MOVE,"¿Operación reciente? Su médico primero.","same | CU | CU"),
  ("40-44","CHUY","Despacio, pero diario. Comente FUERTE y le mando la silla de ocho minutos.","Comente FUERTE","same | sets the buckets down, points to camera | medium"),
 ],
 move=True, tags=["carry"], safety="Loaded carry with loads close; breathe out on the lift; half-bucket regression with a hand on the wall; stop rule in caption.",
 regression="Media cubeta, o una sola con la otra mano en la pared.", skip=SK_MOVE,
 caption="Comente FUERTE y le mando la silla de 8 minutos.\nLas cubetas del mandado: derecho, cubetas pegadas, 10 pasos despacio, saque el aire al levantar. Una revisión Cochrane de 121 estudios (6,700 adultos mayores) encontró que entrenar fuerza 2–3 veces por semana aumentó la fuerza.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#cargarpeso"], tt=["#mayoresde60", "#fuerza", "#donchuyylupe"], yt="Las Cubetas del Mandado (Fuerza Después de los 60)",
 note="E01 Cochrane PRT at grade ('aumentó la fuerza'). Bit 12 visual (Frank's level).", bit=12, wink=False, thumb="CUBETAS = PESAS", music="guitarra cálida instrumental"),

dict(id="ES02", title="Los comerciales de la novela", secs=42, prop="sturdy armless chair against the living-room wall, TV with a paused novela", obj="novela", demo=True,
 beats=[
  ("0-3","CHUY","Si ve la novela cada noche, levántese sin manos en cada comercial.","CADA COMERCIAL: DE PIE",f"{SA} | Chuy on the armless chair, the novela paused behind him | medium-full"),
  ("3-11","CHUY","Silla contra la pared. Pies firmes. Brazos cruzados. Saque el aire y párese.","Silla contra la pared","same | sit-to-stand, side view | side medium-full"),
  ("11-19","CHUY","Cinco veces por comercial. Al final de la novela, ya fueron treinta o cuarenta.","5 por comercial","same | counts on his fingers, sits slowly | medium"),
  ("19-27","CHUY","Levantarse de la silla es la prueba que usan en las clínicas de Estados Unidos. Y se entrena.","La prueba de la silla","same | study card inset (CDC STEADI chair stand) | medium"),
  ("27-33","CHUY","¿Necesita las manos? Úselas. Una almohada en la silla también se vale. Donde empezamos, no donde nos quedamos.","Fácil: con manos o almohada","same | Lupe drops a cushion on the chair from off frame | two-shot"),
  ("33-38","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("38-42","CHUY","Comente FUERTE y le mando la rutina completa de la silla.","Comente FUERTE","same | the novela resumes, he sits | medium"),
 ],
 move=True, tags=["sit_to_stand"], safety="Chair against the wall; breathe out to stand; hands or cushion regression; dizziness skip line.",
 regression="Con las manos en las rodillas o con una almohada en la silla.", skip=SK_MOVE,
 caption="Comente FUERTE y le mando la rutina de la silla.\nCada comercial: 5 veces de pie, sin manos si puede, silla contra la pared. La prueba de la silla de 30 segundos es la que usa el programa STEADI de los CDC; la fuerza para pararse se entrena.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#novela"], tt=["#mayoresde60", "#silla", "#donchuyylupe"], yt="Levántese en Cada Comercial (Rutina de Silla)",
 note="E11 STEADI chair stand as a test (no fall claim); E01 trainability.", bit=0, wink=False, thumb="CADA COMERCIAL, DE PIE", music="bolero instrumental suave"),

dict(id="ES03", title="Agua de cebolla en ayunas", secs=40, prop="glass of onion water next to a steaming pot of caldo", obj="cebolla", myth=True,
 beats=[
  ("0-3","LUPE","¿Agua de cebolla en ayunas? No, mija. La cebolla va en el caldo.","¿AGUA DE CEBOLLA? NO.",f"{LK} | Lupe pours a glass of onion water into the caldo pot | eye-level medium"),
  ("3-10","TOÑA","(audio de WhatsApp) Comadre, dicen que un vaso en ayunas y quedas como nueva.","El audio de la comadre","same | Lupe holds up her phone, voice message playing | CU phone + reaction"),
  ("10-18","LUPE","No hay estudio que diga eso. Lo que sí tiene estudio: comer suficiente proteína en cada comida.","Lo que sí tiene estudio: proteína","same | she taps the study card on the fridge | medium"),
  ("18-27","LUPE","Los expertos recomiendan de veinticinco a treinta gramos por comida para mayores de 65. Un caldo con pollo y garbanzos ya va en camino.","25–30 g por comida","same | ladles chicken and chickpeas into a bowl | CU bowl"),
  ("27-35","LUPE",SK_FOOD,"¿Riñones delicados? Tu doctor primero.","same | CU | CU"),
  ("35-40","LUPE","Toña, te quiero, pero no. Comenta SOPA y te mando mis tres caldos.","Comenta SOPA","same | she sends a heart emoji reply to Toña, points to camera | medium"),
 ],
 move=False, tags=[], safety="Myth named without a condition; protein guidance at grade; kidney/insulin skip line.", regression="", skip=SK_FOOD,
 caption="Comenta SOPA y te mando mis tres caldos.\nEl agua de cebolla en ayunas no tiene estudio. PROT-AGE recomienda 25–30 g de proteína por comida para mayores de 65 (1.0–1.2 g por kilo al día). Un caldo de pollo con garbanzos ayuda a llegar.\n¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida.",
 ig=TAGS_K + ["#caldodepollo"], tt=["#cocinamexicana", "#caldo", "#donchuyylupe"], yt="¿Agua de Cebolla en Ayunas? La Verdad de Doña Lupe",
 note="E28 PROT-AGE. Myth quoted without a condition (BC30 rule). Bit 3 (Toña's audio).", bit=3, wink=False, thumb="LA CEBOLLA VA EN EL CALDO", music="son jarocho suave instrumental"),

dict(id="ES04", title="Las cubetas escondidas", secs=45, prop="the two sand buckets hidden behind the kitchen door", obj="cubetas", demo=True,
 beats=[
  ("0-3","LUPE","Chuy dice que ya calentó. Mire lo que pasa cuando escondo las cubetas.","¿YA CALENTÓ?",f"{DG} | Lupe in the doorway, arms crossed; Chuy looks for his buckets | two-shot"),
  ("3-10","CHUY","Lupita, ¿y mis cubetas? Ya calenté. Moví los brazos.","¿Y mis cubetas?","same | he points at empty mat | two-shot"),
  ("10-20","LUPE","Eso dice él. Ahora te digo yo: espalda primero. Manos en la pared, empuja la cadera atrás, saca el aire.","Manos en la pared · cadera atrás","same | Chuy does a wall-supported hip hinge stretch | side medium-full"),
  ("20-29","CHUY","Luego de gato en la silla: redondea despacito, luego derecho. Cinco veces. Sin forzar.","Gato en la silla · 5 veces","same | seated cat-cow on the chair against the wall | medium-full"),
  ("29-36","LUPE","En casi 250 estudios, el ejercicio ayudó a la gente con dolor de espalda de larga duración a moverse mejor.","250 estudios · moverse mejor","same | study card inset (Cochrane 2021) | medium"),
  ("36-41","CHUY",SK_MOVE,"¿Dolor fuerte? Su médico primero.","same | CU | CU"),
  ("41-45","LUPE","Ahora sí, tus cubetas. Comenta ESPALDA y te mando la rutina de la mañana.","Comenta ESPALDA","same | she slides the buckets out from behind the door | two-shot"),
 ],
 move=True, tags=["hip_flexor_stretch"], safety="Wall-supported hinge and seated cat-cow on a chair against the wall; no loaded flexion; slow range; stop rule.",
 regression="Solo el gato sentado en la silla, movimiento pequeño.", skip=SK_MOVE,
 caption="Comenta ESPALDA y te mando la rutina de la mañana (7 minutos, empieza en la cama).\nPrimero la espalda: manos en la pared, cadera atrás, y el gato sentado en la silla, 5 veces despacio. Una revisión Cochrane de 249 estudios encontró que el ejercicio mejoró la función en personas con dolor de espalda baja de larga duración.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#movilidad"], tt=["#mayoresde60", "#estiramiento", "#donchuyylupe"], yt="Primero la Espalda, Luego las Cubetas",
 note="E30 Cochrane at grade (function improved). Bit 20 hidden buckets + bit 4.", bit=20, wink=False, thumb="PRIMERO LA ESPALDA", music="cumbia lenta instrumental"),

dict(id="ES05", title="La prueba de la silla", secs=46, prop="wooden chair against the patio wall, kitchen timer", obj="silla", demo=True,
 beats=[
  ("0-3","CHUY","Prueba de la silla, hoy: ¿cuántas veces se levanta en 30 segundos?","¿CUÁNTAS EN 30 SEGUNDOS?",f"{PA} | Chuy sets a kitchen timer on the chair against the wall | eye-level medium-full"),
  ("3-11","CHUY","Silla de unas diecisiete pulgadas, contra la pared. Brazos cruzados. Párese completito y siéntese.","Silla contra la pared · brazos cruzados","same | demo, side view | side medium-full"),
  ("11-20","CHUY","Cuente las veces en treinta segundos. Apúntelo con la fecha. Ese número es suyo, no de nadie más.","Apunte su número","same | writes '12' on the wall calendar | CU calendar"),
  ("20-28","CHUY","Los CDC usan esta misma prueba. Y un estudio con más de siete mil adultos de 60 a 94 años dio los rangos normales por edad.","CDC · 7,000 adultos","same | study card inset (STEADI; Rikli & Jones) | medium"),
  ("28-35","CHUY","¿No sale sin manos? Hágala con las manos y apúntelo también. En treinta días la repetimos.","Con manos también cuenta","same | Frank does it with hands on his knees | two-shot"),
  ("35-41","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("41-46","CHUY","Comente PRUEBA y le mando la prueba completa con sus números.","Comente PRUEBA","same | taps the calendar | medium"),
 ],
 move=True, tags=["sit_to_stand"], safety="Chair against the wall; arms crossed or hands on knees regression; someone nearby; dizziness skip line.",
 regression="Con las manos en las rodillas; cuenta igual.", skip=SK_MOVE,
 caption="Comente PRUEBA y le mando la prueba completa.\nLa prueba de la silla de 30 segundos: silla de unas 17 pulgadas contra la pared, brazos cruzados, cuente las veces. Es la prueba del programa STEADI de los CDC; los rangos normales por edad vienen de un estudio con 7,183 adultos de 60 a 94 años (Rikli & Jones).\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#pruebadefuerza"], tt=["#mayoresde60", "#prueba", "#donchuyylupe"], yt="La Prueba de la Silla de 30 Segundos",
 note="E11 + E49 as tests and norms; no risk framing in prominent fields.", bit=12, wink=False, thumb="¿CUÁNTAS EN 30 SEGUNDOS?", music="guitarra cálida instrumental"),

dict(id="ES06", title="Tu desayuno sin proteína", secs=41, prop="plate with pan dulce next to a plate of huevos a la mexicana and beans", obj="desayuno",
 beats=[
  ("0-3","LUPE","No es la edad, no es el clima: es tu desayuno sin proteína.","TU DESAYUNO, NO TU EDAD",f"{LT} | Lupe slides away a plate of pan dulce, slides in eggs and beans | top-down then medium"),
  ("3-11","LUPE","Café con pan dulce: casi nada de proteína. Huevos a la mexicana con frijoles: ahí sí.","Pan dulce vs huevos y frijoles","same | two plates side by side with gram labels | top-down"),
  ("11-20","LUPE","Pasando los 65, los expertos piden entre veinticinco y treinta gramos cada vez que comes. Dos huevos y media taza de frijoles ya te acercan.","25–30 g por comida","same | study card inset (PROT-AGE) | medium"),
  ("20-27","LUPE","El pan dulce no es enemigo. Va después, chiquito. Primero la verdad, luego el pan dulce.","Primero proteína, luego pan dulce","same | she breaks a concha in half, eats a bite | CU"),
  ("27-35","LUPE",SK_FOOD,"¿Riñones delicados? Tu doctor primero.","same | CU | CU"),
  ("35-41","LUPE","Comenta SOPA y te mando mis desayunos con los gramos apuntados.","Comenta SOPA","same | taps her recipe notebook | medium"),
 ],
 move=False, tags=[], safety="Protein at grade; no body/weight talk; kidney/insulin skip line.", regression="", skip=SK_FOOD,
 caption="Comenta SOPA y te mando mis desayunos con gramos.\nPROT-AGE recomienda 25–30 g de proteína por comida para mayores de 65. Dos huevos (unos 12 g) y media taza de frijoles cocidos (unos 7 g) ya te acercan; agrega queso fresco o leche.\n¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida.",
 ig=TAGS_K + ["#desayunomexicano"], tt=["#cocinamexicana", "#desayuno", "#donchuyylupe"], yt="El Problema No Es Tu Edad: Es Tu Desayuno",
 note="E28 + E52 (USDA grams). Signature 12.", bit=15, wink=False, thumb="PRIMERO LA PROTEÍNA", music="bolero instrumental suave"),

dict(id="ES07", title="Los escalones de su casa", secs=46, prop="four concrete porch steps with a black iron handrail", obj="escalones", demo=True,
 beats=[
  ("0-3","CHUY","Si sube los escalones de su casa cada día, ya tiene gimnasio.","SUS ESCALONES = GIMNASIO",f"{ESC} | Chuy at the bottom step, hand on the iron handrail | eye-level full body"),
  ("3-11","CHUY","Mano en el barandal. Todo el pie en el escalón. Empuje con el talón y saque el aire al subir.","Mano en el barandal · talón","same | step-up, side view | side full body"),
  ("11-19","CHUY","Baje despacito, contando tres. Diez de cada lado. La rodilla apunta al dedo de en medio.","Baje en 3 · 10 por lado","same | slow step-down | CU knee tracking"),
  ("19-27","CHUY","Los expertos en fuerza dicen: dos o tres veces por semana, poco a poco, y es seguro hasta para los más frágiles.","2–3 por semana, poco a poco","same | study card inset (NSCA position statement) | medium"),
  ("27-33","CHUY","¿Mucho? Solo el primer escalón, las dos manos en el barandal. Ahí empezamos.","Fácil: un escalón, dos manos","same | Frank does single step with both hands | two-shot"),
  ("33-39","CHUY",SK_MOVE,"¿Operación reciente? Su médico primero.","same | CU | CU"),
  ("39-46","CHUY","Estamos armando algo para empezar juntos, y la lista de espera es gratis. Comente LISTA y le aviso.","Comente LISTA (gratis)","same | sits on the top step, smiles | medium"),
 ],
 move=True, tags=["step_up"], safety="Handrail always; whole foot on the step; slow lowering; one-step two-hands regression; surgery/dizziness skip.",
 regression="Solo el primer escalón con las dos manos en el barandal.", skip=SK_MOVE,
 caption="Comente LISTA y le aviso cuando abramos. " + WL + "\nSubir escalones con la mano en el barandal: todo el pie, empuje con el talón, baje en 3. La NSCA dice que entrenar fuerza 2–3 veces por semana, progresando poco a poco, es seguro y efectivo en adultos mayores.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#escalones"], tt=["#mayoresde60", "#piernasfuertes", "#donchuyylupe"], yt="Sus Escalones Son Su Gimnasio",
 note="E01/E02 at grade. Signature 9.", bit=12, wink=False, thumb="SUS ESCALONES = GIMNASIO", music="guitarra cálida instrumental"),

dict(id="ES08", title="El calendario de la cocina", secs=44, prop="kitchen calendar with balance seconds in marker", obj="calendario", demo=True,
 beats=[
  ("0-3","CHUY","Lupe dice que aguanta más que yo en un pie. Mire lo que pasa.","¿QUIÉN AGUANTA MÁS?",f"{DK} | Chuy points at the kitchen calendar 'LUPE 26 s / CHUY 22 s'; Lupe smirks | two-shot"),
  ("3-11","LUPE","Mano cerquita de la mesa. Un pie, despacito. Los ojos en un punto fijo.","Mano cerca de la mesa","same | both stand on one foot beside the table, fingertips hovering | medium-full"),
  ("11-20","CHUY","Primero pies juntos, luego un pie delante del otro, luego en un pie. Diez segundos cada uno.","Juntos · uno delante · un pie","same | the three stages, Chuy wobbles on the last | full body"),
  ("20-28","LUPE","Es la prueba de equilibrio de cuatro etapas que usan los CDC. Se practica como todo lo demás.","Prueba de 4 etapas (CDC)","same | study card inset (STEADI 4-stage) | medium"),
  ("28-34","CHUY","¿Se tambalea? Ponga la mano en la mesa. Eso no es perder, es entrenar.","Fácil: mano en la mesa","same | Chuy puts his hand down, Lupe writes 23 s | CU calendar"),
  ("34-39","LUPE",SK_MOVE_TU,"¿Mareo al pararte? Tu doctor primero.","same | CU | CU"),
  ("39-44","LUPE","Veintiséis contra veintitrés. Comenta EQUILIBRIO y te mando la prueba.","Comenta EQUILIBRIO","same | she underlines her number twice | CU calendar"),
 ],
 move=True, tags=["balance_static"], safety="Hand hovering over the table; progression from feet together; stop on dizziness; hand-down regression.",
 regression="Con la mano apoyada en la mesa.", skip=SK_MOVE_TU,
 caption="Comenta EQUILIBRIO y te mando la prueba de 4 etapas.\nPies juntos, medio paso, un pie delante del otro, un pie: hasta 10 segundos cada uno, con la mano cerca de la mesa. Es la prueba de equilibrio STEADI de los CDC.\n¿Operación reciente, mareo al pararte o dolor fuerte? Pregúntale a tu doctor primero.",
 ig=TAGS_IG + ["#equilibrio"], tt=["#mayoresde60", "#equilibrio", "#donchuyylupe"], yt="La Prueba de Equilibrio de Doña Lupe (y Don Chuy Pierde)",
 note="E50 as a test only; no fall claims. Bit 5 calendar.", bit=5, wink=False, thumb="LUPE 26 · CHUY 23", music="danzón instrumental suave"),

dict(id="ES09", title="El té para limpiar por dentro", secs=41, prop="box of 'tea' with a blank label next to a bowl of beans and oats", obj="té", myth=True,
 beats=[
  ("0-3","LUPE","¿Té para limpiar por dentro? No. Tu cuerpo ya tiene quien haga ese trabajo.","¿TÉ PARA LIMPIAR? NO.",f"{LT} | Lupe holds a box of tea with a blank label, puts it in a drawer | medium"),
  ("3-10","LUPE","Tu cuerpo hace ese trabajo todo el día, sin cobrarte. Lo que sí le ayuda: fibra y agua.","Lo que sí: fibra y agua","same | she sets out beans, oats and a glass of water | top-down"),
  ("10-19","LUPE","Comer de veinticinco a veintinueve gramos de fibra al día se ha relacionado con mejor salud en estudios grandes. Frijoles, avena, nopales, fruta.","25–29 g de fibra al día","same | study card inset (Reynolds, Lancet 2019) | medium"),
  ("19-27","LUPE","Súbele poquito a poquito, una porción por semana, y toma agua. Si no, la panza se queja.","Poco a poco · con agua","same | adds one scoop of beans to a plate | CU"),
  ("27-35","LUPE",SK_FOOD,"¿Riñones delicados? Tu doctor primero.","same | CU | CU"),
  ("35-41","LUPE","Comenta SOPA y te mando mi escalera de fibra de siete días.","Comenta SOPA","same | closes the drawer on the tea | medium"),
 ],
 move=False, tags=[], safety="No detox/cleanse wording; fiber association phrased as association; go slow with water; kidney/insulin skip.", regression="", skip=SK_FOOD,
 caption="Comenta SOPA y te mando mi escalera de fibra.\nUn análisis grande (Reynolds, Lancet 2019) relacionó comer 25–29 g de fibra al día con mejores resultados de salud en adultos. Frijoles, avena, nopales y fruta; sube una porción por semana y toma agua.\n¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida.",
 ig=TAGS_K + ["#fibra"], tt=["#cocinamexicana", "#fibra", "#donchuyylupe"], yt="¿Té Para Limpiar Por Dentro? Doña Lupe Dice que No",
 note="E24 phrased as association, no mortality wording. No BC32 phrase quoted.", bit=0, wink=False, thumb="FIBRA Y AGUA. YA.", music="son jarocho suave instrumental"),

dict(id="ES10", title="La mesa es su barra", secs=45, prop="kitchen table edge", obj="mesa", demo=True,
 beats=[
  ("0-3","CHUY","La mesa de la cocina es su barra de equilibrio.","LA MESA = SU BARRA",f"{CK} | Chuy stands at the kitchen table edge, fingertips on it | eye-level medium-full"),
  ("3-11","CHUY","Las yemas de los dedos en la mesa. Un pie delante del otro, talón con punta. Diez segundos.","Talón con punta · 10 s","same | tandem stance, side view | side full body"),
  ("11-19","CHUY","Luego cambie de pie. Luego intente levantar los dedos un poquito. La mesa ahí, siempre.","Cambie de pie · mesa cerca","same | switches feet, fingers lift a centimeter | medium-full"),
  ("19-27","CHUY","Esta postura es una etapa de la prueba de equilibrio de los CDC. Practicarla en casa es fácil y barato.","Prueba de los CDC","same | study card inset (STEADI 4-stage) | medium"),
  ("27-33","CHUY","¿Difícil? Medio paso nomás, el pie de atrás a un lado. Ahí empezamos.","Fácil: medio paso","same | semi-tandem stance | CU feet"),
  ("33-39","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("39-45","CHUY","Vamos a abrir algo para practicar juntos. La lista de espera es gratis. Comente LISTA y le aviso.","Comente LISTA (gratis)","same | pats the table | medium"),
 ],
 move=True, tags=["balance_static"], safety="Fingertips on the table; semi-tandem regression; stop on dizziness.",
 regression="Medio paso: el pie de atrás a un lado del otro.", skip=SK_MOVE,
 caption="Comente LISTA y le aviso cuando abramos. " + WL + "\nTalón con punta junto a la mesa, 10 segundos por lado, las yemas de los dedos en la mesa. Es una etapa de la prueba de equilibrio STEADI de los CDC.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#equilibrio"], tt=["#mayoresde60", "#equilibrio", "#donchuyylupe"], yt="Su Mesa de Cocina Es Su Barra de Equilibrio",
 note="E50 as practice of a test stage; no fall claims.", bit=0, wink=False, thumb="TALÓN CON PUNTA", music="guitarra cálida instrumental"),

dict(id="ES11", title="Nopales, frijoles, avena", secs=43, prop="bowl of nopales, olla de frijoles, oats, digital scale", obj="nopales",
 beats=[
  ("0-3","LUPE","Nopales, frijoles, avena: así llego a 25 gramos de fibra.","25 GRAMOS DE FIBRA",f"{LK} | Lupe sets nopales, beans and oats on the scale | top-down"),
  ("3-11","LUPE","Avena en la mañana: unos cuatro gramos. Una taza de frijoles de olla: unos quince.","Avena 4 g · frijoles 15 g","same | gram labels appear by each bowl | top-down"),
  ("11-19","LUPE","Una taza de nopales: unos tres. Una naranja: otros tres. Ya llegaste. Gramos, no cuentos.","Nopales 3 g · naranja 3 g","same | she slices an orange | CU"),
  ("19-27","LUPE","Los números son de la base de datos del gobierno de Estados Unidos, la USDA. Los apunto en mi cuaderno.","Datos: USDA","same | study card inset (USDA FoodData Central) | medium"),
  ("27-35","LUPE",SK_FOOD,"¿Riñones delicados? Tu doctor primero.","same | CU | CU"),
  ("35-43","LUPE","Sube poco a poco, con agua. Comenta SOPA y te mando la lista con los gramos.","Comenta SOPA","same | writes '25 g' in red pen in her notebook | CU notebook"),
 ],
 move=False, tags=[], safety="USDA gram values approximate; go slow with water; kidney/insulin skip line.", regression="", skip=SK_FOOD,
 caption="Comenta SOPA y te mando la lista con gramos.\nAvena (½ taza seca) unos 4 g de fibra, frijoles de olla (1 taza) unos 15 g, nopales cocidos (1 taza) unos 3 g, una naranja unos 3 g. Datos: USDA FoodData Central. Sube poco a poco y toma agua.\n¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida.",
 ig=TAGS_K + ["#nopales"], tt=["#cocinamexicana", "#nopales", "#donchuyylupe"], yt="Así Llego a 25 Gramos de Fibra (Nopales, Frijoles, Avena)",
 note="E24 target, E52 USDA values (approximate, verify per recipe).", bit=15, wink=False, thumb="25 G DE FIBRA", music="son jarocho suave instrumental"),

dict(id="ES12", title="Las bolsas del mandado", secs=45, prop="two full reusable grocery bags", obj="bolsas", demo=True,
 beats=[
  ("0-3","LUPE","Las bolsas del mandado son pesas. Eso dice él. Y por una vez tiene razón.","EL MANDADO = PESAS",f"{DK} | Chuy lifts two full grocery bags off the counter; Lupe raises an eyebrow | two-shot"),
  ("3-11","CHUY","Una bolsa en cada mano, mismo peso. Párese derecho, hombros abajo, y camine al refri despacio.","Mismo peso · hombros abajo","same | carry across the kitchen | tracking medium-full"),
  ("11-19","LUPE","Y las dejas en la silla, no en el piso. Doblas las rodillas, no la espalda.","Rodillas, no espalda","same | he sets the bags on a chair, knees bent | side medium"),
  ("19-27","CHUY","Cargar cosas de todos los días cuenta como entrenar fuerza, si lo hace seguido y con buena postura.","Cargar = entrenar","same | study card inset (Cochrane PRT) | medium"),
  ("27-33","LUPE","¿Pesan mucho? Media bolsa en cada mano. Dos viajes. Nadie te está cronometrando, Jesús.","Fácil: media bolsa, dos viajes","same | Chuy splits bags, Lupe pats his arm | two-shot"),
  ("33-39","CHUY",SK_MOVE,"¿Dolor fuerte? Su médico primero.","same | CU | CU"),
  ("39-45","LUPE","Seis y medio, por bonito. Comenta FUERTE y te mandamos la rutina.","Comenta FUERTE","same | she writes 6.5 on the calendar | CU"),
 ],
 move=True, tags=["carry"], safety="Even loads; set bags on a chair, knees bent; half-bag regression; stop rule.",
 regression="Media bolsa en cada mano, dos viajes.", skip=SK_MOVE,
 caption="Comenta FUERTE y te mandamos la rutina de la silla.\nBolsas del mandado: mismo peso en cada mano, derecho, hombros abajo, y se dejan en la silla doblando las rodillas. La revisión Cochrane de 121 estudios encontró que entrenar fuerza 2–3 veces por semana aumentó la fuerza en adultos mayores.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#mandado"], tt=["#mayoresde60", "#fuerza", "#donchuyylupe"], yt="Las Bolsas del Mandado Son Pesas",
 note="E01 at grade. Bit 4 + 7.", bit=4, wink=False, thumb="EL MANDADO = PESAS", music="cumbia lenta instrumental"),

dict(id="ES13", title="La prueba del piso", secs=48, prop="yoga mat on the patio next to the chair", obj="piso", demo=True,
 beats=[
  ("0-3","CHUY","Prueba del piso, hoy: ¿se puede sentar en el piso y pararse, con la silla cerca?","¿SE PUEDE PARAR DEL PISO?",f"{PA} | Chuy beside a mat and the chair against the wall | eye-level full body"),
  ("3-12","CHUY","La silla al lado. Rodilla al piso, luego la otra. Siéntese de lado. Despacio.","Rodilla · rodilla · de lado","same | backward chain down to sitting | side full body"),
  ("12-21","CHUY","Para subir: de lado a rodillas, una mano en la silla, un pie adelante, y empuje. Saque el aire.","Rodillas · un pie · empuje","same | rises with a hand on the chair seat | side full body"),
  ("21-29","CHUY","Levantarse del piso se puede enseñar a cualquier edad. Mejor practicarlo antes de necesitarlo.","Se aprende a cualquier edad","same | study card inset (floor-rise training) | medium"),
  ("29-36","CHUY","¿El piso está lejos? Empiece con un cojín grueso o el sofá. Ahí empezamos.","Fácil: cojín o sofá","same | Frank practices kneeling onto a thick cushion | two-shot"),
  ("36-42","CHUY",SK_MOVE,"¿Rodilla operada? Su médico primero.","same | CU | CU"),
  ("42-48","CHUY","Comente PRUEBA y le mando las tres pruebas: la silla, un pie y el piso.","Comente PRUEBA","same | sits on the chair, wipes hands | medium"),
 ],
 move=True, tags=["floor_transfer"], safety="Chair beside; backward chaining; cushion/sofa regression; knee-surgery skip line.",
 regression="Con un cojín grueso o desde el sofá.", skip=SK_MOVE,
 caption="Comente PRUEBA y le mando las tres pruebas.\nLevantarse del piso se puede enseñar a cualquier edad: rodillas, un pie adelante, una mano en la silla, empuje sacando el aire. Practíquelo antes de necesitarlo.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#pararsedelpiso"], tt=["#mayoresde60", "#piso", "#donchuyylupe"], yt="La Prueba del Piso: ¿Se Puede Parar Sin Ayuda?",
 note="E45 floor-rise teaching; no mortality framing from E08.", bit=12, wink=False, thumb="ROD · ROD · DE PIE", music="guitarra cálida instrumental"),

dict(id="ES14", title="Después de comer, nadie se sienta", secs=42, prop="dining table after lunch, plates cleared", obj="comer",
 beats=[
  ("0-3","LUPE","No es flojera, no es la edad: después de comer, nadie se sienta.","DESPUÉS DE COMER: A CAMINAR",f"{LC} | Lupe opens her parasol at the front door after lunch | eye-level medium-full"),
  ("3-10","LUPE","Dos minutos. A la esquina y de regreso. O alrededor de la mesa si llueve.","2 minutos · a la esquina","same | walks to the corner and back with Toña's back in frame | tracking"),
  ("10-19","LUPE","Varios estudios compararon caminar poquito después de comer contra quedarse sentado. Caminar salió mejor. Hasta dos minutos cuentan.","2 a 5 minutos cuentan","same | study card inset (Buffey 2022) | medium"),
  ("19-26","LUPE","Muchos de ustedes viven con diabetes. Aquí no la tratamos. Hablamos de hábitos que su médico firmaría.","Hábitos, no tratamientos","same | CU, serious and kind | CU"),
  ("26-35","LUPE",SK_FOOD,"¿Insulina? Tu doctor primero.","same | CU | CU"),
  ("35-42","LUPE","Estamos preparando algo, y la lista de espera es gratis. Comenta LISTA y te aviso.","Comenta LISTA (gratis)","same | closes the parasol, points | medium"),
 ],
 move=True, tags=["walking"], safety="Gentle walk; table-loop indoor option; insulin/kidney skip line; no glucose numbers in prominent fields.",
 regression="Alrededor de la mesa, con una mano cerca del respaldo de la silla.", skip=SK_FOOD,
 caption="Comenta LISTA y te aviso cuando abramos. " + WL + "\nCaminar de 2 a 5 minutos después de comer, en vez de quedarse sentado: una revisión de estudios (Buffey, Sports Medicine 2022) encontró diferencias a favor de caminar. Es un hábito, no un tratamiento.\n¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida.",
 ig=TAGS_IG + ["#caminar"], tt=["#mayoresde60", "#caminar", "#donchuyylupe"], yt="Después de Comer, Nadie Se Sienta",
 note="E23 as habit; diabetes acknowledged, not treated (§10.2). Bit 14 parasol.", bit=14, wink=False, thumb="2 MINUTOS DESPUÉS DE COMER", music="cumbia lenta instrumental"),

dict(id="ES15", title="A tu edad ya no se cargan pesas", secs=46, prop="the wooden chair ('la Jefa') and a 10 lb dumbbell", obj="pesas", myth=True, demo=True,
 beats=[
  ("0-3","LUPE","\"A tu edad ya no se cargan pesas.\" ¿Quién dijo? Chuy, enséñales.","¿YA NO SE CARGAN PESAS?",f"{DP} | Lupe reads a comment on her phone; Chuy picks up a 10 lb dumbbell by the chair | two-shot"),
  ("3-11","CHUY","Saluden a la Jefa. Siéntese, la pesa pegada al pecho, y levántese sacando el aire.","Pesa al pecho · saque el aire","same | goblet sit-to-stand on the chair against the wall | side full body"),
  ("11-19","LUPE","Aquí la jefa soy yo. Pero sí: ocho a doce veces, dos o tres días por semana.","8–12 veces · 2–3 días","same | Lupe counts on her fingers | two-shot"),
  ("19-28","CHUY","Los expertos en fuerza dicen que es seguro y efectivo en adultos mayores, hasta en los más frágiles, si se avanza poco a poco.","Seguro · poco a poco","same | study card inset (NSCA) | medium"),
  ("28-34","LUPE","¿Sin pesa? Una botella de agua llena. O nada. La silla sola ya es trabajo.","Fácil: botella o nada","same | Lupe hands him a water bottle instead | two-shot"),
  ("34-40","CHUY",SK_MOVE,"¿Operación reciente? Su médico primero.","same | CU | CU"),
  ("40-46","LUPE","Comenta FUERTE y te mandamos la rutina de la silla.","Comenta FUERTE","same | she sits on the chair; he waits | two-shot"),
 ],
 move=True, tags=["sit_to_stand", "squat_to_chair"], safety="Chair against the wall; load held close; breathe out to stand; bottle/no-load regression; progression gradual.",
 regression="Con una botella de agua, o sin peso.", skip=SK_MOVE,
 caption="Comenta FUERTE y te mandamos la rutina de la silla.\nLa NSCA (posición oficial) dice que entrenar fuerza es seguro y efectivo para adultos mayores, incluidos los frágiles: 2–3 veces por semana, avanzando poco a poco. Empiece con la silla sola.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#pesas"], tt=["#mayoresde60", "#pesas", "#donchuyylupe"], yt="¿A Tu Edad Ya No Se Cargan Pesas? Mira Esto",
 note="E01/E02. Bit 2 la Jefa.", bit=2, wink=False, thumb="SÍ SE CARGAN PESAS", music="danzón instrumental suave"),

dict(id="ES16", title="Talones en el lavabo", secs=44, prop="toothbrush, bathroom sink", obj="dientes", demo=True,
 beats=[
  ("0-3","CHUY","Si se lava los dientes cada noche, haga diez elevaciones de talón en el lavabo.","DIENTES + 10 TALONES",f"{BA} | Chuy brushing, free hand on the sink edge | medium"),
  ("3-11","CHUY","Mano en el lavabo. Suba a las puntas sacando el aire. Dos segundos arriba, dos abajo.","Mano en el lavabo · 2 y 2","same | heel raises, side view | side medium-full"),
  ("11-20","CHUY","La pantorrilla es una bomba: cada vez que aprieta, empuja la sangre de regreso al corazón. Es fisiología básica.","La pantorrilla = una bomba","same | anatomy inset of calf veins and valves | inset"),
  ("20-27","CHUY","Caminar y subir talones la ponen a trabajar. Diez mientras se lava, todas las noches.","10 cada noche","same | finishes brushing, last reps | medium"),
  ("27-33","CHUY","¿Difícil? Las dos manos en el lavabo y suba poquito. Ahí empezamos.","Fácil: dos manos, poquito","same | small-range raises | CU feet"),
  ("33-39","CHUY","Una pantorrilla hinchada, roja y caliente no es para ejercicio: es para su médico, hoy.","Pantorrilla hinchada: médico hoy","same | CU, serious | CU"),
  ("39-44","CHUY","Comente FUERTE y le mando la rutina de ocho minutos.","Comente FUERTE","same | turns off the light | medium"),
 ],
 move=True, tags=["heel_raise"], safety="Hand on the sink; slow tempo; two-hand regression; red flag: one swollen red painful calf → doctor today.",
 regression="Las dos manos en el lavabo, subiendo poquito.", skip="Una pantorrilla hinchada, roja y caliente no es para ejercicio: es para su médico, hoy.",
 caption="Comente FUERTE y le mando la rutina de 8 minutos.\nLa bomba de la pantorrilla: al apretar el músculo, las venas profundas y sus válvulas empujan la sangre de regreso al corazón (fisiología básica). Caminar y subir talones la activan.\nUna pantorrilla hinchada, roja y caliente no es para ejercicio: es para su médico, hoy.",
 ig=TAGS_IG + ["#pantorrillas"], tt=["#mayoresde60", "#rutinadenoche", "#donchuyylupe"], yt="10 Talones Mientras Se Lava los Dientes",
 note="E47 standard physiology + red flag.", bit=0, wink=False, thumb="DIENTES + 10 TALONES", music="bolero instrumental suave"),

dict(id="ES17", title="Dos huevos y una taza de frijoles", secs=40, prop="two eggs and a cup of beans on the digital scale", obj="huevos",
 beats=[
  ("0-3","LUPE","Dos huevos y una taza de frijoles: casi 25 gramos de proteína.","CASI 25 GRAMOS",f"{LK} | Lupe cracks two eggs onto the comal, beans in a bowl on the scale | top-down"),
  ("3-11","LUPE","Dos huevos: unos doce gramos. Los frijoles, otros quince. Ahí está.","12 g + 15 g","same | gram labels by each | top-down"),
  ("11-19","LUPE","La recomendación pasando los 65: veinticinco a treinta gramos en cada comida, no todo en la cena.","25–30 g en cada comida","same | study card inset (PROT-AGE) | medium"),
  ("19-26","LUPE","Ponle salsa de la casa, no salero. Y una tortilla, no cinco. Chuy, te estoy viendo.","Salsa sí · una tortilla","same | Chuy reaching for a stack of tortillas, freezes | two-shot"),
  ("26-34","LUPE",SK_FOOD,"¿Riñones delicados? Tu doctor primero.","same | CU | CU"),
  ("34-40","LUPE","Comenta SOPA y te mando mis desayunos con gramos.","Comenta SOPA","same | slides the plate to camera | CU"),
 ],
 move=False, tags=[], safety="Protein at grade; salt swap; kidney/insulin skip line.", regression="", skip=SK_FOOD,
 caption="Comenta SOPA y te mando mis desayunos con gramos.\n2 huevos (unos 12 g de proteína) + 1 taza de frijoles de olla (unos 15 g) = casi 25 g. PROT-AGE recomienda 25–30 g por comida para mayores de 65. Datos: USDA FoodData Central.\n¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida.",
 ig=TAGS_K + ["#huevosalamexicana"], tt=["#cocinamexicana", "#proteina", "#donchuyylupe"], yt="Dos Huevos y Frijoles: Casi 25 Gramos de Proteína",
 note="E28 + E52. Bit 6 tortillas.", bit=6, wink=False, thumb="CASI 25 G DE PROTEÍNA", music="son jarocho suave instrumental"),

dict(id="ES18", title="Las velitas del pastel", secs=40, prop="birthday cake candle on a cupcake", obj="aire",
 beats=[
  ("0-3","CHUY","Saque el aire largo, como soplando las velitas del pastel, y mire lo que pasa.","SOPLE LAS VELITAS",f"{SA} | Chuy seated, holds up a cupcake with one candle | medium"),
  ("3-11","CHUY","Aire por la nariz, contando cuatro. Sáquelo por la boca, contando seis. Despacito.","Entra 4 · sale 6","same | breath count overlay, his shoulders drop | medium"),
  ("11-19","CHUY","Mire los hombros: bajan solitos. Respirar lento, unas seis veces por minuto, calma al cuerpo.","Unas 6 por minuto","same | CU shoulders lowering | CU"),
  ("19-27","CHUY","Estudios de respiración lenta muestran que el corazón cambia su ritmo hacia la calma mientras la practica.","Respiración lenta = calma","same | study card inset (Laborde 2022) | medium"),
  ("27-34","CHUY","Cinco minutos. Sentado, con la espalda en el respaldo. Si se marea, respire normal y descanse.","5 min · sentado","same | Pirata lies on his feet | medium-full"),
  ("34-40","CHUY","Comente RESPIRA y le mando la respiración de cinco minutos.","Comente RESPIRA","same | blows out the candle, smiles | CU"),
 ],
 move=False, tags=[], safety="Seated; no breath holds; stop if dizzy; no anxiety/BP claims.", regression="", skip="Si se marea, respire normal y descanse.",
 caption="Comente RESPIRA y le mando la respiración de 5 minutos.\nEntra 4, sale 6, unas 6 respiraciones por minuto, sentado. Un metaanálisis (Laborde 2022) encontró que la respiración lenta aumenta la variabilidad del ritmo cardiaco, una señal de calma del cuerpo.\nSi se marea, respire normal y descanse.",
 ig=TAGS_IG + ["#respiracion"], tt=["#mayoresde60", "#respirar", "#donchuyylupe"], yt="Respire Como Soplando las Velitas",
 note="E19 at grade (HRV). Bit 8 Pirata.", bit=8, wink=False, thumb="ENTRA 4 · SALE 6", music="guitarra cálida instrumental"),

dict(id="ES19", title="Lo que le contestamos a Marisol", secs=46, prop="phone on a stand for the video call", obj="marisol", demo=True,
 beats=[
  ("0-3","LUPE","Mándeselo a su hija: así le contestamos a Marisol cuando dice que hacemos demasiado.","PARA LAS HIJAS PREOCUPADAS",f"{DS} | the phone on the coffee table shows Marisol on a video call | two-shot + phone"),
  ("3-10","MARISOL","(videollamada) Papá, ¿otra vez cargando cubetas? Me preocupa que te lastimes.","\"Me preocupa\"","same | Marisol's face on the phone | CU phone"),
  ("10-18","CHUY","Mija, primero la silla, luego las cubetas, con la pared cerca. Y si duele fuerte, paro.","Silla · pared · si duele, paro","same | Chuy shows the chair against the wall | medium"),
  ("18-27","LUPE","Tu papá está bien. Tu papá es presumido. Y entrenar la fuerza, dos o tres días a la semana, tiene muchísimos estudios.","2–3 por semana · con estudios","same | study card inset (Cochrane PRT) | two-shot"),
  ("27-34","CHUY","Lo que sí le pedimos: que entrene con nosotros. Una silla en Houston, otra en Los Ángeles.","Entrene con sus papás","same | Marisol laughs, holds up her own chair | split"),
  ("34-40","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("40-46","LUPE","La lista de espera es gratis, para ti y para tus papás. Comenta LISTA.","Comenta LISTA (gratis)","same | waves at Marisol | two-shot"),
 ],
 move=True, tags=["sit_to_stand"], safety="Shows support and stop rule; no product result claims; dizziness skip line.",
 regression="Primero la silla sola, con la pared cerca.", skip=SK_MOVE,
 caption="Comenta LISTA y te avisamos cuando abramos. " + WL + "\nPara las hijas y los hijos preocupados: primero la silla, luego la carga, la pared cerca, y si duele fuerte se para. La revisión Cochrane de 121 estudios encontró que entrenar fuerza 2–3 veces por semana aumentó la fuerza en adultos mayores.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#familia"], tt=["#mayoresde60", "#familia", "#donchuyylupe"], yt="Lo Que Le Contestamos a Nuestra Hija Preocupada",
 note="E01. Bit 21 Marisol's call.", bit=21, wink=False, thumb="PARA LAS HIJAS", music="bolero instrumental suave"),

dict(id="ES20", title="Caminar no es suficiente", secs=44, prop="two 5 lb dumbbells on the patio chair", obj="caminar", myth=True, demo=True,
 beats=[
  ("0-3","LUPE","¿Que caminar ya es suficiente? No, comadre. Las piernas también piden carga.","¿CAMINAR ES SUFICIENTE?",f"{DP} | Lupe in her track jacket with two 5 lb dumbbells by the chair | medium-full"),
  ("3-11","LUPE","Caminar es bueno. Pero el músculo pide algo que pese un poquito más que tu bolsa.","Caminar + carga","same | she sits and stands holding the dumbbells by her sides | side full body"),
  ("11-19","LUPE","Silla contra la pared, pesitas a los lados, levántate sacando el aire. Ocho veces.","Silla · pesitas · 8 veces","same | sit-to-stand demo | full body"),
  ("19-28","LUPE","En un estudio con mujeres después de la menopausia, entrenar con supervisión dos veces por semana mejoró la densidad de los huesos.","Con supervisión · 2 por semana","same | study card inset (LIFTMOR) | medium"),
  ("28-34","LUPE","¿Sin pesitas? Dos latas de frijoles. ¿Sin latas? Solo la silla.","Fácil: latas o nada","same | swaps dumbbells for cans | CU"),
  ("34-39","LUPE",SK_MOVE_TU,"¿Operación reciente? Tu doctor primero.","same | CU | CU"),
  ("39-44","LUPE","Comenta FUERTE y te mando la rutina de la silla.","Comenta FUERTE","same | sets the cans on the chair | medium"),
 ],
 move=True, tags=["sit_to_stand"], safety="Chair against the wall; light load at sides; cans/no-load regression; LIFTMOR framed as supervised; stop rule.",
 regression="Dos latas de frijoles, o solo la silla.", skip=SK_MOVE_TU,
 caption="Comenta FUERTE y te mando la rutina de la silla.\nCaminar es bueno; el músculo además pide carga. En el estudio LIFTMOR, mujeres posmenopáusicas con baja masa ósea entrenaron con supervisión 2 veces por semana durante 8 meses y su densidad ósea mejoró. Empieza con la silla.\n¿Operación reciente, mareo al pararte o dolor fuerte? Pregúntale a tu doctor primero.",
 ig=TAGS_IG + ["#mujeresfuertes"], tt=["#mayoresde60", "#mujeresfuertes", "#donchuyylupe"], yt="¿Caminar Es Suficiente? Doña Lupe Dice que No",
 note="E29 framed as supervised (no menopause claim in prominent fields); E01.", bit=0, wink=False, thumb="LAS PIERNAS PIDEN CARGA", music="cumbia lenta instrumental"),

dict(id="ES21", title="El costal de arena", secs=46, prop="sewn canvas sandbag (el costal)", obj="costal", demo=True,
 beats=[
  ("0-3","CHUY","Costal de arena: lo cosí yo. Así se carga con la espalda derecha.","EL COSTAL",f"{CO} | Chuy beside the canvas sandbag on the mat | eye-level medium-full"),
  ("3-11","CHUY","Pies abiertos. Cadera atrás, como si cerrara la puerta del carro con las pompas. Pecho arriba.","Cadera atrás · pecho arriba","same | hinge to the bag, side view | side full body"),
  ("11-19","CHUY","Abrácelo pegado a la panza y párese sacando el aire. Nunca se agache con la espalda redonda.","Abrazado · espalda derecha","same | bear-hug lift, stands tall | side full body"),
  ("19-27","CHUY","Las guías para huesos frágiles dicen: fuerza sí, pero sin doblar la espalda con peso ni girar con fuerza.","Sin doblar la espalda con peso","same | study card inset (bone-health exercise guidance) | medium"),
  ("27-34","CHUY","¿Pesado? Póngalo en la silla y levántelo desde ahí. Menos distancia, misma postura.","Fácil: desde la silla","same | lifts the bag from the chair seat | medium-full"),
  ("34-40","CHUY",SK_MOVE,"¿Dolor fuerte? Su médico primero.","same | CU | CU"),
  ("40-46","CHUY","Como block bien nivelado. Comente FUERTE y le mando la rutina.","Comente FUERTE","same | sets the costal down, Lupe groans off-camera at the metaphor | medium"),
 ],
 move=True, tags=["carry"], safety="Hip hinge; load close; no loaded spinal flexion or twisting (E40); lift-from-chair regression; stop rule.",
 regression="Levantarlo desde el asiento de la silla.", skip=SK_MOVE,
 caption="Comente FUERTE y le mando la rutina.\nEl costal: cadera atrás, pecho arriba, abrazado a la panza, párese sacando el aire. Las guías de ejercicio para huesos frágiles recomiendan fuerza y equilibrio, y evitar doblar la espalda con peso y los giros con fuerza.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#costal"], tt=["#mayoresde60", "#fuerza", "#donchuyylupe"], yt="Cómo Cargar un Costal con la Espalda Derecha",
 note="E01 + E40. Bit 13 bricklayer metaphor.", bit=13, wink=False, thumb="ESPALDA DERECHA", music="guitarra cálida instrumental"),

dict(id="ES22", title="El danzón del domingo", secs=42, prop="small radio playing danzón in the living room", obj="danzón", demo=True,
 beats=[
  ("0-3","LUPE","Si bailan danzón en cada fiesta, ya saben que el cuerpo todavía responde.","¿BAILAN DANZÓN?",f"{DS} | radio on; Chuy offers his hand to Lupe | two-shot"),
  ("3-10","CHUY","Para mí el danzón es cardio, mi reina.","\"Es cardio\"","same | they start a slow danzón step | full body"),
  ("10-18","LUPE","Para ti es pretexto. Pasitos cortos, Jesús. Mano en mi hombro, no en la radio.","Pasitos cortos","same | Lupe leads, Chuy follows | full body"),
  ("18-27","CHUY","Bailar despacito es moverse, cambiar el peso de un pie al otro, y reírse. Las tres cosas cuentan.","Moverse · cambiar el peso · reírse","same | CU feet shifting weight | CU"),
  ("27-35","LUPE","Ella baila mejor. Cincuenta y un años y todavía no aprende. Si te mareas, siéntate.","Si te mareas, siéntate","same | they laugh, she dips him slightly | two-shot"),
  ("35-42","LUPE","Estamos armando la clase del domingo. La lista de espera es gratis. Comenta LISTA.","Comenta LISTA (gratis)","same | radio off, they sit on the sofa | two-shot"),
 ],
 move=True, tags=["weight_shift"], safety="Slow steps; partner hand support near the sofa; sit if dizzy.",
 regression="Solo el cambio de peso, con una mano en el respaldo del sofá.", skip="Si te mareas, siéntate.",
 caption="Comenta LISTA y te avisamos cuando abramos. " + WL + "\nEl danzón del domingo: pasitos cortos, cambiar el peso de un pie al otro, con una mano en el hombro de tu pareja o en el sofá. Moverse con alguien que quieres también cuenta.\nSi te mareas, siéntate.",
 ig=TAGS_IG + ["#danzon"], tt=["#mayoresde60", "#danzon", "#donchuyylupe"], yt="El Danzón del Domingo (Él Dice Que Es Cardio)",
 note="P17 couple, opinion; no evidence claim. Bit 19.", bit=19, wink=False, thumb="\"ES CARDIO\"", music="danzón instrumental"),

dict(id="ES23", title="Tres minutos antes de dormir", secs=42, prop="bedside lamp, glass of water, phone face-down", obj="colchón",
 beats=[
  ("0-3","LUPE","No es el colchón, no es la almohada: son tres minutos de calma antes de dormir.","3 MINUTOS ANTES DE DORMIR",f"{LR} | Lupe sits on the bed edge, turns the phone face-down | medium"),
  ("3-11","LUPE","El celular boca abajo y lejos. La luz bajita. Sentada en la orilla de la cama.","Celular lejos · luz bajita","same | dims the lamp | medium"),
  ("11-19","LUPE","Aire por la nariz contando cuatro, sale por la boca contando seis. Diez veces.","Entra 4 · sale 6 · 10 veces","same | breath overlay | CU"),
  ("19-27","LUPE","No te prometo dormir de corrido. Te prometo tres minutos tranquilos. La respiración lenta calma al cuerpo; hay estudios.","No promesas · 3 min tranquilos","same | study card inset (Laborde 2022) | medium"),
  ("27-36","LUPE","Si roncas fuerte y alguien te ha visto dejar de respirar dormido, eso no es para respirar: es para tu doctor.","¿Ronquidos y pausas? Tu doctor.","same | CU, serious | CU"),
  ("36-42","LUPE","Comenta SUEÑO y te mando la rutina de diez minutos para la noche.","Comenta SUEÑO","same | lies down, lamp off | medium"),
 ],
 move=False, tags=[], safety="No sleep-outcome promise; snoring/apnea red flag (E48).", regression="",
 skip="Si roncas fuerte y alguien te ha visto dejar de respirar dormido, eso no es para respirar: es para tu doctor.",
 caption="Comenta SUEÑO y te mando la rutina de 10 minutos para la noche.\nCelular lejos, luz bajita, entra 4 y sale 6, diez veces. La respiración lenta aumenta la variabilidad del ritmo cardiaco (Laborde 2022), una señal de calma. No es una promesa de dormir de corrido.\nSi roncas fuerte y alguien te ha visto dejar de respirar dormido, eso no es para respirar: es para tu doctor.",
 ig=TAGS_IG + ["#rutinadenoche"], tt=["#mayoresde60", "#noche", "#donchuyylupe"], yt="Tres Minutos de Calma Antes de Dormir",
 note="E19 at grade; E48 red flag. No insomnia claim.", bit=0, wink=False, thumb="3 MINUTOS DE CALMA", music="bolero instrumental muy suave"),

dict(id="ES24", title="No tengo rodillas", secs=40, prop="the wooden chair against the patio wall", obj="rodillas",
 beats=[
  ("0-3","CHUY","No soy de verdad, no tengo rodillas: soy de inteligencia artificial. La silla sí es real.","SOY IA. LA SILLA, NO.",f"{PA} | Chuy beside the chair against the wall, corner tag 'Personaje de IA' enlarged | medium-full"),
  ("3-10","LUPE","Y aun así no se estira. Así de realista quedó.","\"Y aun así no se estira\"","same | Lupe leans into frame | two-shot"),
  ("10-18","CHUY","Nos hizo un equipo de gente real que quiere a sus papás. Cada número que decimos viene de un estudio publicado.","Equipo real · estudios publicados","same | study card stack on the table | medium"),
  ("18-26","CHUY","Las fuentes están en la descripción y en nuestra página. Léalas. Lupe las lee todas.","Fuentes en la descripción","same | Lupe reads a card over her glasses | two-shot"),
  ("26-33","CHUY","Lo que sí es suyo: sus piernas. Esas no las hace nadie más que usted, con una silla.","Sus piernas son suyas","same | he sits and stands once | full body"),
  ("33-40","CHUY","Información general, no consejo médico. Estamos por abrir; la lista de espera es gratis. Comente LISTA.","Comente LISTA (gratis)","same | waves | medium"),
 ],
 move=False, tags=[], safety="AI disclosure; general information, not medical advice.", regression="", skip="Información general, no consejo médico.",
 caption="Comente LISTA y le avisamos cuando abramos. " + WL + "\nDon Chuy y Doña Lupe son personajes creados con inteligencia artificial por un equipo real. Cada número viene de un estudio publicado; las fuentes están en nuestra página.\nInformación general, no consejo médico.",
 ig=TAGS_IG + ["#inteligenciaartificial"], tt=["#ia", "#mayoresde60", "#donchuyylupe"], yt="Somos de Inteligencia Artificial (La Silla No)",
 note="P20 disclosure; wink 1. Bit 17.", bit=17, wink=True, thumb="SOY IA. LA SILLA, NO.", music="guitarra cálida instrumental"),

dict(id="ES25", title="Siete días, una silla", secs=44, prop="the chair with a hand-drawn 7-day checklist taped to it", obj="compadre", demo=True,
 beats=[
  ("0-3","CHUY","Etiquete a su compadre: siete días, una silla, ocho minutos, empezando el lunes.","7 DÍAS, 1 SILLA, 8 MIN",f"{DP} | a 7-day checklist taped to the chair back | medium-full"),
  ("3-11","CHUY","Día uno: levantarse de la silla. Día dos: talones. Día tres: la mesa y un pie.","Día 1 · 2 · 3","same | quick cuts of each move with support | montage"),
  ("11-19","LUPE","Día cuatro: cargar el mandado. Y el domingo, caldo. Ese lo pongo yo.","Día 4 · domingo: caldo","same | Lupe adds 'CALDO' to the list in red pen | CU"),
  ("19-27","CHUY","Más de cien estudios respaldan la fuerza dos o tres días por semana. Ocho minutos es por dónde empezar.","2–3 por semana · con estudios","same | study card inset (Cochrane PRT) | medium"),
  ("27-33","CHUY","Cada movimiento tiene su versión fácil, con la silla o la pared. Nadie se queda afuera.","Versión fácil en todo","same | Frank does the easy version, thumbs up | two-shot"),
  ("33-38","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("38-44","LUPE","Avisamos cuando abra, y la lista de espera es gratis. Comenta LISTA.","Comenta LISTA (gratis)","same | both point at camera | two-shot"),
 ],
 move=True, tags=["sit_to_stand", "heel_raise"], safety="Every move with chair/wall support and an easy version; dizziness skip line.",
 regression="La versión fácil de cada día, con la silla o la pared.", skip=SK_MOVE,
 caption="Comenta LISTA y te avisamos cuando abramos. " + WL + "\nSiete días, una silla, ocho minutos: levantarse, talones, la mesa y un pie, el mandado, y caldo el domingo. La revisión Cochrane de 121 estudios respalda entrenar fuerza 2–3 veces por semana.\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#reto7dias"], tt=["#mayoresde60", "#reto", "#donchuyylupe"], yt="Siete Días, Una Silla, Ocho Minutos",
 note="E01. Bit 15 notebook pen.", bit=15, wink=False, thumb="7 DÍAS · 1 SILLA", music="cumbia lenta instrumental"),

# ===================================================================== LAUNCH (ES26–ES40) =====
dict(id="ES26", title="El plan de siete días", secs=52, prop="printed page 1 of 'Fuerza en 7 Días' on the chair", obj="silla", launch=True,
 beats=[
  ("0-3","CHUY","Si quiere empezar cada mañana con una silla, aquí está el plan de siete días.","EL PLAN DE 7 DÍAS",f"{PA} | Chuy holds page 1 of the book next to the chair against the wall | medium-full"),
  ("3-11","CHUY","Soy Don Chuy, un personaje de inteligencia artificial. El plan sí es de verdad: siete mañanas, ocho minutos, una silla.","Personaje de IA · plan real","same | flips pages: day 1 to day 7 | CU pages"),
  ("11-19","CHUY","Cada día trae la versión fácil, la regla para parar y dónde poner las manos.","Versión fácil · regla para parar","same | page detail: easy version box | CU"),
  ("19-27","CHUY","Y el libro de Lupe: recetas con los gramos de proteína y fibra apuntados.","+ el libro de Lupe","same | Lupe's book cover on screen | CU"),
  ("27-38","CHUY",SAY_LIBRO,"{{EBOOK_PRICE}} hoy · cancela en línea","same | price card on screen, read slowly | medium"),
  ("38-45","CHUY","La página dice exactamente lo que incluye antes de pagar. Nada viene marcado.","Todo escrito antes de pagar","same | phone screenshot of the offer page | CU phone"),
  ("45-52","CHUY","Comente LIBRO y le mando el enlace por mensaje. "+SK_MOVE,"Comente LIBRO","same | taps the chair | medium"),
 ],
 move=False, tags=[], safety="Offer only; skip line; AI disclosure.", regression="", skip=SK_MOVE,
 caption="Comente LIBRO y le mando el enlace por mensaje.\n" + LIBRO + "\nDon Chuy y Doña Lupe son personajes de IA. ¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG, tt=["#mayoresde60", "#donchuyylupe"], yt="El Plan de 7 Días de Don Chuy",
 note="Launch LIBRO, cell B wording + cell A disclosure.", bit=0, wink=False, thumb="7 MAÑANAS · 1 SILLA", music="guitarra cálida instrumental"),

dict(id="ES27", title="Mi cuaderno ahora es libro", secs=50, prop="Lupe's worn recipe notebook next to the printed book", obj="cuaderno", launch=True,
 beats=[
  ("0-3","LUPE","Mi cuaderno de recetas, con los gramos apuntados, ahora es libro.","MI CUADERNO, AHORA LIBRO",f"{LK} | Lupe sets her worn notebook beside the printed 'La Cocina Fuerte' | medium"),
  ("3-11","LUPE","Somos personajes de IA, mija. Las recetas son de casa: caldo de pollo, frijoles de olla, huevos a la mexicana.","Personajes de IA · recetas de casa","same | flips pages: caldo, frijoles, huevos | CU pages"),
  ("11-19","LUPE","Cada receta trae los gramos de proteína y fibra, y una cajita de quién debe saltársela.","Gramos + quién se la salta","same | CU of the 'quién debe saltarse esto' box | CU"),
  ("19-31","LUPE",SAY_LIBRO_TU,"{{EBOOK_PRICE}} hoy · cancelas en línea","same | price card on screen | medium"),
  ("31-38","LUPE","La página te dice exactamente qué incluye antes de pagar. Nada viene marcado.","Todo escrito antes de pagar","same | phone screenshot | CU phone"),
  ("38-44","LUPE",SK_FOOD,"¿Riñones delicados? Tu doctor primero.","same | CU | CU"),
  ("44-50","LUPE","Comenta LIBRO y te mando el enlace por mensaje.","Comenta LIBRO","same | closes the notebook | medium"),
 ],
 move=False, tags=[], safety="Offer; kidney/insulin skip line; AI disclosure.", regression="", skip=SK_FOOD,
 caption="Comenta LIBRO y te mando el enlace por mensaje.\n" + LIBRO + "\n¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida.",
 ig=TAGS_K, tt=["#cocinamexicana", "#donchuyylupe"], yt="El Cuaderno de Recetas de Doña Lupe, Ahora Libro",
 note="Launch LIBRO. Bit 15 notebook.", bit=15, wink=False, thumb="MI CUADERNO, AHORA LIBRO", music="son jarocho suave instrumental"),

dict(id="ES28", title="No es magia", secs=56, prop="the kitchen calendar with a month of marks", obj="magia", launch=True,
 beats=[
  ("0-3","LUPE","No es magia, no es un reto de una semana: es todos los días, con nosotros.","TODOS LOS DÍAS, CON NOSOTROS",f"{DC} | a calendar full of check marks on the table | two-shot"),
  ("3-11","CHUY","Somos de inteligencia artificial. Años Fuertes es real: una sesión nueva cada mañana, de ocho a doce minutos.","Personajes de IA · Años Fuertes","same | phone shows the morning session screen | CU phone"),
  ("11-19","LUPE","Con versión de silla para todo, mis recetas cada domingo, y una prueba de fuerza cada mes.","Silla · recetas · prueba mensual","same | Lupe ticks items on a card | CU card"),
  ("19-31","CHUY","La Membresía Fundadora: {{FOUNDING_PRICE}} al mes. Se cobra el primer mes hoy, se renueva cada mes, y se cancela en línea cuando quiera.","{{FOUNDING_PRICE}}/mes · cancela en línea","same | price card, read slowly | medium"),
  ("31-40","LUPE","Garantía de devolución de 14 días en el cobro de la membresía. Y el precio fundador queda bloqueado mientras sigas suscrito.","14 días · precio bloqueado","same | terms card | CU card"),
  ("40-46","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("46-56","LUPE","Eso dice él. Ahora te digo yo: lee la página completa antes de pagar. Comenta UNIRME y te mandamos todo.","Comenta UNIRME","same | she taps the calendar | two-shot"),
 ],
 move=False, tags=[], safety="Membership terms spoken; skip line; AI disclosure.", regression="", skip=SK_MOVE,
 caption="Comenta UNIRME y te mandamos el enlace con todos los términos.\n" + UNIRME + "\nDon Chuy y Doña Lupe son personajes de IA. ¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG, tt=["#mayoresde60", "#donchuyylupe"], yt="Años Fuertes: Todos los Días, con Nosotros",
 note="Launch UNIRME, full S-02 terms spoken and in caption. Bit 4.", bit=4, wink=False, thumb="TODOS LOS DÍAS", music="bolero instrumental suave"),

dict(id="ES29", title="Las tortillas del libro", secs=50, prop="the printed cookbook open to the tortilla page", obj="tortillas", launch=True,
 beats=[
  ("0-3","CHUY","Chuy contó las tortillas del libro de Lupe. Mire lo que pasa.","¿CUÁNTAS TORTILLAS?",f"{DK} | Chuy reads the cookbook, a stack of tortillas beside him | two-shot"),
  ("3-10","CHUY","Aquí dice: una tortilla por plato. Una, Lupita.","\"Una tortilla por plato\"","same | he points at the page, betrayed | CU page"),
  ("10-18","LUPE","Van cinco. Cinco, Jesús. Yo cuento. El libro tiene los gramos, no tus ganas.","Gramos, no ganas","same | she moves four tortillas back to the basket | two-shot"),
  ("18-26","CHUY","Somos personajes de IA. Las recetas sí son de casa, con proteína y fibra en cada página.","Personajes de IA · recetas reales","same | flips pages | CU pages"),
  ("26-38","LUPE",SAY_LIBRO_TU,"{{EBOOK_PRICE}} hoy · cancelas en línea","same | price card on screen | medium"),
  ("38-45","LUPE",SK_FOOD,"¿Riñones delicados? Tu doctor primero.","same | CU | CU"),
  ("45-50","LUPE","Comenta LIBRO y te mando el enlace.","Comenta LIBRO","same | hands Chuy one tortilla | two-shot"),
 ],
 move=False, tags=[], safety="Offer; kidney/insulin skip line; AI disclosure.", regression="", skip=SK_FOOD,
 caption="Comenta LIBRO y te mando el enlace por mensaje.\n" + LIBRO + "\n¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida.",
 ig=TAGS_K, tt=["#cocinamexicana", "#donchuyylupe"], yt="Don Chuy Contó las Tortillas del Libro",
 note="Launch LIBRO. Bit 6 tortillas.", bit=6, wink=False, thumb="UNA TORTILLA, JESÚS", music="cumbia lenta instrumental"),

dict(id="ES30", title="Regálale fuerza a mamá", secs=46, prop="gift card printed with 'Años Fuertes' on the comedor table", obj="hermana", launch=True,
 beats=[
  ("0-3","LUPE","Mándaselo a tu hermana: así se le regala fuerza a mamá.","REGÁLALE FUERZA A MAMÁ",f"{LT} | Lupe holds a printed gift card | medium"),
  ("3-11","LUPE","Somos personajes de IA. El regalo es real: Años Fuertes para tu mamá o tu papá, con su propia cuenta.","Personajes de IA · regalo real","same | phone shows the gift page | CU phone"),
  ("11-20","LUPE","Tres meses por cuarenta y nueve dólares, o doce meses por ciento diecinueve, pagados una vez.","3 meses $49 · 12 meses $119","same | price card | medium"),
  ("20-28","LUPE","Empieza el día que lo abren, termina solo, y nunca se renueva solo. Nadie le cobra nada a tu mamá.","Nunca se renueva solo","same | terms card | CU card"),
  ("28-35","LUPE","Lo que sí le das: una silla, una rutina cada mañana, y mis recetas los domingos.","Silla · rutina · recetas","same | flips to recipe page | CU"),
  ("35-40","LUPE",SK_MOVE_TU,"¿Operación reciente? Su doctor primero.","same | CU | CU"),
  ("40-46","LUPE","Comenta FAMILIA y te mando la página del regalo.","Comenta FAMILIA","same | slides the card toward camera | medium"),
 ],
 move=False, tags=[], safety="Gift terms; skip line; AI disclosure.", regression="", skip=SK_MOVE_TU,
 caption="Comenta FAMILIA y te mando la página del regalo.\n" + GIFT + "\nDon Chuy y Doña Lupe son personajes de IA. ¿Operación reciente, mareo al pararte o dolor fuerte? Pregúntale a tu doctor primero.",
 ig=TAGS_IG + ["#regaloparamama"], tt=["#regalo", "#mama", "#donchuyylupe"], yt="Regálale Fuerza a Mamá",
 note="Launch FAMILIA gift terms.", bit=0, wink=False, thumb="REGÁLALE FUERZA A MAMÁ", music="bolero instrumental suave"),

dict(id="ES31", title="Prueba de la silla, y el plan", secs=55, prop="chair against the patio wall, the printed plan", obj="prueba", launch=True, demo=True,
 beats=[
  ("0-3","CHUY","Prueba de la silla, hoy. Y si quiere el plan completo, se lo explico claro.","PRUEBA DE LA SILLA, HOY",f"{PA} | Chuy at the chair against the wall, the book on the seat | medium-full"),
  ("3-11","CHUY","Brazos cruzados, párese y siéntese treinta segundos. Cuente. Apunte. Con manos también cuenta.","30 s · cuente · apunte","same | demo | side full body"),
  ("11-18","CHUY","Soy un personaje de IA. El número que apunte es suyo, de verdad.","Personaje de IA · su número real","same | writes on the wall calendar | CU"),
  ("18-25","CHUY","El libro trae siete mañanas para empezar desde ese número, con versión fácil en cada día.","7 mañanas desde su número","same | flips the plan | CU pages"),
  ("25-37","CHUY",SAY_LIBRO,"{{EBOOK_PRICE}} hoy · cancela en línea","same | price card | medium"),
  ("37-43","CHUY","La página dice todo antes de pagar. Nada marcado de más.","Todo escrito antes de pagar","same | phone screenshot | CU phone"),
  ("43-49","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("49-55","CHUY","Comente LIBRO y le mando el enlace.","Comente LIBRO","same | sits | medium"),
 ],
 move=True, tags=["sit_to_stand"], safety="Chair against the wall; hands regression; dizziness skip; AI disclosure.",
 regression="Con las manos en las rodillas.", skip=SK_MOVE,
 caption="Comente LIBRO y le mando el enlace por mensaje.\n" + LIBRO + "\nLa prueba de la silla de 30 segundos es la del programa STEADI de los CDC. ¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG, tt=["#mayoresde60", "#donchuyylupe"], yt="La Prueba de la Silla y el Plan de 7 Días",
 note="Launch LIBRO with a demo; E11 test only.", bit=0, wink=False, thumb="SU NÚMERO DE HOY", music="guitarra cálida instrumental"),

dict(id="ES32", title="Sin cuenta regresiva", secs=55, prop="kitchen timer, deliberately unplugged", obj="apurar", launch=True,
 beats=[
  ("0-3","LUPE","No te voy a apurar, no hay cuenta regresiva: te digo el precio y ya.","SIN CUENTA REGRESIVA",f"{LT} | Lupe unplugs a kitchen timer and puts it away | medium"),
  ("3-10","LUPE","Somos de inteligencia artificial, comadre. Los términos son de verdad, y te los leo.","Personajes de IA · términos reales","same | puts on her reading glasses | CU"),
  ("10-21","LUPE","Membresía Fundadora: {{FOUNDING_PRICE}} al mes. El primer mes se cobra hoy, se renueva cada mes, y cancelas en línea cuando quieras, en dos pantallas.","{{FOUNDING_PRICE}}/mes · 2 pantallas","same | price card | medium"),
  ("21-30","LUPE","Garantía de devolución de 14 días en el cobro de la membresía, una vez por persona. Tu precio queda bloqueado mientras sigas suscrito.","14 días · precio bloqueado","same | terms card | CU card"),
  ("30-37","LUPE","El precio fundador tiene fecha de cierre, y está en la página. Nada de inventar prisa.","Fecha de cierre en la página","same | phone shows the terms page | CU phone"),
  ("37-43","LUPE",SK_MOVE_TU,"¿Operación reciente? Tu doctor primero.","same | CU | CU"),
  ("43-55","LUPE","Primero la verdad, luego el pan dulce. Comenta UNIRME y te mando el enlace con todo escrito.","Comenta UNIRME","same | offers a concha to camera | medium"),
 ],
 move=False, tags=[], safety="Full terms spoken; no urgency; skip line; AI disclosure.", regression="", skip=SK_MOVE_TU,
 caption="Comenta UNIRME y te mando el enlace con todos los términos.\n" + UNIRME + "\n¿Operación reciente, mareo al pararte o dolor fuerte? Pregúntale a tu doctor primero.",
 ig=TAGS_IG, tt=["#mayoresde60", "#donchuyylupe"], yt="Sin Cuenta Regresiva: El Precio, Claro",
 note="Launch UNIRME; T-04 honesty (real cap, live count).", bit=0, wink=False, thumb="EL PRECIO, CLARO", music="bolero instrumental suave"),

dict(id="ES33", title="Una silla, siete mañanas", secs=50, prop="the chair and the printed plan, morning light", obj="silla", launch=True,
 beats=[
  ("0-3","CHUY","Una silla, siete mañanas, ocho minutos: eso trae el primer libro.","1 SILLA · 7 MAÑANAS",f"{PA} | sunrise light on the chair against the wall, the plan on the seat | medium-full"),
  ("3-11","CHUY","Mañana uno: levantarse. Dos: talones. Tres: la mesa. Cuatro: el mandado. Y así hasta el siete.","Mañana 1 a 7","same | quick cuts with support visible | montage"),
  ("11-18","CHUY","Soy Don Chuy, personaje de IA. La silla, el plan y sus piernas son de verdad.","Personaje de IA","same | pats the chair | medium"),
  ("18-30","CHUY",SAY_LIBRO,"{{EBOOK_PRICE}} hoy · cancela en línea","same | price card | medium"),
  ("30-37","CHUY","Todo está escrito en la página antes de pagar. Lo que incluye y cuándo se renueva.","Todo escrito antes de pagar","same | phone screenshot | CU phone"),
  ("37-44","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("44-50","CHUY","Despacio, pero diario. Comente LIBRO y le mando el enlace.","Comente LIBRO","same | sits, coffee in hand | medium"),
 ],
 move=False, tags=[], safety="Offer; skip line; AI disclosure.", regression="", skip=SK_MOVE,
 caption="Comente LIBRO y le mando el enlace por mensaje.\n" + LIBRO + "\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG, tt=["#mayoresde60", "#donchuyylupe"], yt="Una Silla, Siete Mañanas, Ocho Minutos",
 note="Launch LIBRO. Bit 1.", bit=1, wink=False, thumb="1 SILLA · 7 MAÑANAS", music="guitarra cálida instrumental"),

dict(id="ES34", title="El regalo del domingo", secs=48, prop="phone on a stand, video call with Marisol", obj="mamá", launch=True,
 beats=[
  ("0-3","LUPE","Si le hablas a tu mamá cada domingo, este domingo regálale algo que use.","ESTE DOMINGO, UN REGALO",f"{DS} | Marisol on a Sunday video call on the coffee table | two-shot + phone"),
  ("3-10","MARISOL","(videollamada) Mamá, ya les regalé Años Fuertes. ¿Ya lo abrieron?","\"¿Ya lo abrieron?\"","same | Marisol on the phone | CU phone"),
  ("10-18","CHUY","Somos personajes de IA, mija. Pero tu papá ya hizo la prueba de la silla. Doce.","Personajes de IA","same | Chuy shows the calendar mark | medium"),
  ("18-28","LUPE","El regalo: tres meses por cuarenta y nueve dólares, o doce meses por ciento diecinueve. Se paga una vez y nunca se renueva solo.","$49 · $119 · nunca se renueva solo","same | price card | medium"),
  ("28-35","LUPE","Tu papá está bien. Tu papá es presumido. Pero ahora entrena con la silla, no con las cubetas.","Primero la silla","same | Lupe laughs; Marisol laughs | split"),
  ("35-41","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("41-48","LUPE","Comenta FAMILIA y te mando la página del regalo.","Comenta FAMILIA","same | waves to Marisol | two-shot"),
 ],
 move=False, tags=[], safety="Gift terms; no product-result claims; skip line; AI disclosure.", regression="", skip=SK_MOVE,
 caption="Comenta FAMILIA y te mando la página del regalo.\n" + GIFT + "\nDon Chuy y Doña Lupe son personajes de IA. ¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG + ["#regaloparamama"], tt=["#regalo", "#familia", "#donchuyylupe"], yt="Este Domingo, Regálale a Tu Mamá Algo que Use",
 note="Launch FAMILIA. Bit 21 Marisol. The '12' is Chuy's fictional own number, not a product result.", bit=21, wink=False, thumb="ESTE DOMINGO, UN REGALO", music="bolero instrumental suave"),

dict(id="ES35", title="Comida de casa con gramos", secs=50, prop="plate of caldo de pollo with garbanzos and a gram label", obj="recetario", launch=True,
 beats=[
  ("0-3","LUPE","No es recetario de dieta, no es de antojos: es comida de casa con gramos.","COMIDA DE CASA, CON GRAMOS",f"{LK} | Lupe sets down caldo de pollo with a gram label | medium"),
  ("3-10","LUPE","Caldo de pollo con garbanzos: unos treinta gramos de proteína el plato. Frijoles de olla, nopales, avena.","Caldo: unos 30 g","same | gram labels on screen | top-down"),
  ("10-18","LUPE","Soy un personaje de IA. Los gramos salen de la base de datos de la USDA, y te los apunto.","Personaje de IA · gramos USDA","same | flips the book | CU pages"),
  ("18-30","LUPE",SAY_LIBRO_TU,"{{EBOOK_PRICE}} hoy · cancelas en línea","same | price card | medium"),
  ("30-37","LUPE","Lo que incluye y cuándo se renueva, todo está en la página antes de pagar.","Todo escrito antes de pagar","same | phone screenshot | CU phone"),
  ("37-45","LUPE",SK_FOOD,"¿Riñones delicados? Tu doctor primero.","same | CU | CU"),
  ("45-50","LUPE","Comenta LIBRO y te mando el enlace.","Comenta LIBRO","same | serves a bowl | CU"),
 ],
 move=False, tags=[], safety="Offer; kidney/insulin skip line; AI disclosure.", regression="", skip=SK_FOOD,
 caption="Comenta LIBRO y te mando el enlace por mensaje.\n" + LIBRO + "\n¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida.",
 ig=TAGS_K, tt=["#cocinamexicana", "#donchuyylupe"], yt="Comida de Casa con Gramos (El Libro de Doña Lupe)",
 note="Launch LIBRO; E52 USDA grams (verify per recipe).", bit=0, wink=False, thumb="COMIDA DE CASA, CON GRAMOS", music="son jarocho suave instrumental"),

dict(id="ES36", title="Así se cancela", secs=56, prop="phone screen recording of the two-screen cancel flow", obj="cancela", launch=True,
 beats=[
  ("0-3","CHUY","Mire cómo se cancela, antes de que pague un centavo.","ASÍ SE CANCELA",f"{CM} | Chuy at the table, phone in hand, glasses on | medium"),
  ("3-10","CHUY","Soy un personaje de IA, pero esta pantalla es de verdad. Cuenta, membresía, cancelar.","Personaje de IA · pantalla real","same | screen recording: account → membership | CU phone"),
  ("10-17","CHUY","Dos pantallas. En la segunda hay dos botones del mismo tamaño: cambiar de plan, o terminar de cancelar.","2 pantallas · botones iguales","same | screen recording: the two equal buttons | CU phone"),
  ("17-29","CHUY","La Membresía Fundadora es {{FOUNDING_PRICE}} al mes. El primer mes se cobra hoy, se renueva cada mes, y se cancela así, cuando quiera.","{{FOUNDING_PRICE}}/mes · se renueva cada mes","same | price card | medium"),
  ("29-38","CHUY","Garantía de devolución de 14 días en el cobro de la membresía. Y el precio fundador queda bloqueado mientras sigas suscrito, pausas incluidas.","14 días · precio bloqueado","same | terms card | CU card"),
  ("38-44","LUPE","Él le enseñó a cancelar antes de venderle. Siete de diez. Bueno, ocho.","\"Ocho de diez\"","same | Lupe leans in, writes 8 on a card | two-shot"),
  ("44-50","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("50-56","CHUY","Comente UNIRME y le mando el enlace con los términos completos.","Comente UNIRME","same | puts the phone down | medium"),
 ],
 move=False, tags=[], safety="Cancel path shown before purchase; full terms; skip line; AI disclosure.", regression="", skip=SK_MOVE,
 caption="Comente UNIRME y le mando el enlace con los términos completos.\n" + UNIRME + "\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG, tt=["#mayoresde60", "#donchuyylupe"], yt="Así Se Cancela (Antes de Pagar un Centavo)",
 note="Launch UNIRME; cancel flow per CANON UPDATE 3 (equal buttons). Bit 7.", bit=7, wink=False, thumb="ASÍ SE CANCELA", music="guitarra cálida instrumental"),

dict(id="ES37", title="Treinta años de recetas", secs=50, prop="Lupe's notebook with thirty years of stains, the printed book", obj="cuaderno", launch=True,
 beats=[
  ("0-3","CHUY","El cuaderno de Lupe tiene treinta años de recetas. Ahora le toca a usted.","30 AÑOS DE RECETAS",f"{DC} | Chuy opens Lupe's stained notebook; Lupe watches over her glasses | two-shot"),
  ("3-10","LUPE","De la fonda a tu cocina. Con los gramos en rojo, desde que este señor me hizo caso.","Gramos en rojo","same | CU red-pen grams | CU"),
  ("10-17","CHUY","Somos personajes de IA. El cuaderno es de la historia; las recetas y los gramos, de verdad.","Personajes de IA · recetas reales","same | the printed book beside the notebook | CU"),
  ("17-29","LUPE",SAY_LIBRO_TU,"{{EBOOK_PRICE}} hoy · cancelas en línea","same | price card | medium"),
  ("29-36","CHUY","Lo que trae y lo que cobra, Lupe lo dejó por escrito en la página. Léala antes de pagar.","Todo escrito antes de pagar","same | phone screenshot | CU phone"),
  ("36-44","LUPE",SK_FOOD,"¿Riñones delicados? Tu doctor primero.","same | CU | CU"),
  ("44-50","LUPE","Comenta LIBRO y te mando el enlace.","Comenta LIBRO","same | closes the notebook gently | two-shot"),
 ],
 move=False, tags=[], safety="Offer; lore labeled as story; kidney/insulin skip; AI disclosure.", regression="", skip=SK_FOOD,
 caption="Comenta LIBRO y te mando el enlace por mensaje.\n" + LIBRO + "\n¿Usas insulina o pastillas para el azúcar, o tienes los riñones delicados? Pregúntale a tu doctor antes de cambiar tu comida.",
 ig=TAGS_K, tt=["#cocinamexicana", "#donchuyylupe"], yt="Treinta Años de Recetas de Doña Lupe",
 note="Launch LIBRO; lore stated as story. Bit 15.", bit=15, wink=False, thumb="30 AÑOS DE RECETAS", music="son jarocho suave instrumental"),

dict(id="ES38", title="Regalo para mamá", secs=44, prop="gift card in an envelope", obj="regalo", launch=True,
 beats=[
  ("0-3","LUPE","Regalo para mamá: tres meses o un año, y nunca se renueva solo.","REGALO PARA MAMÁ",f"{LS} | Lupe holds an envelope with the gift card | medium"),
  ("3-10","LUPE","Somos personajes de IA. El regalo es de verdad, y tu mamá no tiene que meter ninguna tarjeta.","Personajes de IA · sin tarjeta para ella","same | phone shows the gift redemption page | CU phone"),
  ("10-19","LUPE","Tres meses por cuarenta y nueve dólares, o doce por ciento diecinueve. Pagas una vez. Empieza cuando lo abre.","$49 · $119 · pagas una vez","same | price card | medium"),
  ("19-27","LUPE","Al terminar, se termina. No se renueva solo, no hay sorpresas en su banco.","Termina solo","same | terms card | CU card"),
  ("27-33","LUPE","Ella recibe la rutina de cada mañana, con silla, y mis recetas los domingos.","Rutina · recetas","same | flips to a recipe | CU"),
  ("33-38","LUPE",SK_MOVE_TU,"¿Operación reciente? Su doctor primero.","same | CU | CU"),
  ("38-44","LUPE","Comenta FAMILIA y te mando la página del regalo.","Comenta FAMILIA","same | seals the envelope | CU"),
 ],
 move=False, tags=[], safety="Gift terms; skip line; AI disclosure.", regression="", skip=SK_MOVE_TU,
 caption="Comenta FAMILIA y te mando la página del regalo.\n" + GIFT + "\n¿Operación reciente, mareo al pararte o dolor fuerte? Pregúntale a tu doctor primero.",
 ig=TAGS_IG + ["#regaloparamama"], tt=["#regalo", "#mama", "#donchuyylupe"], yt="Regalo para Mamá: Nunca Se Renueva Solo",
 note="Launch FAMILIA.", bit=0, wink=False, thumb="NUNCA SE RENUEVA SOLO", music="bolero instrumental suave"),

dict(id="ES39", title="Si usa las manos, empiece aquí", secs=54, prop="chair against the wall, the printed plan open to day 1", obj="manos", launch=True, demo=True,
 beats=[
  ("0-3","CHUY","Si cada vez que se para de la silla usa las manos, empiece aquí.","¿USA LAS MANOS? EMPIECE AQUÍ",f"{PA} | Chuy stands from the chair pushing on his knees, on purpose | side full body"),
  ("3-11","CHUY","Así empecé yo, en la historia: con las dos manos. Día uno del plan: manos en las rodillas, cinco veces, sacando el aire.","Día 1: manos en las rodillas","same | demo of day 1 | side full body"),
  ("11-18","CHUY","Soy un personaje de IA. Pero levantarse del piso y de la silla se puede practicar a cualquier edad; hay estudios.","Personaje de IA · se practica","same | study card inset (floor-rise training) | medium"),
  ("18-30","CHUY",SAY_LIBRO,"{{EBOOK_PRICE}} hoy · cancela en línea","same | price card | medium"),
  ("30-37","CHUY","Antes de pagar, la página le enseña cada término, y ninguna casilla viene marcada.","Todo escrito antes de pagar","same | phone screenshot | CU phone"),
  ("37-43","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("43-54","CHUY","Donde empezamos, no donde nos quedamos. Comente LIBRO y le mando el enlace.","Comente LIBRO","same | stands without hands, slowly, sits again | full body"),
 ],
 move=True, tags=["sit_to_stand"], safety="Hands-on-knees start; chair against the wall; dizziness skip; AI disclosure; lore labeled as story.",
 regression="Manos en las rodillas, cinco veces.", skip=SK_MOVE,
 caption="Comente LIBRO y le mando el enlace por mensaje.\n" + LIBRO + "\n¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG, tt=["#mayoresde60", "#donchuyylupe"], yt="¿Usa las Manos para Pararse? Empiece Aquí",
 note="Launch LIBRO; E45/E01; lore labeled 'en la historia'.", bit=0, wink=False, thumb="EMPIECE AQUÍ", music="guitarra cálida instrumental"),

dict(id="ES40", title="Los libros son de verdad", secs=52, prop="both printed books on the patio chair", obj="libros", launch=True,
 beats=[
  ("0-3","LUPE","Somos de inteligencia artificial. Los libros son de verdad. Mire lo que trae.","LOS LIBROS SON DE VERDAD",f"{DP} | both books on the chair against the wall; Lupe holds one up | two-shot"),
  ("3-10","CHUY","Yo no envejezco, me renderizan. Usted sí tiene que entrenar. Siete mañanas, una silla.","\"Me renderizan\"","same | Chuy flips 'Fuerza en 7 Días' | CU pages"),
  ("10-17","LUPE","Y mis recetas, cada una con su proteína y su fibra apuntadas, y quién se las debe saltar.","Recetas con gramos","same | Lupe flips 'La Cocina Fuerte' | CU pages"),
  ("17-29","CHUY",SAY_LIBRO,"{{EBOOK_PRICE}} hoy · cancela en línea","same | price card | medium"),
  ("29-36","LUPE","Lo que incluye y cuándo se renueva, todo en la página antes de pagar. Léela completa.","Todo escrito antes de pagar","same | phone screenshot | CU phone"),
  ("36-42","CHUY",SK_MOVE,"¿Mareo al pararse? Su médico primero.","same | CU | CU"),
  ("42-52","LUPE","Tú ni rodillas tienes, Jesús. Comenta LIBRO y te mandamos el enlace.","Comenta LIBRO","same | Chuy: 'Unas rodillas preciosas. En 4K.' (mouthed) | two-shot"),
 ],
 move=False, tags=[], safety="Offer; AI wink; skip line.", regression="", skip=SK_MOVE,
 caption="Comenta LIBRO y te mandamos el enlace por mensaje.\n" + LIBRO + "\nDon Chuy y Doña Lupe son personajes de IA. ¿Operación reciente, mareo al pararse o dolor fuerte? Pregúntele a su médico primero.",
 ig=TAGS_IG, tt=["#mayoresde60", "#donchuyylupe"], yt="Somos IA. Los Libros Son de Verdad.",
 note="Launch LIBRO; wink 2. Bit 17.", bit=17, wink=True, thumb="LOS LIBROS SON DE VERDAD", music="cumbia lenta instrumental"),
]
