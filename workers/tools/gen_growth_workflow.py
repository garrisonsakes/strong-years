"""Generate ../n8n_growth_workflow.json (importable n8n workflow) for the organic growth engine.

Source of truth for the growth workflow is THIS generator (the core workflow's generator lives outside the repo, so
tools/patch_workflow.py patches its JSON; the growth workflow is small enough to regenerate). Same helper shapes.

  python -m tools.gen_growth_workflow            # writes ../n8n_growth_workflow.json

Two triggers:
  Hourly  : posts published < 96 h -> Worker /growth/metrics/fetch (live only with GROWTH_LIVE_METRICS=1; otherwise
            the raw `metrics` rows n8n already collects) -> /growth/metrics/normalize -> post_metrics upsert ->
            /growth/baselines -> page_baselines -> /growth/score -> post_scores + winners -> /growth/actions ->
            remix_jobs + boost_queue -> Slack (human queue)
  Nightly : pages x platforms -> /growth/allocate -> briefs (queued slot plan for tomorrow) ->
            governor state (approved budget + ledger + orders rollups) -> /growth/governor/plan (dry-run) ->
            governor_decisions -> Slack approval notification.
No node in this workflow publishes, spends or calls an ad API. The executor endpoint is deliberately not wired.
"""
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

nodes: list[dict] = []
connections: dict = {}
_names: set[str] = set()


def nid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, "changsun-growth/" + name))


def add(name, type_, version, params, pos, creds=None, **extra):
    assert name not in _names, name
    _names.add(name)
    n = {"parameters": params, "id": nid(name), "name": name, "type": type_, "typeVersion": version, "position": pos}
    if creds:
        n["credentials"] = creds
    n.update(extra)
    nodes.append(n)
    return name


def link(a, b, out=0, inp=0):
    connections.setdefault(a, {"main": []})
    main = connections[a]["main"]
    while len(main) <= out:
        main.append([])
    main[out].append({"node": b, "type": "main", "index": inp})


C_SUPA = {"httpCustomAuth": {"id": "REPLACE_SUPABASE_CUSTOM_AUTH", "name": "Supabase service (apikey + Bearer)"}}
C_WORKER = {"httpHeaderAuth": {"id": "REPLACE_WORKER", "name": "Render/QA worker X-Worker-Token"}}
C_SLACK = {"slackApi": {"id": "REPLACE_SLACK", "name": "Slack (ops bot)"}}
SUPA = "{{ $env.SUPABASE_URL }}"
WORKER = "{{ $env.QA_WORKER_URL }}"


def http(name, pos, method, url, creds, body=None, headers=None, timeout=120000, retry=True, cred_type="httpHeaderAuth", **kw):
    p = {"method": method, "url": url, "options": {"timeout": timeout}}
    if creds is not None:
        p["authentication"] = "genericCredentialType"
        p["genericAuthType"] = cred_type
    if headers:
        p["sendHeaders"] = True
        p["headerParameters"] = {"parameters": [{"name": k, "value": v} for k, v in headers]}
    if body is not None:
        p["sendBody"] = True
        p["specifyBody"] = "json"
        p["jsonBody"] = body
    extra = {}
    if retry:
        extra.update({"retryOnFail": True, "maxTries": 3, "waitBetweenTries": 5000})
    extra.update(kw)
    return add(name, "n8n-nodes-base.httpRequest", 4.2, p, pos, creds, **extra)


def supa_http(name, pos, method, path, body=None, prefer=None, **kw):
    headers = [("Content-Type", "application/json")]
    if prefer:
        headers.append(("Prefer", prefer))
    return http(name, pos, method, "=" + SUPA + path, C_SUPA, body=body, headers=headers, cred_type="httpCustomAuth", **kw)


def worker(name, pos, path, body, timeout=180000):
    return http(name, pos, "POST", "=" + WORKER + path, C_WORKER, body=body,
                headers=[("Content-Type", "application/json")], timeout=timeout)


def code(name, pos, js):
    return add(name, "n8n-nodes-base.code", 2, {"mode": "runOnceForAllItems", "jsCode": js.strip() + "\n"}, pos)


