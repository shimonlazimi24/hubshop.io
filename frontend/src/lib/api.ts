const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface FetchOptions extends RequestInit {
  token?: string;
}

async function apiFetch<T>(path: string, options: FetchOptions = {}): Promise<T> {
  const { token, headers: customHeaders, ...rest } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...((customHeaders as Record<string, string>) || {}),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${path}`, {
    headers,
    ...rest,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

// Auth
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export function register(data: {
  email: string;
  password: string;
  full_name: string;
  organization_name: string;
}): Promise<TokenResponse> {
  return apiFetch("/auth/register", { method: "POST", body: JSON.stringify(data) });
}

export function login(data: { email: string; password: string }): Promise<TokenResponse> {
  return apiFetch("/auth/login", { method: "POST", body: JSON.stringify(data) });
}

export function refreshTokens(refresh_token: string): Promise<TokenResponse> {
  return apiFetch("/auth/refresh", {
    method: "POST",
    body: JSON.stringify({ refresh_token }),
  });
}

export interface UserResponse {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
}

export function getMe(token: string): Promise<UserResponse> {
  return apiFetch("/auth/me", { token });
}

// Connect
export interface ConnectedAccount {
  id: string;
  platform: string;
  platform_account_id: string;
  platform_account_name: string | null;
  status: string;
  identity_group_id: string | null;
}

export function getAuthorizeUrl(
  platform: string,
  workspaceId: string,
  token: string
): Promise<{ authorize_url: string }> {
  return apiFetch(`/connect/${platform}/authorize?workspace_id=${workspaceId}`, { token });
}

export function listConnectedAccounts(
  workspaceId: string,
  token: string
): Promise<ConnectedAccount[]> {
  return apiFetch(`/connect/accounts?workspace_id=${workspaceId}`, { token });
}

// Commerce - Types
export interface Shop {
  id: string;
  shop_id: string;
  shop_name: string;
  region: string;
  last_product_sync_at: string | null;
  last_order_sync_at: string | null;
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface ProductSummary {
  id: string;
  platform_product_id: string;
  title: string;
  status: string;
  main_image_url: string | null;
  price_amount: string | null;
  currency: string | null;
  inventory_total: number;
  sku_count: number;
  created_at: string;
  updated_at: string;
}

export interface ProductSku {
  id: string;
  platform_sku_id: string;
  seller_sku: string | null;
  price_amount: string | null;
  inventory_quantity: number;
  sku_name: string | null;
}

export interface ProductDetail extends ProductSummary {
  skus: ProductSku[];
  detail_json: Record<string, unknown> | null;
}

export interface OrderSummary {
  id: string;
  platform_order_id: string;
  status: string;
  total_amount: string;
  currency: string;
  item_count: number;
  fulfillment_type: string | null;
  rts_sla: string | null;
  created_at: string;
  updated_at: string;
}

export interface OrderLineItem {
  id: string;
  platform_sku_id: string | null;
  product_name: string;
  quantity: number;
  unit_price: string;
  total_price: string;
}

export interface PackageInfo {
  id: string;
  platform_package_id: string;
  status: string;
  tracking_number: string | null;
  shipping_provider: string | null;
  created_at: string;
  updated_at: string;
}

export interface OrderDetail extends OrderSummary {
  line_items: OrderLineItem[];
  packages: PackageInfo[];
  detail_json: Record<string, unknown> | null;
}

export interface TimelineEvent {
  id: string;
  from_status: string | null;
  to_status: string;
  source: string;
  occurred_at: string;
}

export interface ReturnRequest {
  id: string;
  platform_return_id: string;
  order_id: string;
  return_type: string;
  status: string;
  reason: string | null;
  refund_amount: string | null;
  created_at: string;
  updated_at: string;
}

export interface RevenueSummary {
  total_revenue: string;
  total_orders: number;
  average_order_value: string;
  return_rate: number;
  period_start: string;
  period_end: string;
}

export interface RevenuePoint {
  date: string;
  revenue: string;
  order_count: number;
}

export interface TopProduct {
  product_id: string;
  title: string;
  total_revenue: string;
  total_quantity: number;
  main_image_url: string | null;
}

export interface OrderStatusDistribution {
  status: string;
  count: number;
  percentage: number;
}

// Commerce - Shops
export function listShops(workspaceId: string, token: string): Promise<Shop[]> {
  return apiFetch(`/commerce/shops?workspace_id=${workspaceId}`, { token });
}

export function syncShops(workspaceId: string, token: string): Promise<Shop[]> {
  return apiFetch(`/commerce/shops/sync?workspace_id=${workspaceId}`, {
    method: "POST",
    token,
  });
}

// Commerce - Products
export function listProducts(
  workspaceId: string,
  token: string,
  params?: { shop_id?: string; status_filter?: string; search?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<ProductSummary>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.shop_id) query.set("shop_id", params.shop_id);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.search) query.set("search", params.search);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/commerce/products?${query}`, { token });
}

