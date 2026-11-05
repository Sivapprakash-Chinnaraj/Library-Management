variable "aws_region" {
  description = "AWS Region to deploy resources"
  type        = string
  default     = "ap-south-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "instance_type" {
  description = "EC2 instance type for Jenkins and Docker"
  type        = string
  default     = "t2.medium"
}

variable "key_name" {
  description = "Name of the existing EC2 key pair"
  type        = string
  default     = "Linux"
}

variable "db_name" {
  description = "Initial database name for MySQL"
  type        = string
  default     = "library"
}

variable "db_username" {
  description = "Master username for the RDS instance"
  type        = string
  default     = "admin"
}

variable "db_password" {
  description = "Master password for the RDS instance"
  type        = string
  sensitive   = true
}