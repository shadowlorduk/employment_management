# Employment Management 

This repository contains an application and frontend for managing and interacting with an Azure SQL database.

## Table of Contents

- [About](#about)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [Flow Diagram](#Flow-Diagram)

## About

This project is designed to manage database files and provide a frontend interface for interacting with the database. It is written entirely in Python.

## Getting Started

To get started with this project, you will need to have Python installed on your machine. Follow these steps to set up the project:

This project uses a .env file for storing the Azure SQL connection details and the login detials to open the app - default user_name: admin password: password123

if you are connecting to Azure SQL with a Private network access connection, ensure you add your client ip address detials to the allowed list.

## Usage 

To run the application execute the followng into a terminal: 

pip install -r requirements.txt

To run the application, execute the following command:

python employment_management.py or replace with python3 if it does not execute. 

### Flow Diagram:

Outline the main components and their interactions. The flow diagram will include the following key elements:

Explanation:
1. **Initialisation**:
   - Import necessary modules, configure logging, and load environment variables.

2. **Database Connection**:
   - Define a function to connect to the database.

3. **Data Display**:
   - Define a function to display data with optional masking.

4. **Data Operations**:
   - Define functions to add, update, and delete records.
   - Define a function to search data.
   - Define a function to populate fields for editing.

5. **Login Handling**:
   - Define functions to show login windows and validate login.

6. **GUI Setup**:
   - Create the main window and add labels, entry widgets, and buttons.
   - Configure the menu bar and bind events.

7. **Main Event Loop**:
   - Start the main event loop to run the application.

This flow diagram provides a high-level overview of the script's structure and the interactions between its components.
