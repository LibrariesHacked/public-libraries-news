﻿var PublicLibrariesNews = {
    locationsUrl: '/data/PLNLocations.json',
    dataUrl: '/data/PLN_YY_M_TYPE.json',
    locations: {},
    stories: {
        changes: {},
        local: {}
    },
    loadData: function (months, callback) {
        // Need to work out which files to load.
        // Filenames are in the form PLN_2015_11_changes
        var urls = [];
        for (x = 0; x <= months ; x++) {
            var date = moment().subtract(x, 'months');
            var year = date.year();
            var month = date.month() + 1;
            for (type in this.stories){
                if (!this.stories[type][year]) this.stories[type][year] = {};
                if (!this.stories[type][year][month]) {
                    this.stories[type][year][month] = {};
                    urls.push([month,year,type,this.dataUrl.replace('YY',year).replace('M',month).replace('TYPE',type)]);
                }
            }
        }
        if (Object.keys(this.locations).length == 0) urls.push(['','','locations',this.locationsUrl]);
        var requests = [];
        for (i = 0; i < urls.length; i++) {
            requests.push($.ajax(urls[i][3]));
        }
        $.when.apply($, requests).done(function () {
            $.each(arguments, function (i, data) {
                var month = urls[i][0];
                var year = urls[i][1];
                var type = urls[i][2];
                if (type != 'locations') this.stories[type][year][month] = data[0];
                if (type == 'locations') this.locations = data[0];
            }.bind(this));
            callback();
        }.bind(this));
    },
    getStoriesGroupedByLocation: function (type) {
        var locs = {};
        $.each(this.stories[type], function (i, y) {
            $.each(y, function (x, m) {
                $.each(m, function (z, s) {
                    if (!locs[s[0]]) locs[s[0]] = { lat: this.locations[s[0]][0], lng: this.locations[s[0]][1], stories: [] };
                    locs[s[0]].stories.push({ date: s[1], text: s[2], url: s[3] });
                }.bind(this));
            }.bind(this));
        }.bind(this));
        return locs;
    },
    getLocationList: function () {

    }
};