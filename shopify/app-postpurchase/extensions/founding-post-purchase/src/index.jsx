/**
 * Strong Years: one-click founding membership offer on the post-purchase page.
 *
 * Shows ONLY when Shopify can actually add a subscription to this order:
 *  - the order has a shipping address (destinationCountryCode set). Digital-only Starter Books orders have none,
 *    so for them Shopify cannot add a subscription here; those buyers get the Thank you page offer instead
 *    (extensions/founding-thank-you) plus the 3 onboarding emails.
 *  - the order doesn't already contain a subscription (Shopify can't add a second one post-purchase).
 *  - the server says the founding group is open and the buyer is not already a member.
 * For digital-only orders it offers the $9 Wall Plan (one-time, one click) if it isn't already in the order.
 *
 * Consent: the full auto-renewal terms are shown above the button, and Shopify's <BuyerConsent policy="subscriptions">
 * checkbox (unticked) must be ticked; applyChangeset is called with buyerConsentToSubscriptions.
 */
import React, { useState } from "react";
import {
  extend, render, useExtensionInput,
  BlockStack, Button, CalloutBanner, Heading, Layout, TextBlock, TextContainer, View, BuyerConsent, Separator,
} from "@shopify/post-purchase-ui-extensions-react";

// The members app hosts the two endpoints (shopify/app-postpurchase/server/*). Same origin as MEMBERS_APP_URL.
const APP_URL = "https://members.strongyears.com/api/shopify/post-purchase";

extend("Checkout::PostPurchase::ShouldRender", async ({ inputData, storage }) => {
  const res = await fetch(`${APP_URL}/offer`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${inputData.token}` },
    body: JSON.stringify({
      referenceId: inputData.initialPurchase.referenceId,
      hasShippingAddress: Boolean(inputData.initialPurchase.destinationCountryCode),
      lineItems: inputData.initialPurchase.lineItems.map((l) => ({ productId: l.product.id, variantId: l.product.variant.id, sellingPlanId: l.sellingPlan ? l.sellingPlan.id : null })),
    }),
  }).catch(() => null);
  const offer = res && res.ok ? await res.json() : null;
  if (!offer || !offer.kind) return { render: false };
  await storage.update(offer);
  return { render: true };
});

render("Checkout::PostPurchase::Render", () => <Offer />);

export function Offer() {
  const { storage, inputData, calculateChangeset, applyChangeset, done } = useExtensionInput();
  const offer = storage.initialData;
  const [consent, setConsent] = useState(false);
  const [consentError, setConsentError] = useState();
  const [loading, setLoading] = useState(false);
  const isSub = offer.kind === "founding";

  async function accept() {
    if (isSub && !consent) { setConsentError("Please tick the box to confirm the membership terms."); return; }
    setLoading(true);
    const token = await fetch(`${APP_URL}/sign-changeset`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${inputData.token}` },
      body: JSON.stringify({ referenceId: inputData.initialPurchase.referenceId, offerKind: offer.kind, consentTextSha256: offer.termsSha256 }),
    }).then((r) => r.json()).then((j) => j.token).catch(() => null);
    if (!token) { setLoading(false); done(); return; }
    await applyChangeset(token, isSub ? { buyerConsentToSubscriptions: consent } : undefined);
    done();
  }

  return (
    <BlockStack spacing="loose">
      <CalloutBanner title={isSub ? "Your order is confirmed. One optional offer." : "Your order is confirmed."}>
        {isSub ? "Nothing is added unless you choose it below." : "One optional add-on, then you're done."}
      </CalloutBanner>
      <Layout maxInlineSize={0.95}>
        <TextContainer>
          <Heading>{offer.heading}</Heading>
          {offer.body.map((p, i) => <TextBlock key={i}>{p}</TextBlock>)}
        </TextContainer>
      </Layout>
      <View border="base" padding="base" cornerRadius="base">
        <BlockStack spacing="tight">
          {offer.terms.map((t, i) => <TextBlock key={i} emphasized={i === 0}>{t}</TextBlock>)}
        </BlockStack>
      </View>
      {isSub ? (
        <BuyerConsent policy="subscriptions" checked={consent} onChange={(v) => { setConsent(v); setConsentError(undefined); }} error={consentError} />
      ) : null}
      <Button submit onPress={accept} loading={loading}>{offer.acceptLabel}</Button>
      <Separator />
      <Button subdued onPress={done} disabled={loading}>{offer.declineLabel}</Button>
      <TextBlock size="small">Chang Yin and Sun Yoon are AI characters. General fitness and nutrition education, not medical advice.</TextBlock>
    </BlockStack>
  );
}
