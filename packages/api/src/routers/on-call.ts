import { z } from "zod";

import { publicProcedure } from "../index";

export const onCallRouter = {
	triggerIncident: publicProcedure
		.input(z.object({ mockUrl: z.string().optional() }))
		.handler(async ({ input }) => {
			try {
				const agentUrl = process.env.HERMES_AGENT_URL || "http://localhost:8678";
				const response = await fetch(`${agentUrl}/webhook`, {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(input),
				});

				if (!response.ok) {
					throw new Error("Failed to trigger agent");
				}
				return await response.json();
			} catch (error) {
				console.error("Agent error:", error);
				return { error: "Agent is not running or failed to trigger." };
			}
		}),

	getLogs: publicProcedure.handler(async () => {
		try {
			const agentUrl = process.env.HERMES_AGENT_URL || "http://localhost:8678";
			const response = await fetch(`${agentUrl}/logs`);
			if (!response.ok) {
				throw new Error("Failed to get logs");
			}
			return await response.json();
		} catch (_error) {
			return {
				logs: [],
				error: "Agent is not running or failed to fetch logs.",
			};
		}
	}),
	chat: publicProcedure
		.input(z.object({ message: z.string() }))
		.handler(async ({ input }) => {
			try {
				const agentUrl = process.env.HERMES_AGENT_URL || "http://localhost:8678";
				const response = await fetch(`${agentUrl}/chat`, {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
					},
					body: JSON.stringify(input),
				});

				if (!response.ok) {
					throw new Error("Failed to chat with agent");
				}
				return await response.json();
			} catch (error) {
				console.error("Chat error:", error);
				return {
					response: "Error: Agent is not running or failed to respond.",
				};
			}
		}),
};