export function getProduct(productId: string, token: string): Promise<ProductDetail> {
  return apiFetch(`/commerce/products/${productId}`, { token });
}

export function syncProducts(
  workspaceId: string,
  token: string,
  shopId?: string
): Promise<{ synced: number }> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (shopId) query.set("shop_id", shopId);
  return apiFetch(`/commerce/products/sync?${query}`, { method: "POST", token });
}

// Commerce - Orders
export function listOrders(
  workspaceId: string,
  token: string,
  params?: { shop_id?: string; status_filter?: string; date_from?: string; date_to?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<OrderSummary>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.shop_id) query.set("shop_id", params.shop_id);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.date_from) query.set("date_from", params.date_from);
  if (params?.date_to) query.set("date_to", params.date_to);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/commerce/orders?${query}`, { token });
}

export function getOrder(orderId: string, token: string): Promise<OrderDetail> {
  return apiFetch(`/commerce/orders/${orderId}`, { token });
}

export function getOrderTimeline(orderId: string, token: string): Promise<TimelineEvent[]> {
  return apiFetch(`/commerce/orders/${orderId}/timeline`, { token });
}

export function getOrderTracking(
  orderId: string,
  token: string
): Promise<{ tracking: Record<string, unknown>[] }> {
  return apiFetch(`/commerce/orders/${orderId}/tracking`, { token });
}

// Commerce - Fulfillment
export function shipPackage(
  data: { order_id: string; shipping_provider: string; tracking_number: string },
  token: string
): Promise<PackageInfo> {
  return apiFetch("/commerce/fulfillment/ship", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

// Commerce - Returns
export function listReturns(
  workspaceId: string,
  token: string,
  params?: { page?: number; page_size?: number }
): Promise<PaginatedResponse<ReturnRequest>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/commerce/returns?${query}`, { token });
}

export function approveReturn(returnId: string, token: string): Promise<ReturnRequest> {
  return apiFetch(`/commerce/returns/${returnId}/approve`, {
    method: "POST",
    token,
  });
}

export function rejectReturn(
  returnId: string,
  token: string,
  reason?: string
): Promise<ReturnRequest> {
  return apiFetch(`/commerce/returns/${returnId}/reject`, {
    method: "POST",
    body: JSON.stringify({ reason: reason || null }),
    token,
  });
}

// Commerce - Analytics
export function getCommerceSummary(
  workspaceId: string,
  token: string,
  days?: number
): Promise<RevenueSummary> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (days) query.set("days", String(days));
  return apiFetch(`/commerce/analytics/summary?${query}`, { token });
}

export function getRevenueTimeseries(
  workspaceId: string,
  token: string,
  days?: number
): Promise<RevenuePoint[]> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (days) query.set("days", String(days));
  return apiFetch(`/commerce/analytics/revenue?${query}`, { token });
}

export function getTopProducts(
  workspaceId: string,
  token: string,
  limit?: number
): Promise<TopProduct[]> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (limit) query.set("limit", String(limit));
  return apiFetch(`/commerce/analytics/top-products?${query}`, { token });
}

export function getOrderDistribution(
  workspaceId: string,
  token: string
): Promise<OrderStatusDistribution[]> {
  return apiFetch(`/commerce/analytics/order-distribution?workspace_id=${workspaceId}`, {
    token,
  });
}

// Advertising - Types
export interface AdAccount {
  id: string;
  advertiser_id: string;
  advertiser_name: string;
  currency: string | null;
  timezone: string | null;
  last_sync_at: string | null;
  created_at: string;
}

export interface CampaignSummary {
  id: string;
  platform_campaign_id: string;
  campaign_name: string;
  objective_type: string | null;
  budget_mode: string | null;
  budget: string | null;
  operation_status: string;
  secondary_status: string | null;
  created_at: string;
  updated_at: string;
}

export interface CampaignDetail extends CampaignSummary {
  detail_json: Record<string, unknown> | null;
}

export interface AdGroupSummary {
  id: string;
  platform_adgroup_id: string;
  adgroup_name: string;
  placement_type: string | null;
  bid_type: string | null;
  bid_amount: string | null;
  budget: string | null;
  optimization_goal: string | null;
  operation_status: string;
  created_at: string;
  updated_at: string;
}

export interface AdGroupDetail extends AdGroupSummary {
  targeting_json: Record<string, unknown> | null;
  detail_json: Record<string, unknown> | null;
}

export interface AdSummary {
  id: string;
  platform_ad_id: string;
  ad_name: string;
  ad_format: string | null;
  ad_text: string | null;
  call_to_action: string | null;
  landing_page_url: string | null;
  image_url: string | null;
  operation_status: string;
  created_at: string;
  updated_at: string;
}

export interface AdDetail extends AdSummary {
  detail_json: Record<string, unknown> | null;
}