def cond_if(name, pos, left, op_type, operation, right=None):
    c = {"id": nid(name + "-c"), "leftValue": left, "operator": {"type": op_type, "operation": operation}}
    if right is None:
        c["operator"]["singleValue"] = True
        c["rightValue"] = ""
    else:
        c["rightValue"] = right
    params = {"conditions": {"options": {"caseSensitive": True, "leftValue": "", "typeValidation": "loose"},
                             "conditions": [c], "combinator": "and"}, "options": {}}
    return add(name, "n8n-nodes-base.if", 2, params, pos)


def slack(name, pos, text):
    return add(name, "n8n-nodes-base.slack", 2.2,
               {"resource": "message", "operation": "post", "select": "channel",
                "channelId": {"__rl": True, "mode": "name", "value": "={{ $env.SLACK_GROWTH_CHANNEL || '#growth' }}"},
                "text": text, "otherOptions": {}}, pos, C_SLACK, onError="continueRegularOutput")


def sticky(name, pos, content, w=520, h=260, color=None):
    p = {"content": content, "height": h, "width": w}
    if color:
        p["color"] = color
    return add(name, "n8n-nodes-base.stickyNote", 1, p, pos)


# ============================================================ HOURLY: metrics -> score -> actions
sticky("Note: hourly loop", [0, -320],
       "## Hourly growth loop\nposts < 96 h → worker metrics (live only with GROWTH_LIVE_METRICS=1) → post_metrics → baselines → "
       "scores → winners → remix_jobs + boost_queue → Slack.\n\nNothing here publishes or spends. Boost candidates wait for a "
       "human in `v_boost_approval_queue`; remix jobs become briefs only after /uniqueness/check + compliance + judge.", color=4)

add("Hourly: Growth Tick", "n8n-nodes-base.scheduleTrigger", 1.2,
    {"rule": {"interval": [{"field": "hours", "hoursInterval": 1}]}}, [0, 0])

supa_http("Supabase: Recent Published Posts", [260, 0], "GET",
          "/rest/v1/posts?select=id,platform,published_at,external_post_id,page_account_id,"
          "page_accounts(page_id,token_vault_key),variants(duration_s)"
          "&status=eq.published&published_at=gte.{{ $now.minus({ hours: 96 }).toISO() }}&limit=1000")

supa_http("Supabase: Raw Captures (metrics)", [520, 0], "GET",
          "/rest/v1/metrics?select=post_id,captured_at,views,reach,likes,comments,shares,saves,profile_visits,link_clicks,"
          "keyword_comments,dm_optins,avg_watch_pct&captured_at=gte.{{ $now.minus({ hours: 120 }).toISO() }}&limit=20000")

supa_http("Supabase: Member Rollup (orders by post)", [780, 0], "GET",
          "/rest/v1/orders?select=attributed_post_id,created_at&is_subscription=eq.true"
          "&created_at=gte.{{ $now.minus({ hours: 120 }).toISO() }}&attributed_post_id=not.is.null&limit=20000")

