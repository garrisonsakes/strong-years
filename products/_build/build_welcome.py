"""Product 5: Welcome Kit for new Strong Years members. Rendered once per checkout arm so billing text is exact."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import render, cover_html, DISCLOSURE, PRODUCTS, box, say
from library import STOP, EMERGENCY, PAIN_RULE
from evidence import appendix_md

NAME = "Strong Years Welcome Kit"
DOMAIN = os.environ.get("SY_DOMAIN", "strongyears.com")
# Pricing canon (BRIEF.md CANON UPDATE 2 + 3, Oct 1 2026): launch default = the $12 starter offer (both books + the first
# founding month, then $25/mo); founding $25/mo locked while subscribed ($30 only if cell data supports it); $35 standard
# after the founding cohort fills. NO $1 trial, ever. Every membership: 14-day money-back guarantee on the first monthly
# charge. Reminders by email (SMS is off until the texting line is approved: no "text CANCEL").
# One PDF per price so the billing text always matches what the member pays (app/src/lib/products.ts file names).
GUARANTEE = ("**14-day money-back guarantee.** If Strong Years isn't worth it, ask for a refund within 14 days of your first monthly charge "
             "(tap Account → Refund, or ask a human coach) and you get every penny back. No questions, no forms to mail.")


def _founding(P):
    return dict(label=f"Founding membership, {P}/month", price=P, today=P, founding=True,
        billing=lambda P, D: f"""You paid **{P} today** for your first month as a founding member. Your membership **renews at {P} every month, on the same date, until you cancel**. Your founding price stays the same for as long as you stay subscribed. We email you a reminder before each renewal date.""",
        first_charge="Day 12: An email reminding you that your 14-day money-back window closes in 2 days.", guarantee=GUARANTEE)


ARMS = {
    # CANON UPDATE 6 (Oct 2 2026): the launch offer. $12 today for both books; the membership is a 7-day trial ($0 today);
    # the first $25 is charged on day 7, then every month. Money-back window: 14 days from that first charge.
    "trial_2500": dict(label="$12 today for both books and a 7-day trial, then $25/month from day 7", price="$25", today="$12", founding=True,
        billing=lambda P, D: f"""You paid **$12 today** for Chang Yin's 7-Day Strength Reset and Sun Yoon's Strong Kitchen (both yours to keep). Your founding membership started as a **7-day trial: $0 today**. Seven days after you joined, your card is charged **{P}**, and your membership then **renews at {P} every month, on the same date, until you cancel**. Cancel before day 7 and the membership costs nothing. Your founding price stays the same for as long as you stay subscribed. We email you a reminder **2 days before your first {P} charge** and before every renewal.""",
        first_charge="Day 5: An email reminding you that your first $25 charge is in 2 days (cancel online before then and nothing is charged). Day 7: your first $25 charge. Day 19: an email reminding you that your 14-day money-back window closes in 2 days.", guarantee=GUARANTEE),
    "starter_2500": dict(label="$12 today for both books and your first month, then $25/month", price="$25", today="$12", founding=True,
        billing=lambda P, D: f"""You paid **$12 today** for Chang Yin's 7-Day Strength Reset, Sun Yoon's Strong Kitchen (both yours to keep) and your first month as a founding member. One month after you joined, your membership **renews at {P} every month, on the same date, until you cancel**. Your founding price stays the same for as long as you stay subscribed. We email you a reminder **before your first {P} charge** and before every renewal.""",
        first_charge="Day 12: An email reminding you that your 14-day money-back window closes in 2 days; another reminder 2 days before your first $25 charge.", guarantee=GUARANTEE),
    "founding_2500": _founding("$25"),
    "founding_3000": _founding("$30"),
    "standard_3500": dict(label="Membership, $35/month", price="$35", today="$35", founding=False,
        billing=lambda P, D: f"""You paid **{P} today** for your first month. Your membership **renews at {P} every month, on the same date, until you cancel**. We email you a reminder before each renewal date.""",
        first_charge="Day 12: An email reminding you that your 14-day money-back window closes in 2 days.", guarantee=GUARANTEE),
}


def md_for(arm):
    A = ARMS[arm]
    P = A["price"]
    D = DOMAIN
    fc = f"| **{A['first_charge'].split(':')[0]}** | {A['first_charge'].split(': ', 1)[1]} |"
    d7 = '| **Day 7** | Your "week 1 done" summary, and choose your first 12-week program. |'
    ROWS = d7 + "\n" + fc
    welcome_chang = say("chang", "Welcome. I'm Chang Yin. I'm 74, I lift, and I'm an AI character. A team of real people made me, and they built every session on published exercise research for older adults.\n\nYour first session is 8 minutes. You can do it in your chair. Do it today. Strong is a habit, and habits start on day one.")
    welcome_sun = say("sun", "Sun Yoon. His wife. Also AI. He'll tell you it's easy. It's not hard. Those are different. Start at the easier level, eat some protein, and if anything hurts, tell us. A real person reads it.")
    return f"""