export interface ReportRow {
  dimensions: Record<string, string>;
  metrics: Record<string, string | number>;
}

export interface ReportResponse {
  rows: ReportRow[];
  total_rows: number;
}

// Advertising - Ad Accounts
export function listAdAccounts(workspaceId: string, token: string): Promise<AdAccount[]> {
  return apiFetch(`/ads/accounts?workspace_id=${workspaceId}`, { token });
}

export function getAdAccount(adAccountId: string, token: string): Promise<AdAccount> {
  return apiFetch(`/ads/accounts/${adAccountId}`, { token });
}

export function syncAdAccounts(
  workspaceId: string,
  token: string
): Promise<{ synced: number }> {
  return apiFetch(`/ads/accounts/sync?workspace_id=${workspaceId}`, {
    method: "POST",
    token,
  });
}

// Advertising - Campaigns
export function listCampaigns(
  workspaceId: string,
  token: string,
  params?: {
    ad_account_id?: string;
    objective?: string;
    status_filter?: string;
    search?: string;
    page?: number;
    page_size?: number;
  }
): Promise<PaginatedResponse<CampaignSummary>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.ad_account_id) query.set("ad_account_id", params.ad_account_id);
  if (params?.objective) query.set("objective", params.objective);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.search) query.set("search", params.search);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/ads/campaigns?${query}`, { token });
}

export function getCampaign(campaignId: string, token: string): Promise<CampaignDetail> {
  return apiFetch(`/ads/campaigns/${campaignId}`, { token });
}

export function createCampaign(
  workspaceId: string,
  data: {
    ad_account_id: string;
    campaign_name: string;
    objective_type: string;
    budget_mode: string;
    budget?: string;
  },
  token: string
): Promise<CampaignDetail> {
  return apiFetch(`/ads/campaigns?workspace_id=${workspaceId}`, {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function updateCampaignStatus(
  campaignId: string,
  operationStatus: string,
  token: string
): Promise<CampaignDetail> {
  return apiFetch(`/ads/campaigns/${campaignId}/status`, {
    method: "POST",
    body: JSON.stringify({ operation_status: operationStatus }),
    token,
  });
}

export function syncCampaigns(
  workspaceId: string,
  token: string,
  adAccountId?: string
): Promise<{ synced: number }> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (adAccountId) query.set("ad_account_id", adAccountId);
  return apiFetch(`/ads/campaigns/sync?${query}`, { method: "POST", token });
}

// Advertising - Ad Groups
export function listAdGroups(
  workspaceId: string,
  token: string,
  params?: {
    campaign_id?: string;
    ad_account_id?: string;
    status_filter?: string;
    page?: number;
    page_size?: number;
  }
): Promise<PaginatedResponse<AdGroupSummary>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.campaign_id) query.set("campaign_id", params.campaign_id);
  if (params?.ad_account_id) query.set("ad_account_id", params.ad_account_id);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/ads/ad-groups?${query}`, { token });
}

export function getAdGroup(adGroupId: string, token: string): Promise<AdGroupDetail> {
  return apiFetch(`/ads/ad-groups/${adGroupId}`, { token });
}

export function updateAdGroupStatus(
  adGroupId: string,
  operationStatus: string,
  token: string
): Promise<AdGroupDetail> {
  return apiFetch(`/ads/ad-groups/${adGroupId}/status`, {
    method: "POST",
    body: JSON.stringify({ operation_status: operationStatus }),
    token,
  });
}

export function syncAdGroups(
  workspaceId: string,
  token: string,
  adAccountId?: string
): Promise<{ synced: number }> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (adAccountId) query.set("ad_account_id", adAccountId);
  return apiFetch(`/ads/ad-groups/sync?${query}`, { method: "POST", token });
}

// Advertising - Ads (Creatives)
export function listAds(
  workspaceId: string,
  token: string,
  params?: {
    adgroup_id?: string;
    ad_account_id?: string;
    status_filter?: string;
    page?: number;
    page_size?: number;
  }
): Promise<PaginatedResponse<AdSummary>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.adgroup_id) query.set("adgroup_id", params.adgroup_id);
  if (params?.ad_account_id) query.set("ad_account_id", params.ad_account_id);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/ads/creatives?${query}`, { token });
}

export function getAd(adId: string, token: string): Promise<AdDetail> {
  return apiFetch(`/ads/creatives/${adId}`, { token });
}

export function updateAdStatus(
  adId: string,
  operationStatus: string,
  token: string
): Promise<AdDetail> {
  return apiFetch(`/ads/creatives/${adId}/status`, {
    method: "POST",
    body: JSON.stringify({ operation_status: operationStatus }),
    token,
  });
}

export function syncAds(
  workspaceId: string,
  token: string,
  adAccountId?: string
): Promise<{ synced: number }> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (adAccountId) query.set("ad_account_id", adAccountId);
  return apiFetch(`/ads/creatives/sync?${query}`, { method: "POST", token });
}

// Advertising - Reports
export function getSyncReport(
  data: {
    ad_account_id: string;
    report_type?: string;
    data_level?: string;
    date_start: string;
    date_end: string;
    metrics?: string[];
    dimensions?: string[];
  },
  token: string
): Promise<ReportResponse> {
  return apiFetch("/ads/reports/sync", {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

// Advertising - Audiences
export interface Audience {
  id: string;
  platform_audience_id: string;
  name: string;
  audience_type: string;
  size: number | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export function listAudiences(
  workspaceId: string,
  token: string,
  params?: { ad_account_id?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<Audience>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.ad_account_id) query.set("ad_account_id", params.ad_account_id);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/ads/audiences?${query}`, { token });
}

