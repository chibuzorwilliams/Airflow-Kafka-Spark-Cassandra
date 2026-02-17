# Real-Time Data Streaming Pipeline

An end-to-end real-time data engineering pipeline that ingests user data from a public API, streams it through Apache Kafka, processes it with Apache Spark, and persists it in Apache Cassandra, all orchestrated with Apache Airflow and containerised with Docker.

![System Architecture](system_architecture.png)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | Apache Airflow 2.6.0 |
| Message Broker | Apache Kafka (Confluent 7.4.0) |
| Stream Processing | Apache Spark 3.5.0 |
| Storage | Apache Cassandra 4.1 |
| Metadata DB | PostgreSQL 14 |
| Containerisation | Docker & Docker Compose |

---

## Architecture Overview

The pipeline follows a linear streaming flow:

```
Random User API → Airflow → Kafka → Spark (Master + Workers) → Cassandra
```

**1. Data Ingestion (Airflow)**
An Airflow DAG (`user_automation`) triggers a Python task that calls the [Random User API](https://randomuser.me/) in a loop for 60 seconds, formats each response into a flat JSON object with a generated UUID, and produces messages to the Kafka topic `users_created`.

**2. Message Streaming (Kafka)**
Kafka acts as the central message bus. The Confluent stack includes:
- **Broker** — receives and stores messages
- **ZooKeeper** — manages broker coordination
- **Schema Registry** — manages message schemas
- **Control Center** — web UI for monitoring topics and consumers

**3. Stream Processing (Spark)**
A PySpark streaming job (`spark_stream.py`) subscribes to the `users_created` Kafka topic, deserialises the JSON payload, applies a schema, and writes each micro-batch to Cassandra using the Spark-Cassandra connector.

**4. Storage (Cassandra)**
Processed records are persisted in the `spark_streams.created_users` table with a UUID primary key, enabling fast, distributed reads at scale.

---

## Project Structure

```
Airflow-Kafka-Spark-Cassandra/
├── dags/
│   └── kafka_stream.py          # Airflow DAG — API ingestion & Kafka producer
├── script/
│   └── entrypoint.sh            # Airflow container initialisation script
├── spark_stream.py              # Spark structured streaming consumer
├── requirements.txt             # Python dependencies
├── system_architecture.png      # System architecture diagram
├── docker-compose.yml           # Full stack definition (11 services)
├── .gitignore
└── README.md
```

---

## Services

| Service | Port | Description |
|---|---|---|
| Airflow Webserver | 8080 | DAG management UI |
| Kafka Broker | 9092 | Message broker |
| Kafka Control Center | 9021 | Kafka monitoring UI |
| Schema Registry | 8081 | Schema management |
| Spark Master | 9090 | Spark cluster UI |
| Spark Master RPC | 7077 | Spark job submission |
| Cassandra | 9042 | Database |
| PostgreSQL | 5432 | Airflow metadata |

---

## Getting Started

### Prerequisites

- Docker Desktop (with at least 6GB RAM allocated)
- Docker Compose

### Run the stack

```bash
git clone https://github.com/YOUR_USERNAME/Airflow-Kafka-Spark-Cassandra.git
cd Airflow-Kafka-Spark-Cassandra

docker compose up -d
```

Wait for all containers to be healthy (2 minutes):

```bash
docker compose ps
```

### Trigger the pipeline

**1. Start the Airflow DAG**

Open [http://localhost:8080](http://localhost:8080) (credentials: `admin` / `admin`), enable the `user_automation` DAG, and trigger it manually. It will stream user records to Kafka for 60 seconds.

**2. Submit the Spark streaming job**

```bash
# Copy the script into the container
docker cp spark_stream.py spark-master:/opt/spark/spark_stream.py

# Install the Cassandra driver
docker exec -it --user root spark-master pip install cassandra-driver

# Submit the job
docker exec -it spark-master /opt/spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  --packages com.datastax.spark:spark-cassandra-connector_2.12:3.4.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1 \
  /opt/spark/spark_stream.py
```

**3. Verify data in Cassandra**

```bash
docker exec -it cassandra cqlsh -e "SELECT first_name, last_name, email FROM spark_streams.created_users LIMIT 10;"
```

---

## Monitoring

| UI | URL |
|---|---|
| Airflow | http://localhost:8080 |
| Kafka Control Center | http://localhost:9021 |
| Spark Master | http://localhost:9090 |

---

## Tear Down

```bash
docker compose down --remove-orphans
```

---

## Key Learnings

- Configured Kafka dual-listener setup (`PLAINTEXT` for internal Docker networking, `PLAINTEXT_HOST` for host access) to support both intra-container and host-machine connectivity
- Resolved Python 3.12+ incompatibility with `cassandra-driver` by running Spark jobs inside the container (Python 3.8 environment)
- Managed Spark permission issues on the `apache/spark` image by running `spark-submit` and `pip install` as root
- Debugged a `NullKeyColumnException` caused by missing UUID generation in the Kafka producer, which Cassandra requires as a primary key
