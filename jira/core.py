from jira import JIRA
from jira import JIRAError

from models import IssueResult
# from ../utils.timeit import timeit

def create_jira_connection(url, username, password):
  try:
    jira = JIRA(
      {
        'server': url,
        #HN updated:
        #'verify': True
        'verify': False
      },
      basic_auth=(username, password)
    )
    print("Connection to Jira Established")
    return jira

  except JIRAError as e:
    print("Error: Jira Connection to {0} Unsuccessful. Msg: {1}\nStatus Code:{2}\nHeaders:{3}\n".format(url, e.response.text, e.response.status_code, e.response.headers))

def check_for_existing_jira_issue(jira, title, projectKey, issueType):
  return IssueResult.search_jira_issues(jira, 'project={0} AND issueType={1} AND status=Open AND summary~"{2}"'.format(projectKey, issueType, title))

def create_jira_issue(jira, failedtestcase, projectKey, issueType = "Bug", env = "DEV", assignee = ""):
  try:
    response = jira.create_issue(
      project=projectKey,
      summary=failedtestcase.title,
      description=failedtestcase.description,
      assignee={
        'name': assignee
      },
      issuetype={
        'name': issueType
      },
      customfield_19003={
        'value': env
      },
      customfield_19400={
        'value': 'Test - Test Plan Miss'
      }
    )
    return True

  except Exception as e:
    print('Warning, unable to create JIRA issue. Error: {0} for Test Case: {1}'.format(str(e), failedtestcase.title))
    return False