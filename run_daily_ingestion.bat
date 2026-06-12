@echo off
cd /d "c:\Users\shahn\Groww Buddy"
python -m ingestion.ingest_daily >> daily_ingestion_log.txt 2>&1