export function createCustomAudience(
  data: { ad_account_id: string; name: string; file_paths?: string[] },
  token: string
): Promise<Audience> {
  return apiFetch("/ads/audiences/custom", { method: "POST", body: JSON.stringify(data), token });
}

export function createLookalikeAudience(
  data: { ad_account_id: string; name: string; source_audience_id: string; lookalike_ratio?: number },
  token: string
): Promise<Audience> {
  return apiFetch("/ads/audiences/lookalike", { method: "POST", body: JSON.stringify(data), token });
}

export function deleteAudience(audienceId: string, token: string): Promise<void> {
  return apiFetch(`/ads/audiences/${audienceId}`, { method: "DELETE", token });
}

export function syncAudiences(
  workspaceId: string,
  token: string,
  adAccountId?: string
): Promise<{ synced: number }> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (adAccountId) query.set("ad_account_id", adAccountId);
  return apiFetch(`/ads/audiences/sync?${query}`, { method: "POST", token });
}

// Advertising - Pixels
export interface Pixel {
  id: string;
  platform_pixel_id: string;
  name: string;
  pixel_code: string | null;
  created_at: string;
  updated_at: string;
}

export function listPixels(
  workspaceId: string,
  token: string,
  params?: { ad_account_id?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<Pixel>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.ad_account_id) query.set("ad_account_id", params.ad_account_id);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/ads/pixels?${query}`, { token });
}

export function createPixel(
  data: { ad_account_id: string; name: string },
  token: string
): Promise<Pixel> {
  return apiFetch("/ads/pixels", { method: "POST", body: JSON.stringify(data), token });
}

export function getPixelCode(pixelId: string, token: string): Promise<{ pixel_code: string }> {
  return apiFetch(`/ads/pixels/${pixelId}/code`, { token });
}

// Advertising - Catalogs
export interface Catalog {
  id: string;
  platform_catalog_id: string;
  name: string;
  product_count: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export function listCatalogs(
  workspaceId: string,
  token: string,
  params?: { ad_account_id?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<Catalog>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.ad_account_id) query.set("ad_account_id", params.ad_account_id);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/ads/catalogs?${query}`, { token });
}

export function createCatalog(
  data: { ad_account_id: string; name: string },
  token: string
): Promise<Catalog> {
  return apiFetch("/ads/catalogs", { method: "POST", body: JSON.stringify(data), token });
}

export function addProductsToCatalog(
  catalogId: string,
  data: { product_ids: string[] },
  token: string
): Promise<{ added: number }> {
  return apiFetch(`/ads/catalogs/${catalogId}/products`, { method: "POST", body: JSON.stringify(data), token });
}

export function syncCatalogs(
  workspaceId: string,
  token: string,
  adAccountId?: string
): Promise<{ synced: number }> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (adAccountId) query.set("ad_account_id", adAccountId);
  return apiFetch(`/ads/catalogs/sync?${query}`, { method: "POST", token });
}

// Content - Types
export interface VideoSummary {
  id: string;
  platform_video_id: string;
  title: string | null;
  description: string | null;
  cover_url: string | null;
  duration: number | null;
  status: string;
  view_count: number;
  like_count: number;
  comment_count: number;
  share_count: number;
  create_time: string | null;
  created_at: string;
  updated_at: string;
}

export interface VideoDetail extends VideoSummary {
  video_url: string | null;
  embed_link: string | null;
  detail_json: Record<string, unknown> | null;
}

export interface VideoMetrics {
  id: string;
  date: string;
  views: number;
  likes: number;
  comments: number;
  shares: number;
  avg_watch_time: number | null;
  reach: number | null;
}

export interface PublishJob {
  id: string;
  publish_id: string;
  title: string | null;
  video_url: string | null;
  privacy_level: string;
  status: string;
  platform_video_id: string | null;
  error_message: string | null;
  created_at: string;
  updated_at: string;
}

export interface CreatorInfo {
  creator_username: string | null;
  creator_avatar_url: string | null;
  privacy_level_options: string[];
  comment_disabled: boolean;
  duet_disabled: boolean;
  stitch_disabled: boolean;
  max_video_post_duration_sec: number;
}

