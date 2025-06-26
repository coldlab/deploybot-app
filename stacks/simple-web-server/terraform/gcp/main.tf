    terraform {
      required_providers {
        google = {
          source  = "hashicorp/google"
          version = "~> 4.0"
        }
      }
    }

    provider "google" {
      project = var.project_id
      region  = var.region
      zone    = var.zone
    }

    # Compute instance
    resource "google_compute_instance" "web_server" {
      name         = "web-server"
      machine_type = var.instance_type
      zone         = var.zone

      boot_disk {
        initialize_params {
          image = "debian-cloud/debian-11"
          size  = var.disk_size
        }
      }

      network_interface {
        network = "default"
        access_config {
          // Ephemeral public IP
        }
      }

      metadata_startup_script = <<-SCRIPT
        #!/bin/bash
        apt-get update
        apt-get install -y nginx
        systemctl start nginx
      SCRIPT

      tags = ["http-server", "https-server"]
    }

    # Firewall rule
    resource "google_compute_firewall" "http" {
      name    = "allow-http"
      network = "default"

      allow {
        protocol = "tcp"
        ports    = ["80"]
      }

      source_ranges = ["0.0.0.0/0"]
      target_tags   = ["http-server"]
    }
