/**
 * Legal policies and content pages, generated from OFFER.md §0.1/§2.3/§3.4 and FUNNEL.md canonical policies + §5.5.
 * Copy rules (SAFETY_RULES.md): no outcome claims; "guarantee" appears only in "14-day money-back guarantee";
 * founding price is "locked for as long as you stay subscribed" (never "for life"); no fall/disease/mortality claims;
 * no "text CANCEL" while SMS is off; no reviewer claims (FALLBACK strings only until a reviewer signs).
 *
 * COUNSEL REVIEW REQUIRED before go-live (RUNBOOK step 17). These are plain-language drafts of OUR practices,
 * not legal advice.
 */

export interface LegalFacts {
  brand: string;
  companyLegalName: string;
  mailingAddress: string;
  supportEmail: string;
  billingPhone: string;
  domain: string;
  membersUrl: string;
  foundingCloseDate: string; // human readable, e.g. "January 9, 2027"
  foundingCap: number;
  foundingPrice: string; // "$25"
  standardPrice: string; // "$35"
  annualPrice: string; // "$249"
  essentialsPrice: string; // "$12"
  governingState: string;
  kitShipDays: string;
  smsEnabled: boolean;
  reviewerSigned: boolean;
  effectiveDate: string;
}

export const PLACEHOLDER_RE = /\{\{[A-Z0-9_]+\}\}/g;

const esc = (s: string) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");

function cancelMethods(f: LegalFacts): string {
  return `online in your account at <a href="https://${f.domain}/account">${esc(f.domain)}/account</a> (at most two screens: the last tap is on your subscription page on our store)${f.smsEnabled ? ", or by texting CANCEL" : ""}. Emailing us also works, but it is read by a person and can take up to one business day, so for a same-day cancel use your account`;
}

function reviewLine(f: LegalFacts): string {
  // Reviewer gate (FUNNEL.md): FALLBACK text until a credentialed reviewer has signed.
  return f.reviewerSigned
    ? "Sessions and recipes are reviewed by licensed professionals named on our How we make this page."
    : "Sessions and recipes are built from published exercise and nutrition guidelines for older adults.";
}

export function aiDisclosureHtml(f: LegalFacts): string {
  return `<p><strong>Chang Yin and Sun Yoon are AI characters</strong> created by the ${esc(f.brand)} team. Their life story (the welding, the garage, the fifty years of marriage) is fiction. They are not real people, not doctors, not physical therapists, not dietitians and not religious teachers. ${reviewLine(f)} Everything here is general fitness and nutrition education, not medical advice. Check with your doctor before starting new exercise.</p>`;
}

/** The plain-language summary box (FUNNEL.md §5.5 G) that sits on top of the membership policy. */
export function membershipSummaryHtml(f: LegalFacts): string {
  return `<div class="sy-summary">
<h2>The short version</h2>
<ul>
<li><strong>It renews automatically.</strong> A monthly membership is charged today and then every month on the same date until you cancel. A yearly membership is charged today and then every year until you cancel.</li>
<li><strong>Founding price:</strong> ${f.foundingPrice} a month, locked for as long as you stay subscribed (pauses included). If you cancel and rejoin later, you pay the price at that time.</li>
<li><strong>Cancel anytime</strong> ${cancelMethods(f)}. Nobody needs to call. You keep access until the end of the period you paid for.</li>
<li><strong>14-day money-back guarantee</strong> on your membership charge, once per person: ask within 14 days of the charge and we refund it in full.</li>
<li><strong>Reminders:</strong> we email you before every renewal charge (7 and 2 days before your first renewal, 3 days before each one after that, 30 days before a yearly renewal) and once a year with a summary of your plan.</li>
<li><strong>Price changes:</strong> we tell you by email exactly 30 days before any change, with a one-tap cancel link.</li>
<li><strong>Gifts</strong> are paid once and never renew.</li>
</ul>
</div>`;
}

