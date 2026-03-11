import { Badge } from "@hermes-on-call/ui/components/badge";
import { Button } from "@hermes-on-call/ui/components/button";
import {
	Card,
	CardContent,
	CardDescription,
	CardFooter,
	CardHeader,
	CardTitle,
} from "@hermes-on-call/ui/components/card";
import { Input } from "@hermes-on-call/ui/components/input";
import { Label } from "@hermes-on-call/ui/components/label";
import { Separator } from "@hermes-on-call/ui/components/separator";
import { Skeleton } from "@hermes-on-call/ui/components/skeleton";
import { useMutation, useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import {
	Activity,
	AlertTriangle,
	CheckCircle2,
	Clock,
	Cpu,
	Play,
	Search,
	ServerCrash,
	Terminal,
	Zap,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { orpc } from "../utils/orpc";

export const Route = createFileRoute("/dashboard/on-call")({
	component: OnCallDashboardOverhaul,
});

const INCIDENT_TEMPLATES = [
	{
		id: "503",
		name: "API 503 Critical",
		description: "Simulate a wholesale outage of the gateway.",
		icon: <ServerCrash className="h-4 w-4 text-red-500" />,
		url: "http://api.internal/v1/gateway/503",
		color: "destructive" as const,
	},
	{
		id: "latency",
		name: "High Latency",
		description: "Database queries exceeding p99 thresholds.",
		icon: <Clock className="h-4 w-4 text-amber-500" />,
		url: "http://db.internal/slow-queries",
		color: "outline" as const,
	},
	{
		id: "memory",
		name: "Memory Leak",
		description: "Node.js process heap memory climbing.",
		icon: <Cpu className="h-4 w-4 text-purple-500" />,
		url: "http://k8s.internal/metrics/memory-leak",
		color: "outline" as const,
	},
];

function OnCallDashboardOverhaul() {
	const [mockUrl, setMockUrl] = useState("");
	const scrollRef = useRef<HTMLDivElement>(null);

	const {
		data: logsData,
		refetch: refetchLogs,
		isLoading: isLogsLoading,
	} = useQuery({
		...orpc.onCall.getLogs.queryOptions(),
		refetchInterval: 2000,
	});

	const triggerMutation = useMutation(
		orpc.onCall.triggerIncident.mutationOptions({
			onSuccess: () => {
				refetchLogs();
			},
		}),
	);

	// Auto-scroll to bottom of terminal
	useEffect(() => {
		if (scrollRef.current) {
			scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
		}
	}, [logsData]);

	return (
		<div className="flex flex-col gap-8 py-4">
			<div className="flex flex-col justify-between gap-4 md:flex-row md:items-end">
				<div className="space-y-1">
					<div className="flex items-center gap-2">
						<Badge
							variant="outline"
							className="border-primary/20 bg-primary/5 px-2 py-0 font-mono text-primary text-xs"
						>
							v1.2.0-alpha
						</Badge>
						<span className="flex items-center gap-1.5 font-semibold text-muted-foreground text-xs uppercase tracking-widest">
							<Zap className="h-3 w-3 fill-amber-500 text-amber-500" />
							Autonomous Ops
						</span>
					</div>
					<h1 className="font-extrabold text-4xl tracking-tighter">
						Systems Sentinel
					</h1>
					<p className="text-lg text-muted-foreground">
						Deploy Hermes agents to triage and remediate production anomalies.
					</p>
				</div>

				<div className="flex items-center gap-4 rounded-full border border-border bg-secondary/30 p-1.5 px-4 py-2">
					<div className="flex items-center gap-2">
						<div className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
						<span className="font-medium text-sm">Agent Active</span>
					</div>
					<Separator orientation="vertical" className="h-4" />
					<div className="flex items-center gap-2 text-muted-foreground">
						<Search className="h-3.5 w-3.5" />
						<span className="text-xs">Uptime: 14d 2h</span>
					</div>
				</div>
			</div>

			<div className="grid grid-cols-1 gap-8 lg:grid-cols-12">
				{/* Left Sidebar: Controls */}
				<div className="space-y-6 lg:col-span-4">
					<Card className="border-primary/10 shadow-lg">
						<CardHeader>
							<CardTitle className="flex items-center gap-2 text-xl">
								<Terminal className="h-5 w-5" />
								Trigger Incident
							</CardTitle>
							<CardDescription>
								Initiate a response sequence by simulating a service failure.
							</CardDescription>
						</CardHeader>
						<CardContent className="space-y-6">
							<div className="space-y-3">
								<Label className="font-bold text-muted-foreground text-xs uppercase tracking-wider">
									Quick Templates
								</Label>
								<div className="grid gap-3">
									{INCIDENT_TEMPLATES.map((item) => (
										<button
											type="button"
											key={item.id}
											onClick={() => setMockUrl(item.url)}
											className={`group flex items-start gap-3 rounded-lg border p-3 text-left transition-all hover:bg-muted ${mockUrl === item.url ? "border-primary bg-primary/5 shadow-sm" : "border-border"}`}
										>
											<div className="mt-0.5">{item.icon}</div>
											<div className="space-y-1">
												<div className="font-bold text-sm transition-colors group-hover:text-primary">
													{item.name}
												</div>
												<div className="text-muted-foreground text-xs leading-snug">
													{item.description}
												</div>
											</div>
										</button>
									))}
								</div>
							</div>

							<Separator />

							<div className="space-y-2">
								<Label
									htmlFor="mockUrl"
									className="font-bold text-muted-foreground text-xs uppercase tracking-wider"
								>
									Manual Target
								</Label>
								<div className="group relative">
									<Input
										id="mockUrl"
										type="url"
										placeholder="https://service.production.com/health"
										value={mockUrl}
										onChange={(e) => setMockUrl(e.target.value)}
										className="h-11 pr-10 pl-4 focus-visible:ring-primary"
									/>
									<ServerCrash className="absolute top-3 right-3 h-5 w-5 text-muted-foreground/50 transition-colors group-hover:text-primary" />
								</div>
							</div>
						</CardContent>
						<CardFooter>
							<Button
								onClick={() => triggerMutation.mutate({ mockUrl })}
								disabled={triggerMutation.isPending || !mockUrl}
								className="h-12 w-full font-bold text-md shadow-md transition-all active:scale-95"
								variant={triggerMutation.isPending ? "secondary" : "default"}
							>
								{triggerMutation.isPending ? (
									<Activity className="mr-2 h-5 w-5 animate-spin" />
								) : (
									<Play className="mr-2 h-5 w-5" />
								)}
								{triggerMutation.isPending
									? "Dispatching Agent..."
									: "Deploy Sentinel"}
							</Button>
						</CardFooter>
					</Card>

					{/* Quick stats / feedback */}
					{triggerMutation.isSuccess && (
						<div className="fade-in slide-in-from-top-4 animate-in rounded-xl border border-green-500/20 bg-green-500/10 p-4 duration-300">
							<div className="flex gap-3">
								<CheckCircle2 className="mt-0.5 h-5 w-5 text-green-500" />
								<div className="space-y-1">
									<div className="font-bold text-green-700 dark:text-green-400">
										Sentinel Dispatched
									</div>
									<div className="text-green-600 text-xs dark:text-green-500/80">
										The agent is now triaging the provided endpoint. Check the
										telemetry for real-time updates.
									</div>
								</div>
							</div>
						</div>
					)}

					{triggerMutation.isError && (
						<div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4">
							<div className="flex gap-3">
								<AlertTriangle className="mt-0.5 h-5 w-5 text-red-500" />
								<div className="space-y-1">
									<div className="font-bold text-red-700 dark:text-red-400">
										Dispatch Failed
									</div>
									<div className="text-red-600 text-xs dark:text-red-500/80">
										{triggerMutation.error.message}
									</div>
								</div>
							</div>
						</div>
					)}
				</div>

				{/* Right Panel: Terminal Telemetry */}
				<div className="lg:col-span-8">
					<Card className="flex h-[700px] flex-col overflow-hidden border-border bg-background shadow-xl">
						<div className="flex items-center justify-between border-b bg-muted/50 px-4 py-3">
							<div className="flex items-center gap-3">
								<div className="mr-1 flex gap-1.5">
									<div className="h-3 w-3 rounded-full bg-red-500/30" />
									<div className="h-3 w-3 rounded-full bg-amber-500/30" />
									<div className="h-3 w-3 rounded-full bg-green-500/30" />
								</div>
								<Separator orientation="vertical" className="h-4" />
								<div className="flex items-center gap-2">
									<Terminal className="h-4 w-4 text-primary" />
									<span className="font-bold font-mono text-xs uppercase tracking-tight">
										Sentinel Telemetry Feed
									</span>
								</div>
							</div>
							<div className="flex items-center gap-3">
								{logsData?.logs && logsData.logs.length > 0 && (
									<div className="flex items-center gap-2 rounded-md border bg-background px-2 py-0.5 font-mono text-[10px]">
										<div className="h-1.5 w-1.5 animate-pulse rounded-full bg-green-500" />
										STREAMING
									</div>
								)}
								<Badge variant="outline" className="h-5 text-[10px]">
									UTC-0
								</Badge>
							</div>
						</div>

						<CardContent className="group relative flex-1 bg-black/95 p-0">
							<div
								ref={scrollRef}
								className="scrollbar-thin scrollbar-thumb-zinc-800 absolute inset-0 overflow-y-auto overflow-x-hidden p-6 font-mono text-sm"
							>
								{isLogsLoading && !logsData ? (
									<div className="space-y-4">
										<Skeleton className="h-4 w-3/4 bg-zinc-900" />
										<Skeleton className="h-4 w-1/2 bg-zinc-900" />
										<Skeleton className="h-4 w-5/6 bg-zinc-900" />
										<Skeleton className="h-4 w-2/3 bg-zinc-900" />
									</div>
								) : logsData?.error ? (
									<div className="flex h-full flex-col items-center justify-center gap-3 text-destructive opacity-80">
										<AlertTriangle className="h-12 w-12" />
										<div className="font-bold text-xs uppercase tracking-widest">
											Connection Terminated
										</div>
										<div className="rounded-lg border border-destructive/20 bg-destructive/10 px-4 py-2 text-xs">
											{logsData.error}
										</div>
										<Button
											variant="ghost"
											size="sm"
											onClick={() => refetchLogs()}
											className="mt-2 text-destructive hover:bg-destructive/10"
										>
											Re-establish Uplink
										</Button>
									</div>
								) : logsData?.logs && logsData.logs.length > 0 ? (
									<div className="space-y-1.5">
										{logsData.logs.map((log: string, i: number) => {
											const isError =
												log.toLowerCase().includes("error") ||
												log.toLowerCase().includes("fail") ||
												log.toLowerCase().includes("❌") ||
												log.toLowerCase().includes("⚠️");
											const isSuccess =
												log.toLowerCase().includes("success") ||
												log.toLowerCase().includes("resolv") ||
												log.toLowerCase().includes("✅") ||
												log.toLowerCase().includes("💡");
											const isAction =
												log.toLowerCase().includes("trigger") ||
												log.toLowerCase().includes("deploy") ||
												log.toLowerCase().includes("🚨");

											return (
												<div
													key={i}
													className="fade-in slide-in-from-left-2 flex animate-in items-start gap-3 py-0.5 duration-300"
												>
													<span className="mt-1 select-none font-bold text-[10px] text-zinc-700 tabular-nums">
														{(i + 1).toString().padStart(3, "0")}
													</span>
													<span
														className={`break-all leading-relaxed ${
															isError
																? "font-medium text-red-400"
																: isSuccess
																	? "font-medium text-green-400"
																	: isAction
																		? "font-bold text-sky-400"
																		: "text-zinc-400"
														}`}
													>
														{log}
													</span>
												</div>
											);
										})}
										<div className="h-4 animate-pulse pt-2">
											<span className="font-bold text-primary">_</span>
										</div>
									</div>
								) : (
									<div className="flex h-full flex-col items-center justify-center space-y-4 text-zinc-800">
										<Activity className="h-16 w-16 animate-pulse opacity-10" />
										<div className="space-y-1 text-center">
											<p className="font-bold text-xs uppercase tracking-widest opacity-50">
												Signal Buffer Empty
											</p>
											<p className="text-[10px] opacity-30">
												Sentinel is in silent observation mode. Deploy an
												incident to see its logic.
											</p>
										</div>
									</div>
								)}
							</div>
						</CardContent>
						<div className="flex items-center justify-between border-t bg-muted/30 px-4 py-2 font-bold font-mono text-[10px] text-muted-foreground uppercase tracking-tight">
							<div className="flex gap-4">
								<span>Packets: {logsData?.logs?.length || 0}</span>
								<span>Latency: 42ms</span>
							</div>
							<div className="flex items-center gap-1.5">
								<div className="h-1.5 w-1.5 rounded-full bg-primary" />
								Secure WebSocket Established
							</div>
						</div>
					</Card>
				</div>
			</div>
		</div>
	);
}