code("Build Normalize Request", [1040, 0], r"""
// posts + raw captures (+ rollups) -> /growth/metrics/normalize body. Captures already carry canonical counters
// (raw_format 'capture'); keyword_comments / dm_optins ride along as cumulative rollup points, members from orders.
const posts = $('Supabase: Recent Published Posts').all().map(i => i.json);
const caps = $('Supabase: Raw Captures (metrics)').all().map(i => i.json);
const orders = $('Supabase: Member Rollup (orders by post)').all().map(i => i.json);
const byPost = {};
for (const c of caps) (byPost[c.post_id] = byPost[c.post_id] || []).push(c);
const memb = {};
for (const o of orders) (memb[o.attributed_post_id] = memb[o.attributed_post_id] || []).push(o.created_at);
const body = { now: new Date().toISOString(), posts: [] };
for (const p of posts) {
  const cs = (byPost[p.id] || []).sort((a, b) => a.captured_at.localeCompare(b.captured_at));
  const rollups = {};
  if (cs.some(c => c.keyword_comments != null)) rollups.keyword_comments = cs.map(c => ({ at: c.captured_at, count: c.keyword_comments || 0 }));
  if (cs.some(c => c.dm_optins != null)) rollups.optins = cs.map(c => ({ at: c.captured_at, count: c.dm_optins || 0 }));
  if (memb[p.id]) { const ts = memb[p.id].sort(); rollups.members = ts.map((t, i) => ({ at: t, count: i + 1 })); }
  const dur = (p.variants && p.variants[0] && p.variants[0].duration_s) || null;
  body.posts.push({ post_id: p.id, page_id: p.page_accounts && p.page_accounts.page_id, platform: p.platform,
    published_at: p.published_at, external_post_id: p.external_post_id, duration_s: dur, raw_format: 'capture',
    captures: cs.map(c => ({ captured_at: c.captured_at, views: c.views, reach: c.reach, likes: c.likes, comments: c.comments,
      shares: c.shares, saves: c.saves, profile_visits: c.profile_visits, link_clicks: c.link_clicks, avg_watch_pct: c.avg_watch_pct })),
    rollups });
}
return [{ json: body }];
""")

worker("Worker: Normalize Metrics", [1300, 0], "/growth/metrics/normalize", "={{ JSON.stringify($json) }}")

code("Rows: post_metrics", [1560, 0], r"""
const res = $input.first().json;
const rows = (res.snapshots || []).map(s => ({ post_id: s.post_id, page_id: s.page_id, platform: s.platform, horizon_h: s.horizon_h,
  published_at: s.published_at, captured_at: s.captured_at, age_h: s.age_h, views: s.views, reach: s.reach, likes: s.likes,
  comments: s.comments, shares: s.shares, saves: s.saves, profile_visits: s.profile_visits, link_clicks: s.link_clicks,
  follows: s.follows, avg_watch_pct: s.avg_watch_pct, keyword_comments: s.keyword_comments, optins: s.optins, members: s.members,
  interpolated: s.interpolated, missing: s.missing, rollups_as_of_now: s.rollups_as_of_now, source: s.source }));
return [{ json: { rows, count: rows.length } }];
""")

supa_http("Supabase: Upsert post_metrics", [1820, 0], "POST", "/rest/v1/post_metrics?on_conflict=post_id,horizon_h",
          body="={{ JSON.stringify($json.rows) }}", prefer="resolution=merge-duplicates,return=minimal")

supa_http("Supabase: post_metrics History (30d)", [2080, 0], "GET",
          "/rest/v1/post_metrics?select=post_id,page_id,platform,horizon_h,published_at,views,shares,saves,keyword_comments,"
          "profile_visits,link_clicks,optins,members,interpolated&published_at=gte.{{ $now.minus({ days: 30 }).toISO() }}&limit=50000")

code("Build Baselines Request", [2340, 0], r"""
const history = $input.all().map(i => i.json);
const pages = [...new Set(history.map(h => h.page_id).filter(Boolean))];
return [{ json: { history, pages } }];
""")

worker("Worker: Baselines", [2600, 0], "/growth/baselines", "={{ JSON.stringify($json) }}")

supa_http("Supabase: Insert page_baselines", [2860, 0], "POST", "/rest/v1/page_baselines",
          body="={{ JSON.stringify($json.baselines.map(b => ({ page_id: b.page_id, platform: b.platform, horizon_h: b.horizon_h, n_posts: b.n_posts, components: b.components, config_version: b.config_version }))) }}",
          prefer="return=minimal")

code("Build Score Request", [3120, 0], r"""
const snaps = $('Rows: post_metrics').first().json.rows;
const baselines = $('Worker: Baselines').first().json.baselines;
return [{ json: { snapshots: snaps, baselines } }];
""")

worker("Worker: Score", [3380, 0], "/growth/score", "={{ JSON.stringify($json) }}")

