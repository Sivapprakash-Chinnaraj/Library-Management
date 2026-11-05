provider "aws" {
  region = var.aws_region
}

# ==========================================
# 1. VPC & Networking
# ==========================================
resource "aws_vpc" "library_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = { Name = "VPC-for-library-app" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.library_vpc.id
  tags = { Name = "library-app-igw" }
}

# ==========================================
# 2. Subnets
# ==========================================
resource "aws_subnet" "public_subnet" {
  vpc_id                  = aws_vpc.library_vpc.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, 1) # Outputs 10.0.1.0/24
  map_public_ip_on_launch = true
  availability_zone       = "${var.aws_region}a"
  tags = { Name = "Public-subnet-for-Library-app" }
}

resource "aws_subnet" "private_subnet_1" {
  vpc_id            = aws_vpc.library_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 2) # Outputs 10.0.2.0/24
  availability_zone = "${var.aws_region}a"
  tags = { Name = "Private-subnet-for-Library-app-1" }
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id            = aws_vpc.library_vpc.id
  cidr_block        = cidrsubnet(var.vpc_cidr, 8, 3) # Outputs 10.0.3.0/24
  availability_zone = "${var.aws_region}b"
  tags = { Name = "Private-subnet-for-Library-app-2" }
}

# ==========================================
# 3. Routing
# ==========================================
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.library_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "Library-app-rtb" }
}

resource "aws_route_table_association" "public_assoc" {
  subnet_id      = aws_subnet.public_subnet.id
  route_table_id = aws_route_table.public_rt.id
}

# ==========================================
# 4. Security Groups
# ==========================================
resource "aws_security_group" "ec2_sg" {
  name        = "Library-VPC-SG"
  description = "Allow HTTP and SSH"
  vpc_id      = aws_vpc.library_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "all-tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "VPC-for-RDS-sg"
  description = "Allow MySQL traffic from EC2 strictly"
  vpc_id      = aws_vpc.library_vpc.id

  ingress {
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.ec2_sg.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ==========================================
# 5. EC2 Instance (Jenkins/Docker Host)
# ==========================================
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"]
  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

resource "aws_instance" "app_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  subnet_id              = aws_subnet.public_subnet.id
  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  root_block_device {
    volume_size = 16
    volume_type = "gp3"
  }

  tags = { Name = "Library-app-instance" }
}

# ==========================================
# 6. RDS Database (MySQL)
# ==========================================
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "private-rds-subnet-group"
  subnet_ids = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
  tags = { Name = "library-db-subnet-group" }
}

resource "aws_db_instance" "library_db" {
  identifier             = "library-app-db"
  engine                 = "mysql"
  engine_version         = "8.0"
  instance_class         = "db.t4g.micro"
  allocated_storage      = 20
  db_name                = var.db_name
  username               = var.db_username
  password               = var.db_password
  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  skip_final_snapshot    = true
  publicly_accessible    = false

  tags = { Name = "library-db" }
}

# ==========================================
# 7. Outputs
# ==========================================
output "ec2_public_ip" {
  description = "The public IP of the Ubuntu server"
  value       = aws_instance.app_server.public_ip
}

output "rds_endpoint" {
  description = "The endpoint URL for PyMySQL in config.py"
  value       = aws_db_instance.library_db.endpoint
}