export function membershipPolicyHtml(f: LegalFacts): string {
  return `${membershipSummaryHtml(f)}
<h2>Membership and cancellation policy</h2>
<p>Effective ${esc(f.effectiveDate)}. This policy covers every ${esc(f.brand)} membership sold at ${esc(f.domain)}. ${esc(f.brand)} is made by ${esc(f.companyLegalName)}, ${esc(f.mailingAddress)}.</p>

<h3>1. Plans and prices</h3>
<ul>
<li><strong>Founding membership:</strong> ${f.foundingPrice} charged today for your first month, then ${f.foundingPrice} every month until you cancel.</li>
<li><strong>Starter offer (where shown):</strong> $12 charged today for the Starter Books and your first founding month, then ${f.foundingPrice} every month until you cancel.</li>
<li><strong>Standard membership</strong> (after the founding group closes): ${f.standardPrice} charged today, then ${f.standardPrice} every month until you cancel.</li>
<li><strong>Founding annual</strong> (offered to founding members after their first renewal): ${f.annualPrice} charged today, then ${f.annualPrice} every year until you cancel.</li>
<li><strong>Essentials:</strong> ${f.essentialsPrice} a month until you cancel.</li>
<li><strong>Gift memberships:</strong> 3 months for $49 or 12 months for $119, paid once. They do not renew. Near the end of a gift, the person who received it can choose to continue on their own card, with new consent. Nobody is charged automatically.</li>
</ul>
<p>Prices are in US dollars. Sales tax is added where it applies. On your bank statement the charge appears as STRONGYEARS MEMBER.</p>

<h3 id="founding">2. The founding group</h3>
<p>Founding membership is open to the first ${f.foundingCap.toLocaleString("en-US")} members or until ${esc(f.foundingCloseDate)}, whichever comes first. The count is the real number of founding memberships whose first charge succeeded and was not refunded or charged back. It is never reset, extended or reopened. If someone takes a refund, their seat goes back. The live count is shown on the founding membership page. After the group closes, new members join at the standard price of ${f.standardPrice} a month, and that price is actually charged.</p>
<p>Your founding price stays the same for as long as you stay subscribed, including while your membership is paused. If you cancel and rejoin, you pay the price offered at that time.</p>

<h3>3. Your consent</h3>
<p>Before you pay, we show these terms directly above the button and ask you to tick a separate box that is not ticked for you. We keep a record of the exact terms you saw, the time, and the price, for at least three years.</p>

<h3>4. How to cancel</h3>
<p>Cancel ${cancelMethods(f)}. Cancelling stops all future charges immediately. You keep access until the end of the period you have paid for. We send a confirmation email right away. We never require a phone call to cancel; the billing line ${esc(f.billingPhone)} is for questions only.</p>
<p>You can also pause instead of cancelling. A paused membership is not charged and keeps your founding price.</p>

<h3>5. Refunds</h3>
<ul>
<li><strong>Membership:</strong> 14-day money-back guarantee on your membership charge, once per person (matched by email and payment card). Ask within 14 days of the charge, in your account or by replying to any email, and we refund that charge in full.</li>
<li><strong>Books, printables and other digital add-ons:</strong> refund on request within 14 days of purchase. Email ${esc(f.supportEmail)}.</li>
<li><strong>The Strong Years Kit:</strong> refund on request within 30 days, no return needed.</li>
<li><strong>Gift memberships:</strong> refund on request within 14 days of purchase if the gift has not been started.</li>
</ul>

<h3>6. Reminders and notices</h3>
<p>We email you before every renewal charge: 7 and 2 days before your first renewal, then 3 days before each monthly renewal after that, and 30 days before a yearly renewal. Every auto-renewing member gets a yearly summary of the plan, the price, how often it bills and how to cancel. If a price ever changes, we email you exactly 30 days before the change with a one-tap cancel link. Our payment system may also send its own reminder a few days before each charge.</p>

<h3>7. State automatic renewal laws</h3>
<p>We follow the automatic renewal laws of California, New York, Minnesota, Virginia and the other states that have them, and we apply the strictest rule to everyone, wherever you live. That means clear terms before you pay, your express consent, a confirmation email that repeats the terms and how to cancel, online cancellation through the same website you joined on, reminders before renewals, a yearly summary, and advance notice of price changes. This policy follows the federal Restore Online Shoppers' Confidence Act (ROSCA).</p>

<h3>8. Failed payments</h3>
<p>If a renewal payment fails, we retry it a few times over several days and email you a link to update your card. Your access continues while we retry.</p>

<h3>9. AI characters</h3>
${aiDisclosureHtml(f)}

<h3>10. Contact</h3>
<p>${esc(f.companyLegalName)}, ${esc(f.mailingAddress)}. Email ${esc(f.supportEmail)}. Billing questions ${esc(f.billingPhone)}.</p>`;
}

