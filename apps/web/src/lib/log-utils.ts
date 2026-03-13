export type LogLevel = "info" | "warn" | "error" | "debug" | "tool";
export type LogSource =
	| "system"
	| "agent"
	| "github"
	| "tool"
	| "incident"
	| "unknown";

export interface ParsedLog {
	id: string;
	timestamp: string;
	source: LogSource;
	level: LogLevel;
	message: string;
	details?: string;
	isToolCall?: boolean;
	toolName?: string;
	toolArgs?: unknown;
	toolResult?: unknown;
}

export function parseLogLine(line: string, index: number): ParsedLog {
	const id = `log-${index}`;
	const timestamp = new Date().toISOString(); // Asıl logda timestamp yoksa şimdiki zamanı kullanıyoruz

	let source: LogSource = "unknown";
	let level: LogLevel = "info";
	let message = line;
	let isToolCall = false;
	let toolName: string | undefined;
	let details: string | undefined;

	if (
		line.includes("[SYSTEM]") ||
		line.includes("🎯") ||
		line.includes("Initializing")
	) {
		source = "system";
		message = line.replace("[SYSTEM]", "").trim();
	} else if (line.includes("[AGENT]")) {
		source = "agent";
		message = line.replace("[AGENT]", "").trim();
		if (
			message.toLowerCase().includes("calling") ||
			message.includes("tool_call")
		) {
			isToolCall = true;
			level = "tool";
		}
	} else if (line.includes("[GITHUB]")) {
		source = "github";
		message = line.replace("[GITHUB]", "").trim();
	} else if (line.includes("[TOOL]")) {
		source = "tool";
		level = "tool";
		message = line.replace("[TOOL]", "").trim();
		isToolCall = true;
	} else if (
		line.includes("[ERROR]") ||
		line.includes("🚨") ||
		line.includes("Error:")
	) {
		source = "system";
		level = "error";
		message = line.replace("[ERROR]", "").trim();
	} else if (line.includes("[INCIDENT]")) {
		source = "incident";
		message = line.replace("[INCIDENT]", "").trim();
	} else if (
		line.includes("✅") ||
		line.includes("Successfully") ||
		line.includes("completed")
	) {
		source = "system";
		level = "info";
	}

	// Basit bir tool name tespiti (Örn: Calling: list_files({ ... }))
	if (isToolCall) {
		const toolMatch = message.match(/(?:calling|tool_call)[:\s]+(\w+)/i);
		if (toolMatch) {
			toolName = toolMatch[1];
		}
	}

	return {
		id,
		timestamp,
		source,
		level,
		message,
		isToolCall,
		toolName,
		details,
	};
}