export interface CalendarEntry {
  date: string;
  video_count: number;
  videos: VideoSummary[];
}

// Content - Videos
export function listVideos(
  workspaceId: string,
  token: string,
  params?: { status_filter?: string; search?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<VideoSummary>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.search) query.set("search", params.search);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/content/videos?${query}`, { token });
}

export function getVideo(videoId: string, token: string): Promise<VideoDetail> {
  return apiFetch(`/content/videos/${videoId}`, { token });
}

export function getVideoMetrics(videoId: string, token: string): Promise<VideoMetrics[]> {
  return apiFetch(`/content/videos/${videoId}/metrics`, { token });
}

export function syncVideos(workspaceId: string, token: string): Promise<{ synced: number }> {
  return apiFetch(`/content/videos/sync?workspace_id=${workspaceId}`, { method: "POST", token });
}

export function getCreatorInfo(workspaceId: string, token: string): Promise<CreatorInfo> {
  return apiFetch(`/content/creator-info?workspace_id=${workspaceId}`, { token });
}

// Content - Publish
export function publishVideo(
  workspaceId: string,
  data: {
    video_url: string;
    title?: string;
    privacy_level?: string;
    disable_duet?: boolean;
    disable_comment?: boolean;
    disable_stitch?: boolean;
    brand_content_toggle?: boolean;
    brand_organic_toggle?: boolean;
  },
  token: string
): Promise<PublishJob> {
  return apiFetch(`/content/publish?workspace_id=${workspaceId}`, {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function listPublishJobs(
  workspaceId: string,
  token: string,
  params?: { status_filter?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<PublishJob>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/content/publish/jobs?${query}`, { token });
}

export function getPublishStatus(publishId: string, workspaceId: string, token: string): Promise<PublishJob> {
  return apiFetch(`/content/publish/${publishId}/status?workspace_id=${workspaceId}`, { token });
}

// Content - Calendar
export function getCalendar(
  workspaceId: string,
  year: number,
  month: number,
  token: string
): Promise<CalendarEntry[]> {
  return apiFetch(`/content/calendar?workspace_id=${workspaceId}&year=${year}&month=${month}`, { token });
}

// Commerce - Affiliate
export interface AffiliateProduct {
  id: string;
  product_id: string;
  commission_rate: string | null;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface OpenCollaboration {
  id: string;
  product_id: string;
  commission_rate: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface TargetCollaboration {
  id: string;
  product_id: string;
  creator_id: string;
  commission_rate: string;
  status: string;
  invite_status: string;
  created_at: string;
  updated_at: string;
}

export function listAffiliateProducts(
  workspaceId: string,
  token: string,
  params?: { shop_id?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<AffiliateProduct>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.shop_id) query.set("shop_id", params.shop_id);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/commerce/affiliate/products?${query}`, { token });
}

export function addToMarketplace(
  data: { shop_id: string; product_id: string; commission_rate: string },
  token: string
): Promise<AffiliateProduct> {
  return apiFetch("/commerce/affiliate/marketplace/add", { method: "POST", body: JSON.stringify(data), token });
}

export function removeFromMarketplace(productId: string, shopId: string, token: string): Promise<void> {
  return apiFetch(`/commerce/affiliate/marketplace/remove?product_id=${productId}&shop_id=${shopId}`, {
    method: "POST",
    token,
  });
}

export function listCollaborations(
  workspaceId: string,
  token: string,
  params?: { page?: number; page_size?: number }
): Promise<PaginatedResponse<OpenCollaboration>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/commerce/affiliate/collaborations?${query}`, { token });
}

export function createOpenCollaboration(
  data: { shop_id: string; product_id: string; commission_rate: string },
  token: string
): Promise<OpenCollaboration> {
  return apiFetch("/commerce/affiliate/collaborations/open", { method: "POST", body: JSON.stringify(data), token });
}

export function createTargetCollaboration(
  data: { shop_id: string; product_id: string; creator_id: string; commission_rate: string },
  token: string
): Promise<TargetCollaboration> {
  return apiFetch("/commerce/affiliate/collaborations/target", { method: "POST", body: JSON.stringify(data), token });
}

// Commerce - Promotions
export interface Promotion {
  id: string;
  platform_activity_id: string;
  promotion_type: string;
  title: string;
  status: string;
  start_time: string | null;
  end_time: string | null;
  discount_type: string | null;
  discount_value: string | null;
  created_at: string;
  updated_at: string;
}

export function listPromotions(
  workspaceId: string,
  token: string,
  params?: { shop_id?: string; status_filter?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<Promotion>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.shop_id) query.set("shop_id", params.shop_id);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/commerce/promotions?${query}`, { token });
}

export function createPromotion(
  data: {
    shop_id: string;
    title: string;
    promotion_type: string;
    start_time?: string;
    end_time?: string;
    discount_type?: string;
    discount_value?: string;
    product_ids?: string[];
  },
  token: string
): Promise<Promotion> {
  return apiFetch("/commerce/promotions", { method: "POST", body: JSON.stringify(data), token });
}

export function deactivatePromotion(promotionId: string, token: string): Promise<Promotion> {
  return apiFetch(`/commerce/promotions/${promotionId}/deactivate`, { method: "POST", token });
}

export function syncPromotions(
  workspaceId: string,
  shopId: string,
  token: string
): Promise<{ synced: number }> {
  return apiFetch(`/commerce/promotions/sync?workspace_id=${workspaceId}&shop_id=${shopId}`, {
    method: "POST",
    token,
  });
}

// Commerce - Finance
export interface Settlement {
  id: string;
  platform_settlement_id: string;
  amount: string;
  currency: string;
  status: string;
  period_start: string | null;
  period_end: string | null;
  created_at: string;
  updated_at: string;
}

export interface Transaction {
  id: string;
  platform_transaction_id: string;
  transaction_type: string;
  amount: string;
  currency: string;
  order_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface Payment {
  id: string;
  platform_payment_id: string;
  amount: string;
  currency: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export function listSettlements(
  workspaceId: string,
  token: string,
  params?: { shop_id?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<Settlement>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.shop_id) query.set("shop_id", params.shop_id);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/commerce/finance/settlements?${query}`, { token });
}