export function refundPolicyHtml(f: LegalFacts): string {
  return `<p><strong>Membership:</strong> 14-day money-back guarantee on your membership charge, once per person (matched by email and payment card). Ask within 14 days of the charge, in your account at ${esc(f.membersUrl)} or by replying to any email from us, and we refund that charge in full. If you also want to stop future charges, cancel ${cancelMethods(f)}.</p>
<p><strong>Books, printables and other digital add-ons:</strong> they are delivered instantly as downloads. Refund on request within 14 days of purchase: email ${esc(f.supportEmail)}. One refund per add-on.</p>
<p><strong>The Strong Years Kit:</strong> refund on request within 30 days of delivery. No return needed.</p>
<p><strong>Gift memberships:</strong> refund on request within 14 days of purchase if the gift has not been started.</p>
<p>Refunds go back to the original payment method. Banks usually show them within 5 to 10 business days.</p>
<p>Full details: <a href="https://${f.domain}/pages/membership-and-cancellation">Membership and cancellation policy</a>.</p>`;
}

export function subscriptionPolicyHtml(f: LegalFacts): string {
  return membershipPolicyHtml(f);
}

export function termsOfServiceHtml(f: LegalFacts): string {
  return `<p>Effective ${esc(f.effectiveDate)}. These terms are an agreement between you and ${esc(f.companyLegalName)} ("we"), ${esc(f.mailingAddress)}, for the ${esc(f.brand)} website at ${esc(f.domain)}, the members area at ${esc(f.membersUrl)}, and everything we sell.</p>
<h3>1. Who can use ${esc(f.brand)}</h3>
<p>You must be 18 or older to buy or to create a members account.</p>
<h3>2. What ${esc(f.brand)} is, and what it is not</h3>
<p>${esc(f.brand)} is general fitness and nutrition education: follow-along exercise sessions, recipes, printables and an AI coach chat. It is not medical care, physical therapy, a diagnosis or a treatment, and it does not replace your doctor or anyone who can examine you in person. Check with your doctor before starting new exercise, especially if you have a heart condition, high blood pressure, recent surgery, a joint replacement, osteoporosis or dizziness. Stop any exercise if you feel chest pain, dizziness or sharp pain. In an emergency, call 911.</p>
<h3>3. AI characters</h3>
${aiDisclosureHtml(f)}
<p>The member chat is an AI. It says so at the start of every conversation and again during long conversations. It does not give medical advice, does not change medications and does not provide therapy. If you write about harming yourself, it shows crisis resources: call or text 988 (Suicide &amp; Crisis Lifeline, free, 24/7), or call 911 in an emergency. Our crisis protocol is published at <a href="https://${f.domain}/pages/safety">${esc(f.domain)}/pages/safety</a>.</p>
<h3>4. Memberships, renewals and cancellation</h3>
<p>Memberships renew automatically until you cancel. Prices, renewal terms, cancellation, reminders and refunds are set out in our <a href="https://${f.domain}/pages/membership-and-cancellation">Membership and cancellation policy</a>, which is part of these terms. You can cancel ${cancelMethods(f)}.</p>
<h3>5. Digital products</h3>
<p>Books, printables and programs are licensed to you for personal, non-commercial use. Please don't resell or share the files publicly.</p>
<h3>6. Reviews and member stories</h3>
<p>We never write, buy or invent reviews or testimonials. We only show a member's words with their written permission.</p>
<h3>7. Your content and community rules</h3>
<p>Be kind in the community. We remove harassment, sales pitches and requests for money. There are no private messages between members.</p>
<h3>8. Limits</h3>
<p>To the extent the law allows, our total liability to you is limited to the amount you paid us in the 12 months before the claim. Nothing in these terms limits rights you have under consumer protection law that cannot be limited.</p>
<h3>9. Changes</h3>
<p>If we change these terms in a way that matters to you, we email you at least 30 days before the change takes effect.</p>
<h3>10. Law and contact</h3>
<p>These terms are governed by the laws of ${esc(f.governingState)} and applicable US federal law. Questions: ${esc(f.supportEmail)}, ${esc(f.billingPhone)}, ${esc(f.mailingAddress)}.</p>`;
}

