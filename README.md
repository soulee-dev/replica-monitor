# Replica-Monitor

Replica-Monitor is a tool designed to automate the setup of a master-slave MySQL replication and a master-python-mysql-replication. With just a single command, it will create numerous tables and columns, populate them with random data, and then compare the metrics between the two replication structures. Finally, it provides a comprehensive CSV report of the results.

## Features

- Automated setup of **Master**-**Slave** replication.
- Automated setup of **Master**-**[python-mysql-replication](https://github.com/julien-duponchelle/python-mysql-replication)**.
- Creation of multiple tables and columns.
- Populating the database with random data.
- Metrics comparison between the two replication structures.
- Generation of a CSV report.

## Getting Started

### Prerequisites

Before running Replica-Monitor, ensure you have the following installed:

- Docker, Docker Compose
- Python

### Installation

Clone this repository:

```
git clone https://github.com/soulee-dev/replica-monitor.git
cd replica-monitor
pip install -r requiriements.txt
```

### Usage

To run the full setup, metrics comparison, and report generation, simply type:

```
make
```

## Example Report

To view a sample of the generated CSV report, click [here](https://github.com/soulee-dev/replica-monitor/blob/main/diff_metrics.pdf).

## Contributing

If you'd like to contribute, please fork the repository and make changes as you'd like. Pull requests are warmly welcomed.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
