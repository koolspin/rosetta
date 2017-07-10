#!/bin/bash
curl -H "Content-Type: application/json" -X POST -d '{"device_id": 123, "device_name":"fizz_buzz"}' http://localhost:8888/db/device_state

