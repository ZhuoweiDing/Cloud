from jira import JIRA
import requests

from influxdb import InfluxDBClient

def createJiraConnection(url,user,password):

        jira = JIRA(
            {
                'server':url,
                'verify':False
            },
            basic_auth = (user,password)
        )
        return jira
def insertIssues2Influxdb(jira,key):
    influxClient = InfluxDBClient("39.104.48.57", 8086, "admin", "admin", "Influxdb")
    jiraIssues = jira.search_issues('project={0}'.format(key),startAt=0);
    for issue in jiraIssues:
        metric =  {
            "measurement":"jira",
            "tags":{
               "project_ID": str(key),
                "ID": str(issue.key),
                "status": str(issue.fields.status)

            },
            "time": "2019-05-13T23:00:00Z",
            "fields":{
                "id": str(issue.key),
                "project": str(key),
                "type": str(issue.fields.issuetype),
                "status": str(issue.fields.status),
                "assignee": str(issue.fields.assignee),
           }

        }
        json2influxdb = [metric];
        influxClient.write_points(json2influxdb)

jira = createJiraConnection("http://39.104.48.57:8080","lingji",'Ling00218077')
insertIssues2Influxdb(jira,"Dashboard");