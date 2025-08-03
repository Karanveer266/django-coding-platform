# Secure Python execution environment
FROM python:3.11-alpine

# Create non-root user
RUN adduser -D -s /bin/sh sandbox

# Remove potentially dangerous packages and commands
RUN apk del --purge \
    curl \
    wget \
    git \
    openssh \
    && rm -rf /var/cache/apk/*

# Create sandbox directory
RUN mkdir -p /sandbox && chown sandbox:sandbox /sandbox
WORKDIR /sandbox

# Switch to non-root user
USER sandbox

# Set resource limits in environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python3"]