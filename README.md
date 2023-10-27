# Robot-Framework V1

This repo is meant to be used as a template for robots made for [OpenOrchestrator](https://github.com/itk-dev-rpa/OpenOrchestrator).

## Quick start

1. To use the template simply use the repo as a template as shown [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).

2. Fill out the requirements.txt file with all packages needed by the robot.

3. Implement all functions in the files:
* src/initialize.py
* src/get_constants.py
* src/reset.py
* src/process.py
* Feel free to add more files as needed.

4. Make sure the smtp setup in error_screenshot.py is set up to your needs.

When the robot is run from OpenOrchestrator the main.bat file is run.
main.bat does a few things:
1. A virtual environment is automatically setup with the required packages.
2. The framework is called passing on all arguments needed by [OpenOrchestratorConnection](https://github.com/itk-dev-rpa/OpenOrchestratorConnection).

## Requirements
Minimum python version 3.10

## Flow

The flow of the framework is sketched up in the following illustration:

![Flow diagram](Robot-Framework.svg)
