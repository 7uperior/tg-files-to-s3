"""This module is concerned with handling settings with environment variables.

The settings are created using a Pydantic class that reads environment variables from a `.env` file in the
`/api` directory if it is available.

Example `.env` file:
```
DB_USER = postgres
DB_PASSWORD = postgres
DB_HOST = postgres
DB_PORT = 5432
DB_NAME = fastapi
SECRET_KEY = d751923806645de8f6f6376798574ef844bb6d6d5ca36a8224718a84c775ad19
ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTE = 30
```

Although it is recommended to use a .env file if deploying docker-compose, the settings will also read from
environment variables that are defined in the current terminal session.

Example creating the environment variables through the terminal:
`$ export DB_USER=postgres`
"""

from pydantic import BaseSettings


class Settings(BaseSettings):
	db_user: str
	db_password: str
	db_host: str
	db_port: str
	db_name: str
	secret_key: str
	algorithm: str
	access_token_expire_minute: int

	class Config:
		env_file = '.env'
		env_file_encoding = 'utf-8'


settings = Settings()
