# Set up
Initial setup of the `venv` requires following commands:
```
python -m pip install --upgrade pip
pip install python-dotenv
pip install jira
pip install datetime
```

# Configuration
This script requires some data to be provided before it can be executed:

| config name  | description           | example                                      |
|--------------|:----------------------|----------------------------------------------|
| AUTH_SERVER  | JIRA server address   | https://example.atlassian.net                |
| AUTH_EMAIL   | User's e-mail address | address@mail.com                             |
| AUTH_TOKEN   | User's token          | token-for-JIRA-taht-is-very-very-long-string |
| FILTER       |                       | issuetype in (Story, Task, Bug)              |
| STATUSES_BEG |                       | In Progress                                  |
| STATUSES_END |                       | Done;Close                                   |