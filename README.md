# ufcpy

## Local development

#### Install and start MySQL server
```
$ brew install mysql
$ mysql.server start
```

#### Create db, temp user and grant privileges
```
$ sudo mysql
CREATE DATABASE ufcdb;
CREATE USER 'tempuser'@'localhost' IDENTIFIED BY 'temppassword';
GRANT ALL PRIVILEGES ON ufcdb . * TO 'tempuser'@'localhost';
FLUSH PRIVILEGES;
exit
```

#### Install dependencies
`$ pip install -r requirements.txt`

#### Save dependencies
`$ pip freeze > requirements.txt`

## Architecture

- crawler
    - multiple data sources
    - event based updates 
- storage
- predictor(s)
    - featurizer
    - learner
    - verifier
        - cross-validation
        - benchmarking (against trivial predictors) 

