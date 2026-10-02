# OFFER_ES.md: Años Fuertes (Spanish) on Shopify Markets, handles, legal copy and onboarding emails

**Scope.** The Spanish storefront, offer copy and first emails for @donchuyylupe (CHARACTERS_ES.md). **Same USD prices and the same cells as the US** (OFFER.md §0, BRIEF.md CANON UPDATE 2/3): launch default cell B "$12 hoy = los dos libros + tu primer mes, luego $25 al mes" (founding plan + STARTER12 first-payment code; STARTER12S on the $35 standard plan after the founding close), test cell A = the books alone at `{{EBOOK_PRICE}}`, founding $25/mo locked while subscribed, honest 5,000 cap shared across languages, $35 standard after the cap, gifts $49 / $119 never auto-renew, 14-day money-back once per person, Essentials $12 save offer. **Opens at the $30K retained-MRR rung** (CANON UPDATE 5); nothing here is built, bought or published before the governor flips it. No accounts were created and nothing was posted in this round.

> **LEGAL COPY FLAG (applies to §3 and §4, every block marked ⚖):** drafted by the content team, **not legal advice and not a certified translation.** Before publishing: (1) a US consumer-protection attorney reviews the Spanish price displays, checkout consent, renewal reminder and cancellation text against ROSCA and the state automatic-renewal laws for the states we sell into, and confirms whether California Civil Code §1632 (translations of certain contracts negotiated primarily in Spanish) applies to a Spanish-language subscription checkout [CHARACTERS_ES R16]; (2) a certified Spanish translator signs a line-by-line equivalence check against the English terms in OFFER.md and the live `/terms` page. Until both sign-offs are logged, the Spanish pages link to the English terms with a Spanish summary marked "Resumen; los términos oficiales están en inglés."

---

## 1. Handles (reserve when the rung opens; availability NOT checked in this round)

| Surface | Primary | Fallbacks (in order) | Notes |
|---|---|---|---|
| Instagram / Facebook / Threads | **@donchuyylupe** | @donchuy.y.lupe · @donchuyfuerte (EXPANSION.md §5 name) · @chuyylupe.fuertes | Bio = CHARACTERS_ES.md §9.1 bio string; IG "AI info" label on; FB page category "Digital creator" |
| TikTok | **@donchuyylupe** | @donchuy.y.lupe · @donchuyfuerte | TikTok AI-generated content label on every post |
| YouTube | **@DonChuyyLupe** | @DonChuyYDonaLupe · @DonChuyFuerte | Channel description carries the AI disclosure; "altered or synthetic content" toggle on |
| X | **@donchuyylupe** | @donchuy_y_lupe | |
| WhatsApp Channel | **Don Chuy y Doña Lupe** | — | Free channel, top-of-funnel only (never paid templates for daily content; EXPANSION.md §5.7) |
| Staged (Doña Carmen) | @donacarmen.fuerte | @lasdedonacarmen | Only if her page opens (CHARACTERS_ES.md §0) |

Account creation, verification and recovery follow ACCOUNT_SETUP.md; handles are reserved by a person, never by automation.

---

## 2. Shopify Markets setup (same store, same products' prices, Spanish language)

Shopify lets a store add Spanish under Settings → Languages, assign it per market under Markets → Languages and domains, translates checkout automatically (Spanish is pre-translated), keeps currency separate from language, and needs app content translated separately [CHARACTERS_ES R14, R15].

