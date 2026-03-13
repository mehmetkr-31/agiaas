import { sql } from "drizzle-orm";
import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const hermesSecrets = sqliteTable("hermes_secrets", {
	id: text("id").primaryKey(),
	projectId: text("project_id").notNull(),
	keyName: text("key_name").notNull(),
	encryptedValue: text("encrypted_value").notNull(),
	createdAt: integer("created_at", { mode: "timestamp" })
		.default(sql`(strftime('%s', 'now'))`)
		.notNull(),
});
