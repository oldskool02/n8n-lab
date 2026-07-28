# Design Functionality

## Function:
    check_docker_cli()

## Purpose and Responsibility:
    Verify that the Docker CLI is installed and operational.

## Returns:
    EXIT_SUCCESS
    EXIT_ERROR

## Side Effects:
    Reports status to the user.
    Displays Docker CLI version on success.


## doctor
  Mission
    Evaluate the health of the development environment.

  Responsibilities
    - Verify prerequisites
    - Verify Docker
    - Verify managed services
    - Report issues requiring attention

  Does NOT
    - Repair problems automatically
    - Update software
    - Change configuration