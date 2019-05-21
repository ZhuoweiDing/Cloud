# -*- coding: utf-8 -*-


import glob, os, sys, datetime
import xml.etree.ElementTree as ET 

from jira import JIRA, exceptions

import core
from models import TestCase, IssueResult

class ParseResults(object):
  testcases = []
  createdCount = 0
  resolvedCount = 0
  updatedCount = 0

  def _init_(self, createdCount = 0, resolvedCount = 0, updatedCount = 0):
    self.testcases = []
    self.createdCount = createdCount
    self.resolvedCount = resolvedCount
    self.updatedCount = updatedCount

def parse_results_to_jira(url, key, username, password, result_path, issueType = "Bug", environment = "DEV", assignee = ""):
  jira = core.create_jira_connection(url, username, password)

  xmlGlob = glob.glob("{0}/*.xml".format(result_path))
  testResults = ParseResults()

  #HN DEBUG:
  print("xmlGlob:", len(xmlGlob), flush=True)
  for xml in xmlGlob:
    result = ET.parse(xml).getroot()

    for testCase in result.iter('testcases'):
      if testCase.find('error') is not None or testCase.find('Failure') is not None:
        testResults.testcases.append(TestCase.generate_testcase_object(
          environment,
          testCase.attrib.get('classname'),
          testCase.attrib.get('name'),
          testCase.find('error').attrib.get('type') if testCase.find('error') is not None else testCase.find('Failure').get('type'),
          testCase.find('error').text if testCase.find('error') is not None else testCase.find('Failure').text 
        ))
      else:
        testResults.testcases.append(TestCase.generate_testcase_object(
          environment,
          testCase.attrib.get('classname'),
          testCase.attrib.get('name')
        ))
      continue

  #HN DEBUG:
  print("testResults.testcases", len(testResults.testcases), flush=True)
  for testcase in testResults.testcases:
    existingIssues = core.check_for_existing_jira_issue(jira, testcase.title, key, issueType)

    if testcase.description is not None:
      print("existingIssues.count:", existingIssues.count, flush=True)
      if existingIssues.count > 0:
        jira.add_comment(
          existingIssues.results[0],
          "h2. {0}: Test Case Additional Fail\n\n{{code:borderStyle=solid}}{1}{{code}}".format(datetime.datetime.today().strftime("%Y.%m.%d %H:%M"),testcase.description)
        )
        testResults.updatedCount +=1
      else:
        core.create_jira_issue(jira, testcase, key, issueType, environment, assignee)
        testResults.createdCount +=1
    else:
      #HN DEBUG:
      print("testcase.description:", testcase.description, flush=True)
      print("existingIssues.count:", existingIssues.count, flush=True)
      if existingIssues.count > 0:
        for issue in existingIssues.results:
          jira.transition_issue(
            jira.issue(issue),
            #T000: Set up ENUM for Resolution states on defferent issue types, just in case
            '2',
            fields={
              'resolution':{'name':'Closed'}
            }
          )
          testResults.resolvedCount +=1

    existingIssues.results.clear()
    existingIssues.count = 0

  print("""
      JIRA - PROJECT: {0} ({1})
      -------------------------------
      Defects Created: {2}
      Defects Updated: {3}
      Defects Closed: {4}
  """.format(
          jira.project(key).name,
          key,
          testResults.createdCount,
          testResults.updatedCount,
          testResults.resolvedCount 
      )
  )

  return True

if _name_ == '_main_':
  parse_results_to_jira(*sys.argv[1:])