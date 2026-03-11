import { useQuery } from "@tanstack/react-query";
import { createFileRoute, Link, Outlet } from "@tanstack/react-router";

import { orpc } from "@/utils/orpc";

export const Route = createFileRoute("/dashboard")({
	component: RouteComponent,
});

function RouteComponent() {
	const privateData = useQuery(orpc.privateData.queryOptions());

	return (
		<div className="flex flex-col gap-4 p-4">
			<div className="flex items-center justify-between border-b pb-4">
				<div>
					<h1 className="font-bold text-2xl tracking-tight">Dashboard</h1>
					<p className="text-muted-foreground text-sm">
						System Monitoring & Autonomy Control
					</p>
				</div>
				<Link
					to="/dashboard/on-call"
					className="rounded-md bg-primary px-4 py-2 text-primary-foreground hover:bg-primary/90"
				>
					View On-Call Agent
				</Link>
			</div>
			<div>
				<p>API: {privateData.data?.message}</p>
			</div>
			<Outlet />
		</div>
	);
}