code("Rows: post_scores + winners", [3640, 0], r"""
const res = $input.first().json;
const scores = (res.scores || []).map(s => ({ post_id: s.post_id, page_id: s.page_id, platform: s.platform, horizon_h: s.horizon_h,
  score: s.score, z: s.z, components_used: s.components_used, views: s.views, class: s.class, breakout: s.breakout,
  reward: s.reward, conversion_norm: s.conversion_norm, reasons: s.reasons, config_version: s.config_version }));
const winners = (res.winners || []).map(w => ({ post_id: w.post_id, page_id: w.page_id, platform: w.platform, best_score: w.score,
  best_horizon_h: w.horizon_h, breakout: w.breakout, last_seen_at: new Date().toISOString() }));
return [{ json: { scores, winners, all: res.scores || [] } }];
""")

supa_http("Supabase: Upsert post_scores", [3900, 0], "POST", "/rest/v1/post_scores?on_conflict=post_id,horizon_h",
          body="={{ JSON.stringify($json.scores) }}", prefer="resolution=merge-duplicates,return=minimal")

supa_http("Supabase: Upsert winners", [4160, 0], "POST", "/rest/v1/winners?on_conflict=post_id",
          body="={{ JSON.stringify($('Rows: post_scores + winners').first().json.winners) }}",
          prefer="resolution=merge-duplicates,return=minimal")

cond_if("Any winners or losers?", [4420, 0],
        "={{ $('Rows: post_scores + winners').first().json.all.filter(s => s.class === 'WINNER' || s.class === 'LOSER').length }}",
        "number", "gt", 0)

supa_http("Supabase: Pages", [4680, -160], "GET",
          "/rest/v1/pages?select=id,slug,status,locale,page_dna&status=eq.active")

supa_http("Supabase: Post Context (briefs)", [4940, -160], "GET",
          "/rest/v1/posts?select=id,published_at,variant:variants(video:videos(brief:briefs(pillar,editorial_format,hook_id,speaker_mode,brief)))"
          "&id=in.({{ $('Rows: post_scores + winners').first().json.all.filter(s => s.class === 'WINNER' || s.class === 'LOSER').map(s => s.post_id).join(',') }})")

supa_http("Supabase: Recent remix_jobs", [5200, -160], "GET",
          "/rest/v1/remix_jobs?select=source_post_id,target_page_id,created_at&created_at=gte.{{ $now.minus({ days: 3 }).toISO() }}")

code("Build Actions Request", [5460, -160], r"""
const scores = $('Rows: post_scores + winners').first().json.all.filter(s => s.class === 'WINNER' || s.class === 'LOSER');
const pages = $('Supabase: Pages').all().map(i => i.json);
const ctx = $('Supabase: Post Context (briefs)').all().map(i => i.json);
const recent = $('Supabase: Recent remix_jobs').all().map(i => i.json);
const posts = ctx.map(p => {
  const b = (((p.variant || {}).video || {}).brief) || {};
  const bb = b.brief || {};
  return { post_id: p.id, published_at: p.published_at, arm: { pillar: b.pillar, grammar: bb.grammar, format: b.editorial_format,
    speaker: b.speaker_mode, length: bb.length_bucket }, set_code: bb.set_code, hook_id: b.hook_id, evidence: bb.evidence || [] };
});
return [{ json: { scores, posts, pages, recent_remixes: recent, now: new Date().toISOString() } }];
""")

worker("Worker: Winner Actions", [5720, -160], "/growth/actions", "={{ JSON.stringify($json) }}")

code("Rows: remix_jobs + boost_queue", [5980, -160], r"""
const res = $input.first().json;
const remix = (res.remix_jobs || []).map(j => ({ source_post_id: j.source_post_id, source_page_id: j.source_page_id,
  source_platform: j.source_platform, target_page_id: j.target_page_id, status: 'queued', priority: j.priority,
  earliest_at: j.earliest_at, preferred_slot_hour: j.preferred_slot_hour, level: j.level, payload: j }));
const boosts = (res.boost_candidates || []).map(b => ({ post_id: b.post_id, page_id: b.page_id, platform: b.platform,
  channel: b.channel, class: b.class, score: b.score, status: b.status, requested_daily_usd: b.requested_daily_usd,
  compliance: b.compliance, ai_label_kept: true }));
return [{ json: { remix, boosts, pins: res.pin_suggestions || [], downweights: res.downweights || [], counts: res.counts } }];
""")

