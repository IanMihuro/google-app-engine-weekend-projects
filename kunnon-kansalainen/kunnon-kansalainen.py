#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Copyright 2008 Juha Autero
#
# Copyright 2009 Juha Autero <jautero@iki.fi>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

project="Kunnon kansalainen"
version="1.0"
author="Juha Autero <jautero@iki.fi>"
copyright="Copyright 2009 Juha Autero <jautero@iki.fi>"
application="kunnon-kansalainen"
import wsgiref.handlers
import os

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db

import model

class KunnonKansalainen(webapp.RequestHandler):
  unit_multi=[1,60,1440]
  freq_multi=[365,52,12,1]
  units=[u"minuuttia",u"tuntia",u"p&auml;iv&auml;&auml;"]
  freqs=[u"p&auml;iv&auml;ss&auml;",u"viikossa",u"kuukaudessa",u"vuodessa"]
  def get(self):
    template_values=dict(globals())
    template_values["loginurl"]=users.create_login_url("/")
    template_values["logouturl"]=users.create_logout_url("/")
    if users.get_current_user():
      template_values["user"]=True
    else:
      template_values["user"]=False
    if users.is_current_user_admin():
      template_values["canwrite"]=True
    else:
      template_values["canwrite"]=False
    template_values["things"]=db.GqlQuery("SELECT * FROM KunnonKansalainen ORDER BY date DESC")
    total=0
    for thing in template_values["things"]:
      total+=thing.total_time
    template_values["timeleft"]=525600-total
    if total>525600:
      template_values["valuetype"]="negative"
    else:
      template_values["valuetype"]="positive"
    
    path = os.path.join(os.path.dirname(__file__), 'index.html')
    self.response.out.write(template.render(path, template_values))
    
  def post(self):
    action=self.request.get("action")
    time=int(self.request.get("time"))
    unit=int(self.request.get("unit"))
    freq=int(self.request.get("freq"))
    total=time*self.unit_multi[unit]*self.freq_multi[freq]
    new_entry=model.KunnonKansalainen(action=action,time=time,unit=self.units[unit],freq=self.freqs[freq],total_time=total)
    if users.is_current_user_admin():
      new_entry.put()
    self.redirect("/")
    
    

def main():
  application = webapp.WSGIApplication([('/', KunnonKansalainen)],
                                       debug=True)
  wsgiref.handlers.CGIHandler().run(application)


if __name__ == '__main__':
  main()
