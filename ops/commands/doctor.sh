#!/usr/bin/env bash
run_doctor() {
    check_system
    check_docker
    check_all_services
}