supa_http("Supabase: Insert remix_jobs", [6240, -160], "POST", "/rest/v1/remix_jobs?on_conflict=source_post_id,target_page_id",
          body="={{ JSON.stringify($json.remix) }}", prefer="resolution=ignore-duplicates,return=minimal")

supa_http("Supabase: Insert boost_queue", [6500, -160], "POST", "/rest/v1/boost_queue",
          body="={{ JSON.stringify($('Rows: remix_jobs + boost_queue').first().json.boosts) }}", prefer="return=minimal")

slack("Slack: Growth Hourly Summary", [6760, -160],
      "=Growth: {{ $('Rows: remix_jobs + boost_queue').first().json.counts.remix_jobs }} remix jobs queued, "
      "{{ $('Rows: remix_jobs + boost_queue').first().json.counts.boost_candidates }} boost candidates waiting for a human "
      "(v_boost_approval_queue), {{ $('Rows: remix_jobs + boost_queue').first().json.pins.length }} pin suggestions: "
      "{{ $('Rows: remix_jobs + boost_queue').first().json.pins.map(p => p.platform + ':' + p.action + ' ' + p.post_id).join(', ') }}")

for a, b in [("Hourly: Growth Tick", "Supabase: Recent Published Posts"),
             ("Supabase: Recent Published Posts", "Supabase: Raw Captures (metrics)"),
             ("Supabase: Raw Captures (metrics)", "Supabase: Member Rollup (orders by post)"),
             ("Supabase: Member Rollup (orders by post)", "Build Normalize Request"),
             ("Build Normalize Request", "Worker: Normalize Metrics"), ("Worker: Normalize Metrics", "Rows: post_metrics"),
             ("Rows: post_metrics", "Supabase: Upsert post_metrics"),
             ("Supabase: Upsert post_metrics", "Supabase: post_metrics History (30d)"),
             ("Supabase: post_metrics History (30d)", "Build Baselines Request"), ("Build Baselines Request", "Worker: Baselines"),
             ("Worker: Baselines", "Supabase: Insert page_baselines"), ("Supabase: Insert page_baselines", "Build Score Request"),
             ("Build Score Request", "Worker: Score"), ("Worker: Score", "Rows: post_scores + winners"),
             ("Rows: post_scores + winners", "Supabase: Upsert post_scores"), ("Supabase: Upsert post_scores", "Supabase: Upsert winners"),
             ("Supabase: Upsert winners", "Any winners or losers?"), ("Any winners or losers?", "Supabase: Pages"),
             ("Supabase: Pages", "Supabase: Post Context (briefs)"), ("Supabase: Post Context (briefs)", "Supabase: Recent remix_jobs"),
             ("Supabase: Recent remix_jobs", "Build Actions Request"), ("Build Actions Request", "Worker: Winner Actions"),
             ("Worker: Winner Actions", "Rows: remix_jobs + boost_queue"), ("Rows: remix_jobs + boost_queue", "Supabase: Insert remix_jobs"),
             ("Supabase: Insert remix_jobs", "Supabase: Insert boost_queue"), ("Supabase: Insert boost_queue", "Slack: Growth Hourly Summary")]:
    link(a, b)

# ============================================================ NIGHTLY: allocator -> governor dry run -> approval
sticky("Note: nightly allocator + governor", [0, 480],
       "## Nightly (23:10 page-local)\npages × platforms → /growth/allocate (Thompson sampling, ≥ 20% exploration) → briefs (queued, "
       "slot plan for tomorrow) → governor state from spend_budgets + spend_ledger + sy_orders rollups → /growth/governor/plan "
       "(DRY RUN: SPEND_ENABLED=0 by default) → governor_decisions → Slack.\n\nThe executor endpoint is not wired on purpose: a "
       "human approves in the review app and the client flips SPEND_ENABLED only after the §11 gate.", color=5)

