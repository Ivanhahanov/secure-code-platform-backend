# Platform Utils

## Upload Challenges
Filename: `upload_challenges.py`

Requirements: 
- `requests`

Usage:
```
python3 utils/upload_challenge.py example_challenges -u admin -p JxvmsiUz
```

## Generate test data
### create data
```
docker-compose -f docker-compose-dev.yml up --build create_data
```
### remove data
```
docker-compose -f docker-compose-dev.yml up --build remove_data
```