export function listTransactions(
  workspaceId: string,
  token: string,
  params?: { shop_id?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<Transaction>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.shop_id) query.set("shop_id", params.shop_id);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/commerce/finance/transactions?${query}`, { token });
}

export function listPayments(
  workspaceId: string,
  token: string,
  params?: { shop_id?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<Payment>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.shop_id) query.set("shop_id", params.shop_id);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/commerce/finance/payments?${query}`, { token });
}

// Commerce - Customer Service
export function listConversations(
  workspaceId: string,
  shopId: string,
  token: string
): Promise<{ conversations: Record<string, unknown>[] }> {
  return apiFetch(`/commerce/conversations?workspace_id=${workspaceId}&shop_id=${shopId}`, { token });
}

export function getConversationMessages(
  conversationId: string,
  workspaceId: string,
  shopId: string,
  token: string
): Promise<{ messages: Record<string, unknown>[] }> {
  return apiFetch(
    `/commerce/conversations/${conversationId}/messages?workspace_id=${workspaceId}&shop_id=${shopId}`,
    { token }
  );
}

export function sendMessage(
  conversationId: string,
  workspaceId: string,
  shopId: string,
  content: string,
  token: string
): Promise<Record<string, unknown>> {
  return apiFetch(
    `/commerce/conversations/${conversationId}/messages?workspace_id=${workspaceId}&shop_id=${shopId}`,
    { method: "POST", body: JSON.stringify({ content }), token }
  );
}

// Creators - Types
export interface CreatorSummary {
  id: string;
  platform_creator_id: string;
  username: string | null;
  display_name: string | null;
  avatar_url: string | null;
  follower_count: number;
  tier: string | null;
  engagement_rate: string | null;
  is_saved: boolean;
  created_at: string;
}

export interface CreatorDetail extends CreatorSummary {
  bio: string | null;
  following_count: number;
  likes_count: number;
  video_count: number;
  categories: Record<string, unknown> | null;
  audience_demographics: Record<string, unknown> | null;
  detail_json: Record<string, unknown> | null;
  updated_at: string;
}