add("Nightly 23:10: Allocator + Governor", "n8n-nodes-base.scheduleTrigger", 1.2,
    {"rule": {"interval": [{"field": "cronExpression", "expression": "10 23 * * *"}]}}, [0, 800])

supa_http("Supabase: Active Page Accounts", [260, 800], "GET",
          "/rest/v1/page_accounts?select=id,page_id,platform,daily_post_target,status,page:pages(id,slug,page_dna,status)"
          "&status=in.(warming,active)")

supa_http("Supabase: Bandit Observations (30d)", [520, 800], "GET",
          "/rest/v1/post_scores?select=post_id,page_id,platform,reward,scored_at,class,"
          "post:posts(variant:variants(video:videos(brief:briefs(pillar,editorial_format,speaker_mode,brief))))"
          "&scored_at=gte.{{ $now.minus({ days: 30 }).toISO() }}&horizon_h=gte.24&limit=50000")

supa_http("Supabase: Recent Briefs (7d)", [780, 800], "GET",
          "/rest/v1/briefs?select=page_id,pillar,editorial_format,brief&target_date=gte.{{ $now.minus({ days: 7 }).toISODate() }}&limit=20000")

code("Build Allocate Requests", [1040, 800], r"""
// one item per page x platform for tomorrow; observations mapped to arm keys; LOSER posts carry reward 0
const accounts = $('Supabase: Active Page Accounts').all().map(i => i.json);
const obs = $('Supabase: Bandit Observations (30d)').all().map(i => i.json);
const briefs = $('Supabase: Recent Briefs (7d)').all().map(i => i.json);
const tomorrow = $now.plus({ days: 1 }).toISODate();
const armOf = (b) => { const bb = (b && b.brief) || {}; if (!b || !b.pillar) return null;
  return `pillar=${b.pillar}|grammar=${bb.grammar || 'MYTH'}|format=${b.editorial_format || 'F02'}|speaker=${b.speaker_mode || 'CHANG'}|length=${bb.length_bucket || 'M'}`; };
const out = [];
for (const a of accounts) {
  if (!a.page || a.page.status !== 'active') continue;
  const observations = obs.filter(o => o.page_id === a.page_id && o.platform === a.platform).map(o => {
    const key = armOf((((o.post || {}).variant || {}).video || {}).brief);
    return key ? { arm_key: key, reward: o.class === 'LOSER' ? 0 : o.reward, at: o.scored_at } : null; }).filter(Boolean);
  const recent = briefs.filter(b => b.page_id === a.page_id).map(b => ({ pillar: b.pillar, grammar: (b.brief || {}).grammar, format: b.editorial_format }));
  out.push({ json: { page: a.page, platform: a.platform, date: tomorrow, cadence: a.daily_post_target, observations, recent,
    page_account_id: a.id, now: new Date().toISOString() } });
}
return out;
""")

worker("Worker: Allocate Slots", [1300, 800], "/growth/allocate", "={{ JSON.stringify($json) }}")

code("Rows: briefs (slot plan)", [1560, 800], r"""
const rows = [];
for (const item of $input.all()) {
  const plan = item.json;
  for (const s of plan.slots || []) {
    rows.push({ page_id: plan.page_id, target_date: plan.date, slot_index: s.slot_index, format: s.render_format,
      editorial_format: s.editorial_format, pillar: s.pillar, speaker_mode: s.speaker, status: 'queued', priority: s.priority,
      brief: { grammar: s.grammar, length_bucket: s.length_bucket, length_s: s.length_s, running_bit: s.running_bit,
        arm_key: s.arm_key, mode: s.mode, platform: plan.platform, hour: s.hour, proven_grammar: s.proven_grammar,
        allocator: { theta: s.theta, posterior_mean: s.posterior_mean, observations: s.observations, config_version: plan.config_version } } });
  }
}
return [{ json: { rows, count: rows.length } }];
""")

