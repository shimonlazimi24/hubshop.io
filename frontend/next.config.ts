import type { NextConfig } from "next";

const nextConfig: NextConfig = {
	output: "standalone",
	poweredByHeader: false,
	images: {
		remotePatterns: [
			{
				protocol: "https",
				hostname: "p16-sign.tiktokcdn.com",
			},
			{
				protocol: "https",
				hostname: "p16-sign-sg.tiktokcdn.com",
			},
			{
				protocol: "https",
				hostname: "p19-sign.tiktokcdn.com",
			},
			{
				protocol: "https",
				hostname: "p77-sign.tiktokcdn.com",
			},
		],
	},
};

export default nextConfig;
