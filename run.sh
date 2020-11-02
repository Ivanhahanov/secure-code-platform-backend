#!/bin/bash
docker network create -d bridge checkers-network
docker-compose up --build