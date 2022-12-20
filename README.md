# COSN Faculty Services
  
The main purpose of this work is the development of a microservices based educational system for a University. To achieve this, each group of Cloud Service-Oriented Computing was responsible for the implementation of a part of the system and its respective services. The part represented in this repository concerns the Faculty, Classroom and Tuition Fee service.

## **Running**

A **Makefile** was created inside each service with all the commands needed to run the application. The following will demonstrate the most important.

### **Docker Compose**

To facilitate, it is being used Docker Compose to run the multiple services.

**Run the production environment** 

In the production environment all the services are started on Docker containers. The following command will start the services containers:

``docker-compose up -d``

**Other useful Make commands to do inside services folders**

To make a new Python virtual environment:

``make venv``
  
To make a new Python virtual environment (if needed) and install all the requirements:

``make install``

To make and apply Django migrations:

``make migrate``

To run Django server on local computer :

``make run``
  
## **REST API Documentation**

Swagger documentation available on the endpoint ``/api/schema/swagger-ui/`` fo each service