1. **Market:** keep the **United States** market (USD). Add **Español (es)** as a language on it and publish it on the `/es` subfolder of the store domain. No new currency, no new price list: one US price across languages (AUDIT F34).
2. **Products (separate Spanish products, identical prices):** `libros-de-inicio-es` (PDF bundle "Fuerza en 7 Días" + "La Cocina Fuerte", Spanish files) and the founding membership variant on the **same** selling plan as the English one (shared 5,000-cap inventory). Separate products, not a language toggle on the English product, so the members app delivers the right watermarked PDFs and attribution splits by language. Prices: same as the US product in every cell.
3. **Discounts:** STARTER12 / STARTER12S apply to the Spanish founding / standard variants unchanged (first payment only, once per customer).
4. **Translations:** product titles, descriptions, policies and the offer form via Translate & Adapt, then the certified translator's pass (⚖). Shopify Subscriptions customer-facing text: check the app's Spanish coverage; anything untranslated is replaced by our own copy on the product page and in the members app.
5. **Members app:** `members.<domain>/es` uses the same webhooks (`orders/paid`, renewals, refunds, `customers/*`); the language comes from the order's `customer_locale` and decides the PDF files, the email language and the app UI.
6. **`/b` redirect:** keyword `LIBRO`/`UNIRME`/`FAMILIA` with `lang=es` → the `/es` product page; cell assignment unchanged (signed visitor cookie). Before the Spanish checkout opens (the page's own runway), `/b?lang=es` sends to `/es/lista`.

---

## 3. Años Fuertes offer copy (product pages)

### 3.1 Cell B (launch default) ⚖
**Título:** Años Fuertes: los libros de inicio + tu primer mes
**Precio grande:** **$12 hoy** · luego **$25 al mes**
**Bajo el precio (misma talla de letra que el texto, alto contraste, nada en gris):**
> Hoy pagas $12 y recibes los dos libros (PDF en español, tuyos para quedártelos) y tu primer mes de la Membresía Fundadora de Años Fuertes. Tu primer cobro de $25 será el **{{FIRST_RENEWAL_DATE}}**, y después se renueva cada mes al mismo precio hasta que canceles. Cancela en línea cuando quieras, en máximo dos pantallas. Te mandamos un correo antes del primer cobro de $25. Garantía de devolución de 14 días en el cobro de la membresía, una vez por persona. Tu precio fundador queda bloqueado mientras sigas suscrito, pausas incluidas. Abierta a los primeros 5,000 miembros fundadores (conteo en vivo: {{COUNT_LINE}}).

**Casilla de consentimiento (sin marcar):** ☐ Acepto que Años Fuertes me cobre $25 cada mes a partir del {{FIRST_RENEWAL_DATE}} hasta que cancele. Puedo cancelar en línea cuando quiera.
**Botón (texto oscuro sobre fondo claro o blanco sobre color fuerte; nunca gris):** Pagar $12 hoy

### 3.2 Cell A (test: books only) ⚖
**Título:** Los libros de inicio de Años Fuertes
**Precio:** **{{EBOOK_PRICE}}, un solo pago.** No es suscripción. Los libros son tuyos para quedártelos.
**Botón:** Comprar los libros

### 3.3 Membership only (UNIRME) ⚖
**Título:** Membresía Fundadora de Años Fuertes
**Precio:** **$25 al mes.** El primer mes se cobra hoy; se renueva cada mes al mismo precio hasta que canceles.
Same terms block as 3.1 (cancel, reminder, 14-day money-back, "bloqueado mientras sigas suscrito", cap) + the unticked consent box.

### 3.4 What's inside (value stack; access, not outcomes)
- **La rutina del día:** una sesión nueva cada mañana con Don Chuy, de 8 a 12 minutos, con versión de silla para todo.
- **La Cocina Fuerte:** las recetas de Doña Lupe cada domingo, con gramos de proteína y fibra y la cajita de "quién debe saltarse esto".
- **Las pruebas del mes:** la silla, un pie y el piso, para que apuntes tus números.
- **Plan familiar:** un perfil más para tu mamá o tu papá, en la misma cuenta.
- **Personajes de IA, información general, no consejo médico.** Las fuentes de cada número están en {{DOMAIN}}/es/fuentes.

### 3.5 Gift (FAMILIA) ⚖
**Regálale fuerza a tu mamá.** 3 meses **$49** o 12 meses **$119**, pagados una vez por quien regala. Empieza el día que lo abren, termina a los 3 o 12 meses y **nunca se renueva solo**. Tu mamá no tiene que poner ninguna tarjeta.

### 3.6 Cancel page (Spanish) ⚖
Two equal-size buttons (CANON UPDATE 3): **[Cambiar a Esenciales, $12 al mes]** and **[Terminar de cancelar]** (the latter goes to Shopify's cancel page). Essentials requests are applied by a person within 1 business day. No guilt copy, no extra screens.

### 3.7 Words we never use on these pages
"de por vida", "para siempre" (price), "garantía" outside "garantía de devolución de 14 días", "últimos lugares", "termina hoy", "precio especial solo por hoy", any health result ("más fuerte en 7 días", "adiós al dolor"), and condition names. Enforced for scripts by tools/build_content_es.py and prompts/blocked_claims.json BC26–BC37; landing copy runs through the same scanner before publish.

---

## 4. Three Spanish onboarding emails (cell A books-only buyers; the founding offer lives on the thank-you page and here, CANON UPDATE 3) ⚖

Sender: "Don Chuy y Doña Lupe (Años Fuertes)". Every email: 18–20 px body, black on white, buttons white-on-deep-color, no gray text; footer = AI disclosure + "Información general, no consejo médico" + one-click unsubscribe + postal address. Members (cell B buyers) get the member welcome series instead.

**Email 1 (minute 0) · Asunto:** Tus libros ya están aquí (y la silla, contra la pared)
> Hola {nombre}:
>
> Aquí están tus libros, en español y tuyos para quedártelos: **[Descargar "Fuerza en 7 Días"]** **[Descargar "La Cocina Fuerte"]**
>
> Empieza por la página 3: el día uno son ocho minutos y una silla contra la pared. Si necesitas las manos, úsalas. Ahí empezamos, no ahí nos quedamos.
>
> Soy Don Chuy, un personaje de inteligencia artificial. La silla sí es de verdad.
>
> **Si quieres seguir con nosotros todos los días:** la Membresía Fundadora de Años Fuertes es $25 al mes. El primer mes se cobra el día que te unes y se renueva cada mes al mismo precio hasta que canceles. Cancela en línea cuando quieras, en máximo dos pantallas. Garantía de devolución de 14 días en el cobro de la membresía, una vez por persona. Tu precio fundador queda bloqueado mientras sigas suscrito, pausas incluidas. Abierta a los primeros 5,000 miembros fundadores ({{COUNT_LINE}}). **[Ver la membresía y los términos]**
>
> ¿Operación reciente, mareo al pararte o dolor fuerte? Pregúntale a tu doctor primero.
>
> Despacio, pero diario.
> Don Chuy (y Lupe, que revisó este correo)

**Email 2 (day 2) · Asunto:** Lo que desayuna Lupe (con los gramos)
> {nombre}, aquí Lupe.
>
> Dos huevos y una taza de frijoles de olla: casi 25 gramos de proteína. Está en la página 14 de tu libro, con la cajita de quién debe saltárselo. Si usas insulina o pastillas para el azúcar, o tienes los riñones delicados, pregúntale a tu doctor antes de cambiar tu comida.
>
> Somos personajes de IA, mija. Las recetas son de casa.
>
> En la membresía mando una receta nueva cada domingo y Chuy una sesión cada mañana. $25 al mes, se renueva cada mes hasta que canceles, cancelas en línea cuando quieras, garantía de devolución de 14 días en el cobro de la membresía (una vez por persona), y el precio fundador queda bloqueado mientras sigas suscrito. **[Ver la membresía]**
>
> Gramos, no cuentos.
> Lupe

**Email 3 (day 5; the last offer email) · Asunto:** El último correo de la oferta (te lo digo claro)
> {nombre}:
>
> Este es el último correo sobre la membresía. No hay cuenta regresiva y el precio no cambia a medianoche.
>
> Lo que es: una sesión cada mañana con Don Chuy, recetas de Lupe los domingos, las pruebas del mes, y un perfil más para tu mamá o tu papá. Lo que cuesta: $25 al mes, el primer mes se cobra el día que te unes, se renueva cada mes hasta que canceles. Cómo se cancela: en línea, en dos pantallas, cuando quieras. Garantía de devolución de 14 días en el cobro de la membresía, una vez por persona. Precio fundador bloqueado mientras sigas suscrito, pausas incluidas. Abierta a los primeros 5,000 miembros fundadores ({{COUNT_LINE}}).
>
> Si no es para ti, quédate con los libros. Son tuyos.
>
> **[Unirme a Años Fuertes]**
>
> Somos personajes de inteligencia artificial; el equipo detrás es real y lee tus respuestas.
> Don Chuy y Doña Lupe

---

## 5. Open items (for the client)
1. Attorney + certified translator sign-off (⚖ blocks) and the CA §1632 answer.
2. Handle reservation by a person when the $30K rung opens.
3. Spanish PDFs of both books (native writing, not translation), USDA gram values re-checked per recipe (E52).
4. Shopify Subscriptions Spanish coverage check on a dev store.
5. Spanish support macros (EXPANSION.md §3.2) and a Spanish-speaking human in the inbox before any LIBRO/UNIRME post.
