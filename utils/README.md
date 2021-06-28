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

### create all data
```
docker build -t create-data utils
docker run --rm --network=secure-code-platform-backend_main-network create-data python3 generate_test_data.py --create -U api -u <username> -p <password>
```

### create challenges
```
docker-compose -f docker-compose-dev.yml up --build create_data -U api -u <username> -p <password>
```
### remove challenges
```
docker-compose -f docker-compose-dev.yml up --build remove_data
```