export function privacyPolicyHtml(f: LegalFacts): string {
  return `<p>Effective ${esc(f.effectiveDate)}. ${esc(f.companyLegalName)} ("we") runs ${esc(f.domain)} and ${esc(f.membersUrl)}.</p>
<h3>What we collect</h3>
<ul>
<li><strong>Account and order details:</strong> name, email, billing details and order history. Payments are processed by Shopify; we never see your full card number.</li>
<li><strong>How you found us:</strong> the link you arrived from (for example utm tags, the post or page that sent you, and the keyword you commented). We use this to know which posts help people, and to pay affiliates.</li>
<li><strong>What you tell us in the app:</strong> your level, test scores, goals and anything you choose to tell the AI coach. Health-related details are consumer health data. We collect them only with your opt-in consent, use them only to run your plan, never sell them and never send them to advertising platforms.</li>
<li><strong>Device and usage data</strong> such as pages viewed and sessions completed.</li>
</ul>
<h3>How we use it</h3>
<p>To deliver your membership and downloads, send the emails you need (receipts, renewal reminders, the yearly summary), improve the program, prevent fraud and repeat refunds, and meet legal duties such as keeping consent records for automatic renewals.</p>
<h3>Advertising</h3>
<p>We may use advertising pixels to measure purchases. We send event names that don't describe health (for example "Purchase") and never send quiz answers, test scores or anything you tell the coach.</p>
<h3>Who we share it with</h3>
<p>Service providers that run the store and the members area (Shopify for checkout, our hosting and database providers, our email provider), under contracts that limit their use. We don't sell personal information.</p>
<h3>Your choices and rights</h3>
<p>You can see, correct, download or delete your data, see and delete what the AI coach remembers, and withdraw consent at any time in your account or by emailing ${esc(f.supportEmail)}. Residents of California, Washington, Nevada, Connecticut, Colorado, Virginia and other states have additional rights, which we honor for everyone.</p>
<h3>Age</h3>
<p>${esc(f.brand)} is for adults 18 and older.</p>
<h3>Contact</h3>
<p>${esc(f.companyLegalName)}, ${esc(f.mailingAddress)}, ${esc(f.supportEmail)}.</p>`;
}

export function shippingPolicyHtml(f: LegalFacts): string {
  return `<p><strong>Digital products and memberships</strong> are delivered instantly by email and in your members area. Nothing is shipped.</p>
<p><strong>The Strong Years Kit</strong> ships to US addresses only. Orders leave our warehouse within ${esc(f.kitShipDays)}. You get a tracking email when it ships. Refund on request within 30 days of delivery, no return needed.</p>`;
}

export function contactHtml(f: LegalFacts): string {
  return `<p>${esc(f.companyLegalName)}<br>${esc(f.mailingAddress)}<br>Email: ${esc(f.supportEmail)}<br>Billing questions: ${esc(f.billingPhone)}</p><p>A real person on our team reads messages 7:00 to 23:00 Eastern, 7 days a week.</p>`;
}

