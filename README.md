# 📚 Cloud-Native Library Management System

A full-stack, containerized Library Management System deployed on AWS. This project demonstrates a complete Cloud and DevOps lifecycle, including custom AWS networking, relational database management, containerization, and an automated CI/CD pipeline.

## 🏗️ Architecture & Cloud Infrastructure

This application is hosted on a custom-built AWS architecture designed for security and scalability:

* **Custom VPC (10.0.0.0/16):** Network isolated environment with customized route tables and Internet Gateways.
* **Public Subnet:** Hosts the Ubuntu EC2 instance running the application container, Jenkins server, and Docker host.
* **Private Subnets:** Houses the AWS RDS instance, restricting direct internet access for enhanced data security.
* **Security Groups:** Strictly defined ingress/egress rules (e.g., allowing Port 80 to EC2, and only Port 3306 from EC2 to RDS).
* **AWS RDS (MySQL):** Managed relational database ensuring persistent storage and automated backups.

## ⚙️ DevOps & CI/CD Pipeline

The project utilizes a fully automated Continuous Integration and Continuous Deployment (CI/CD) pipeline:

1. **Source Control:** Code is version-controlled via GitHub.
2. **Webhook Trigger:** Pushing code to the `main` branch automatically triggers the Jenkins pipeline via GitHub Webhooks.
3. **Jenkins CI/CD:** A declarative `Jenkinsfile` orchestrates the build process on the EC2 host.
4. **Containerization:** Docker builds the image containing the Python Flask app and its dependencies.
5. **Artifact Registry:** The Jenkins pipeline authenticates and pushes the finalized Docker image to Docker Hub (`sivapprakash1634/library-management`).
6. **Deployment:** The container is pulled and run dynamically on the EC2 host, mapping port 80 to the Flask application.

## 🛠️ Tech Stack

* **Application:** Python 3, Flask, HTML/CSS/JavaScript
* **Database:** AWS RDS MySQL (connected via `PyMySQL` and `DictCursor`)
* **Cloud Provider:** Amazon Web Services (VPC, EC2, RDS, Security Groups)
* **DevOps Tools:** Git, GitHub, Jenkins, Docker, Docker Hub
* **OS:** Ubuntu Linux

## ✨ Core Application Features

* **Role-Based Access Control (RBAC):** Distinct dashboards and permissions for `Staff` and `Student` roles.
* **Inventory Management:** Staff can add, update, and remove books from the system.
* **Circulation Desk:** Secure checkout and return system tracking available copies and due dates.
* **Student Portal:** Users can log in to view their currently borrowed books and due dates.

## 🚀 Local Setup & Testing

To run this project locally, ensure you have Docker installed.

1. Clone the repository:
   ```bash
   git clone https://github.com/Sivapprakash-Chinnaraj/library-management.git
   cd library-management
   ```
2. Set up your environment variables in `.env` (or update `config.py`):
   ```ini
   MYSQL_HOST=localhost
   MYSQL_USER=admin
   MYSQL_PASSWORD=yourpassword
   MYSQL_DB=library
   ```
3. Build and run the Docker container:
   ```bash
   docker build -t library-app .
   docker run -d -p 80:5000 --name library-app library-app
   ```
4. Access the app at `http://localhost`.

*Default Login Credentials for testing:*
* **Admin:** admin@library.com | password123
* **Student:** alice@example.com | password123