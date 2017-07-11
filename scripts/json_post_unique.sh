#!/bin/bash
curl -H "Content-Type: application/json" -X POST -d '{"device_key": 4242, "device_status":"ready"}' http://localhost:8888/db/device_info
curl -H "Content-Type: application/json" -X POST -d '{"device_key": 2121, "device_status":"offline"}' http://localhost:8888/db/device_info
curl -H "Content-Type: application/json" -X POST -d '{"device_key": 1234, "device_status":"pending"}' http://localhost:8888/db/device_info

