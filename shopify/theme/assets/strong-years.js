/* Strong Years storefront behaviour.
   1. Attribution: utm_*, post_id (alias pid), page, keyword, character, platform, mc_id → first touch + last touch,
      persisted to cart attributes → order note_attributes → members-app webhook (app/src/lib/billing/shopify.ts
      cartContextFromAttributes). Attribute names and limits match that reader exactly: flat "sy_" keys,
      values <= 100 characters: sy_ft_<field>, sy_ft_at, sy_lt_<field>, sy_lt_at, sy_cell, sy_vid, sy_sku.
   2. Cell/arm stickiness (assigned before paint in layout/theme.liquid) → sy_cell (e7 | e12 | e15 | m12).
   3. Offer forms: explicit auto-renewal consent (unticked, required), recorded as sy_consent_sha (SHA-256 of the exact
      terms text + checkbox label shown), sy_consent_at, sy_consent_price; then buy-now: clear cart → add →
      (cell B in the Shopify Subscriptions engine: /discount/STARTER12) → /checkout.
   4. Renewal dates in the buyer's local time.
   No third-party calls. Works without JS (native forms + required checkbox). */
(function () {
  'use strict';
  var FIELDS = ['platform', 'page', 'post_id', 'keyword', 'character', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term', 'mc_id'];
  var ALIASES = { pid: 'post_id', kw: 'keyword', char: 'character' };
  var MAX = 100;
  var CONFIG = {};
  try { CONFIG = JSON.parse(document.getElementById('sy-config').textContent) || {}; } catch (e) {}

  function store(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function read(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
  function cookie(k) { var m = document.cookie.match('(?:^|; )' + k + '=([^;]*)'); return m ? decodeURIComponent(m[1]) : null; }
  function parse(s) { try { return JSON.parse(s) || null; } catch (e) { return null; } }
  function clip(v) { return String(v).replace(/[\u0000-\u001f]/g, '').slice(0, MAX); }

  /* ---------- 1. attribution ---------- */
  function captureAttribution() {
    var q = new URLSearchParams(location.search), touch = {}, any = false;
    q.forEach(function (v, k) {
      var key = ALIASES[k] || k;
      if (FIELDS.indexOf(key) !== -1 && v) { touch[key] = clip(v); any = true; }
    });
    if (!any) return false;
    touch.at = new Date().toISOString();
    if (!read('sy_ft')) store('sy_ft', JSON.stringify(touch));
    store('sy_lt', JSON.stringify(touch));
    return true;
  }
  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    var b = new Uint8Array(16); crypto.getRandomValues(b); b[6] = (b[6] & 15) | 64; b[8] = (b[8] & 63) | 128;
    var h = Array.from(b, function (x) { return x.toString(16).padStart(2, '0'); }).join('');
    return h.slice(0, 8) + '-' + h.slice(8, 12) + '-' + h.slice(12, 16) + '-' + h.slice(16, 20) + '-' + h.slice(20);
  }
  function visitorId() { var v = read('sy_vid'); if (!v) { v = uuid(); store('sy_vid', v); } return v; }
  function cartAttributes(extra) {
    var a = { sy_vid: visitorId(), sy_cell: clip(read('sy_cell') || cookie('sy_cell') || ''), sy_arm: clip(read('sy_arm') || cookie('sy_arm') || '') };
    var ft = parse(read('sy_ft')), lt = parse(read('sy_lt'));
    FIELDS.forEach(function (f) {
      if (ft && ft[f]) a['sy_ft_' + f] = clip(ft[f]);
      if (lt && lt[f]) a['sy_lt_' + f] = clip(lt[f]);
    });
    if (ft && ft.at) a.sy_ft_at = clip(ft.at);
    if (lt && lt.at) a.sy_lt_at = clip(lt.at);
    for (var k in (extra || {})) a[k] = clip(extra[k]);
    return a;
  }
  function syncAttributes(extra) {
    return fetch('/cart/update.js', {
      method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ attributes: cartAttributes(extra) })
    });
  }
  var changed = captureAttribution();
  var sig = [read('sy_lt'), read('sy_cell'), read('sy_arm')].join('|');
  if (changed || read('sy_synced') !== sig) { syncAttributes().then(function () { store('sy_synced', sig); }).catch(function () {}); }

  /* ---------- 2. landing links follow the visitor's ebook cell ---------- */
  var cells = (CONFIG.cells && CONFIG.cells.ebook) || [];
  var myCell = read('sy_ebook_cell') || cookie('sy_ebook_cell');
  cells.forEach(function (c) {
    if (c.id !== myCell) return;
    document.querySelectorAll('a[data-sy-ebook-link]').forEach(function (a) { a.setAttribute('href', '/products/' + c.handle); });
  });

  /* ---------- 3. renewal dates ---------- */
  function addMonths(d, n) { var x = new Date(d.getFullYear(), d.getMonth() + n, d.getDate()); if (x.getDate() !== d.getDate()) x.setDate(0); return x; }
  var now = new Date();
  document.querySelectorAll('[data-sy-renew]').forEach(function (el) {
    var months = parseInt(el.getAttribute('data-sy-renew'), 10) || 1;
    el.textContent = addMonths(now, months).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  });

  /* ---------- 4. offer forms ---------- */
  async function sha256(text) {
    if (!(window.crypto && crypto.subtle)) return '';
    var buf = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(text));
    return Array.from(new Uint8Array(buf)).map(function (b) { return b.toString(16).padStart(2, '0'); }).join('');
  }
  function textOf(sel, root) { var el = root.querySelector(sel); return el ? el.innerText.replace(/\s+/g, ' ').trim() : ''; }
  /* sy_consent_price records what the page showed. A starter page (first-payment code) shows BOTH prices, "12|25":
     the code price and the plan price the checkout charges a returning customer; the members app compares the
     charged line with this record on orders/paid (R5-8). */
  async function consentAttrs(root, price) {
    var text = textOf('[data-sy-terms]', root) + ' | ' + textOf('[data-sy-consent-label]', root);
    var full = root.getAttribute && root.getAttribute('data-sy-full-price');
    var shown = full && full !== price ? price + '|' + full : (price || '');
    return { sy_consent_sha: await sha256(text), sy_consent_at: new Date().toISOString(), sy_consent_price: shown, sy_consent_v: '2' };
  }
  function showError(err, msg) { if (err) { err.textContent = msg; err.hidden = false; } }

  document.querySelectorAll('form[data-sy-offer]').forEach(function (form) {
    var consent = form.querySelector('input[name="sy_consent"]');
    var err = form.querySelector('[data-sy-error]');
    form.addEventListener('submit', async function (ev) {
      ev.preventDefault();
      if (err) err.hidden = true;
      if (consent && !consent.checked) {
        showError(err, 'Please tick the box above to confirm the membership terms.');
        consent.focus(); consent.scrollIntoView({ block: 'center' });
        return;
      }
      var required = form.querySelectorAll('[data-sy-required]');
      for (var i = 0; i < required.length; i++) {
        if (!required[i].value.trim()) { showError(err, required[i].getAttribute('data-sy-required')); required[i].focus(); return; }
      }
      var btn = form.querySelector('button[type="submit"]');
      if (btn) { btn.setAttribute('aria-busy', 'true'); btn.disabled = true; }
      try {
        var chosen = form.querySelector('input[name="id"]:checked') || form.querySelector('[name="id"]');
        var main = { id: Number(chosen.value), quantity: 1 };
        var plan = form.querySelector('[name="selling_plan"]');
        if (plan && plan.value) main.selling_plan = Number(plan.value);
        var props = {};
        form.querySelectorAll('[name^="properties["]').forEach(function (p) { if (p.value) props[p.name.slice(11, -1)] = p.value; });
        if (Object.keys(props).length) main.properties = props;
        var items = [main];
        form.querySelectorAll('input[name="sy_bump"]:checked').forEach(function (b) { items.push({ id: Number(b.value), quantity: 1 }); });
        /* R5-11: a membership is one seat per contract; quantity is always 1 (the cart page has no quantity control either). */
        items.forEach(function (it) { it.quantity = 1; });

        var extra = { sy_entry: form.getAttribute('data-sy-offer') || '', sy_sku: chosen.getAttribute('data-sy-sku') || form.getAttribute('data-sy-sku') || '' };
        if (consent) Object.assign(extra, await consentAttrs(form, form.getAttribute('data-sy-price')));

        await fetch('/cart/clear.js', { method: 'POST', headers: { Accept: 'application/json' } });
        var add = await fetch('/cart/add.js', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify({ items: items }) });
        if (!add.ok) {
          var body = await add.json().catch(function () { return {}; });
          throw new Error(body.description || 'That could not be added. Please try again.');
        }
        await syncAttributes(extra);
        var code = form.getAttribute('data-sy-discount');
        location.href = code ? '/discount/' + encodeURIComponent(code) + '?redirect=%2Fcheckout' : '/checkout';
      } catch (e) {
        showError(err, (e && e.message) || 'Something went wrong. Please try again.');
        if (btn) { btn.removeAttribute('aria-busy'); btn.disabled = false; }
      }
    });
  });

  /* Cart page: a subscription line needs the consent tick before checkout. */
  var cartForm = document.querySelector('form[data-sy-cart]');
  if (cartForm) {
    cartForm.addEventListener('submit', async function (ev) {
      var c = cartForm.querySelector('input[name="sy_consent"]');
      if (!c) return;
      ev.preventDefault();
      if (!c.checked) { showError(cartForm.querySelector('[data-sy-error]'), 'Please tick the box above to confirm the membership terms.'); c.focus(); return; }
      /* R5-11: force every subscription line back to quantity 1 before checkout. */
      try {
        var cart = await (await fetch('/cart.js', { headers: { Accept: 'application/json' } })).json();
        for (var i = 0; i < (cart.items || []).length; i++) {
          var li = cart.items[i];
          if (li.selling_plan_allocation && li.quantity > 1) await fetch('/cart/change.js', { method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify({ id: li.key, quantity: 1 }) });
        }
      } catch (e) {}
      await syncAttributes(Object.assign({ sy_entry: 'cart' }, await consentAttrs(cartForm, cartForm.getAttribute('data-sy-price')))).catch(function () {});
      location.href = '/checkout';
    });
  }
})();
