/**
 * Founding offer on the Thank you page (and Order status page) for Starter Books buyers.
 * Shown only when the order has no subscription line (members never see it). Links to the membership page,
 * where the full auto-renewal terms + unticked consent checkbox are. Never a cart permalink.
 */
import "@shopify/ui-extensions/preact";
import { render } from "preact";

export default function extension() {
  render(<FoundingOffer />, document.body);
}

function FoundingOffer() {
  const lines = (shopify.lines && shopify.lines.value) || [];
  const hasSubscription = lines.some((l) => l.merchandise && l.merchandise.sellingPlan);
  if (hasSubscription) return null;
  const settings = (shopify.settings && shopify.settings.value) || {};
  const price = settings.price || "$25";
  const base = settings.founding_url || `${shopify.shop.storefrontUrl}/products/founding-membership`;
  const url = `${base}?utm_source=shopify&utm_medium=thank_you&utm_campaign=founding_offer`;
  return (
    <s-section heading="Keep going with Chang Yin">
      <s-stack gap="base">
        <s-paragraph>
          Your books are on their way to your inbox. Want a new 8 to 12 minute session every day at your level, Sun Yoon's Sunday recipes and a monthly Strength Age retest?
        </s-paragraph>
        <s-paragraph>
          <s-text type="strong">Founding membership: {price} today for your first month, then {price} a month until you cancel.</s-text> Founding price locked for as long as you stay subscribed. 14-day money-back guarantee. Cancel online anytime.
        </s-paragraph>
        <s-button href={url} variant="primary">See the founding membership</s-button>
        <s-paragraph>Nothing is added unless you choose it on the next page. Chang Yin and Sun Yoon are AI characters.</s-paragraph>
      </s-stack>
    </s-section>
  );
}
