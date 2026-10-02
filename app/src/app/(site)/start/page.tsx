import type { Metadata } from "next";
import { livePrices } from "@/lib/livePricing";
import Link from "next/link";
import { CharacterArt, ExampleStrengthCard, PhoneSession } from "@/components/Art";
import { OtherWaysToStart, PricingCards, RenewalNote } from "@/components/Pricing";
import { StickyBar } from "@/components/StickyBar";
import { getShopCta } from "@/lib/shopCheckout";
import { ExampleChart } from "@/components/StrengthChart";
import { blitz, messaging, offerRules, prices } from "@/lib/config";
import { copy } from "@/lib/copy";
import { money } from "@/lib/pricing";
import { getArm, getFoundingOffer } from "@/lib/request";
import type { FoundingOffer } from "@/lib/blitz";

export const metadata: Metadata = { title: "Get stronger after 60" };
export const dynamic = "force-dynamic";

const BEGIN = [
  { say: "I push on the armrests to stand up.", start: "The Chair Builder (Legs, Day 1)", len: "9 min", know: "Your 30-second chair-stand count at the next monthly retest." },
  { say: "My knees complain on the stairs.", start: "Knees & Stairs, Session 1: The Step Builder (partial-range step-ups at the bottom stair, holding the rail)", len: "10 min", know: "Count the stairs you can climb without pulling on the rail." },
  { say: "I'm scared of falling.", start: "Steady Feet, Session 1 (counter-supported balance ladder)", len: "8 min", know: "How long you hold the heel-to-toe stand at your retest (goal: 10 seconds)." },
  { say: "My back is stiff every morning.", start: "Morning Unlock (bed-to-standing mobility; cat-cow on the bed, hip hinges at the counter)", len: "7 min", know: "How far you can turn to look behind you, and how many minutes of morning stiffness." },
  { say: "I can't open jars anymore.", start: "Hands & Grip, Session 1 (towel wrings, water-jug carries, finger spreads with a rubber band)", len: "8 min", know: "Carry test: how long you can carry two full water jugs at your retest." },
  { say: "I lie awake with my mind racing.", start: "Sleep Wind-Down, Night 1 (slow exhale breathing, 4 seconds in, 6 out, plus gentle neck and hip release)", len: "10 min", know: "Your own sleep log in the app: minutes to fall asleep, nights you woke rested." },
  { say: "I'm tired by 2 in the afternoon.", start: "After-Meal Walk + Sun Yoon's Protein Breakfast (10-minute walk after your biggest meal; 25–30g protein breakfast)", len: "10 min", know: "Your afternoon energy score, 1 to 5, logged for 14 days." },
  { say: "I haven't exercised in years, I don't know where to start.", start: "Day 1: The Gentle Start (fully seated, Rebuild track)", len: "8 min", know: "Finishing 3 sessions this week. That is the whole goal." },
];

