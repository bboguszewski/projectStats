from src.jira_search import JiraSearch
import os
from dotenv import load_dotenv
from datetime import datetime
from datetime import timezone
import csv

# Load environment variables
load_dotenv()

datetime_format = '%Y-%m-%dT%H:%M:%S.%f%z'
datetime_now = datetime.now(timezone.utc)

# Create search and get issues
search = JiraSearch(
    jira_server=os.getenv('AUTH_SERVER'),
    jira_mail=os.getenv('AUTH_EMAIL'),
    jira_token=os.getenv('AUTH_TOKEN')
)

issues = search.get_issues(
    jql=os.getenv('FILTER'),
    batch_size=int(os.getenv('SEARCH_BATCH', '50'))
)

statuses = []
results = []
for issue in issues:

    row = {
        'Issue Key': issue.key,
        'Issue Type': issue.fields.issuetype.name,
        'Summary': issue.fields.summary,
        'Current Status': issue.fields.status.name
    }

    date = datetime.strptime(issue.fields.created, datetime_format)
    date_from = date
    histories = reversed(issue.changelog.histories)
    for history_item in histories:
        for item in history_item.items:
            if item.field == "status":

                if item.fromString not in statuses:
                    statuses.append(item.fromString)

                duration = (datetime.strptime(history_item.created, datetime_format) - date).total_seconds()/3600
                date_from = date
                date = datetime.strptime(history_item.created, datetime_format)

                print( issue.key +' '+ item.fromString +' '+ date_from.strftime("%Y/%m/%d %H:%M") +' '+ date.strftime("%Y/%m/%d %H:%M") +' '+ duration.__str__())
                row.update({f'{status}': f'{hours:.2f}'.replace('.', ',') for status, hours in [[item.fromString, duration]]})

    if issue.fields.status.name not in statuses:
        statuses.append(issue.fields.status.name)

    duration = (datetime_now - date).total_seconds()/3600
    print( issue.key +' '+ issue.fields.status.name +' '+ date_from.strftime("%Y/%m/%d %H:%M")  +' '+ datetime_now.strftime("%Y/%m/%d %H:%M") +' '+ duration.__str__())
    row.update({f'{status}': f'{hours:.2f}'.replace('.', ',') for status, hours in [[issue.fields.status.name, duration]]})
    results.append(row)

print(len(results))

# Export to CSV
if results:
    # Get all possible status columns
    status_columns = set()
    for result in results:
        status_columns.update([col for col in result.keys()
                               if col.startswith('Time in ')])

    # Prepare headers
    headers = ['Issue Key', 'Issue Type', 'Current Status', 'Summary'] + sorted(list(statuses))

    # Write to CSV
    with open('time-01.csv', 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile,
                                fieldnames=headers,
                                delimiter=';',
                                quotechar='"',
                                quoting=csv.QUOTE_MINIMAL
        )

        writer.writeheader()
        for row in results:
            writer.writerow(row)

    print(f"\nResults exported to time.csv")
    print(f"Total issues processed: {len(results)}")