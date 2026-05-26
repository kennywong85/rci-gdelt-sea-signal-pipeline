# Local Scheduled Refresh

This document explains how the local RCI GDELT SEA pipeline can be refreshed on a schedule.

The core MVP is run manually through:

```bash
python scripts/run_pipeline.py --days 90 --max-files 14