function faqFor(offer: FoundingOffer, trialOn: boolean): [string, string][] {
  const live = livePrices(offer);
  const fp = money(live.memberCents);
  const all: [string, string][] = [
  ["Is Chang Yin real?", "No. Chang Yin and Sun Yoon are AI characters created by our team. Their story (a retired welder from Incheon's Chinatown and a lunch-counter owner from Incheon, married 50 years, in California since 1983) is invented. We're telling you plainly because you should always know who, or what, you're learning from. What is real: the exercises, the progressions and the recipes. Every session and recipe is built by our team from published exercise and nutrition guidelines for older adults, and our sources are listed on the How we make this page. When an AI video can't show a movement precisely, a real, named coach demonstrates it. Chang Yin has no medical license and no teaching credentials, and we'll never say he does."],
  ["Who writes and checks the sessions?", "Our team writes them from published exercise and nutrition guidelines for older adults (CDC, ACSM, PROT-AGE), with conservative safety cues on every movement. You can read our full process on the How we make this page."],
  ["I'm 78, I use a cane, and I haven't exercised in years. Can I do this?", "Very likely, yes, starting on the Rebuild track, where every movement is done seated or holding a sturdy counter. Please check with your doctor before starting any new exercise, especially if you've had a fall, surgery, heart problems or dizziness recently. If anything causes sharp pain, chest discomfort, dizziness or shortness of breath, stop and call your doctor."],
  ["I have bad knees, a replaced hip or osteoporosis. Is it safe?", "Every session has options that avoid deep knee bending, twisting under load, and floor work, and a sore knee / sore back button that swaps in a modified version. Sessions include general notes for people with knee or hip replacements and osteoporosis, drawn from published guidance. Follow your surgeon's or physical therapist's instructions first; ours never override theirs."],
  ["Do I need equipment?", `No. A sturdy chair without wheels and a kitchen counter are enough. Later, two water jugs or a resistance band help you progress. We also sell an optional kit (3 resistance loops, a door anchor and a grip trainer, ${money(prices.kitUpsell)}), but you never need it.`],
  ["How do I watch?", "On your phone, tablet or computer, or cast it to your TV. Captions are on by default and large. Everything works with one tap from our daily text or email, no app store required."],
  ["What happens after 7 days?", `Your trial costs $1. 48 hours before it ends, we ${messaging.smsEnabled ? "email and text" : "email"} you a reminder, and again before every monthly charge. If you do nothing, your Strong Years membership continues at ${money(live.trialRenewCents)} per month, charged on the same date each month, until you cancel. You can cancel anytime online in your account in at most two screens${messaging.smsEnabled ? ", or by texting CANCEL" : ", or by replying \u201ccancel\u201d to any email"}.`],
  ["What is the founding membership?", `Your first month (${fp}) is charged today and your price stays ${fp} a month for as long as you stay subscribed. It comes with a 14-day money-back guarantee: tap Refund in your account within ${offerRules.guaranteeDaysFoundingArm} days and you get the membership charge back. The founding price is limited to the first ${offerRules.foundingCap.toLocaleString("en-US")} members, and the counter on this page is the real number from our member database.`],
  ["How do I cancel?", `Go to Account, then Cancel membership${messaging.smsEnabled ? ", or text CANCEL" : ", or reply \u201ccancel\u201d to any email"}. You'll see one option (pause or a cheaper plan) and a clear Finish canceling button right beside it, the same size. That's two screens at most. Your cancellation is confirmed on screen and by email. Nobody will call you, you never need to call us, and the AI characters are never part of it.`],
  ["Can my husband or wife use it too?", `Yes. Add your partner for ${money(prices.partner)} a month. They get their own level, their own Strength Age and their own progress.`],
  ["I'm buying this for my mother or father. How does that work?", `Choose Give Strong Years, pick 3 months (${money(prices.gift3)}) or 12 months (${money(prices.gift12)}), and we'll send them a welcome card from Sun Yoon. Gifts are prepaid and never renew automatically. When the gift ends, they can choose to continue on their own card.`],
  ["Will this fix my arthritis, blood pressure or blood sugar?", "No program can promise that, and we don't. Strong Years is general fitness and nutrition education. Regular strength, balance and walking are habits your doctor will likely encourage, and research in older adults links them with better strength, balance and everyday function. Keep working with your doctor, and don't change any medication because of anything you see here."],
  ["Is this religious or spiritual?", "No. Chang Yin is a retired welder, not a monk or a master, and this isn't a religious practice. Tai chi and qigong appear as movement and breathing practices, taught for balance, mobility and calm."],
  ["What's the Strength Age number? Is it medical?", "It's a motivational estimate that compares your chair-stand and balance results with published norms for your age and sex. It's a helpful way to see progress, not a medical test or a diagnosis."],
  ["What if I miss days?", "Nothing bad happens. Your streak counts Strong Weeks (3 sessions in a week) and has grace weeks, and Chang Yin picks up where you left off."],
  ["Do you sell my information?", "No. We use your information to run your membership and send you the messages you ask for. Your quiz answers and health details are never shared with advertisers. You can delete your account and data anytime."],
];
  return all.filter(([q]) => trialOn || q !== "What happens after 7 days?").map(([q, a]) => [q, trialOn ? a : a.replace(/ ?or \$1 trial/g, "")]);
}

function Section({ id, children, tone = "paper" }: { id?: string; children: React.ReactNode; tone?: "paper" | "rice" | "cream" }) {
  const bg = tone === "rice" ? "bg-rice" : tone === "cream" ? "bg-cream" : "bg-paper";
  return (
    <section id={id} className={`${bg} border-b-2 border-ink/10 py-14 sm:py-20`}>
      <div className="wrap">{children}</div>
    </section>
  );
}

