# Babex
The babex baby experiment system

The babes baby experiment system is designed to handle information about
experiments, labs, parents and there children. As such it contains contains
sensitive data about people operating and participating in the Babex system 

In order to achieve an high level of protection of the data we've decided to
have a private part that is accessible to the people of the lab and a more
public part that is tailored for the parents of the babies participating in
the experiment.

## The lab app
This application in located in the $PROJECT_ROOT/lab and this application holds
the database for storing most sensitive data as such it should be hosted on
a place on only accessible from the local network or a VPN connection.
You can find more about it in [lab folder][1]

## The parent app
This app is in $PROJECT_ROOT/parent. This application is mend to be accessible
by the parents of the infants participating in the experiments. It uses
django rest framework to communicate with the back end. Hence, this server should
be accessible from the internet, but located inside the local network of the
lab app. You can find more about it in the [parent folder][2]

### Running integration tests

```
cd lab/integration_tests
pytest
cd parent/integration_tests
pytest
```

[1]:lab/README.md
[2]:parent/README.md
