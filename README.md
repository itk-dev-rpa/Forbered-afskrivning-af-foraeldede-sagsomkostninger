# Restancelister til FOSA

1. GRAPH get emails
2. Treat excel files according to alteryx rules
3. Get rykkerspærre from SAP
4. Filter excel output
5. Insert results into job queue.

## Testing 
Run from terminal as python process
```bash
python src\framework.py "test_fosa_forbered" "Driver={ODBC Driver 17 for SQL Server};Server=SRVSQLHOTEL03;Database=MKB-ITK-RPA;Trusted_Connection=yes;" "<secret key>"
```

## Requirements
Minimum python version 3.10

## Flow

The flow of the framework is sketched up in the following illustration:

![Flow diagram](Robot-Framework.svg)
