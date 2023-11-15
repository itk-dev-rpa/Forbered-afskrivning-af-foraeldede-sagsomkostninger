# Restancelister til FOSA
Part one of the procedure https://github.com/itk-dev-rpa/Afskrivning-af-foraeldede-sagsomkostninger
1. Graph get emails. 
2. Treat Excel files according to Alteryx rules
3. Get rykkerspærre from SAP
4. Filter excel output
5. Insert results into job queue.

## Testing 
Run from terminal as python process
```bash
python src\framework.py "test_fosa_forbered" "<connection string>" "<secret key>" "my_args"
```

## Requirements
Minimum python version 3.10

## Flow

The flow of the framework is sketched up in the following illustration:

![Flow diagram](Robot-Framework.svg)
