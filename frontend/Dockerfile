FROM node:24-slim AS deps
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

FROM node:24-slim AS builder
WORKDIR /app
ARG NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
ENV NEXT_PUBLIC_API_BASE_URL=$NEXT_PUBLIC_API_BASE_URL
COPY --from=deps /app/node_modules ./node_modules
COPY frontend ./
RUN npm run build

FROM node:24-slim AS runner
WORKDIR /app
ENV NODE_ENV=production \
    PORT=3000

RUN addgroup --system app && adduser --system --ingroup app app

COPY --from=builder /app/public ./public
COPY --from=builder --chown=app:app /app/.next/standalone ./
COPY --from=builder --chown=app:app /app/.next/static ./.next/static

USER app
EXPOSE 3000

CMD ["sh", "-c", "node server.js"]
