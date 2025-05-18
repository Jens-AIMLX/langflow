# Setting up Langflow for Development

This guide will help you set up Langflow for local development.

## Prerequisites

- Python 3.10 to 3.13
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended)
- [Node.js](https://nodejs.org/en/download/package-manager)
- Git

## Fork and Clone the Repository

1. Navigate to the [Langflow GitHub repository](https://github.com/langflow-ai/langflow), and click **Fork**.

2. Clone your fork to your local machine:
   ```bash
   git clone https://github.com/<your_username>/langflow.git
   cd langflow
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/langflow-ai/langflow.git
   git remote set-url --push upstream no_push
   ```

## Initialize the Development Environment

Run the following command to set up the development environment:

```bash
make init
```

This command:
- Installs backend dependencies
- Installs frontend dependencies
- Builds the frontend static files
- Starts the Langflow application

## Development Mode

For active development with hot-reloading:

1. In one terminal, start the backend:
   ```bash
   make backend
   ```

2. In another terminal, start the frontend:
   ```bash
   make frontend
   ```

The Langflow UI will be available at http://localhost:3000/

## Documentation Development

To run the documentation locally:

```bash
cd docs
yarn install
yarn start
```

The documentation will be available at http://localhost:3001/ (or another port if 3000 is already in use).

## Before Submitting Changes

Run these commands to ensure your code meets the project standards:

```bash
make lint        # Run linters
make format      # Format code
make unit_tests  # Run unit tests
```

## Troubleshooting

**Windows/WSL Users**: If you encounter file mode changes in git, you can fix this with:
```bash
git config core.filemode false
```