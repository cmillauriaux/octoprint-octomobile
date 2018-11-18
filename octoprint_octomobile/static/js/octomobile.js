$(function () {
    function OctomobileViewModel(parameters) {
        var self = this;

        // assign the injected parameters, e.g.:
        // self.loginStateViewModel = parameters[0];
        // self.settingsViewModel = parameters[1];
        self.settings = parameters[0];
        // TODO: Implement your plugin's view model here.

        self.user = ko.observable();
        self.pass = ko.observable();
        self.error = ko.observable();
        self.mail = ko.observable();
        self.isConnected = ko.observable(false);
        self.isLoading = ko.observable(false);

        self.onBeforeBinding = function () {
            if (self.settings.settings.plugins.octomobile.user_mail() && self.settings.settings.plugins.octomobile.user_mail() !== "") {
                self.isConnected(true);
                self.mail(self.settings.settings.plugins.octomobile.user_mail());
            }
        }

        self.connect = function () {
            self.error("");
            self.isLoading(true);
            $.ajax({
                url: PLUGIN_BASEURL + "octomobile/connect",
                type: "POST",
                dataType: "json",
                data: JSON.stringify({
                    user: self.user(),
                    pass: self.pass()
                }),
                success: function () {
                    self.error("Connection successfull");
                    self.isConnected(true);
                    self.mail(self.user());
                    self.isLoading(false);
                },
                error: function (XMLHttpRequest, textStatus, errorThrown) {
                    self.error("Unknown user or wrong password");
                    self.isLoading(false);
                },
                contentType: "application/json; charset=UTF-8"
            }).fail(function (jqXHR, textStatus, error) {
                self.error("Unknown user or wrong password");
                self.isLoading(false);
            });
        };

        self.disconnect = function () {
            self.settings.settings.plugins.octomobile.user_mail("");
            self.settings.settings.plugins.octomobile.user_refreshed_token("");
            self.isConnected(false);
        };
    }

    /* view model class, parameters for constructor, container to bind to
     * Please see http://docs.octoprint.org/en/master/plugins/viewmodels.html#registering-custom-viewmodels for more details
     * and a full list of the available options.
     */
    OCTOPRINT_VIEWMODELS.push({
        construct: OctomobileViewModel,
        // ViewModels your plugin depends on, e.g. loginStateViewModel, settingsViewModel, ...
        dependencies: ["settingsViewModel"/* "loginStateViewModel", "settingsViewModel" */],
        // Elements to bind to, e.g. #settings_plugin_octomobile, #tab_plugin_octomobile, ...
        elements: ["#settings_plugin_octomobile"]
    });
});
