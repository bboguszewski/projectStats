import os
import csv
from dotenv import load_dotenv
from jira.client import JIRA
from datetime import datetime

load_dotenv()

datetime_format = '%Y-%m-%dT%H:%M:%S.%f%z'

jira = JIRA(options={'server': os.getenv('AUTH_SERVER')}, basic_auth=(os.getenv('AUTH_EMAIL'), os.getenv('AUTH_TOKEN')))
statusesBeg = os.getenv('STATUSES_BEG').split(';')
statusesEnd = os.getenv('STATUSES_END').split(';')

class HistoryItem:

    def __init__(self, id, name, date, duration):
        self.id = id
        self.name = name
        self.date = date
        self.duration = duration


searchLoop = True
maxResults = 15
startAt = 0
issues = []
while searchLoop:
    search = jira.search_issues(os.getenv('FILTER'), expand='changelog', maxResults=maxResults, startAt=startAt)
    searchLoop = len(search) > 0
    issues = issues + search
    startAt += maxResults


def calculate_history(issue):
    print(issue)


# Find the first status indicated that work has started
def find_first_work(status_change):
    if len(status_change) > 1:
        for x in range(len(status_change)):
            if status_change[x].name in statusesBeg:
                return x
        return -1
    return -1


# Find the last status indicated that work has finished
# In case we have following status changes for a given tasks:
# 'To Do' -> 'In Progress' -> 'Ready to Release' -> 'In Progress' -> 'Ready to Release' -> 'Released'
# the correct status should be second 'Ready to Release'
def find_last_done(status_change: []):
    for x in reversed(range(len(status_change))):
        if status_change[x].name in statusesEnd:
            return x
    return -1

output = []
items = []
counter = 0
for issue in issues:
    status_change = []
    date = datetime.strptime(issue.fields.created, datetime_format)
    histories = reversed(issue.changelog.histories)
    for history in histories:
        for item in history.items:
            if item.field == "status":
                duration = (datetime.strptime(history.created, datetime_format) - date).total_seconds()
                date = datetime.strptime(history.created, datetime_format)
                status_change.append(HistoryItem(getattr(item, 'from'), item.fromString, date, duration))
            # if item.field == "Sprint":
            #     status_change.append(HistoryItem(getattr(item, 'from'), item.fromString, date))

    status_change.append(HistoryItem(issue.fields.status.id, issue.fields.status.name, date, -1))

    count_from = find_first_work(status_change)
    count_to = find_last_done(status_change)

    if 0 < count_from < count_to and count_to > 0:
        end_date = datetime.now()
        counter += 1
        cycle_time = 0
        for x in range(count_from, count_to, 1):
            cycle_time += status_change[x].duration
            end_date = status_change[x].date

        cycle_time = cycle_time / 3600
        print(issue.key + ' ' + issue.fields.status.name + ' ' + end_date.strftime(
            "%Y/%m/%d %H:%M") + ' ' + cycle_time.__str__())
        output.append([
            issue.key,
            issue.fields.status.name,
            end_date.strftime("%Y/%m/%d %H:%M"),
            cycle_time.__str__().replace('.', ','),
            issue.fields.issuetype.name,
            issue.fields.customfield_10026.__str__().replace('.', ',')
        ])

    else:
        print(issue.key + ' ' + issue.fields.status.name)

    items.append([
        issue.key,
        issue.fields.status.name
    ]);

# Export data to csv file
with open('data.csv', mode='w') as data_file:
    data_file = csv.writer(data_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for d in output:
        data_file.writerow(d)

with open('data2.csv', mode='w') as data_file:
    data_file = csv.writer(data_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for d in items:
        data_file.writerow(d)