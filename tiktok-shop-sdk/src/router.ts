import crypto from "node:crypto";
import type { FastifyInstance } from "fastify";
import { v4 as uuidv4 } from "uuid";
import { listAllOperations } from "./sdk-registry";

const BASE_URL = "https://open-api.tiktokglobalshop.com";
const EXCLUDE_SIGN_KEYS = ["access_token", "sign"];
const ALLOWED_METHODS = new Set(["GET", "POST", "PUT", "DELETE", "PATCH"]);
const API_PATH_PATTERN = /^\/[a-z_]+\/\d{6}\/[a-z0-9_/{}]+$/;
const REQUEST_TIMEOUT_MS = 30_000;

interface ProxyRequestBody {
	method: string;
	path: string;
	access_token: string;
	shop_cipher?: string;
	query_params?: Record<string, any>;
	body?: Record<string, any>;
}

/**
 * Generate HMAC-SHA256 signature matching TikTok Shop API spec.
 */
function generateSignature(
	path: string,
	params: Record<string, string>,
	body: string,
	appSecret: string,
): string {
	const sortedParams = Object.keys(params)
		.filter((key) => !EXCLUDE_SIGN_KEYS.includes(key))
		.sort()
		.map((key) => `${key}${params[key]}`)
		.join("");

	let signString = `${path}${sortedParams}`;
	if (body && body !== "{}") {
		signString += body;
	}
	signString = `${appSecret}${signString}${appSecret}`;

	return crypto
		.createHmac("sha256", appSecret)
		.update(signString)
		.digest("hex");
}

export function registerRoutes(
	app: FastifyInstance,
	appKey: string,
	appSecret: string,
	sidecarAuthToken: string,
): void {
	// Authentication hook — all endpoints except /health require the shared secret
	app.addHook("onRequest", async (request, reply) => {
		if (request.url === "/health") return;
		const token = request.headers["x-sidecar-auth"];
		if (token !== sidecarAuthToken) {
			reply.status(401).send({ error: "Unauthorized" });
			return;
		}
	});

	// Discovery endpoint
	app.get("/api/shop/operations", async (_req, reply) => {
		const operations = listAllOperations();
		let totalOps = 0;
		for (const group of operations) {
			totalOps += group.operations.length;
		}
		reply.send({
			success: true,
			data: {
				total_domains: operations.length,
				total_operations: totalOps,
				operations,
			},
		});
	});

	// Signing proxy — the main endpoint
	app.post<{ Body: ProxyRequestBody }>(
		"/api/shop/proxy",
		async (req, reply) => {
			const requestId = uuidv4();
			const {
				method,
				path,
				access_token,
				shop_cipher,
				query_params,
				body: reqBody,
			} = req.body;

			// Validate required fields
			if (!access_token) {
				reply.status(400).send({
					success: false,
					error: {
						code: "MISSING_ACCESS_TOKEN",
						message: "access_token is required",
					},
					request_id: requestId,
				});
				return;
			}

			if (!path) {
				reply.status(400).send({
					success: false,
					error: { code: "MISSING_PATH", message: "path is required" },
					request_id: requestId,
				});
				return;
			}

			// Validate HTTP method
			const httpMethod = (method || "POST").toUpperCase();
			if (!ALLOWED_METHODS.has(httpMethod)) {
				reply.status(400).send({
					success: false,
					error: {
						code: "INVALID_METHOD",
						message: `Unsupported method: ${method}`,
					},
					request_id: requestId,
				});
				return;
			}

			// Validate and normalize path
			const apiPath = path.startsWith("/") ? path : `/${path}`;
			if (!API_PATH_PATTERN.test(apiPath)) {
				reply.status(400).send({
					success: false,
					error: {
						code: "INVALID_PATH",
						message: "path does not match expected API format",
					},
					request_id: requestId,
				});
				return;
			}

			// Build query parameters
			const timestamp = Math.floor(Date.now() / 1000).toString();
			const allParams: Record<string, string> = {
				app_key: appKey,
				timestamp,
			};

			if (shop_cipher) {
				allParams.shop_cipher = shop_cipher;
			}

			if (query_params) {
				for (const [key, value] of Object.entries(query_params)) {
					if (Array.isArray(value)) {
						allParams[key] = value.join(",");
					} else {
						allParams[key] = String(value);
					}
				}
			}

			// Serialize body
			const bodyStr =
				reqBody && Object.keys(reqBody).length > 0
					? JSON.stringify(reqBody)
					: "";

			// Generate signature
			allParams.sign = generateSignature(
				apiPath,
				allParams,
				bodyStr,
				appSecret,
			);
			allParams.access_token = access_token;

			// Build URL with query string
			const queryString = new URLSearchParams(allParams).toString();
			const fullUrl = `${BASE_URL}${apiPath}?${queryString}`;

			const headers: Record<string, string> = {
				"Content-Type": "application/json",
				"x-tts-access-token": access_token,
				"User-Agent": "frodo-sdk-sidecar/1.0.0",
			};

			try {
				const controller = new AbortController();
				const timeout = setTimeout(
					() => controller.abort(),
					REQUEST_TIMEOUT_MS,
				);

				const fetchOptions: RequestInit = {
					method: httpMethod,
					headers,
					signal: controller.signal,
				};

				if (bodyStr && httpMethod !== "GET") {
					fetchOptions.body = bodyStr;
				}

				const response = await fetch(fullUrl, fetchOptions);
				clearTimeout(timeout);

				const responseBody = await response.json();

				if (response.ok) {
					reply.send({
						success: true,
						data: responseBody,
						request_id: requestId,
					});
				} else {
					reply.status(response.status).send({
						success: false,
						error: {
							code: "API_ERROR",
							message: `TikTok API returned ${response.status}`,
							details: responseBody,
						},
						request_id: requestId,
					});
				}
			} catch (err: any) {
				req.log.error({ err, requestId }, "Upstream request failed");

				const isTimeout = err.name === "AbortError";
				reply.status(502).send({
					success: false,
					error: {
						code: isTimeout ? "UPSTREAM_TIMEOUT" : "UPSTREAM_ERROR",
						message: isTimeout
							? "TikTok API request timed out"
							: "Failed to reach TikTok API",
						details: null,
					},
					request_id: requestId,
				});
			}
		},
	);
}
