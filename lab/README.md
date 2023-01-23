# babex
The babex baby experiment system


## Development

### Running integration tests

```
cd integration_tests
pytest
```

## User roles

* A registered user (`User` model) is a leader if they are added as leader to an experiment (`Experiment.leaders`).
* A staff user (`User.is_staff = True`) is a lab manager.
* A superuser (`User.is_superuser = True`) can do everything (should be reserved for technicians).

Notes:

* At some point in the future we should have a /researcher/ role.
This could be implemented with a regular user that's assigned to specific experiments via an `Experiment.researchers` foreign key, just like leaders.
* Parents/participants should not have a user account on the lab app.
