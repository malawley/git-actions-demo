# === Stage 1: Build the Go binary ===
FROM golang:1.24 AS builder

WORKDIR /app

# Copy go.mod and go.sum first to leverage Docker layer caching
COPY go.mod go.sum ./
RUN go mod download

# Copy the application source code
COPY cmd/ ./cmd/

# Build the binary
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o extractor ./cmd/extractor.go

# === Stage 2: Minimal runtime image ===
FROM gcr.io/distroless/static-debian11

WORKDIR /

# Copy binary from builder
COPY --from=builder /app/extractor .

# Expose port (Cloud Run uses the PORT env var)
ENV PORT=8000

# Command to run the binary
ENTRYPOINT ["/extractor"]
