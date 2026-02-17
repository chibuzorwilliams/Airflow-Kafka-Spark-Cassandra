# Real-Time Data Streaming Pipeline  
### Airflow + Kafka + Spark Structured Streaming + Cassandra (Dockerized)

---

##  Overview

This project implements a fully containerized real-time data streaming pipeline using:

- **Apache Airflow** – workflow orchestration  
- **Apache Kafka (Confluent stack)** – event streaming backbone  
- **Apache Spark Structured Streaming** – real-time processing engine  
- **Apache Cassandra** – distributed NoSQL storage  
- **Docker Compose** – local infrastructure orchestration  

The pipeline simulates a production-style streaming architecture by ingesting live user data from an external API, streaming it through Kafka, processing it with Spark, and persisting it into Cassandra.

---

## System Architecture

![System Architecture](system_architecture.png)

### Data Flow

```
Random User API → Airflow Producer → Kafka Topic → Spark Streaming → Cassandra
```

1. Airflow triggers a short-lived producer job (demo-style ingestion).
2. Producer publishes JSON events to Kafka (`users_created` topic).
3. Spark consumes and parses the stream.
4. Processed records are written to Cassandra.

---

## 🧠 Why This Architecture?

This project demonstrates core distributed data engineering principles:

| Component | Role | Why It’s Used |
|------------|-------|---------------|
| Airflow | Orchestration | Manages reproducible, schedulable ingestion workflows |
| Kafka | Event Streaming | Durable, scalable message buffer between producer and consumer |
| Spark Structured Streaming | Processing | Fault-tolerant, scalable stream computation engine |
| Cassandra | Storage | Distributed write-optimized NoSQL database |
| Docker | Infrastructure | Portable local deployment |

This decoupled architecture improves:

- Scalability  
- Fault isolation  
- Reproducibility  
- Horizontal processing capability  

---

## 🛠 Tech Stack

- Python 3.9+
- Apache Spark 3.5.x
- Kafka (Confluent Platform)
- Cassandra 4.x
- Apache Airflow 2.x
- Docker & Docker Compose

---

## 📂 Project Structure

```
Airflow-Kafka-Spark-Cassandra/
│
├── dags/
│   └── kafka_stream.py        # Airflow DAG (Kafka producer)
│
├── spark_stream.py            # Spark Structured Streaming consumer
├── docker-compose.yml         # Infrastructure definition
├── requirements.txt           # Python dependencies
├── system_architecture.png    # Architecture diagram
└── README.md
```

---

## ⚙️ Setup & Execution

### 1️⃣ Start All Services

```bash
docker compose up -d
```

This launches:

- Airflow (Web UI)
- Kafka + Zookeeper
- Confluent Control Center
- Spark master + workers
- Cassandra
- PostgreSQL (Airflow metadata)

---

### 2️⃣ Trigger Airflow DAG

- Open Airflow UI
- Enable the DAG
- Trigger manually

The DAG:
- Pulls user data from RandomUser API
- Publishes records to Kafka topic `users_created`

---

### 3️⃣ Start Spark Streaming Job

```bash
spark-submit   --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0   spark_stream.py
```

Spark will:

- Subscribe to Kafka topic
- Parse JSON records
- Write streaming output to Cassandra

> **Note:** Make sure your Spark image/version matches the connector version you use above (e.g., Spark 3.5.x ↔ `:3.5.0`). If your stack uses Spark 3.4.x, update the package versions accordingly.

---

### 4️⃣ Verify Data in Cassandra

```bash
docker exec -it cassandra cqlsh
```

```sql
SELECT * FROM spark_streams.created_users;
```

---

## 🧪 What This Project Demonstrates

- Real-time event ingestion
- Kafka topic configuration and streaming
- Spark Structured Streaming (micro-batch processing)
- Cassandra table design for streaming workloads
- Multi-container orchestration with Docker
- Debugging distributed service connectivity

---

## ⚠ Engineering Tradeoffs & Notes

This is a local simulation of a distributed architecture.

In production, improvements would include:

- Dedicated long-running producer service (not Airflow loop)
- Schema enforcement via Schema Registry (Avro/Protobuf), not just raw JSON
- Stronger typing (e.g., consistent UUID handling end-to-end)
- Monitoring via Prometheus/Grafana
- Infrastructure-as-Code deployment (Terraform/K8s)
- Partition + throughput tuning for Kafka and Spark

Airflow is used here to **orchestrate** a demo ingestion workflow. In a production streaming system, ingestion services typically run independently of schedulers.

---

## 🐛 Common Issues Encountered

<<<<<<< HEAD
- Configured Kafka dual-listener setup (`PLAINTEXT` for internal Docker networking, `PLAINTEXT_HOST` for host access) to support both intra-container and host-machine connectivity
- Resolved Python 3.12+ incompatibility with `cassandra-driver` by running Spark jobs inside the container (Python 3.8 environment)
- Managed Spark permission issues on the `apache/spark` image by running `spark-submit` and `pip install` as root
- Debugged a `NullKeyColumnException` caused by missing UUID generation in the Kafka producer, which Cassandra requires as a primary key
=======
- Kafka listener configuration mismatches
- Cassandra driver compatibility with Python 3.12
- Docker memory limits affecting Spark
- Port binding conflicts

---

## 📈 Future Improvements

- Add Spark checkpointing for fault tolerance
- Introduce watermarking & windowed aggregations
- Add structured logging
- Implement exactly-once write semantics (where applicable)
- Deploy via Kubernetes

---

## 🎯 Learning Outcome

This project reinforced:

- Distributed systems fundamentals  
- Streaming vs batch processing differences  
- Decoupled microservice-style architectures  
- Operational debugging across containerized services  
>>>>>>> 4b8cf0a (Updated README)
