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