# Welcome {{: .nobreak}}

{welcome_chang}

{welcome_sun}

**In this kit:** how Strong Years works · your first 72 hours · staying safe · how to reach a human · about the AI · your billing and how to cancel · a fridge card.

# How Strong Years works

## Every day: one session, 8 to 12 minutes

A new follow-along session with Chang every day, in the same weekly rhythm:

| Day | What | Why |
|---|---|---|
| Monday | Strength | Legs first: chair stands, push, pull, calves |
| Tuesday | Mobility | Hips, back, shoulders, ankles. Nothing forced |
| Wednesday | Balance | At the kitchen counter, always with support |
| Thursday | Strength | Stand up faster, step-ups, carry |
| Friday | Breath + qigong | Slow breathing and gentle baduanjin and tai chi, taught as exercise |
| Saturday | Walk-and-talk | Walk with Chang, indoors or out |
| Sunday | Rest + stretch | Gentle stretches and your weekly check-in |

Strength training two to three times a week is what the research uses: a review of 121 trials in 6,700 older adults found large gains in strength and easier chair stands (E01, E02).

## Four levels, so it always fits

| Level | For |
|---|---|
| **Rebuild** | Chair-based. Seated, or standing with both hands on the counter and the chair behind you. |
| **Steady** | The standard version with counter or wall support. Most people start here. |
| **Strong** | Added weight, slower lowering, less hand support. |
| **Iron** | For people who already train. Some moves are labelled advanced. |

The app suggests your level from your Strength Age test. You can change it any day. Having a bad day? Tap **"sore knee / sore back / low energy today"** and the session swaps in a gentler version.

## Everything else inside

- **Six 12-week programs** to finish, one at a time: Strong at 70, Back Strong, Balance and Steady Feet, Gut Reset with Sun Yoon, Grip and Hands, Walk Stronger.
- **Sun Yoon's Kitchen, every Sunday:** three recipes, a grocery list, and one kitchen remedy graded honestly (good evidence, some evidence, or tradition only).
- **Your daily message** from Chang at the time you choose, with a link to today's session: by email at first, and by text once our texting line is approved (we'll ask before we text you; reply STOP anytime). Sun writes on Sundays.
- **Ask Chang / Ask Sun:** an AI chat that can swap an exercise, adapt a recipe or explain why. It can remember your level and your sore spots if you allow it (see "About the AI").
- **Strength Age retest every month:** six at-home tests, charted, so you can see the line move. A fitness estimate, not a medical test.
- **Streaks with grace days:** miss a day and your streak doesn't reset. Badges at 7, 30 and 100 sessions. At 100 sessions we mail you a printed certificate.
- **The Courtyard:** a members' feed with daily prompts ("post your chair-stand score"). Moderated by real people. There are no private messages between members, which keeps scammers out.
- **Sunday Premiere and Wednesday Live Q&A:** Sunday, a 20-minute episode with live chat. Wednesday, **a real human coach** answers your questions live for 30 minutes. Replays are kept.
- **Printables:** weekly plan, grocery list, exercise cards, the fridge Strength Age chart.
- **Partner:** add your husband, wife or partner for $8 a month, with their own level and progress.

# Your first 72 hours

People who do a first session in the first few minutes are the ones who keep going. So here's the plan.