supa_http("Supabase: Insert briefs (queued)", [1820, 800], "POST", "/rest/v1/briefs?on_conflict=page_id,target_date,slot_index,locale",
          body="={{ JSON.stringify($json.rows) }}", prefer="resolution=ignore-duplicates,return=minimal")

supa_http("Supabase: Approved Budget", [2080, 800], "GET",
          "/rest/v1/spend_budgets?select=*&status=eq.approved&order=approved_at.desc&limit=1")

supa_http("Supabase: Ledger (month)", [2340, 800], "GET",
          "/rest/v1/spend_ledger?select=day,spend_class,amount_usd,source&source=eq.reported&day=gte.{{ $now.startOf('month').toISODate() }}")

supa_http("Supabase: Approved Boosts", [2600, 800], "GET",
          "/rest/v1/boost_queue?select=post_id,class,compliance,requested_daily_usd,approved_by,approved_at,approved_max_daily_usd&status=eq.approved")

code("Build Governor State", [2860, 800], r"""
// Cash and campaign facts come from finance (GROWTH_* env until a finance feed exists); everything else from the DB.
const budget = ($('Supabase: Approved Budget').first() || { json: {} }).json;
const ledger = $('Supabase: Ledger (month)').all().map(i => i.json);
const boosts = $('Supabase: Approved Boosts').all().map(i => i.json);
const today = $now.toISODate();
const spentToday = ledger.filter(l => l.day === today).reduce((s, l) => s + Number(l.amount_usd || 0), 0);
const spentMonth = ledger.reduce((s, l) => s + Number(l.amount_usd || 0), 0);
const num = (v, d) => (v === undefined || v === null || v === '' ? d : Number(v));
const state = {
  price_usd: num(budget.price_usd, 25), campaign_day: num($env.GROWTH_CAMPAIGN_DAY, 0),
  budget: budget.id ? { id: budget.id, daily_cap_usd: budget.daily_cap_usd, monthly_cap_usd: budget.monthly_cap_usd,
    cash_floor_usd: budget.cash_floor_usd, status: budget.status, approved_by: budget.approved_by, approved_at: budget.approved_at,
    expires_at: budget.expires_at } : {},
  cash: { balance_usd: num($env.GROWTH_CASH_BALANCE_USD, 0), spent_today_usd: spentToday, spent_month_usd: spentMonth,
    line_180d_usd: num($env.GROWTH_CASH_LINE_180D_USD, 0) },
  current: { cold_daily_usd: num($env.GROWTH_COLD_DAILY_USD, 0), retarget_daily_usd: num($env.GROWTH_RETARGET_DAILY_USD, 0),
    retarget_requested_usd: num($env.GROWTH_RETARGET_REQUESTED_USD, 0) },
  daily: JSON.parse($env.GROWTH_DAILY_JSON || '[]'),
  refund_rate_14d: $env.GROWTH_REFUND_RATE_14D ? Number($env.GROWTH_REFUND_RATE_14D) : null,
  chargeback_rate_30d: $env.GROWTH_CHARGEBACK_RATE_30D ? Number($env.GROWTH_CHARGEBACK_RATE_30D) : null,
  chargeback_count_30d: $env.GROWTH_CHARGEBACK_COUNT_30D ? Number($env.GROWTH_CHARGEBACK_COUNT_30D) : null,
  renewal1: { rate: $env.GROWTH_RENEWAL1_RATE ? Number($env.GROWTH_RENEWAL1_RATE) : null, cohort_n: num($env.GROWTH_RENEWAL1_COHORT_N, 0) },
  graduation: { charge_today_purchases: num($env.GROWTH_CHARGE_TODAY_PURCHASES, 0),
    factor: $env.GROWTH_FACTOR ? Number($env.GROWTH_FACTOR) : null, media_cost_case: $env.GROWTH_MEDIA_COST_CASE || 'central' },
  boosts: boosts.map(b => ({ post_id: b.post_id, class: b.class, compliance_verdict: (b.compliance || {}).verdict,
    judge_passed: (b.compliance || {}).judge_passed, requested_daily_usd: b.requested_daily_usd,
    approval: { by: b.approved_by, at: b.approved_at, max_daily_usd: b.approved_max_daily_usd } })),
};
return [{ json: { state, now: new Date().toISOString(), actor: 'n8n-nightly' } }];
""")

