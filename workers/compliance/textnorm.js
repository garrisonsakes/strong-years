// AUDIT H10 BEGIN — claims-scanner normalisation, JS mirror of workers/compliance/textnorm.py.
// Generated into the n8n Code nodes by tools/patch_workflow.py; the tables come from textnorm_data.json (TN).
const TN_INV = new RegExp('[' + TN.invisible_class + ']', 'g');
const tnEsc = (s) => s.replace(/[.*+?^${}()|[\]\\\/-]/g, '\\$&');
// separators: ANY non-letter/non-digit character (same as Python's (?:[^\w]|_))
const TN_SPACED = /(?<![A-Za-z])(?:[A-Za-z][^\p{L}\p{N}]{1,3}){2,}[A-Za-z](?![A-Za-z])/gu;
const TN_INNER = /(?<=[A-Za-z])(?:(?![\s'\-])[^\p{L}\p{N}]|_)(?=[A-Za-z])/gu;
const TN_HEALTH = new RegExp('\\b(' + TN.health_words + ')\\b', 'i');
const TN_BENIGN = TN.benign.map((b) => [b.family, new RegExp(b.rx, 'i')]);
const TN_STEMS = TN.stems, TN_JOIN = new Set(TN.join_stems);
const TN_NUMERIC = /^[\d.,:%\/+-]+[A-Za-z]{0,3}$/, TN_EID = /^[Ee]\d{2}b?$/;
const tnConf = (t) => Array.from(t).map((ch) => (ch in TN.confusables ? TN.confusables[ch] : ch)).join('');
const tnCanon = (t) => tnConf(String(t || '').normalize('NFKC').replace(TN_INV, '')).replace(/(?<=[A-Za-z])[̀-ͯ]+/g, '');
const TN_UNIT = new RegExp(TN.unit_token_rx || '^\\d', 'u');
const tnSym = (t) => t.replace(/\S+/g, (tok) => { const core = tok.replace(/^[.,;:!?"'()\[\]]+|[.,;:!?"'()\[\]]+$/g, '');
  if (!/[A-Za-z]/.test(tok) || TN_UNIT.test(core)) return tok;
  return Array.from(tok).map((ch) => ((TN.symbol_letters || {})[ch] ?? ch)).join(''); });
const tnFold = (t) => tnConf(tnSym(t).normalize('NFKD').replace(/\p{M}/gu, ''));
const tnCollapse = (t) => t.replace(TN_SPACED, (m) => m.replace(/[^A-Za-z]/g, '')).replace(TN_INNER, '');
const tnDehyphen = (t) => t.replace(/(?<=[A-Za-z])-(?=[A-Za-z])/g, '');
const tnSquash = (t, n) => t.replace(new RegExp('([A-Za-z])\\1{' + (n - 1) + ',}', 'g'), '$1');
const tnSplit = (tok) => { const m = tok.match(/^(["'(\[]*)(.*?)((?:['\u2019](?:s|re|ll|ve|d|m))?[.,;:!?"')\]]*)$/s); return [m[1], m[2], m[3]]; };
const tnMask = (core) => {
  if (!/[A-Za-z]/.test(core) || !Array.from(core).some((ch) => TN.mask_chars.includes(ch)) || TN_EID.test(core)) return null;
  if (core.replace(/[^A-Za-z]/g, '').length < 2 || TN_NUMERIC.test(core)) return null;
  const rx = new RegExp('^' + Array.from(core).map((ch) => (TN.mask_chars.includes(ch) ? '[a-z]' : tnEsc(ch.toLowerCase()))).join('') + '$');
  for (const s of TN_STEMS) if (s.length === Array.from(core).length && rx.test(s)) return s;
  return null;
};
const tnUnmask = (t) => t.replace(/\S+/g, (tok) => { const [a, c, b] = tnSplit(tok); const s = tnMask(c); return s ? a + s + b : tok; });
const tnSquashStems = (t) => t.replace(/\S+/g, (tok) => { const [a, c, b] = tnSplit(tok); const q = tnSquash(c, 2);
  return q !== c && TN_STEMS.includes(q.toLowerCase()) ? a + q.toLowerCase() + b : tok; });
const tnJoin = (t) => {
  const toks = t.split(/(\s+|[—–-]+)/);
  const words = toks.map((x, i) => [i, x]).filter(([, x]) => x && !/^(\s+|[—–-]+)$/.test(x));
  for (let a = 0; a < words.length; a++) for (const b of [a + 1, a + 2]) {
    if (b >= words.length) break;
    const parts = []; for (let k = a; k <= b; k++) parts.push(words[k][1].replace(/[^A-Za-z]/g, ''));
    const j = parts.join('').toLowerCase();
    if (TN_JOIN.has(j) && parts.every(Boolean) && Math.max(...parts.map((p) => p.length)) < j.length) {
      const i0 = words[a][0], i1 = words[b][0];
      toks.splice(i0, i1 - i0 + 1, j, ...Array(i1 - i0).fill(''));
      return tnJoin(toks.join(''));
    }
  }
  return t;
};
const TN_EXCL = new Set(TN.fuzzy_exclude || []);
const TN_FUZZY = [...new Set([...TN_STEMS, ...(TN.fuzzy_extra_stems || [])])].filter((x) => x.length >= (TN.fuzzy_min_len || 5));
const tnSpeak = (t) => t.replace(/\S+/g, (tok) => { const [a, c, b] = tnSplit(tok); const r = (TN.textspeak || {})[c.toLowerCase()]; return r ? a + r + b : tok; });
const tnLev1 = (a, b) => {
  if (a === b) return true;
  let la = a.length, lb = b.length;
  if (Math.abs(la - lb) > 1) return false;
  if (la === lb) {
    const diff = []; for (let i = 0; i < la; i++) if (a[i] !== b[i]) diff.push(i);
    if (diff.length === 2 && diff[1] === diff[0] + 1 && a[diff[0]] === b[diff[1]] && a[diff[1]] === b[diff[0]]) return true;
    return diff.length === 1;
  }
  if (la > lb) { [a, b] = [b, a]; [la, lb] = [lb, la]; }
  let i = 0; while (i < la && a[i] === b[i]) i++;
  return a.slice(i) === b.slice(i + 1);
};
const tnFuzzyStem = (tok) => {
  const t = tok.toLowerCase();
  if (t.length < (TN.fuzzy_min_len || 5) || !/^[a-z]+$/.test(t) || TN_EXCL.has(t) || TN_STEMS.includes(t)) return null;
  for (const st of TN_FUZZY) if (tnLev1(t, st)) return st;
  return null;
};
const tnFuzzy = (t) => t.replace(/\S+/g, (tok) => { const [a, c, b] = tnSplit(tok); const f = tnFuzzyStem(c); return f ? a + f + b : tok; });
const tnMulti = (t) => t.replace(/\S+/g, (tok) => { if (!/[A-Za-z]/.test(tok)) return tok;
  for (const [seq, r] of (TN.multichar || [])) tok = tok.split(seq).join(r); return tok; });
const tnLeet = (t, one) => t.replace(/\S+/g, (tok) => {
  if (!/[A-Za-z]/.test(tok) || !/[0-9@$!|€+(<]/.test(tok) || TN_EID.test(tok)) return tok;
  const [a, c, b] = tnSplit(tok); if (TN_NUMERIC.test(c)) return tok;
  return a + Array.from(c).map((ch) => (ch === '1' ? one : (TN.leet[ch] || ch))).join('') + b; });
const tnMc = (c) => { const mc = tnMulti(tnFold(c)), mk = tnCollapse(tnUnmask(mc));
  return [mc, mk, tnLeet(mk, 'i'), tnLeet(mk, 'l'), tnFuzzy(tnLeet(mk, 'i')), tnFuzzy(tnLeet(mk, 'l'))]; };
const normVariants = (text) => {
  const c = tnCanon(text), f = tnUnmask(tnFold(c)), k = tnCollapse(f), d = tnDehyphen(k), u = tnUnmask(d), j = tnJoin(u);
  const s3 = tnSquash(j, 3), s2 = tnSquashStems(s3), ts = tnSpeak(s2), z = tnFuzzy(ts);
  return [...new Set([c, f, k, d, u, j, s3, s2, tnLeet(d, 'i'), tnLeet(d, 'l'), tnLeet(j, 'i'), tnLeet(j, 'l'),
    tnUnmask(tnLeet(k, 'i')), tnUnmask(k), tnJoin(tnLeet(u, 'i')), tnSquashStems(tnSquash(tnLeet(j, 'i'), 3)),
    ts, z, tnFuzzy(tnLeet(ts, 'i')), tnFuzzy(tnLeet(ts, 'l')), ...tnMc(c)])];
};
const tnFamily = (term) => { const t = term.toLowerCase(); for (const [fam, stem] of Object.entries(TN.family_of_rule_terms)) if (t.includes(stem)) return fam; return null; };
const tnSentence = (text, idx) => { let a = 0; for (const s of text.split(/(?<=[.!?])\s+|\n+/)) { const i = text.indexOf(s, a); if (i <= idx && idx < i + s.length + 1) return s; a = i + s.length; } return text; };
const tnBenign = (match, sentence) => { const fam = tnFamily(match); if (!fam || TN_HEALTH.test(sentence)) return false;
  return TN_BENIGN.some(([f, rx]) => f === fam && rx.test(sentence)); };
// First non-benign match over every variant; a variant hit whose words are already visible in the canonical text is
// left to the canonical pass (its context rules, e.g. "money-back guarantee", already decided it).
const matchAny = (re, text) => {
  const vs = normVariants(text), base = vs[0].toLowerCase();
  const g = new RegExp(re.source, re.flags.includes('g') ? re.flags : re.flags + 'g');
  for (let vi = 0; vi < vs.length; vi++) for (const m of vs[vi].matchAll(g)) {
    if (!m[0].trim()) continue;
    if (vi && base.includes(m[0].toLowerCase())) continue;
    if (tnBenign(m[0], tnSentence(vs[vi], m.index))) continue;
    return m;
  }
  return null;
};
// AUDIT H10 END
