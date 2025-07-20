# ELT-Pipeline-with-Airflow-PostgreSQL-and-dbt
A complete ELT (Extract, Load, Transform) pipeline built with Apache Airflow, PostgreSQL, and dbt, orchestrated using Docker Compose.

## Architecture

```
Source PostgreSQL → ELT Script → Destination PostgreSQL → dbt Transformations
                ↓
            Apache Airflow (Orchestration)
```

## Features

- **Dockerized Environment**: Complete setup using Docker Compose
- **Apache Airflow**: Workflow orchestration and scheduling
- **PostgreSQL**: Source and destination databases
- **dbt**: Data transformations and modeling
- **Docker-in-Docker**: dbt runs in isolated Docker containers
- **Error Handling**: Comprehensive logging and error handling
- **Health Checks**: Database connectivity monitoring

## Project Structure

```
├── airflow/
│   └── dags/
│       └── elt_dag.py              # Main Airflow DAG
├── elt/
│   └── elt_script.py               # ELT extraction script
├── custom_postgres/
│   ├── dbt_project.yml             # dbt project configuration
│   ├── models/                     # dbt SQL models
│   └── profiles.yml                # dbt connection profiles
├── source_db_init/
│   └── init.sql                    # Source database initialization
├── docker-compose.yaml             # Docker services configuration
└── README.md
```

## Prerequisites

- Docker Desktop
- Docker Compose
- Windows/Linux/macOS

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/elt-pipeline
   cd elt-pipeline
   ```

2. **Set up dbt profiles** (Windows users)
   - Ensure your dbt profiles.yml is located at `C:\Users\<username>\.dbt\profiles.yml`
   - Update the path in `elt_dag.py` if different

3. **Start the services**
   ```bash
   docker-compose up -d
   ```

4. **Access Airflow UI**
   - URL: http://localhost:8080
   - Username: `airflow`
   - Password: `password`

5. **Trigger the DAG**
   - Go to the Airflow UI
   - Find the `elt_and_dbt` DAG
   - Click "Trigger DAG"

## 📊 Database Connections

### Source PostgreSQL
- **Host**: localhost
- **Port**: 5433
- **Database**: source_db
- **User**: postgres
- **Password**: secret

### Destination PostgreSQL
- **Host**: localhost
- **Port**: 5434
- **Database**: destination_db
- **User**: postgres
- **Password**: secret

### Airflow PostgreSQL
- **Host**: localhost
- **Port**: 5432 (internal)
- **Database**: airflow
- **User**: airflow
- **Password**: airflow

## 🔧 Configuration

### Environment Variables
- `HOST_PROJECT_PATH`: Set automatically to current directory
- Modify `docker-compose.yaml` for custom configurations

### dbt Profiles
Ensure your `profiles.yml` contains:
```yaml
custom_postgres:
  outputs:
    dev:
      type: postgres
      host: destination_postgres
      user: postgres
      password: secret
      port: 5432
      dbname: destination_db
      schema: public
      threads: 1
  target: dev
```

## 🔄 Workflow Details

### DAG Tasks
1. **run_elt_script**: Executes the ELT script to move data from source to destination
2. **dbt_run**: Runs dbt transformations in a Docker container

### Task Dependencies
```
run_elt_script >> dbt_run
```
