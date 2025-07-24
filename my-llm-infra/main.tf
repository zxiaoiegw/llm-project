# Provider Configuration
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 4.0"
    }
  }
}

provider "google" {
  project = "zxiao-llm-project-2025"
  region  = "us-central1"
  zone    = "us-central1-a"
}

# Custom VPC Network
resource "google_compute_network" "llm_vpc" {
  name                    = "llm-vpc"
  auto_create_subnetworks = false  
  description             = "Custom VPC for LLM project"
}

# Subnet
resource "google_compute_subnetwork" "llm_subnet" {
  name          = "llm-subnet"
  ip_cidr_range = "10.0.1.0/24"
  region        = "us-central1"
  network       = google_compute_network.llm_vpc.id
  description   = "Subnet for LLM project resources"
}

# SSH Firewall Rules
resource "google_compute_firewall" "allow_ssh" {
  name    = "allow-ssh"
  network = google_compute_network.llm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["22"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["ssh-allowed"]
  
  description = "Allow SSH access"
}

# Web Traffic Firewall Rule
resource "google_compute_firewall" "allow_http_https" {
  name    = "allow-http-https"
  network = google_compute_network.llm_vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
  target_tags   = ["web-server"]
  
  description = "Allow HTTP and HTTPS traffic"
}

# Internal Traffic Firewall Rule
resource "google_compute_firewall" "allow_internal" {
  name    = "allow-internal"
  network = google_compute_network.llm_vpc.name

  allow {
    protocol = "tcp"
  }

  allow {
    protocol = "udp"
  }

  allow {
    protocol = "icmp"
  }

  source_ranges = ["10.0.1.0/24"]
  
  description = "Allow internal traffic within VPC"
}

# Compute VM Instance (for small cost)
resource "google_compute_instance" "llm_vm" {
  name         = "llm-vm"
  machine_type = "e2-micro"
  zone         = "us-central1-a"

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-11"
      size  = 20  # GB, within Always Free tier limit
    }
  }

  network_interface {
    network    = google_compute_network.llm_vpc.id
    subnetwork = google_compute_subnetwork.llm_subnet.id
    
    # Assign external IP
    access_config {
    }
  }

  tags = ["ssh-allowed", "web-server"]

  # Startup script to install Docker and basic dependencies
  metadata_startup_script = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io
    systemctl start docker
    systemctl enable docker
    usermod -aG docker debian
  EOF

  metadata = {
    ssh-keys = "debian:${file("~/.ssh/id_ed25519.pub")}"
  }
}
