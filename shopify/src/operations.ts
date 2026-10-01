/**
 * Every GraphQL document provision.ts can send. Admin GraphQL API 2026-07 (latest stable on
 * 2026-10-01 per shopify.dev/docs/api/usage/versioning; 2026-10 is the release candidate).
 * All documents were validated against the Admin schema with Shopify's validate_graphql_codeblocks
 * tool (results: test/fixtures/schema-validation.json). `npm run export-ops` writes them to
 * test/fixtures/operations.graphql for re-validation.
 */

export const OPS = {
  ShopContext: /* GraphQL */ `
query ShopContext {
  shop {
    id
    name
    currencyCode
    myshopifyDomain
    primaryDomain { url host }
    features { eligibleForSubscriptions sellsSubscriptions }
  }
  locations(first: 10) { nodes { id name isActive } }
  publications(first: 25) { nodes { id catalog { title } } }
}`,

  ProductByHandle: /* GraphQL */ `
query ProductByHandle($handle: String!) {
  productByIdentifier(identifier: { handle: $handle }) {
    id
    handle
    status
    requiresSellingPlan
    variants(first: 10) {
      nodes { id title price sku inventoryItem { id tracked } inventoryQuantity }
    }
    sellingPlanGroups(first: 10) {
      nodes {
        id
        name
        appId
        sellingPlans(first: 10) {
          nodes {
            id
            name
            billingPolicy { ... on SellingPlanRecurringBillingPolicy { interval intervalCount } }
          }
        }
      }
    }
  }
}`,

  ProductUpsert: /* GraphQL */ `
mutation ProductUpsert($input: ProductSetInput!, $identifier: ProductSetIdentifiers) {
  productSet(input: $input, identifier: $identifier, synchronous: true) {
    product {
      id
      handle
      status
      variants(first: 10) { nodes { id title price sku inventoryItem { id } } }
    }
    userErrors { field message code }
  }
}`,

  ProductUpdate: /* GraphQL */ `
mutation ProductUpdate($product: ProductUpdateInput!) {
  productUpdate(product: $product) {
    product { id status requiresSellingPlan }
    userErrors { field message }
  }
}`,

  PublishToOnlineStore: /* GraphQL */ `
mutation PublishToOnlineStore($id: ID!, $input: [PublicationInput!]!) {
  publishablePublish(id: $id, input: $input) {
    userErrors { field message }
  }
}`,

  UnpublishFromOnlineStore: /* GraphQL */ `
mutation UnpublishFromOnlineStore($id: ID!, $input: [PublicationInput!]!) {
  publishableUnpublish(id: $id, input: $input) {
    userErrors { field message }
  }
}`,

  CollectionByHandle: /* GraphQL */ `
query CollectionByHandle($handle: String!) {
  collectionByIdentifier(identifier: { handle: $handle }) { id handle title }
}`,

  CollectionCreate: /* GraphQL */ `
mutation CollectionCreate($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection { id handle }
    userErrors { field message }
  }
}`,

  CollectionUpdate: /* GraphQL */ `
mutation CollectionUpdate($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection { id handle }
    userErrors { field message }
  }
}`,

  InventorySetFounding: /* GraphQL */ `
mutation InventorySetFounding($input: InventorySetQuantitiesInput!) {
  inventorySetQuantities(input: $input) {
    inventoryAdjustmentGroup { reason changes { name delta } }
    userErrors { field message code }
  }
}`,

  InventoryAdjust: /* GraphQL */ `
mutation InventoryAdjust($input: InventoryAdjustQuantitiesInput!) {
  inventoryAdjustQuantities(input: $input) {
    inventoryAdjustmentGroup { reason changes { name delta } }
    userErrors { field message code }
  }
}`,

  VariantInventoryPolicy: /* GraphQL */ `
mutation VariantInventoryPolicy($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
  productVariantsBulkUpdate(productId: $productId, variants: $variants) {
    productVariants { id inventoryPolicy }
    userErrors { field message }
  }
}`,

  MetafieldDefinitionCreate: /* GraphQL */ `
mutation MetafieldDefinitionCreate($definition: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $definition) {
    createdDefinition { id namespace key ownerType }
    userErrors { field message code }
  }
}`,

  MetafieldsSet: /* GraphQL */ `
mutation MetafieldsSet($metafields: [MetafieldsSetInput!]!) {
  metafieldsSet(metafields: $metafields) {
    metafields { key namespace }
    userErrors { field message code }
  }
}`,

  DiscountByCode: /* GraphQL */ `
query DiscountByCode($code: String!) {
  codeDiscountNodeByCode(code: $code) { id }
}`,

  DiscountCodeCreate: /* GraphQL */ `
mutation DiscountCodeCreate($basicCodeDiscount: DiscountCodeBasicInput!) {
  discountCodeBasicCreate(basicCodeDiscount: $basicCodeDiscount) {
    codeDiscountNode { id }
    userErrors { field message code }
  }
}`,

  DiscountCodeUpdate: /* GraphQL */ `
mutation DiscountCodeUpdate($id: ID!, $basicCodeDiscount: DiscountCodeBasicInput!) {
  discountCodeBasicUpdate(id: $id, basicCodeDiscount: $basicCodeDiscount) {
    codeDiscountNode { id }
    userErrors { field message code }
  }
}`,

  WebhookList: /* GraphQL */ `
query WebhookList {
  webhookSubscriptions(first: 100) {
    nodes {
      id
      topic
      uri
    }
  }
}`,

  WebhookCreate: /* GraphQL */ `
mutation WebhookCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
  webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
    webhookSubscription { id topic uri }
    userErrors { field message }
  }
}`,

  WebhookUpdate: /* GraphQL */ `
mutation WebhookUpdate($id: ID!, $webhookSubscription: WebhookSubscriptionInput!) {
  webhookSubscriptionUpdate(id: $id, webhookSubscription: $webhookSubscription) {
    webhookSubscription { id topic uri }
    userErrors { field message }
  }
}`,

  PageByHandle: /* GraphQL */ `
query PageByHandle($query: String!) {
  pages(first: 1, query: $query) { nodes { id handle } }
}`,

  PageCreate: /* GraphQL */ `
mutation PageCreate($page: PageCreateInput!) {
  pageCreate(page: $page) {
    page { id handle }
    userErrors { field message code }
  }
}`,

  PageUpdate: /* GraphQL */ `
mutation PageUpdate($id: ID!, $page: PageUpdateInput!) {
  pageUpdate(id: $id, page: $page) {
    page { id handle }
    userErrors { field message code }
  }
}`,

  ShopPolicyUpdate: /* GraphQL */ `
mutation ShopPolicyUpdate($shopPolicy: ShopPolicyInput!) {
  shopPolicyUpdate(shopPolicy: $shopPolicy) {
    shopPolicy { id type }
    userErrors { field message code }
  }
}`,

  RedirectList: /* GraphQL */ `
query RedirectList($query: String!) {
  urlRedirects(first: 5, query: $query) { nodes { id path target } }
}`,

  RedirectCreate: /* GraphQL */ `
mutation RedirectCreate($urlRedirect: UrlRedirectInput!) {
  urlRedirectCreate(urlRedirect: $urlRedirect) {
    urlRedirect { id path target }
    userErrors { field message code }
  }
}`,

  RedirectUpdate: /* GraphQL */ `
mutation RedirectUpdate($id: ID!, $urlRedirect: UrlRedirectInput!) {
  urlRedirectUpdate(id: $id, urlRedirect: $urlRedirect) {
    urlRedirect { id path target }
    userErrors { field message code }
  }
}`,

  // App engine only (the custom app owns and bills these plans).
  SellingPlanGroupCreate: /* GraphQL */ `
mutation SellingPlanGroupCreate($input: SellingPlanGroupInput!, $resources: SellingPlanGroupResourceInput) {
  sellingPlanGroupCreate(input: $input, resources: $resources) {
    sellingPlanGroup { id sellingPlans(first: 10) { nodes { id name } } }
    userErrors { field message code }
  }
}`,

  SellingPlanGroupAddProducts: /* GraphQL */ `
mutation SellingPlanGroupAddProducts($id: ID!, $productIds: [ID!]!) {
  sellingPlanGroupAddProducts(id: $id, productIds: $productIds) {
    sellingPlanGroup { id }
    userErrors { field message code }
  }
}`,
} as const;

export type OpName = keyof typeof OPS;
