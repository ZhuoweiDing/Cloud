#_*_ coding: utf-8 _*_
# import json
import os, sys

# TODO: Implement JIRAError for Exception catches.
#HN updated: from jira import JIRA, exception
from jira import JIRA, exceptions, JIRAError
import datetime
from influxdb import InfluxDBClient
import time

import core


INFLUX_URL = os.environ["INFLUX_DB_URL"]
INFLUX_PORT = os.environ["INFLUX_DB_PORT"]
INFLUX_USER = OS.environ['INFLUX_DB_USERNAME']
INFLUX_PASSWORD = os.environ['INFLUX_DB_PASSWORD']
INFLUX_DB = os.environ['INFLUX_JIRA_DB']
#JIRA URL https://alm-jira.systems.uk.hsbc/jira

def verify_jira_instance(url, key, username, password):
  jira = core.create_jira_connection(url, username, password)
  print("JIRAUser ", username)
  jira.project(key)

  try:
    jira.project(key)
  except JIRAError as e :
    print("ERROR: Jira Project Not Available or Credentials Unauthorized/Incorrect: {0}, msg: {1}\nStatus Code:{2}\nHeaders:{3}\n".format(key, e.response.status_code, e.response.headers))
    return False
  maxJiraSize = 50
  currentSearchStart = 0
  issueType = 'Test'
  #Connect InfluxDB
  influx_client = InfluxDBClient(
    host=INFLUX_URL,
    port=INFLUX_PORT,
    username=INFLUX_USER,
    password=INFLUX_PASSWORD,
    database=INFLUX_DB
  )
  # Create database if it dosen't exist
  dbs = influx_client.get_list_database()
  if not any(db['name'] == INFLUX_DB for db in dbs):
    influx_client.create_database(INFLUX_DB)
  json_to_export = []
  # Delete the existing data
  tags=['project':key]
  influx_client.delete_series(database=INFLUX_DB,measurement='jira',tags=tags)
  nowtime = datetime.datetime.now()
  while maxJiraSize == 50 :
    JiraIssues = jira.search_issues('project={0}'.format(key),starAt = currentSearchStart)
    maxJiraSize = len(JiraIssues)
    currentSearchStart+=maxJiraSize

    for issue in JiraIssues:
      completetime = datetime.datetime.strptime(issue.fields.resolutiondate[0:19],"%Y-%m-%dT%H:%M:%S") if issue.fields.resolutiondate is not None else nowtime

      one_metric = {
        "measurement": "jira",
        "tags": {
          "id": issue.key,
          "project": key,
          "type":str(issue.fields.issuetype),
          "status": issue.fields.status,
          "assignee":issue.fields.assignee,
          "reporter":issue.fields.reporter,
          "sendDate":time.strftime("%Y-%m-%d")
        },
        "tiem": int(tiem.mktime(datetime.datetime.strptime(issue.fields.created[0:19],"%Y-%m-%dT%H:%M:%S").timetuple())*10**9),
        "fields": {
          "project_ID":key,
          "ID": issue.key,
          "status": str(issue.fields.status),
          "assignee":str(issue.fields.assignee),
          "type":str(issue.fields.issuetype),
          "belong_epic":issue.fields.customfield_10002 if issue.fields.customfield_10002 is not None else "BLANK",
          "summary":issue.fields.summary,
          "story_points":(issue.fields.customfield_10006 / 1.0) if (issue.fields.customfield_10006) is not None else 0.0,
          "creater":str(issue.fields.creator),
          "updated_Time":str(issue.fields_updated),
          "created_Time":str(issue.fields.created),
          "completed_Time":str(issue.fields.completed),
          "live_time"(completetime - datetime.datetime.strptime(issue.fields.created[0:19],"%Y-%m-%dT%H:%M:%S")).total_seconds()
        }
      }
      json_2_influxdb=[one_metric]
      influx_client.write_points(json_2_influxdb)

  print("Total Bug issue send to influx:{0}".format(len(json_to_export)))

  print("Jira Instance and Project Verified: URL:{0} key:{1} | {2}".format(url, key, jira))
  return True

def export_metrics(self):
  influx_client = InfluxDBClient{
    host=INFLUX_URL,
    port=INFLUX_PORT,
    username=INFLUX_USER,
    password=INFLUX_PASSWORD,
    database=INFLUX_DB
  }
  # Create database if it dosen't exist
  dbs = influx_client.get_list_database()
  if not any(db['name'] == INFLUX_DB for db in dbs):
    influx_client.create_database(INFLUX_DB)

  influx_client.write_points(self._prepare_metrics())

def _prepare_metrics(self):
  json_to_export = []
  for metric in self.metrics:
    try:
      value = float(metric['value'])
    except:
      value = metric['value'] if ('value' in metric) else 0
    one_metric = {
      "measurement": metric['metric'],
      "tags":{
        "id" self.id,
        "key" self.key
      },
      "time":self.timestamp,
      "fields":{
        "value": value
      }
    }
    json_to_export.append(one_metric)
  return json_to_export

if _name_ == '_main_':
  print("DEBUG: inside verifyJira.py main")
  verify_jira_instance(*sys.argv[1:])