#!/usr/bin/env bash

celery worker -A celeryworker --concurrency=10 -P gevent