# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import requests
import pyrebase
import netifaces
import flask
from octoprint.server import admin_permission, NO_CONTENT

config = {
  "apiKey": "AIzaSyDmJhgc56kYsNcOUQp7Fixz5uqbvQYuSFQ",
  "authDomain": "octomobile-2aecc.firebaseio.com",
  "databaseURL": "https://databaseName.firebaseio.com",
  "storageBucket": "octomobile-2aecc.appspot.com"
}

firebase = pyrebase.initialize_app(config)

# Get a reference to the auth service
auth = firebase.auth()

authorized_messages = ['Shutdown', 'Startup', 'Disconnected', 'Error', 'PrintStarted', 'PrintFailed', 'PrintDone', 'PrintCancelled']

class OctoMobilePlugin(octoprint.plugin.SettingsPlugin, octoprint.plugin.EventHandlerPlugin, octoprint.plugin.StartupPlugin, octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.AssetPlugin, octoprint.plugin.BlueprintPlugin):
  def get_settings_defaults(self):
    return dict(
      user_mail="",
      user_refreshed_token=""
    )

  def get_assets(self):
    return dict(
      js=["js/octomobile.js"]
    )

  def on_after_startup(self):
    self.register_instance() 

  def on_event(self, event, payload):
    refresh_token = self._settings.get(["user_refreshed_token"])
    if refresh_token != "":
      if event in authorized_messages:
        self._logger.info("EMIT EVENT : " + event)
        user_refreshed = auth.refresh(refresh_token)
        self._settings.set(["user_refreshed_token"], user_refreshed['refreshToken'])
        token = user_refreshed['idToken']
        url = 'https://us-central1-octomobile-2aecc.cloudfunctions.net/sendEvent'
        data = {"event":event}
        response = requests.post(url, data=data, headers={'Authorization': 'Token {}'.format(token)})

      if event == 'ConnectivityChanged':
        self.register_instance() 
    else:
      self._logger.info("User not logged in")

  def register_instance(self):
    refresh_token = self._settings.get(["user_refreshed_token"])
    if refresh_token != "":
      user_refreshed = auth.refresh(refresh_token)
      token = user_refreshed['idToken']
      self._settings.set(["user_refreshed_token"], user_refreshed['refreshToken'])
      url = 'https://us-central1-octomobile-2aecc.cloudfunctions.net/registerOctoprintInstance'
      interfaces = netifaces.interfaces()
      for i in interfaces:
        if i == 'lo':
          continue
        iface = netifaces.ifaddresses(i).get(netifaces.AF_INET)
        if iface != None:
          for j in iface:
            try: 
              data = {"local_address": j['addr']}
              response = requests.post(url, data=data, headers={'Authorization': 'Token {}'.format(token)})
            except:
              self._logger.info("Cannot register instance")
    else:
      self._logger.info("User token doesn't exists")
    return

  @octoprint.plugin.BlueprintPlugin.route("/connect", methods=["POST"])
  @octoprint.server.util.flask.restricted_access
  @octoprint.server.admin_permission.require(403)
  def connect(self):
    value_source = flask.request.json if flask.request.json else flask.request.values
    username = value_source["user"]
    password = value_source["pass"]
    user = auth.sign_in_with_email_and_password(username, password)
    self._settings.set(["user_mail"], username)
    self._settings.set(["user_refreshed_token"], user['refreshToken'])
    self.register_instance()
    return flask.make_response(NO_CONTENT)

__plugin_name__ = "OctoMobile"
__plugin_implementation__ = OctoMobilePlugin()
