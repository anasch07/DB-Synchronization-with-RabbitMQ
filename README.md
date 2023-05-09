# DB Synchronization with RabbitMQ

### Description

This consists of 2 sides:
* 1 Head Office
* Multiple Branch Offices

Each has the following SQL Table structure that represents product sales locally:

<p align="center">
    <img src="/Readme%20Images/table.png"><br/>
</p>

Using SQLite for the database with SQLAlchemy as an ORM.

### Features

* Each office can insert new product sales, edit & delete them.
* Branch offices can send the changes done to their local database to the Head Office via a RabbitMQ Broker.
* Head office can take the changes from RabbitMQ Broker & apply them to the local database.
* RabbitMQ Connection is required only when synchronizing.

### How to use

Example of how to use can be found in bash scripts:
* [BO1.sh](/BO1.sh): Start a Branch Office with ID `BO1` (ID Used for queue name)
* [BO2.sh](/BO2.sh): Start a Branch Office with ID `BO2` (ID Used for queue name)
* [HO.sh](/HO.sh): Start a Branch Office with ID `HO`

### Requirements

Can be found in [requirements](/requirements)
