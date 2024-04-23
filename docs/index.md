<h2 align="center">
    microservice-py-docker

</h2>
<p align="center">
    0.10.0
</p>

<p align="center">
  <img  src="https://github.com/yemaney/microservice-py-docker/actions/workflows/test.yaml/badge.svg" alt="Test">
  <img  src="images/coverage.svg" alt="Coverage">
</p>

<h1 align="center">
    Microservice with python and docker
</h1>
---
<p align="center">
  <img  src="images/diagram.png" alt="Coverage">
</p>
---

### API

Api created using FastAPI. Acts as a gateway that listens for user requests, and routes them to the appropriate services.

- Functionalities
    - create users
        - with password hashing
    - get all users
    - login
    - oath2 authentication with JWT token
    - upload file

### Database

Uses PostgreSQL. Stores information for the users that have been created.

- Table
    - Users

### RabbitMQ

Queue for messages created  whenever file is uploaded

### Backend

Server hosting consumers for the RabbitMQ files queue.

### Fileserver

Server hosting raw files that users upload.