export interface PageSpec { handle: string; title: string; templateSuffix: string; bodyHtml: string; }

export function contentPages(f: LegalFacts): PageSpec[] {
  return [
    {
      handle: "membership-and-cancellation",
      title: "Membership and cancellation policy",
      templateSuffix: "legal",
      bodyHtml: membershipPolicyHtml(f),
    },
    {
      handle: "about-the-characters",
      title: "About Chang Yin and Sun Yoon",
      templateSuffix: "characters",
      bodyHtml: `<p><strong>Hi, we're AI.</strong> Chang Yin and Sun Yoon are AI characters created by a team of real people. Chang Yin is written as a 74-year-old retired welder who trains in his California garage. Sun Yoon is written as his wife, 76, who runs the kitchen and tells the truth about food. Their story is fiction, and we say so everywhere they appear: on every post, in every email, at the top of every page and at the start of every chat.</p>
<p><strong>Why AI characters?</strong> So we can make a new session every day, at four levels, with a chair-based version of everything, without pretending anyone is something they're not.</p>
<p><strong>Why a Chinese and Korean couple?</strong> Chang Yin draws on Chinese movement traditions such as tai chi and qigong, taught as exercise, combined with modern strength training. Sun Yoon draws on Korean home cooking: soups, fermented vegetables and banchan. We work with paid cultural reviewers from each heritage on names, food and settings. They are not monks, priests or healers, and nothing here is presented as ancient secret knowledge.</p>
<p><strong>What's real:</strong> the exercises, the progressions, the recipes and the research behind them. ${reviewLine(f)} Our sources are listed on <a href="/pages/how-we-make-this">How we make this</a>.</p>
<p><strong>What they will never do:</strong> claim to be human, claim to be a doctor or therapist, show you reviews we don't have, or tell you to change your medication.</p>
<p>General fitness and nutrition education, not medical advice. Check with your doctor before starting new exercise.</p>`,
    },
    {
      handle: "faq",
      title: "Questions",
      templateSuffix: "faq",
      bodyHtml: faqHtml(f),
    },
    {
      handle: "how-we-make-this",
      title: "How we make this",
      templateSuffix: "legal",
      bodyHtml: `<p>Every session, recipe and number on ${esc(f.brand)} starts from published research and guidelines for older adults. Each statistic carries an evidence ID that points to the study: who was studied, how many people, and how strong the evidence is. We grade evidence honestly: big reviews and guidelines first; small or observational studies are labelled as such and never presented as proof of cause and effect.</p>
<p>Every movement is shown with a support (a counter, a chair against the wall), an easier version, and a stop rule: stop if you feel chest pain, dizziness or sharp pain. Advanced moves Chang Yin demonstrates are labelled "Chang's level, not your starting point".</p>
<p>Every script passes an automated rules check and an AI review, and anything flagged goes to a person on our team before it is published.</p>
<p>${reviewLine(f)}</p>
<p>The team: ${esc(f.companyLegalName)}, ${esc(f.mailingAddress)}.</p>`,
    },
    {
      handle: "safety",
      title: "Safety and crisis protocol",
      templateSuffix: "legal",
      bodyHtml: `<p>The member chat ("Ask Chang Yin", "Ask Sun Yoon") is an AI. It tells you so at the start of every conversation and again at least every 3 hours of continuing conversation.</p>
<p><strong>If you're thinking about harming yourself, call or text 988</strong> (Suicide &amp; Crisis Lifeline, free, 24/7). <strong>If you're in danger or it's a medical emergency, call 911.</strong> For concerns about an older adult's safety, the Eldercare Locator is 1-800-677-1116.</p>
<p>Every message is checked for signs of self-harm, abuse or a medical emergency (chest pain, stroke signs, a fall with injury or a head strike). When one is found, the chat stops coaching, shows the resources above, logs the event and alerts our team. A real person on our team reads these messages 7:00 to 23:00 Eastern, 7 days a week. Outside those hours, the resources above are shown immediately and a person reads the message at 7:00 Eastern.</p>
<p>The chat never diagnoses, never changes medication, doses or timing, and never offers therapy. Grief, relationship and mental-health conversations get the resources above and a human.</p>
<p>If the AI service is unavailable, the chat goes offline and shows 988, 911, the Eldercare Locator and a way to reach a person.</p>`,
    },
    {
      handle: "welcome",
      title: "Your books are ready",
      templateSuffix: "welcome",
      bodyHtml: `<p>Your Starter Books are in your email and in your downloads. Start with Day 0 of the Strength Reset: six simple tests, about 15 minutes, next to a chair and a kitchen counter.</p>`,
    },
  ];
}

