import {
	Accordion,
	AccordionContent,
	AccordionItem,
	AccordionTrigger,
} from "@agiaas/ui/components/accordion";
import { Badge } from "@agiaas/ui/components/badge";
import { ScrollArea } from "@agiaas/ui/components/scroll-area";
import { cn } from "@agiaas/ui/lib/utils";
import {
	AlertCircle,
	ChevronRight,
	Github,
	Info,
	Terminal,
	Wrench,
} from "lucide-react";
import { type ParsedLog, parseLogLine } from "../lib/log-utils";

interface LogFeedProps {
	logs: string[];
	className?: string;
}

export function LogFeed({ logs, className }: LogFeedProps) {
	const parsedLogs = logs.map((log, i) => parseLogLine(log, i));

	return (
		<ScrollArea
			className={cn("h-full w-full rounded-md border bg-background", className)}
		>
			<div className="flex flex-col space-y-2 p-4">
				{parsedLogs.map((log) => (
					<LogEntryItem key={log.id} log={log} />
				))}
			</div>
		</ScrollArea>
	);
}

function LogEntryItem({ log }: { log: ParsedLog }) {
	const sourceIcons = {
		system: <Info className="h-3.5 w-3.5 text-primary" />,
		agent: (
			<Terminal className="h-3.5 w-3.5 text-indigo-500 dark:text-indigo-400" />
		),
		github: <Github className="h-3.5 w-3.5 text-muted-foreground" />,
		tool: <Wrench className="h-3.5 w-3.5 text-amber-500" />,
		incident: <AlertCircle className="h-3.5 w-3.5 text-destructive" />,
		unknown: <ChevronRight className="h-3.5 w-3.5 text-muted-foreground" />,
	};

	const levelColors = {
		info: "text-foreground",
		warn: "text-amber-500",
		error: "text-destructive font-semibold",
		debug: "text-muted-foreground",
		tool: "text-amber-500 font-medium",
	};

	const rowStyles = cn(
		"group flex items-start gap-2 rounded-sm px-2 py-1 transition-colors hover:bg-accent/30",
		log.level === "error" &&
			"rounded-l-none border-destructive border-l-2 bg-destructive/5 hover:bg-destructive/10",
		log.source === "incident" &&
			"rounded-l-none border-amber-500 border-l-2 bg-amber-500/5 hover:bg-amber-500/10",
	);

	if (log.isToolCall) {
		return (
			<Accordion className="w-full">
				<AccordionItem value={log.id} className="border-none">
					<div className={cn(rowStyles, "hover:bg-accent/50")}>
						<div className="mt-1">{sourceIcons.tool}</div>
						<div className="flex min-w-0 flex-1 flex-col">
							<div className="flex items-center gap-2">
								<span className="font-mono text-[10px] text-muted-foreground">
									{new Date(log.timestamp).toLocaleTimeString([], {
										hour12: false,
										hour: "2-digit",
										minute: "2-digit",
										second: "2-digit",
									})}
								</span>
								<AccordionTrigger className="h-auto flex-1 border-none p-0 py-0 hover:no-underline">
									<div className="flex items-center gap-2">
										<Badge
											variant="outline"
											className="h-4 border-amber-500/20 bg-amber-500/10 px-1 text-[10px] text-amber-600 dark:text-amber-400"
										>
											TOOL CALL
										</Badge>
										<span className="truncate font-mono font-semibold text-amber-600 text-xs dark:text-amber-400">
											{log.toolName || "execute_tool"}
										</span>
									</div>
								</AccordionTrigger>
							</div>
							<p className="mt-0.5 ml-0 truncate text-muted-foreground text-xs italic">
								{log.message}
							</p>
						</div>
					</div>
					<AccordionContent className="pr-2 pl-9">
						<div className="mt-1 rounded-md border border-border/50 bg-muted/30 p-3 font-mono text-[11px]">
							<div className="mb-2 flex items-center justify-between border-border/50 border-b pb-1">
								<span className="font-bold text-[9px] text-muted-foreground uppercase tracking-widest">
									Arguments & Context
								</span>
								<div className="h-1.5 w-1.5 animate-pulse rounded-full bg-amber-500" />
							</div>
							<pre className="whitespace-pre-wrap break-all text-foreground/90">
								{log.message}
							</pre>
						</div>
					</AccordionContent>
				</AccordionItem>
			</Accordion>
		);
	}

	return (
		<div className={rowStyles}>
			<div className="mt-1 opacity-70 transition-opacity group-hover:opacity-100">
				{sourceIcons[log.source]}
			</div>
			<div className="flex min-w-0 flex-1 flex-col">
				<div className="flex items-center gap-2">
					<span className="shrink-0 font-mono text-[10px] text-muted-foreground">
						{new Date(log.timestamp).toLocaleTimeString([], {
							hour12: false,
							hour: "2-digit",
							minute: "2-digit",
							second: "2-digit",
						})}
					</span>
					<span
						className={cn(
							"break-words text-xs leading-relaxed",
							levelColors[log.level],
						)}
					>
						{log.message}
					</span>
				</div>
			</div>
		</div>
	);
}
