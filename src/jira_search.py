from jira.client import JIRA
from jira.resources import Issue
from typing import List


class JiraSearch:
    def __init__(self, jira_server: str, jira_mail: str, jira_token: str):

        self.jira = JIRA(
            options={'server': jira_server},
            basic_auth=(jira_mail, jira_token)
        )

    def get_issues(self, jql: str, batch_size: int = 50, start_at: int = 0, limit: int = -1) -> List[Issue]:
        """
        Get all issues matching the JQL query

        Args:
            jql: JQL query string
            batch_size: Number of issues to fetch per request
            start_at:
            limit:

        Returns:
            List of JIRA issues

        """
        issues = []

        while True:
            batch = self.jira.search_issues(
                jql,
                expand='changelog',
                maxResults=batch_size,
                startAt=start_at
            )

            if not batch:
                break

            issues.extend(batch)
            start_at += batch_size
            print(f"Loaded {len(issues)} issues")

            if 0 < limit <= len(issues):
                break

        return issues