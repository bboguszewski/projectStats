import os
import csv
from dotenv import load_dotenv
from datetime import datetime
from src.jira_search import JiraSearch


load_dotenv()

datetime_format = '%Y-%m-%dT%H:%M:%S.%f%z'

# jira = JIRA(options={'server': os.getenv('AUTH_SERVER')}, basic_auth=(os.getenv('AUTH_EMAIL'), os.getenv('AUTH_TOKEN')))

statusesBeg = os.getenv('STATUSES_BEG').split(';')
for x in range(len(statusesBeg)):
    statusesBeg[x] = str.lower(statusesBeg[x])

statusesEnd = os.getenv('STATUSES_END').split(';')
for x in range(len(statusesEnd)):
    statusesEnd[x] = str.lower(statusesEnd[x])


class HistoryItem:

    def __init__(self, id, name, date, duration):
        self.id = id
        self.name = name
        self.date = date
        self.duration = duration


# counter = 0
# searchLoop = True
# maxResults = int(os.getenv('SEARCH_BATCH'))
# startAt = int(os.getenv('SEARCH_FROM'))
# issues = []
# while searchLoop:
#     search = jira.search_issues(os.getenv('FILTER'), expand='changelog', maxResults=maxResults, startAt=startAt)
#     searchLoop = len(search) > 0
#     issues = issues + search
#     startAt += maxResults
#     # show number, debug only
#     counter += len(search)
#     print(counter)

search = JiraSearch(
    jira_server=os.getenv('AUTH_SERVER'),
    jira_mail=os.getenv('AUTH_EMAIL'),
    jira_token=os.getenv('AUTH_TOKEN')
)
issues = search.get_issues(jql=os.getenv('FILTER'), batch_size=int(os.getenv('SEARCH_BATCH')), start_at=int(os.getenv('SEARCH_FROM')))


def calculate_history(issue):
    print(issue)

# Find the first status that indicates work has started
def find_first_work(status_change):
    if len(status_change) > 1:
        for x in range(len(status_change)):
            if str.lower(status_change[x].name) in statusesBeg:
                return x
        return -1
    return -1


# Find the last status that indicates work has finished
# In case we have the following status changes for a given task:
# 'To Do' -> 'In Progress' -> 'Ready to Release' -> 'In Progress' -> 'Ready to Release' -> 'Released'
# the correct status should be second 'Ready to Release'
def find_last_done(status_change: []):
    for x in reversed(range(len(status_change))):
        if str.lower(status_change[x].name) in statusesEnd:
            return x
    return -1

output = []
items = []
counter = 0
counterFailed = 0
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
        print(issue.key + ' ' + issue.fields.status.name + ' ' + end_date.strftime("%Y/%m/%d %H:%M") + ' ' + cycle_time.__str__())
        output_row = [
            issue.key,
            issue.fields.status.name,
            end_date.strftime("%Y/%m/%d %H:%M"),
            cycle_time.__str__().replace('.', ','),
            issue.fields.issuetype.name
        ]

        # Add check for customfield_10026
        if hasattr(issue.fields, 'customfield_10026') and issue.fields.customfield_10026 is not None:
            output_row.append(issue.fields.customfield_10026.__str__().replace('.', ','))
        else:
            output_row.append('')  # Add

        output.append(output_row)


    else:
        print(issue.key + ' ' + issue.fields.status.name)
        counterFailed += 1

    items.append([
        issue.key,
        issue.fields.status.name
    ]);

print("items calculated: " + counter.__str__() + " items failed: " + counterFailed.__str__())

# Export data to csv file
with open('data.csv', mode='w') as data_file:
    data_file = csv.writer(data_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for d in output:
        data_file.writerow(d)

with open('data2.csv', mode='w') as data_file:
    data_file = csv.writer(data_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for d in items:
        data_file.writerow(d)