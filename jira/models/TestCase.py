class TestCase(object):
  title = ""
  description = ""
  comments = ""

  def _init_(self, title = "", description = "", comments = ""):
    self.title = title
    self.description = description
    self.comments = comments

def generate_testcase_object(env, classname, name, errortype = None, errortrace = None):
  title = "FAIL | {0} | {1}.{2}".format(env, classname.replace("com.hsbc.group.insurance.life400.", ""), name).upper()
  description = "+Error Details+\n{{{{{0}}}}}\n\n+Stack Trace+\n{{code:borderStyle=solid}}{1}{{code}}".format(errortype, errortrace) if errortype is not None and errortrace is not None else None
  testcase = TestCase(title, description, "")

  return testcase