| When | What to do |
|---|---|
| **Right now** | Watch the 60-second welcome from Chang and Sun. Then do **Session 1** (8 minutes, you can do it seated). |
| **+5 minutes** | Your first **Strength Age** check: 3 quick tests, about 4 minutes. It gives you a number to beat. |
| **+10 minutes** | Pick your reminder time. Tip: tie it to something you already do ("with my morning tea"). Add the app to your home screen (the picture guide shows how). |
| **Day 1 evening** | A message from Sun (email, or text once texting is live): tonight's 15-minute dinner and a grocery list. |
| **Day 2** | Session 2. Then tell Chang what hurts, if anything, so sessions can adapt. Try one question in the chat. |
| **Day 3** | One question: too easy, just right, or too hard? Your level adjusts. |
{ROWS}

{box("note", "Tech help:", f"The app works in any web browser on a phone, tablet or computer. Text size, captions and a high-contrast mode are in Settings. Stuck? Tap Help, or ask a family member to join you on the first day. Most people are set up in five minutes.")}

# Staying safe

Most healthy adults can start light-to-moderate exercise like this and build up gradually (E43). Some people should check with their doctor first.

{box("stop", "Check with your doctor before you start if:", "you get chest pain, pressure or unusual shortness of breath when active; you've fainted or get dizzy when you stand; you have a heart, kidney, lung or metabolic condition with symptoms, or your doctor has limited your activity; you've had surgery, a fracture, a fall with injury or a hospital stay in the last few months; you have a new hip or knee (follow your surgeon's or physical therapist's precautions). The app's safety questions start you at the Rebuild level if any of these apply, and give you a one-page plan to show your doctor.")}

**The stop rule.** {STOP} {EMERGENCY}

**The pain rule (E41).** {PAIN_RULE}

**Set up a safe space.** Chair with no wheels against a wall. Counter within reach for anything standing. Shoes on. No rugs underfoot. Good light.

**Stand up slowly.** Blood pressure can dip when older adults stand quickly, especially on some medicines (E46). Pump your ankles ten times, sit a moment, then stand while holding something.

**Breathe out on the effort.** Never hold your breath to push (E42).

**Nothing in Strong Years changes your medicines.** Chang and Sun will never tell you to start, stop or change a medicine or a dose. That's between you, your doctor and your pharmacist.

{box("stop", "Not for exercise. For your doctor, today:", "chest pain or pressure; fainting; sudden weakness or numbness in the face, arm or leg; trouble speaking; a sudden severe headache; new confusion; one calf that is swollen, red and painful; a hot, swollen joint; night pain that wakes you and doesn't change with position; loss of bladder or bowel control; a fall where you hit your head. " + EMERGENCY)}

# How to reach a human

Strong Years is made by real people, and you can always reach one.

| You want to | Do this | When you'll hear back |
|---|---|---|
| Ask a person anything (billing, tech, "is this move right for me?") | Tap **Talk to a human coach** in the app (one tap from every screen), or go to {D}/help | Within 24 hours, usually much sooner |
| Ask a coach live | Join the **Wednesday Live Q&A** (30 minutes, a real human coach, introduced by first name) | Live, with replays |
| Cancel, pause or change your plan | {D}/account (two screens at most, no call) | Right away, online |
| Report a problem with a post in the Courtyard | Tap **Report** on the post | A human moderator reviews it |

**In an emergency, don't message us.** Call **911**. If you or someone you love is thinking about suicide or self-harm, call or text **988** (Suicide & Crisis Lifeline, US) or find a line at findahelpline.com. For help with an older adult's care or safety, the Eldercare Locator is 1-800-677-1116.

# About the AI

Chang Yin and Sun Yoon are **AI characters**. A team of people created them. Their life story (the welding, the lunch counter, fifty years of marriage, the cat) is fiction, like a TV family. We say so everywhere: in the app, on every video, and at the start of every chat.

**What the AI chat can do:** swap an exercise for one that suits your body today, adapt a recipe, explain why a move works, cheer you on, remind you of your plan.

**What it won't do:** diagnose anything; change or comment on your medicines or doses; replace your doctor, physical therapist or dietitian; or pretend to be a person. If you mention chest pain, a fall with injury, stroke signs, or thoughts of harming yourself, the chat stops and gives you the right emergency number, and a human on our team is alerted.

**Every chat starts with:** "I'm Chang Yin, an AI character. I'm not a doctor or physical therapist." You'll see an "AI coach" label on the chat at all times.

