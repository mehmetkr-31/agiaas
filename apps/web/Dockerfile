FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

FROM base AS build
WORKDIR /app
COPY . .
RUN pnpm install --frozen-lockfile
RUN pnpm run build --filter web

FROM base AS runner
WORKDIR /app
COPY --from=build /app/apps/web/.output /app/.output
COPY --from=build /app/apps/web/package.json /app/package.json

EXPOSE 3678
CMD ["node", ".output/server/index.mjs"]
