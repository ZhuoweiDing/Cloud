class IssueResult(object):
  count = 0
  results = []

  def _init_(self, count = 0, results = []):
    self.count = count
    self.results = results

def search_jira_issues(jira, query):
  issueResult = IssueResult()
  results = jira.search_issues(query)

  if len(results) > 0:
    for issue in results:
      issueResult.count = issueResult.count + 1
      issueResult.results.append(issue.key)

  return issueResult