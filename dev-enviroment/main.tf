terraform {
  required_providers {
    coder = {
      source  = "coder/coder"
    }
    docker = {
      source  = "kreuzwerker/docker"
    }
  }
}

locals {
  username = data.coder_workspace_owner.me.name
}

data "coder_provisioner" "me" {
}

provider "docker" {
}

provider "coder" {
}

data "coder_workspace" "me" {
}

data "coder_workspace_owner" "me" {
}
