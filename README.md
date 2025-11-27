# Ondernemer Centraal

## Running the app locally with Docker

This documentation is tested on a Linux environment (Ubuntu).

### Prerequisites

1. [`nvm`](https://github.com/nvm-sh/nvm): 'Node Version Manager'. Can be used to install `node`. Required for building the Docker image.
2. [Docker](https://docs.docker.com/get-started/) and [Docker Compose](https://docs.docker.com/compose/install/)
3. Basic knowledge of Docker and the Linux terminal.

### Overview

The application consists of several modules:

1. The frontend (Vue single-page application)
2. Python (FastAPI) backend (REST API)
3. Postgres (database)
4. Minio (file storage)
5. Keycloak (authentication)
6. Dbgate (a GUI for the database, only used for development)
7. Clamav: a service to scan files for malware

### Starting the application for the first time (with initialization steps)

When starting the application for the first time, some initialization is done for Keycloak and the REST API. Use the steps below to do this correctly:

1. Start the backend
```bash
cd backend
docker compose up keycloak
```
 This will build the Keycloak image and also apply the correct configuration required for this project.

2. Verify Keycloak has started by navigating to http://localhost:8080. You should see the login screen of Keycloak.
3. Start the API
```bash
docker compose up api
```
Navigate to `http://localhost:8000/docs` and verify that you see the Swagger client of the API.

4. Start the frontend.

```bash
# Navigate to the frontend, assuming you are in ./backend
cd ../frontend

# Use the correct Node version (specified in `.nvmrc`)
nvm use
 
 # build the Vue frontend
VITE_API_URL=http://localhost:8000 npx vite build --mode development

# Build the Docker image
docker compose build

# Start the container
docker compose up
```
Note: if you want to change the port at which the API runs (default: 8000), adjust in this command AND with the backend environment variable `FASTAPI_PORT`.

5. Verify that everything works by navigating to `http://localhost:5173/beheer`. You can login with username `admin` and password `admin`.

### Starting the application after initialization

After initialization has been done, starting the application is simpler:

```bash
# Start a terminal in the root of this repository
cd backend
docker compose up api
```

In another terminal"
```bash
# Start a terminal in the root of this repository
cd frontend
docker compose up
```

Verify that everything works by navigating to `http://localhost:5173/beheer`. You can login with username `admin` and password `admin`.

### Configuration

The `compose.yml` in `./backend` uses environment variables with default. Create a `.env` file to override any of these variables if needed.

### Setting up email

E-mails are sent from (1) the backend and (2) Keycloak. By default, this is disabled. 

Enable backend emails:

1. Set an environment variable to `EMAIL_ENABLED=1`
2. Configure the following environment variables:

- `EMAIL_DOMAIN`: the domain of the e-mail server.
- `EMAIL_CLIENT_NAME`: the e-mail address prefix from which emails are sent. The e-mail address will be `<EMAIL_CLIENT_NAME>@<EMAIL_DOMAIN>`.
- `EMAIL_RELAY_PASSWORD_I8S`: the password used to connect to the email relay server.
- `EMAIL_RELAY_HOSTNAME`: the hostname on which the email relay server is available.

Enable Keycloak emails:

1. Set environment variable `KEYCLOAK_REQUIRE_EMAIL_VERIFICATION=1`.
2. Open Keycloak on `localhost:8080` and go to the realm `oc_portaal`
3. Navigate to `Realm settings`
4. Go to tab 'Email' and configure the e-mail settings.

## Keycloak

By default, Keycloak is available at `http://localhost:8080`. The username and password for local development is `admin` and `admin`.

## Security
The configuration in `compose.yml` contains several secret keys. The default value is `this_is_an_unsafe_secret_you_must_change_it`. Change these before rolling out on production, for example with:

```bash
head -c 24 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 32; echo
```