worker("Worker: Governor Plan (dry run)", [3120, 800], "/growth/governor/plan", "={{ JSON.stringify($json) }}")

supa_http("Supabase: Insert governor_decisions", [3380, 800], "POST", "/rest/v1/governor_decisions",
          body="={{ JSON.stringify({ decided_at: $json.decided_at, mode: $json.mode, status: $json.status, valid: $json.valid, "
               "state_hash: $json.state_hash, config_fingerprint: $json.config_fingerprint, planned_daily_usd: ($json.totals || {}).planned_daily_usd || 0, "
               "decision: $json, audit_hash: ($json.audit || {}).hash, prev_hash: ($json.audit || {}).prev_hash }) }}",
          prefer="return=minimal")

slack("Slack: Governor Plan for Approval", [3640, 800],
      "=Governor ({{ $('Worker: Governor Plan (dry run)').first().json.mode }}): status "
      "{{ $('Worker: Governor Plan (dry run)').first().json.status }} · planned ${{ $('Worker: Governor Plan (dry run)').first().json.totals.planned_daily_usd }}/day "
      "(cold {{ $('Worker: Governor Plan (dry run)').first().json.cold.next_daily_usd }}, retarget {{ $('Worker: Governor Plan (dry run)').first().json.retarget.next_daily_usd }}, "
      "boosts {{ $('Worker: Governor Plan (dry run)').first().json.boosts.filter(b => b.status === 'approved').length }}) · "
      "{{ $('Worker: Governor Plan (dry run)').first().json.reasons.join('; ') }} · "
      "Nothing is spent until a human approves this plan in the review app AND SPEND_ENABLED=1.")

for a, b in [("Nightly 23:10: Allocator + Governor", "Supabase: Active Page Accounts"),
             ("Supabase: Active Page Accounts", "Supabase: Bandit Observations (30d)"),
             ("Supabase: Bandit Observations (30d)", "Supabase: Recent Briefs (7d)"),
             ("Supabase: Recent Briefs (7d)", "Build Allocate Requests"), ("Build Allocate Requests", "Worker: Allocate Slots"),
             ("Worker: Allocate Slots", "Rows: briefs (slot plan)"), ("Rows: briefs (slot plan)", "Supabase: Insert briefs (queued)"),
             ("Supabase: Insert briefs (queued)", "Supabase: Approved Budget"), ("Supabase: Approved Budget", "Supabase: Ledger (month)"),
             ("Supabase: Ledger (month)", "Supabase: Approved Boosts"), ("Supabase: Approved Boosts", "Build Governor State"),
             ("Build Governor State", "Worker: Governor Plan (dry run)"),
             ("Worker: Governor Plan (dry run)", "Supabase: Insert governor_decisions"),
             ("Supabase: Insert governor_decisions", "Slack: Governor Plan for Approval")]:
    link(a, b)


def build() -> dict:
    return {
        "name": "ChangSun Growth: metrics → winners → allocator → governor (dry run)",
        "nodes": nodes, "connections": connections, "active": False,
        "settings": {"executionOrder": "v1", "saveManualExecutions": True, "callerPolicy": "workflowsFromSameOwner",
                     "timezone": "America/New_York", "errorWorkflow": "REPLACE_ERROR_WORKFLOW_ID"},
        "staticData": None, "meta": {"templateCredsSetupCompleted": False},
        "pinData": {}, "versionId": str(uuid.uuid5(uuid.NAMESPACE_DNS, "changsun-growth/version")),
        "tags": [{"name": "growth"}],
    }


def main(out: Path | None = None) -> Path:
    out = out or Path(__file__).resolve().parents[2] / "n8n_growth_workflow.json"
    out.write_text(json.dumps(build(), indent=2, ensure_ascii=False) + "\n")
    return out


if __name__ == "__main__":
    p = main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
    print(f"wrote {p} ({len(nodes)} nodes)")
