variable "region" {
  description = "AWS region"
  type        = string
  default = "us-east-1"
}

variable "instance_type" {
  description = "AWS instance type"
  type        = string
  default     = "t2.micro"
}

variable "disk_size" {
  description = "Root disk size in GB"
  type        = number
  default     = 10
}