export default async function StartPage() {
  const arm = await getArm();
  const offer = await getFoundingOffer();
  const trialOn = blitz.trialArmEnabled;
  const useFounding = arm === "B" || !trialOn;
  const live = livePrices(offer);
  const fp = money(live.memberCents);
  const primaryHref = useFounding ? "/join" : "/checkout/trial";
  const primaryLabel = useFounding ? (offer.founding ? `Join as a founding member: ${fp} today` : `Join for ${fp} today`) : "Start 7 days for $1";
  const primaryOffer = useFounding ? "founding" : "trial";
  // CANON UPDATE 2: in Shopify mode every CTA says what /join really sells this visitor.
  const shop = await getShopCta();
  const ctaLabel = shop ? shop.label : primaryLabel;
  const FAQ = faqFor(offer, trialOn);

  return (
    <>
      <section id="hero" className="border-b-2 border-ink bg-paper py-10 sm:py-16">
        <div className="wrap grid items-center gap-10 lg:grid-cols-[1.15fr_1fr]">
          <div>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl">Get stronger after 60. Eight minutes a day, and a number that shows your progress.</h1>
            <p className="mt-6 max-w-prose text-lg">
              Strong Years gives you your Daily Practice: one 8–12 minute follow-along session a day with Chang Yin, strength, balance and mobility, with a chair-based version of everything. Plus Sun Yoon&apos;s simple high-protein recipes every Sunday and a Strength Age retest every month, so you can see the change for yourself.
            </p>
            <div className="mt-8 max-w-md">
              <Link href={primaryHref} className="btn-primary sm:w-full" data-testid="hero-cta">
                {ctaLabel}
              </Link>
              {shop ? <p className="fine mt-3 max-w-prose">{shop.note}</p> : <RenewalNote offer={primaryOffer} priceCents={useFounding ? live.memberCents : live.trialRenewCents} />}
              <p className="mt-3">
                <Link href="#pricing" className="font-bold text-ink underline">
                  See both ways to start
                </Link>
              </p>
            </div>
            <ul className="mt-8 grid gap-3 sm:grid-cols-2">
              {[copy.trustBuilt, "A chair-based version of every session", "Big captions, big buttons, works on TV", "Cancel online anytime, no call needed"].map((t) => (
                <li key={t} className="flex gap-3 font-bold">
                  <span className="marker !bg-jade" aria-hidden="true" />
                  {t}
                </li>
              ))}
            </ul>
          </div>
          <div className="relative mx-auto w-full max-w-[480px] sm:pb-16">
            <PhoneSession />
            <div className="mt-6 flex justify-center sm:absolute sm:bottom-0 sm:right-0 sm:mt-0 sm:block">
              <ExampleStrengthCard />
            </div>
          </div>
        </div>
      </section>

      <Section tone="rice">
        <div className="grid gap-10 lg:grid-cols-[1fr_1.2fr]">
          <CharacterArt who="both" />
          <div>
            <h2 className="text-3xl sm:text-4xl">Yes, we are AI. Here is why that is good news for you.</h2>
            <p className="mt-5 max-w-prose">
              Chang Yin and Sun Yoon are characters our team created with AI. We tell you this up front because you deserve to know who you are learning from, and because some accounts online pretend their AI teachers are real. We never will.
            </p>
            <p className="mt-4 max-w-prose">
              What is real: the movements, the progressions, the recipes and the safety checks. Every session and recipe is built by our team from published exercise and nutrition guidelines for older adults, and we show our sources. When an AI video can&apos;t show a movement precisely enough, a real coach demonstrates it on screen.
            </p>
            <p className="mt-4 max-w-prose">
              Why characters at all? Because a patient teacher who never rushes you, shows up every single morning, and speaks slowly and clearly is exactly what most programs are missing. Chang Yin can do that 365 days a year. And on Wednesdays, a real human coach answers your questions live.
            </p>
            <Link href="/how-we-make-this" className="mt-5 inline-block font-bold text-jade underline">
              Read exactly how we make each session
            </Link>
          </div>
        </div>
      </Section>

      <Section>
        <h2 className="max-w-3xl text-3xl sm:text-4xl">Strength doesn&apos;t leave all at once. It leaves one chair, one stair, one jar lid at a time.</h2>
        <div className="mt-6 grid gap-8 lg:grid-cols-2">
          <div className="space-y-4">
            <p>
              Starting around age 30, most people lose muscle every decade, and the loss speeds up after 60. Leg power, the ability to move quickly, fades even faster than strength. That is why the first signs are small: pushing on the armrests to stand up, holding the rail on the stairs, asking someone else to open the jar.
            </p>
            <p>Balance works the same way. It fades quietly when nobody practises it, and it is one of the most trainable things there is: it often improves faster than strength. The simple answer is to train your legs and your balance, a little, often.</p>
          </div>
          <div>
            <h3 className="text-2xl">The good news is the part nobody says loudly enough.</h3>
            <p className="mt-3">
              Muscle still responds at 60, 70, 80 and beyond. In a well-known study, adults in their nineties who did supervised leg strength training for eight weeks more than doubled their leg strength. You do not need a gym. You need the right movements, in the right order, done most days, and a way to see it working.
            </p>
          </div>
        </div>
        <ul className="mt-8 grid gap-3 sm:grid-cols-2">
          {["Leg strength: standing up, getting off the floor, climbing stairs", "Balance: steadier on uneven ground, in the shower, in the dark", "Grip and upper body: jars, bags, grandchildren, suitcases", "Mobility and breath: turning to look behind you, reaching the top shelf, falling asleep calmer"].map((b) => (
            <li key={b} className="flex gap-3 text-lg">
              <span className="marker" aria-hidden="true" />
              {b}
            </li>
          ))}
        </ul>
        <p className="fine mt-6">Sources: Fiatarone et al., JAMA 1990; CDC STEADI 30-second chair stand and 4-stage balance test protocols.</p>
      </Section>

      <Section tone="rice">
        <h2 className="max-w-3xl text-3xl sm:text-4xl">Three things every other program for &ldquo;seniors&rdquo; gets wrong, and how we do it instead.</h2>
        <div className="mt-8 grid gap-6 md:grid-cols-3">
          {[
            ["Too gentle to change anything. Instead: real strength, started gently.", "Chair yoga alone won't make your legs stronger. Muscle needs a challenge. Every session has a strength part, and every week it gets a little harder, only when you are ready."],
            ["One level for everyone. Instead: four tracks that level with you.", "Your Daily Practice is set to Rebuild (chair-based), Steady, Strong or Iron, and moves you up when the reps get easy. Sore knee, sore back or low energy today? One button swaps in a modified version."],
            ["No way to know if it's working. Instead: a number you retest every month.", "Once a month, Chang Yin walks you through the Strength Age retest: how many times you can stand from a chair in 30 seconds, how long you can hold four balance positions, and four more simple at-home tests. Your number goes on your chart."],
          ].map(([h, b]) => (
            <div key={h} className="card">
              <h3 className="text-2xl">{h}</h3>
              <p className="mt-3">{b}</p>
            </div>
          ))}
        </div>
      </Section>

      <Section>
        <h2 className="text-3xl sm:text-4xl">Here is what tomorrow morning looks like.</h2>
        <ol className="mt-8 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
          {[
            ["7:30 am, a text from Chang Yin (AI coach)", "“Morning, Pat. Today: strength, 9 minutes.” One tap and your Daily Practice opens at your level. No passwords to remember."],
            ["The session", "Chang Yin counts every rep with you. Big captions. A timer you can see across the room. A pause button the size of a coaster."],
            ["Done", "A check mark on your calendar and your Strong Weeks count (with grace weeks, because life happens). Your 12-week program shows Week 3 of 12."],
            ["Wednesday", "A real human coach answers member questions live for 30 minutes."],
            ["Sunday", "Sun Yoon's three recipes and grocery list, and her message. Short, warm, and honest. She tells you when you skipped your walk."],
          ].map(([h, b]) => (
            <li key={h} className="card">
              <p className="font-display text-2xl">{h}</p>
              <p className="mt-2">{b}</p>
            </li>
          ))}
        </ol>
        <div className="mt-8 max-w-md">
          <Link href={primaryHref} className="btn-primary sm:w-full">
            {ctaLabel}
          </Link>
          {shop ? <p className="fine mt-3 max-w-prose">{shop.note}</p> : <RenewalNote offer={primaryOffer} priceCents={useFounding ? live.memberCents : live.trialRenewCents} />}
        </div>
      </Section>

      <Section id="begin" tone="cream">
        <h2 className="text-3xl sm:text-4xl">Where should I begin?</h2>
        <p className="mt-3 max-w-prose text-lg">Tap the sentence that sounds most like you. We&apos;ll show you the exact session to do tonight, and how you&apos;ll know it&apos;s helping.</p>
        <div className="mt-8 grid gap-4 md:grid-cols-2">
          {BEGIN.map((b) => (
            <details key={b.say} className="group card open:bg-rice">
              <summary className="flex min-h-[48px] cursor-pointer list-none items-start justify-between gap-4">
                <span className="font-display text-[24px] italic leading-snug">&ldquo;{b.say}&rdquo;</span>
                <span className="mt-1 flex-none rounded-full border-2 border-ink px-3 py-0.5 text-[16px] font-bold group-open:bg-ink group-open:text-rice">
                  <span className="group-open:hidden">Show</span>
                  <span className="hidden group-open:inline">Hide</span>
                </span>
              </summary>
              <dl className="mt-4 space-y-2">
                <div>
                  <dt className="font-bold">Start with</dt>
                  <dd>
                    {b.start}, {b.len}
                  </dd>
                </div>
                <div>
                  <dt className="font-bold">How you&apos;ll know it&apos;s working</dt>
                  <dd>{b.know}</dd>
                </div>
              </dl>
            </details>
          ))}
        </div>
        <div className="mt-8 flex flex-col gap-4 sm:flex-row sm:items-center">
          <p className="text-lg font-bold">Not sure? The free Strength Age Test picks for you.</p>
          <Link href="/quiz/strength-age" className="btn-jade">
            Find my Strength Age (free)
          </Link>
        </div>
      </Section>

      <Section tone="rice">
        <div className="grid items-center gap-10 lg:grid-cols-2">
          <div>
            <h2 className="text-3xl sm:text-4xl">What&apos;s your Strength Age?</h2>
            <p className="mt-4 max-w-prose">
              Your birthday gives you one age. Your legs and your balance give you another. Strength Age compares your results on two well-known tests, the 30-second chair stand and the 4-stage balance test (both standard fitness tests used in senior fitness research), with typical results for men and women at each age.
            </p>
            <p className="mt-4 max-w-prose">If you stand up more times than is typical for your age, your Strength Age is younger. If fewer, it&apos;s older. Either way, it&apos;s a starting line, not a verdict, and you retest every month.</p>
            <div className="mt-6 max-w-md">
              <Link href="/quiz/strength-age" className="btn-jade sm:w-full">
                Find my Strength Age (free, 3 minutes)
              </Link>
            </div>
          </div>
          <div className="card">
            <ExampleChart />
            <p className="fine mt-3">Strength Age is a motivational estimate based on published fitness norms. It is not a medical test or diagnosis.</p>
          </div>
        </div>
      </Section>

      <Section>
        <h2 className="text-3xl sm:text-4xl">Meet the two of them.</h2>
        <div className="mt-8 grid gap-8 md:grid-cols-2">
          <div>
            <CharacterArt who="chang" />
            <p className="mt-4">
              <strong>Chang Yin</strong> is 74, a retired welder who has trained in his California garage every morning for fourteen years, and he&apos;d like you to join him. He grew up in the Chinese community of Incheon, Korea, and blends modern strength training with the slow, careful Chinese movement practices of tai chi, qigong and baduanjin. &ldquo;Measure twice. Lift once.&rdquo; He counts every rep with you and never rushes.
            </p>
          </div>
          <div>
            <CharacterArt who="sun" />
            <p className="mt-4">
              <strong>Sun Yoon</strong> is his wife. She&apos;s 76, two years older, which she says makes her right. She&apos;s Korean, from Incheon, ran a lunch counter in California for decades, and is honest to a fault. She cooks cheap, high-protein, easy-to-chew food from both of their families: doenjang stew, seaweed soup, jajangmyeon on Sundays, congee, steamed fish, barley tea. She&apos;ll tell you your breakfast is too small. She&apos;s usually right.
            </p>
            <p className="fine mt-3">Korean women traditionally keep their own family name when they marry. That&apos;s why she&apos;s Sun Yoon, not &ldquo;Mrs. Chang.&rdquo; She will remind you.</p>
          </div>
        </div>
        <div className="mt-8 rounded-2xl border-2 border-ink bg-rice p-6">
          <p className="text-lg font-bold">
            Chang Yin and Sun Yoon are AI characters, and their life story is made up. They are not real people, not doctors, and not religious teachers. The practices and recipes are real. Each one is built from published guidelines for older adults.
          </p>
          <Link href="/how-we-make-this" className="mt-3 inline-block font-bold text-jade underline">
            How we make this, and the guidelines we use
          </Link>
        </div>
      </Section>

      <Section tone="rice">
        <h2 className="text-3xl sm:text-4xl">Everything you get in Strong Years.</h2>
        <ul className="card mt-8 space-y-4">
          {[
            ["Your Daily Practice", "a new 8–12 minute follow-along session every day, auto-levelled (Rebuild, Steady, Strong, Iron), with a sore knee / sore back / low energy button"],
            ["Six 12-week programs", "Strong at 70, Back Strong, Balance & Steady Feet, Gut Reset with Sun Yoon, Grip & Hands, Walk Stronger"],
            ["The monthly Strength Age retest", "with your personal chart"],
            ["Sun Yoon's Kitchen", "3 recipes every Sunday, a grocery list, and one remedy with an honest evidence grade"],
            ["A daily message from Chang Yin (AI coach)", "at the time you choose"],
            ["Ask Chang Yin / Ask Sun Yoon", "an AI coach chat that adapts exercises and recipes to you, with memory only if you turn it on"],
            ["Wednesday Live Q&A", "with a real human coach from our team, and a Sunday Premiere episode"],
            ["Large-print printables", "weekly plan, grocery list, exercise cards, fridge chart"],
            ["Doing it together?", `Add your partner for ${money(prices.partner)}/month, with their own level and progress`],
          ].map(([h, b]) => (
            <li key={h} className="flex gap-3">
              <span className="marker" aria-hidden="true" />
              <span>
                <strong>{h}:</strong> {b}
              </span>
            </li>
          ))}
        </ul>
        <h3 className="mt-10 text-2xl">What this is, and what it isn&apos;t.</h3>
        <p className="mt-3 max-w-prose">
          For comparison, a personal trainer once a week costs about $240–400 a month. A physical-therapy visit often means a $30–60 copay. A meal-planning app costs $10–15 a month. Strong Years is not physical therapy and it does not replace your doctor or a trainer who can watch you in person. It&apos;s what makes the other 29 days of the month count: less than one personal-training session a month, for a coach who shows up every single day.
        </p>
      </Section>

      <Section>
        <h2 className="text-3xl sm:text-4xl">We&apos;re new, so we won&apos;t show you reviews we don&apos;t have.</h2>
        <p className="mt-4 max-w-prose text-lg">
          Other accounts fill this space with quotes that may not be real. We&apos;d rather show you nothing than make something up. Try it, and if you like it, tell us, and we&apos;ll ask your permission to share your words here.
        </p>
        <p className="fine mt-3 font-bold">Every quote that appears here will be from a real member, shared with permission. We never pay for reviews or write them ourselves.</p>
      </Section>

      <Section tone="rice">
        <h2 className="text-3xl sm:text-4xl">Is this right for you?</h2>
        <div className="mt-8 grid gap-6 md:grid-cols-2">
          <div className="card">
            <h3 className="text-2xl">It&apos;s for you if:</h3>
            <ul className="mt-4 space-y-3">
              {["You're around 55 to 85 and want to stay strong enough to live on your own terms", "You'd rather do 10 minutes at home than drive to a gym", "You want someone patient to follow, not a loud instructor", "You'd like to see proof you're getting stronger", "You use a cane, have a replaced hip or knee, or haven't exercised in years (start on the Rebuild track, and check with your doctor first)"].map((x) => (
                <li key={x} className="flex gap-3">
                  <span className="marker !bg-jade" aria-hidden="true" />
                  {x}
                </li>
              ))}
            </ul>
          </div>
          <div className="card">
            <h3 className="text-2xl">It&apos;s not for you if:</h3>
            <ul className="mt-4 space-y-3">
              {["You're looking for a cure for a medical condition (we don't offer one, and anyone who does is not being honest with you)", "You're currently in rehab after surgery and haven't been cleared by your surgeon or physical therapist", "You want intense workouts; this is steady, safe progress"].map((x) => (
                <li key={x} className="flex gap-3">
                  <span className="marker" aria-hidden="true" />
                  {x}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </Section>

      <Section id="pricing" tone="cream">
        <h2 className="text-3xl sm:text-4xl">{trialOn ? "Two ways to start this week." : offer.founding ? "Become a founding member this week." : "Join this week."}</h2>
        <p className="mt-3 max-w-prose text-lg">{shop ? `Start with the starter books. Add the membership right after with one tap, ${money(shop.memberCents)} a month until you cancel. Cancel online in two screens at most.` : trialOn ? "Same membership, same everything inside. Pick the one that suits you. Both renew monthly until you cancel, and both cancel online in two screens at most." : `One membership, everything inside. ${fp} today, then ${fp} a month until you cancel. Cancel online in two screens at most.`}</p>
        <div className="mt-8">
          <PricingCards arm={arm} offer={offer} shop={shop} />
        </div>
        <OtherWaysToStart arm={arm} offer={offer} />
      </Section>

      <Section tone="rice">
        <h2 className="text-3xl sm:text-4xl">The 14-day money-back guarantee.</h2>
        <p className="mt-4 max-w-prose">
          {trialOn
            ? `Try Strong Years. If your first membership charge wasn't worth it to you, for any reason, tap Refund in your account or reply to any email, and we'll refund it. With the founding membership you have ${offerRules.guaranteeDaysFoundingArm} days from joining. With the $1 trial, the guarantee covers your first full charge, for 14 days from that charge. No forms, no questions, no returning anything.`
            : `Try Strong Years. If your first month wasn't worth it to you, for any reason, tap Refund in your account within ${offerRules.guaranteeDaysFoundingArm} days of joining, or reply to any email, and we'll refund the membership charge. No forms, no questions, no returning anything.`}{" "}
          One guarantee per person.
        </p>
      </Section>

      <Section>
        <h2 className="text-3xl sm:text-4xl">Questions people ask.</h2>
        <div className="mt-8 space-y-3">
          {FAQ.map(([q, a]) => (
            <details key={q} className="card group">
              <summary className="flex min-h-[48px] cursor-pointer list-none items-center justify-between gap-4 text-[22px] font-bold">
                {q}
                <span aria-hidden="true" className="flex-none text-[28px] leading-none group-open:rotate-45">
                  +
                </span>
              </summary>
              <p className="mt-3 max-w-prose">{a}</p>
            </details>
          ))}
        </div>
      </Section>

      <section className="bg-jade py-16 text-rice">
        <div className="wrap max-w-3xl text-center">
          <h2 className="text-3xl text-rice sm:text-4xl">Tomorrow morning, eight minutes. That&apos;s all we&apos;re asking.</h2>
          <p className="mt-4 text-lg text-rice">Pick your level, follow Chang Yin, and test your Strength Age on day one. If it isn&apos;t worth it, you get every penny back.</p>
          <div className="mx-auto mt-8 max-w-md">
            <Link href={primaryHref} className="btn bg-rice text-ink hover:bg-cream sm:w-full">
              {ctaLabel}
            </Link>
            <p className="mt-3 text-fine text-rice">
              {shop ? shop.note : primaryOffer === "trial" ? `Then ${money(live.trialRenewCents)}/month. Renews until you cancel. Cancel online anytime.` : `${fp} today, then ${fp}/month until you cancel. 14-day money-back guarantee. Cancel online anytime.`}
            </p>
          </div>
        </div>
      </section>
      <StickyBar href={primaryHref} label={ctaLabel} note={shop ? (shop.recurring ? (shop.trialDays ? `$0 for the membership today; ${money(shop.memberCents)} on day ${shop.trialDays}, then monthly. Cancel online anytime.` : `Then ${money(shop.memberCents)}/mo. Cancel online anytime.`) : "One time. Membership optional.") : primaryOffer === "trial" ? `Then ${money(live.trialRenewCents)}/mo. Cancel online anytime.` : `Renews ${fp}/mo. Cancel online anytime.`} />
    </>
  );
}