export interface CreatorCampaign {
  id: string;
  name: string;
  description: string | null;
  status: string;
  budget: string | null;
  start_date: string | null;
  end_date: string | null;
  target_categories: Record<string, unknown> | null;
  requirements: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface CreatorInvitation {
  id: string;
  campaign_id: string;
  creator_id: string;
  status: string;
  message: string | null;
  offered_amount: string | null;
  responded_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContentAuthorization {
  id: string;
  creator_id: string;
  platform_video_id: string | null;
  authorization_code: string | null;
  status: string;
  expires_at: string | null;
  created_at: string;
  updated_at: string;
}

// Creators - Discovery (via TTCM API)
export function discoverCreators(
  workspaceId: string,
  data: { query?: string; min_followers?: number; max_followers?: number; categories?: string[] },
  token: string
): Promise<{ creators: Record<string, unknown>[] }> {
  return apiFetch(`/creators/discover?workspace_id=${workspaceId}`, {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

// Creators - Profiles (locally saved)
export function listCreatorProfiles(
  workspaceId: string,
  token: string,
  params?: { is_saved?: boolean; tier?: string; search?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<CreatorSummary>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.is_saved !== undefined) query.set("is_saved", String(params.is_saved));
  if (params?.tier) query.set("tier", params.tier);
  if (params?.search) query.set("search", params.search);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/creators/profiles?${query}`, { token });
}

export function getCreator(creatorId: string, token: string): Promise<CreatorDetail> {
  return apiFetch(`/creators/profiles/${creatorId}`, { token });
}

export function saveCreator(creatorId: string, isSaved: boolean, token: string): Promise<CreatorSummary> {
  return apiFetch(`/creators/profiles/${creatorId}/save?is_saved=${isSaved}`, { method: "POST", token });
}

// Creators - Campaigns
export function listCreatorCampaigns(
  workspaceId: string,
  token: string,
  params?: { status_filter?: string; page?: number; page_size?: number }
): Promise<PaginatedResponse<CreatorCampaign>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  if (params?.page) query.set("page", String(params.page));
  if (params?.page_size) query.set("page_size", String(params.page_size));
  return apiFetch(`/creators/campaigns?${query}`, { token });
}

export function createCreatorCampaign(
  workspaceId: string,
  data: {
    name: string;
    description?: string;
    budget?: string;
    start_date?: string;
    end_date?: string;
    target_categories?: string[];
    requirements?: Record<string, unknown>;
  },
  token: string
): Promise<CreatorCampaign> {
  return apiFetch(`/creators/campaigns?workspace_id=${workspaceId}`, {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function getCreatorCampaign(campaignId: string, token: string): Promise<CreatorCampaign> {
  return apiFetch(`/creators/campaigns/${campaignId}`, { token });
}

export function updateCreatorCampaign(
  campaignId: string,
  data: { name?: string; description?: string; status?: string; budget?: string },
  token: string
): Promise<CreatorCampaign> {
  return apiFetch(`/creators/campaigns/${campaignId}`, {
    method: "PUT",
    body: JSON.stringify(data),
    token,
  });
}

// Creators - Invitations
export function inviteCreator(
  campaignId: string,
  data: { creator_id: string; message?: string; offered_amount?: string },
  token: string
): Promise<CreatorInvitation> {
  return apiFetch(`/creators/campaigns/${campaignId}/invite`, {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function listInvitations(
  campaignId: string,
  token: string,
  params?: { status_filter?: string }
): Promise<CreatorInvitation[]> {
  const query = new URLSearchParams();
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  return apiFetch(`/creators/campaigns/${campaignId}/invitations?${query}`, { token });
}

// Creators - Spark Ads (Content Authorization)
export function requestSparkAdAuthorization(
  workspaceId: string,
  data: { creator_id: string; platform_video_id: string },
  token: string
): Promise<ContentAuthorization> {
  return apiFetch(`/creators/spark-ads/authorize?workspace_id=${workspaceId}`, {
    method: "POST",
    body: JSON.stringify(data),
    token,
  });
}

export function listSparkAds(
  workspaceId: string,
  token: string,
  params?: { creator_id?: string; status_filter?: string }
): Promise<ContentAuthorization[]> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.creator_id) query.set("creator_id", params.creator_id);
  if (params?.status_filter) query.set("status_filter", params.status_filter);
  return apiFetch(`/creators/spark-ads/authorizations?${query}`, { token });
}

// Analytics
export interface KpiOverview {
  total_orders: number;
  active_campaigns: number;
  total_videos: number;
  total_views: number;
  saved_creators: number;
}

export function getKpiOverview(workspaceId: string, token: string): Promise<KpiOverview> {
  return apiFetch(`/analytics/overview?workspace_id=${workspaceId}`, { token });
}

export interface AnalyticsOverview {
  total_revenue: string;
  total_orders: number;
  total_ad_spend: string;
  roas: string;
  total_video_views: number;
  total_followers: number;
  period_days: number;
}

export function getAnalyticsOverview(
  workspaceId: string,
  token: string,
  days?: number
): Promise<AnalyticsOverview> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (days) query.set("days", String(days));
  return apiFetch(`/analytics/overview?${query}`, { token });
}

export function getRevenueVsSpend(
  workspaceId: string,
  token: string,
  days?: number
): Promise<{ date: string; revenue: string; spend: string }[]> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (days) query.set("days", String(days));
  return apiFetch(`/analytics/revenue-vs-spend?${query}`, { token });
}

export function getContentPerformance(
  workspaceId: string,
  token: string
): Promise<Record<string, unknown>[]> {
  return apiFetch(`/analytics/content-performance?workspace_id=${workspaceId}`, { token });
}

export function getPlatformHealth(
  workspaceId: string,
  token: string
): Promise<{ platform: string; status: string; last_sync: string | null }[]> {
  return apiFetch(`/analytics/platform-health?workspace_id=${workspaceId}`, { token });
}

export function getTopPerformers(
  workspaceId: string,
  token: string,
  limit?: number
): Promise<{
  top_products: Record<string, unknown>[];
  top_videos: Record<string, unknown>[];
  top_campaigns: Record<string, unknown>[];
}> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (limit) query.set("limit", String(limit));
  return apiFetch(`/analytics/top-performers?${query}`, { token });
}

export function exportAnalytics(
  workspaceId: string,
  token: string,
  params?: { dataset?: string; format?: string; days?: number }
): Promise<Record<string, unknown>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.dataset) query.set("dataset", params.dataset);
  if (params?.format) query.set("format", params.format);
  if (params?.days) query.set("days", String(params.days));
  return apiFetch(`/analytics/export?${query}`, { method: "POST", token });
}

// Analytics - Scheduled Reports & Notifications
export interface KpiTimeseries {
  date: string;
  total_orders: number;
  total_revenue: string;
  active_campaigns: number;
  total_views: number;
}

export interface ScheduledReportSummary {
  id: string;
  name: string;
  description: string | null;
  modules: Record<string, unknown>;
  frequency: string;
  format: string;
  is_active: boolean;
  last_run_at: string | null;
  next_run_at: string | null;
  created_at: string;
}

export interface NotificationItem {
  id: string;
  notification_type: string;
  title: string;
  message: string;
  module: string | null;
  action_url: string | null;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

export interface NotificationPref {
  id: string;
  module: string;
  channel: string;
  is_enabled: boolean;
}

export interface ApiKeyItem {
  id: string;
  name: string;
  key_prefix: string;
  scopes: Record<string, unknown>;
  is_active: boolean;
  last_used_at: string | null;
  expires_at: string | null;
  created_at: string;
}

export interface ApiKeyCreateResponse {
  key: ApiKeyItem;
  raw_key: string;
}

export function getKpiTimeseries(workspaceId: string, token: string, days?: number): Promise<KpiTimeseries[]> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (days) query.set("days", String(days));
  return apiFetch(`/analytics/timeseries?${query}`, { token });
}

export function listScheduledReports(
  workspaceId: string, token: string,
  params?: { is_active?: boolean; page?: number }
): Promise<PaginatedResponse<ScheduledReportSummary>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.is_active !== undefined) query.set("is_active", String(params.is_active));
  if (params?.page) query.set("page", String(params.page));
  return apiFetch(`/analytics/reports?${query}`, { token });
}

export function createScheduledReport(
  workspaceId: string,
  data: { name: string; description?: string; modules: string[]; frequency?: string; format?: string },
  token: string
): Promise<ScheduledReportSummary> {
  return apiFetch(`/analytics/reports?workspace_id=${workspaceId}`, { method: "POST", body: JSON.stringify(data), token });
}

export function generateReport(reportId: string, token: string): Promise<Record<string, unknown>> {
  return apiFetch(`/analytics/reports/${reportId}/generate`, { method: "POST", token });
}

export function deleteScheduledReport(reportId: string, token: string): Promise<void> {
  return apiFetch(`/analytics/reports/${reportId}`, { method: "DELETE", token });
}

export function listNotifications(
  workspaceId: string, token: string,
  params?: { is_read?: boolean; module?: string; page?: number }
): Promise<PaginatedResponse<NotificationItem>> {
  const query = new URLSearchParams({ workspace_id: workspaceId });
  if (params?.is_read !== undefined) query.set("is_read", String(params.is_read));
  if (params?.module) query.set("module", params.module);
  if (params?.page) query.set("page", String(params.page));
  return apiFetch(`/analytics/notifications?${query}`, { token });
}

export function getUnreadCount(workspaceId: string, token: string): Promise<{ count: number }> {
  return apiFetch(`/analytics/notifications/unread-count?workspace_id=${workspaceId}`, { token });
}

export function markNotificationRead(notificationId: string, token: string): Promise<NotificationItem> {
  return apiFetch(`/analytics/notifications/${notificationId}/read`, { method: "POST", token });
}

export function markAllNotificationsRead(workspaceId: string, token: string): Promise<{ updated: number }> {
  return apiFetch(`/analytics/notifications/read-all?workspace_id=${workspaceId}`, { method: "POST", token });
}

export function getNotificationPreferences(token: string): Promise<NotificationPref[]> {
  return apiFetch("/analytics/notifications/preferences", { token });
}

export function updateNotificationPreference(
  data: { module: string; channel: string; is_enabled: boolean },
  token: string
): Promise<NotificationPref> {
  return apiFetch("/analytics/notifications/preferences", { method: "PUT", body: JSON.stringify(data), token });
}

export function listApiKeys(workspaceId: string, token: string): Promise<ApiKeyItem[]> {
  return apiFetch(`/analytics/api-keys?workspace_id=${workspaceId}`, { token });
}

export function createApiKey(
  workspaceId: string,
  data: { name: string; scopes?: string[] },
  token: string
): Promise<ApiKeyCreateResponse> {
  return apiFetch(`/analytics/api-keys?workspace_id=${workspaceId}`, { method: "POST", body: JSON.stringify(data), token });
}

export function revokeApiKey(keyId: string, token: string): Promise<ApiKeyItem> {
  return apiFetch(`/analytics/api-keys/${keyId}`, { method: "DELETE", token });
}