export function faqHtml(f: LegalFacts): string {
  const qa: Array<[string, string]> = [
    ["Is Chang Yin real?", "No. Chang Yin and Sun Yoon are AI characters created by our team, and their story is invented. What is real: the exercises, the progressions and the recipes, built from published exercise and nutrition guidelines for older adults."],
    ["What do I get with the Starter Books?", "Two large-print PDF books to keep: Chang Yin's 7-Day Strength Reset (seven follow-along sessions, most of them next to a chair and a counter) and Sun Yoon's Strong Kitchen. They download instantly and they never renew."],
    ["What happens after I join the membership?", `Your first month is charged today. If you do nothing, your membership continues at the same price every month on the same date, until you cancel. We email you before every renewal. Changed your mind within 14 days? You have a 14-day money-back guarantee on your membership charge, once per person.`],
    ["What is the founding price?", `${f.foundingPrice} a month, locked for as long as you stay subscribed, pauses included. Founding membership is open to the first ${f.foundingCap.toLocaleString("en-US")} members or until ${f.foundingCloseDate}, whichever comes first. After that, new members pay ${f.standardPrice} a month.`],
    ["How do I cancel?", `Cancel ${cancelMethods(f).replace(/<[^>]+>/g, "")}. Nobody will call you, and you never need to call us to cancel.`],
    ["Do I need equipment?", "No. A sturdy chair against a wall and a kitchen counter are enough. Some people add resistance loops after a few weeks."],
    ["Is this right for me?", "Strong Years is general fitness education for adults. It isn't physical therapy and doesn't replace your doctor. Check with your doctor before starting new exercise, especially with a heart condition, high blood pressure, recent surgery, a joint replacement, osteoporosis or dizziness. Every session has a chair-based version."],
    ["Can I give it to my mom or dad?", "Yes. Gift memberships are paid once (3 months for $49 or 12 months for $119) and never renew. Near the end, they can choose to continue on their own card."],
    ["Where are the reviews?", "We're new, so we won't show you reviews we don't have. Member words appear only once real members give us written permission."],
  ];
  return qa.map(([q, a]) => `<h3>${esc(q)}</h3><p>${a}</p>`).join("\n");
}

export interface PolicySpec { type: "REFUND_POLICY" | "PRIVACY_POLICY" | "TERMS_OF_SERVICE" | "SUBSCRIPTION_POLICY" | "SHIPPING_POLICY" | "CONTACT_INFORMATION"; body: string; }

export function shopPolicies(f: LegalFacts): PolicySpec[] {
  return [
    { type: "REFUND_POLICY", body: refundPolicyHtml(f) },
    { type: "SUBSCRIPTION_POLICY", body: subscriptionPolicyHtml(f) },
    { type: "TERMS_OF_SERVICE", body: termsOfServiceHtml(f) },
    { type: "PRIVACY_POLICY", body: privacyPolicyHtml(f) },
    { type: "SHIPPING_POLICY", body: shippingPolicyHtml(f) },
    { type: "CONTACT_INFORMATION", body: contactHtml(f) },
  ];
}