**Memory, only if you say yes.** The chat can remember your level, your sore spots and your goals if you switch memory on. Ask "What do you remember about me?" at any time to see it, and delete any of it, or all of it, in Settings → Memory. Health details are treated as sensitive: you opt in, and they are **never shared with advertising platforms**.

**Strong Years is for adults 18 and over.**

**We won't design it to make you need us.** Chang and Sun will never tell you they're all you need, and they'll keep telling you to call your friends and family. When you leave, nobody guilt-trips you.

# Your billing, and how to cancel

**Your plan: Strong Years, {A['label']}.**

{A['billing'](P, D)}

{A['guarantee']}

<div class="box note" markdown="1">
<span class="label">How to cancel, online, in at most two screens:</span>

1. Go to **{D}/account** (or tap Account in the app) and tap **Cancel, pause or pay less**. Emailing us also works, but a person reads it, within one business day; for a same-day cancel use your account.
2. You'll see one offer (a lower-price plan, or a free pause of 1 to 3 months) **next to an equally big "Finish canceling" button**. "Finish canceling" opens your subscription on our store, where one more tap confirms it. No phone call, no chatbot, no forms.

You'll get an on-screen confirmation and a confirmation email. You keep access until the end of the period you've paid for.
</div>

**Pause instead?** Travel, surgery, grandkids visiting: pause for 1, 2 or 3 months at no charge. Your streak and your settings are kept.

**Price changes.** If the price ever changes, we tell you at least 30 days before. {"Founding members keep the founding price for as long as they stay subscribed." if A["founding"] else ""}

**On your bank statement** the charge appears as **STRONGYEARS MEMBER**.

**Annual plans** get a reminder before every yearly renewal.

**Gift memberships** (3 or 12 months, paid by a family member) never renew automatically. Near the end, we ask the member if they'd like to continue, on their own card, with their permission.

# Your fridge card {{: .pb}}

<div class="box" markdown="1">

**My session time:** <span class="blank"></span> &nbsp;&nbsp; **My level:** Rebuild ☐ Steady ☐ Strong ☐ Iron ☐

**My week:** Mon strength · Tue mobility · Wed balance · Thu strength · Fri breath + qigong · Sat walk · Sun rest + stretch

**My Strength Age:** start <span class="blank s"></span> · month 1 <span class="blank s"></span> · month 2 <span class="blank s"></span> · month 3 <span class="blank s"></span>

</div>

{box("stop", "Stop rule:", "chest pain, dizziness or sharp pain: stop and sit. Chest pain, face drooping, trouble speaking: call 911. Pain up to 3 out of 10 that settles by tomorrow is okay; worse the next day, back off and ask your doctor.")}

<div class="box note" markdown="1">
**A human:** tap "Talk to a human coach", or {D}/help (answered within 24 hours) · **Live coach:** Wednesdays · **Cancel or pause:** {D}/account · **Crisis:** call or text 988 · **Emergency:** 911
</div>

{say("chang", "Chair against the wall. Shoes on. Breathe out when it's hard. Same time tomorrow.")}
"""


def build():
    outs = []
    for arm in ARMS:
        md = md_for(arm)
        md += "\n\n" + appendix_md(["E01", "E02", "E41", "E42", "E43", "E46"], intro="The few numbers in this kit trace to these entries (EVIDENCE.md).\n")
        A = ARMS[arm]
        cover = cover_html("Strong Years", "Welcome Kit", f"Everything you need for your first week.<br>How it works, staying safe, reaching a human, and how to cancel.",
                           f"Your plan: {A['label']}", DISCLOSURE)
        out_pdf = os.path.join(PRODUCTS, f"welcome_kit_{arm}.pdf")
        out_md = os.path.join(PRODUCTS, f"welcome_kit_{arm}.md")
        render(md, out_pdf, NAME, cover=cover, out_md=out_md,
               md_header=f"<!-- Source for the {NAME}, checkout arm '{arm}' ({A['label']}, {A['price']}/mo). Generated by products/_build/build_welcome.py. Domain token rendered as {DOMAIN} (env SY_DOMAIN)." + ("") + " -->")
        outs.append(out_pdf)
    return outs


if __name__ == "__main__":
    print(build())
