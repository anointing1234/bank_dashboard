// Fiserv Plugins 1.2.0

// Ajax Locator 1.0.0 (c) JP Larson, Fiserv 2018.  All rights reserved.
// Must be placed after ajaxPost and cmsInclude in plugins.js
(function () {
    jQuery.fn.ajaxLocator = function (options) {
        var settings = jQuery.extend({
            obj: jQuery(this).each(function () {
                return jQuery(this);
            }),
            includeURL: "inc_locator.aspx", //The path to inc_locator.aspx or any include with the locator code.
            submitButton: jQuery("<input type='submit' id='psuedo-submit' class='Button1' value='Search'>"), //The submit button object, which will replace the default input type image.
            aClass: "Button1", //The class applied to the links within the locator results.
            containerClass: 'Locator-Container', //The class of the container used to house the atm locator code. Everything within the container will be replaced on submit.
            busyClass: "busy", //The class used to indicate server activity to the user.
        }, options);
        settings.obj.cmsInclude({

            //If any of the matching query strings are found, the include url is appended with the query strings.
            url: (/(postalCode)/.test(window.location.search) || /(city)/.test(window.location.search) || /(state)/.test(window.location.search)) == true ? settings.includeURL + window.location.search : settings.includeURL,

            //Call the needed form function after the include has bee successfully completed.
            success: function () {

                //All javascript applied to the Locator form is housed inside this fuction to allow it to be applied after submission.
                var initLocator = function () {

                    var container = jQuery('.' + settings.containerClass);

                    //Force submission on click of the new submit button
                    settings.submitButton.click(function (e) {
                        e.preventDefault();
                        container.find('form').submit();
                        container.addClass(settings.busyClass);
                    });

                    //Structure related changes
                    jQuery('#AtmLocatorControl1_goButton').after(settings.submitButton).remove();
                    if (settings.aClass) {
                        jQuery('#ATMLocatorForm .results table a').addClass(settings.aClass);
                    }

                    //Call the ajax post.
                    container.find('form').ajaxPost({
                        url: settings.includeURL, //The URL the form is submitted to.
                        postContainer: container, //The container where the result is displayed.
                        method: "replace", //The method of displaying the result within the container. (replace or append)
                        success: function () { //Javascript ran on the result being successfully returned.
                            container.removeClass(settings.busyClass);

                            //Call the init function to reapply the javascript functionality to the returned form.
                            return initLocator();
                        },
                        dataAddition: "&AtmLocatorControl1%24goButton.x=0&AtmLocatorControl1%24goButton.y=0", //Required data for the server to accept the post.
                    });
                }
                initLocator();
            },
        });
        return this;
    }
}(jQuery));

// Ajax Post 1.1.0 (c) JP Larson, Fiserv 2017.  All rights reserved.
// Code dependencies: none;
// Code Usage: Ajax form, weather, atm locator, pageless pages;
(function () {
    jQuery.fn.ajaxPost = function (options) {

        var settings = jQuery.extend({
            url: '', //The URL to include.
            postContainer: '', //The object the return result will be displayed in.
            success: function () {
                console.log('post succeeded'); //This will be called once the function is complete. This can be used for anything needed to run afterwards.
            },
            dataAddition: "", //Any additional needed form data. This is used by the ATM Locator.
            targetObject: false, //A object on the page can be used in place of the form result, such as a hidden table.
            method: "append", //This has two options, append or replace, for modifying the postContainer with the result.
        }, options),
            forms = jQuery(this).each(function () {
                return jQuery(this);
            }),
            postform = function (thisForm) {
                jQuery.ajax({
                    type: "POST",
                    url: settings.url,
                    data: thisForm.serialize() + settings.dataAddition,
                    success: function (result) {
                        var containerChildren = settings.postContainer.children(),
                            appendObject = jQuery(result);
                        for (j = 0; j < containerChildren.length; j++) {
                            containerChildren.eq(j).remove();
                        }
                        if (settings.targetObject) {
                            appendObject = appendObject.find(settings.targetObject);
                        }
                        switch (settings.method) {
                            case "append":
                                settings.postContainer.append(appendObject);
                                break;
                            case "replace":
                                settings.postContainer.replaceWith(appendObject);
                                break;
                        }
                    },
                    complete: function () {
                        return settings.success();
                    },
                });
            },
            run = forms.off().on('submit', function (e) {
                e.preventDefault();
                postform(jQuery(this));
                return false;
            });
        return this;
    }
}(jQuery));

//CMS Include 1.2.0 (c) JP Larson, Fiserv 2017.  All rights reserved.
// Code dependencies: none;
// Code Usage: ajax form, atm locator, pageless pages;
(function () {
    jQuery.fn.cmsInclude = function (options) {
        var settings = jQuery.extend({
            includeObj: jQuery(this), //The object that will be replaced
            urlAttribute: "href", //An alternate attribute used to target the url example: data-include="url"
            success: function () {
                //This function runs after the include has been placed. This can be used for scripts or functions needed to run after loading.
            },
            url: false, //An alternate URL for loading that negates the urlAttribute. Example: inc_contact-form.aspx
            async: false, //Turns asynchronous on and off. Turning this off will allow asynchronous javascript to be applied, but will activate a deprecation warning in Chrome. Ideally any functions needed should be called asynchronously either within the include or the success function.
            fileRegex: "[a-z]+[\.]{1}[a-z]{3,4}$", //This is the regular expression that determines if the url in the link is a file or not. Added: 1.1.0
            includePath: "inc_cms-include.aspx" //This is the path to the include. Added: 1.2.0
        }, options);
        try {
            if (settings.includeObj.length > 0) {
                settings.includeObj.each(function () {
                    var currentObj = jQuery(this),
                        incUrl = function () {
                            //Determine if the include is an article or a file.
                            var href = currentObj.attr(settings.urlAttribute),
                                fileRegex = new RegExp(settings.fileRegex, 'ig');
                            if (settings.url) {
                                return settings.url;
                            } else if (fileRegex.test(href)) {
                                return href;
                            } else {
                                return settings.includePath + "?name=" + href.replace(/\#/g, '').replace(/[\-\s]/g, '+');
                            }
                        },
                        includeFile = jQuery.ajax({ // AJAX function for loading the include.
                            async: settings.async,
                            type: "GET",
                            url: incUrl(),
                            success: function (result) {
                                if (result.length > 5) {
                                    if (currentObj.parent('p').length > 0) {
                                        currentObj.parent('p').replaceWith(result);
                                    } else {
                                        currentObj.replaceWith(result);
                                    }
                                    settings.success();
                                } else {
                                    throw 'Article "' + currentObj.attr(settings.urlAttribute) + '" could not be found. cmsInclude function failed.';
                                }
                            }
                        });
                });
            }
        } catch (err) {
            console.log(err);
        }
        return this;
    }
}(jQuery));

// Expander v2.5.0 Copyright (c) 2015 Jesse Fowler & Kristen Rogers, Fiserv
// Calls need to be after any div/table replacement scripts in document .ready
// Code dependencies: none;
// Code Usage: none;
(function (jQuery) {

    jQuery.fn.fiservExpandablesInit = function (options) {

        // This is the easiest way to have default options.
        var settings = jQuery.extend({
            // These are the defaults.
            defaultClass: 'expandable',
            TOC: false,
            allExpandable: true,
            openFirstExpandable: false,
            scrollToExpanders: false,
            displayedMobileOnly: jQuery('#tabtoexpander'),
            tagBody: false, //tag the body when expander is open / selected
            baseOffsetTopObject: jQuery('header').eq(0), // Fixed object that overlays the scrollable content area.
            additionalOffsetTop: 10 // Added offset height to the scroll baseOffsetTopObject
        }, options);

        var $this = jQuery(this);

        $this.each(function () {

            var $expandables = jQuery(this),
                expander = []; // Customize with element that is visible only in the mobile view.

            var replacement = jQuery("<div></div>");
            replacement.attr('id', $expandables.attr('id'));
            replacement.addClass(settings.defaultClass);
            $expandables.before(replacement);
            var subsectionContent = "";
            $expandables.children("tbody").children("tr").each(function () {
                jQuery("td:first", this).each(function () {
                    replacement.append(jQuery(this).children()); // Fix for iOS expanders that have youtube embedded videos.
                });
            });
            //replacement.html(subsectionContent);

            $expandables.remove();

            // Create click events for expandables.
            var expandable = replacement;
            expander = expandable.children(':first-child');

            // Set initial height
            var adjustedLineHeight = parseFloat(expander.css("line-height")) + parseFloat(expander.css("padding-bottom")) + parseFloat(expander.css("padding-top"));
            expandable.css("height", adjustedLineHeight);

            var tagBody = function () {
                if (settings.tagBody) {
                    if (settings.allExpandable || settings.displayedMobileOnly.css('display') == 'block') {
                        // Sets the prefixed id as a body class.
                        if (expandable.is(jQuery('.' + settings.defaultClass + '[id*=selected-]'))) {
                            jQuery('body').toggleClass(expandable.attr('id'));
                        };
                    } else {
                        // Removes all the prefixed ids that were added to the body.
                        var prefix = "selected-";
                        var classes = jQuery('body')[0].className.split(" ").filter(function (c) {
                            return c.lastIndexOf(prefix, 0) !== 0;
                        });
                        jQuery('body')[0].className = jQuery.trim(classes.join(" "));
                        // Sets the prefixed id as a body class.
                        if (expandable.is(jQuery('.' + settings.defaultClass + '[id*=selected-]'))) {
                            jQuery('body').toggleClass(expandable.attr('id'));
                        };
                    }
                }
            }

            expander.on({
                click: function (e) {
                    tagBody();
                    if (settings.allExpandable || settings.displayedMobileOnly.css('display') == 'block') {
                        if (expandable.hasClass('expanded')) {
                            expandable.removeClass("expanded");
                            expandable.css("height", adjustedLineHeight);
                        } else {
                            expandable.addClass("expanded");
                            expandable.css("height", "auto");
                        }
                    } else {
                        expandable.parent().children('.expanded').removeClass('expanded');
                        expandable.addClass('expanded');
                        expandable.css("height", "auto");
                        if (settings.scrollToExpanders) {
                            //new Fx.Scroll(window).toElement(this);
                            jQuery('html,body').animate({ "scrollTop": jQuery(this).offset().top - (parseInt(settings.baseOffsetTopObject.height()) + parseInt(settings.additionalOffsetTop)) });
                        }
                    }
                }
            });

            // Create Table of Contents element for the expandables.
            if (settings.TOC) {
                var expandablesTOC = expandable.parent().children('.expandablesTOC');
                //console.warn(expandablesTOC);
                var expandablesLInA = function (obj, toc) {
                    var expandablesTOCli = jQuery('<li></li>'),
                        expandablesTOCaClass = '';
                    if (settings.openFirstExpandable && expandable.is(expandable.parent().children("." + settings.defaultClass).eq(0))) {
                        expandablesTOCaClass = 'active';
                    }
                    var expandablesTOCa = jQuery("<a></a>").html(obj.find('h1,h2,h3,h4,h5,h6,a').eq(0).html()).attr("class", expandablesTOCaClass);
                    if (expandable.attr("id")) {
                        expandablesTOCa.attr("id", settings.defaultClass + "-" + expandable.attr("id"));
                    }

                    if (obj.find('h1,h2,h3,h4,h5,h6,a').eq(0).attr('href')) {
                        expandablesTOCa.attr('href', obj.find('h1,h2,h3,h4,h5,h6,a').eq(0).attr("href"));
                    } else {
                        expandablesTOCa.on({
                            click: function (e) {
                                tagBody();
                                if (!settings.allExpandable) {
                                    jQuery(this).parent().parent().find('li a.active').removeClass('active');
                                    jQuery(this).addClass('active');
                                } else {
                                    jQuery(this).toggleClass('active');
                                }
                                if (settings.allExpandable) {
                                    if (expandable.hasClass("expanded")) {
                                        expandable.removeClass("expanded");
                                    } else {
                                        expandable.addClass("expanded");
                                    }
                                } else {
                                    expandable.parent().children('.expanded').removeClass("expanded");
                                    expandable.addClass("expanded");
                                }
                            }
                        });
                    }
                    expandablesTOCli.append(expandablesTOCa);
                    toc.append(expandablesTOCli);
                }
                if (expandablesTOC.length) {
                    expandablesLInA(expandable, expandablesTOC.eq(0));
                } else {
                    expandablesTOC = jQuery("<ul></ul>").attr("class", "expandablesTOC");
                    if (settings.openFirstExpandable) {
                        expandable.addClass("expanded");
                        expandable.css("height", "");
                    }
                    expandablesLInA(expandable, expandablesTOC);
                    expandable.parent().prepend(expandablesTOC);
                }
            }

        });

        // Finds links on the page that would link to the expanders using a hash and changes them to expand then scroll to them.
        jQuery('a[href^=\\#]').each(function () {
            if (jQuery(jQuery(this).attr('href')).hasClass(settings.defaultClass)) {
                jQuery(this).on('click', function (e) {
                    e.preventDefault();
                    var fullID = '#' + settings.defaultClass + '-' + jQuery(this).attr('href').split('#')[1];
                    if (jQuery(jQuery(this).attr('href')).hasClass(settings.defaultClass) && !jQuery(jQuery(this).attr('href')).hasClass('expanded') && !jQuery(jQuery(this).attr('href')).parent().children().eq(0).hasClass('expandablesTOC')) {
                        jQuery(jQuery(this).attr('href')).children(":first").click();
                    } else if (jQuery(jQuery(this).attr('href')).parent().children().eq(0).hasClass('expandablesTOC') && !jQuery(jQuery(this).attr('href')).hasClass('active')) {
                        jQuery(fullID).click();
                    }
                    // Delay scrollTo to allow for expander to expand - avoid short page
                    if (jQuery(jQuery(this).attr('href')).parent().children().eq(0).hasClass('expandablesTOC') && settings.displayedMobileOnly.css('display') !== 'block') {
                        jQuery('html,body').animate({ "scrollTop": jQuery(fullID).offset().top - (parseInt(settings.baseOffsetTopObject.height()) + parseInt(settings.additionalOffsetTop)) }, 500);
                    } else {
                        if (settings.baseOffsetTopObject.css('position') == 'fixed') {
                            var scrollTopWithOffset = jQuery(jQuery(this).attr('href')).offset().top - (parseInt(settings.baseOffsetTopObject.height()) + parseInt(settings.additionalOffsetTop));
                        } else {
                            var scrollTopWithOffset = jQuery(jQuery(this).attr('href')).offset().top - parseInt(settings.additionalOffsetTop);
                        }
                        jQuery('html,body').animate({ "scrollTop": scrollTopWithOffset }, 500);
                    }
                })
            }
        });

        // Expand from querystring v1.2.0 Copyright (c) Jesse Fowler & Kristen Rogers, Fiserv
        // Requires Querystring parser and the getParameterByName() function.
        // Querystring should be page.aspx?expand=idname

        // Querystring parser
        function getParameterByName(name) {
            name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
            var regexS = "[\\?&]" + name + "=([^&#]*)",
                regex = new RegExp(regexS),
                results = regex.exec(window.location.search);
            if (results == null)
                return "";
            else
                return decodeURIComponent(results[1].replace(/\+/g, " "));
        }

        function fiservExpanderInit() {
            var expand = getParameterByName('expand'),
                offsetTopExpander = 0;
            if (expand) {
                jQuery("." + settings.defaultClass).each(function (el, index) {  // This doesn't appear to be returning anything to offsetTopExpander - Jesse
                    var matchingObj = jQuery(this);
                    if (jQuery(this).attr('id') === expand) {
                        var fullID = '#' + settings.defaultClass + '-' + expand;
                        if (jQuery(this).hasClass(settings.defaultClass) && !jQuery(this).hasClass('expanded') && !jQuery(this).parent().children().eq(0).hasClass('expandablesTOC')) {
                            jQuery(this).children(":first").click();
                        } else if (jQuery(this).parent().children().eq(0).hasClass('expandablesTOC') && !jQuery(this).hasClass('active')) {
                            jQuery(fullID).click();
                        }
                        // Delay scrollTo to allow for expander to expand - avoid short page
                        function scrollToExpand() {
                            var scrollTopWithOffset = '';
                            if (matchingObj.parent().children().eq(0).hasClass('expandablesTOC')) {
                                if (settings.baseOffsetTopObject.css('position') == 'fixed') {
                                    scrollTopWithOffset = jQuery(fullID).offset().top - (parseInt(settings.baseOffsetTopObject.height()) + parseInt(settings.additionalOffsetTop));
                                } else {
                                    scrollTopWithOffset = matchingObj.offset().top - parseInt(settings.additionalOffsetTop);
                                }
                                jQuery('html,body').animate({ "scrollTop": scrollTopWithOffset }, 500);
                            } else {
                                if (settings.baseOffsetTopObject.css('position') == 'fixed') {
                                    scrollTopWithOffset = matchingObj.offset().top - (parseInt(settings.baseOffsetTopObject.height()) + parseInt(settings.additionalOffsetTop));
                                } else {
                                    scrollTopWithOffset = matchingObj.offset().top - parseInt(settings.additionalOffsetTop);
                                }
                                jQuery('html,body').animate({ "scrollTop": scrollTopWithOffset }, 500);
                            }
                        }
                        setTimeout(scrollToExpand, 500);
                    }
                });
            }
        }
        fiservExpanderInit();

        return $this;
    }
}(jQuery));

// LinkLive Chat Status 2.2.0 Copyright (c) 2015 Jesse Fowler, Fiserv
// Code dependencies: none;
// Code Usage: none;
(function (jQuery) {

    jQuery.fn.linkliveChatStatus = function (options) {

        // This is the easiest way to have default options.
        var settings = jQuery.extend({
            // These are the defaults.
            url: "linklive-status.aspx",
            preClass: "support",
            refreshInterval: 2 //in minutes
        }, options);

        var linkLiveStatus = '',
            passObj = jQuery(this),
            chatInterval = 1000 * 60 * settings.refreshInterval;

        function chatRemoveBodyClasses() {
            passObj.removeClass('linklive-' + settings.preClass + '-online');
            passObj.removeClass('linklive-' + settings.preClass + '-busy');
            passObj.removeClass('linklive-' + settings.preClass + '-away');
            passObj.removeClass('linklive-' + settings.preClass + '-offline');
        }

        jQuery.ajax({
            type: "GET",
            url: settings.url,
            dataType: "xml",
            success: linkliveStatus
        });

        function linkliveStatus(xml) {

            jQuery(xml).find("status").each(function () {
                //console.log('Success loading chat');
                linkLiveStatus = jQuery(this).text();
                //console.log(linkLiveStatus);
                if (linkLiveStatus == 'online') {
                    chatRemoveBodyClasses();
                    passObj.addClass('linklive-' + settings.preClass + '-online');
                } else if (linkLiveStatus == 'busy') {
                    chatRemoveBodyClasses();
                    passObj.addClass('linklive-' + settings.preClass + '-busy');
                } else if (linkLiveStatus == 'away') {
                    chatRemoveBodyClasses();
                    passObj.addClass('linklive-' + settings.preClass + '-away');
                } else if (linkLiveStatus == 'offline') {
                    chatRemoveBodyClasses();
                    passObj.addClass('linklive-' + settings.preClass + '-offline');
                } else {
                    //if(console){console.log(settings.preClass + ' Chat status update failed.')};
                }
            });
        }
        function ajaxSuccess() {
            linkliveStatus();
            setInterval(linkliveStatus, chatInterval);
        }
        return passObj;
    };
}(jQuery));

// Page Class 1.0.0 (c) JP Larson, Fiserv 2018. All rights reserved.
// Code dependencies: none;
// Adds a class to the target object using the page name in the URL.;
(function (jQuery) {
    jQuery.fn.pageClass = function (settings) {
        var settings = jQuery.extend({
            obj: jQuery(this), // The object being invoked on.
            pageRegex: /[\_\-\w]+/gi, // The regular expression pulling the page name from the URL.
        });
        //console.log(window.location.pathname.match(settings.pageRegex));
        settings.obj.each(function () {
            if (window.location.pathname.match(settings.pageRegex)) {
                for (i = 0; i < window.location.pathname.match(settings.pageRegex).length; i++) {
                    jQuery(this).addClass(window.location.pathname.match(settings.pageRegex)[i].toLowerCase());
                }
            }
        });
        return this;
    }
}(jQuery));

// Randomizer v1.0
// Code dependencies: none;
// Code Usage: Site Slideshow;
(function (jQuery) {
    jQuery.fn.randomize = function () {
        var $this = jQuery(this),
            contentCount = $this.get(),
            getRandom = function (max) {
                return Math.floor(Math.random() * max);
            },
            shuffled = jQuery.map(contentCount, function () {
                var random = getRandom(contentCount.length),
                    randEl = $(contentCount[random]).clone(true)[0];
                contentCount.splice(random, 1);
                return randEl;
            });
        $this.each(function (i) {
            jQuery(this).replaceWith($(shuffled[i]));
        });
        return this;
    };
}(jQuery));
// Samples
/*Normal Sample
jQuery('.section > div').randomize();

Custom Sample
if (jQuery('body').hasClass('home')) {
    jQuery('.section .promo1, .section .promo2').randomize(
        jQuery("body").addClass("reveal")
    );
}
*/

// Responsive Table 1.0.1 (c) Fiserv 2017.  All rights reserved.
// Reorganize table and adds data labels based on screen size
// Code dependencies: none;
// Code Usage: none;
(function (jQuery) {

    jQuery.fn.responsiveDataTable = function (options) {

        // This is the easiest way to have default options.
        var settings = jQuery.extend({
            // These are the defaults.

        }, options);

        this.each(function () {
            //console.warn(jQuery(this));
            var selectedTable = jQuery(this);
            if (selectedTable.length > 0) {
                for (t = 0; t < selectedTable.length; t++) {
                    //check for table header row
                    if (selectedTable[t].getElementsByTagName("thead").length > 0) {
                        var headerCells = selectedTable[t].getElementsByTagName("th"),
                            dataCells = selectedTable[t].getElementsByTagName("td");

                        //for every td cell in the row
                        for (i = 0; i < dataCells.length; i++) {
                            //get cells cells index
                            var dataCellIndex = dataCells[i].cellIndex,

                                //get same header cells index innerText
                                headerCellText = headerCells[dataCellIndex].innerText;

                            //add the th value as the attribute of the td
                            dataCells[i].setAttribute("data-title", headerCellText);
                        }
                    }
                }
            }
        });
    }
}(jQuery));
/*Examples
Normal Implementation:
jQuery(".Table-Product").responsiveDataTable();

*/

// Responsive Zoom 2.2.1 Copyright (c) 2014 Fiserv.  All rights reserved.
// Code dependencies: Modernizr;
// Code Usage: none;
// Call Needs to be AFTER any section table/div replacement scripts

// This function is global, at this time it is only used in this responzive zoom 2.2.1 plugin. If it is used elsewhere, we should move it outside to its own heading.
function debounce(func, wait, immediate) {
    var timeout;
    return function () {
        var context = this, args = arguments;
        var later = function () {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
};

(function (jQuery) {
    jQuery.fn.responsiveZoom = function (options) {
        var settings = jQuery.extend({
            hideBeforeResized: true
        }, options);

        // This script had to be moved into the responsiveZoom function when placed in the master fiserv-plugins.js file. It was causing every other plugin to requrie modernizr when placed outside. - KR 3/28/18
        Modernizr.addTest('zoom', function () {
            var test = document.createElement('div');
            if (test.style.zoom === undefined) {
                delete test;
                return false;
            }
            delete test;
            return true;
        });


        //console.log('Mobile size detected.');	
        var responsiveZoomers = jQuery(this);
        //console.log(responsiveZoomers.length);
        //console.log('Modernizr.csstransforms: ' + Modernizr.csstransforms);
        responsiveZoomers.each(function () {
            //if ( jQuery( "body" ).hasClass( 'mobile' ) ) {

            // reset zoom before calc.
            if (Modernizr.zoom && !Modernizr.csstransforms) {
                jQuery(this).css("zoom", 1);
                //console.log('Reset the zoom to 1.');
            } else {
                jQuery(this).css("transform-origin", "0 0");
                jQuery(this).css("transform", "scale(1)");
                //console.log('Reset the transform scale to: ' + jQuery( this ).css("transform"));
            }

            // The element being zoomed can't be display:none.
            if (jQuery(this).css("display") === 'none') {
                if (jQuery(this).prop("tagName") == "TABLE") {
                    jQuery(this).css("display", "table");
                } else {
                    jQuery(this).css("display", "inline");
                }
                var elWidth = jQuery(this).width();
                jQuery(this).css("display", "none");
            } else {
                var elWidth = jQuery(this).width();
            }

            // Widths set as a percentage are set to pixels for proper scaling.
            if (jQuery(this).attr("tagName") == "TABLE") {
                if (!jQuery(this).data("original-width-string")) {
                    jQuery(this).data("original-width-string", jQuery(this)[0].style.width);
                }
                if (!jQuery(this).data("original-width")) {
                    jQuery(this).data("original-width", elWidth);
                    jQuery(this).css("width", elWidth);
                    //console.log('Set the width to: ' + elWidth);
                } else {
                    jQuery(this).css("width", jQuery(this).data("original-width"));
                    //console.log('Reset the width to: ' + jQuery( this ).data("original-width"));
                }
            }

            // Calculates the zoom level.
            if (Modernizr.zoom && !Modernizr.cssgradients) {
                if (!jQuery(this).data("original-position")) {
                    jQuery(this).data("original-position", jQuery(this).css("position"));
                }
                jQuery(this).css("position", "absolute").css("visibility", "hidden");
            }
            if (!jQuery(this).parent().hasClass("responsive-zoom-wrapper")) {
                var elParentWidth = jQuery(this).parent().width();
            } else {
                var elParentWidth = jQuery(this).parent().parent().width();
            }
            if (Modernizr.zoom && !Modernizr.cssgradients) {
                jQuery(this).css("position", jQuery(this).data("original-position")).css("visibility", "visible");
            }
            //console.log('elParentWidth: ' + elParentWidth);

            //console.log('elWidth: ' + elWidth + ' / elParentWidth: ' + elParentWidth );
            var elZoom = elParentWidth / elWidth;
            //console.log('elZoom: ' + elZoom);

            // Create a new div to hold the parents height if zoom is not supported.
            if (!jQuery(this).parent().hasClass("responsive-zoom-wrapper")) {
                var responsiveZoomWrapper = jQuery('<div class="responsive-zoom-wrapper"></div>');
                jQuery(this).after(responsiveZoomWrapper);
                responsiveZoomWrapper.append(jQuery(this));
                jQuery(this).parent().css("margin-top", jQuery(this).css("margin-top"));
                jQuery(this).css("margin-top", 0);
                jQuery(this).parent().css("margin-bottom", jQuery(this).css("margin-bottom"));
                jQuery(this).css("margin-bottom", 0);
                //console.log('Created responsiveZoomWrapper');
            }

            // Applies the zoom
            if (elZoom < 1) {
                if (Modernizr.zoom && !Modernizr.csstransforms) {
                    jQuery(this).css("zoom", elZoom);
                    //console.log('Zoom set to: ' + elZoom);
                } else {
                    jQuery(this).css("transform-origin", "0 0");
                    jQuery(this).css("transform", "scale(" + elZoom + ")");
                    jQuery(this).parent().css("width", jQuery(this).width() * elZoom);
                    jQuery(this).parent().css("height", jQuery(this).height() * elZoom);
                }
            } else {
                if (Modernizr.zoom && !Modernizr.csstransforms) {
                    jQuery(this).css("zoom", "");
                } else {
                    jQuery(this).css("transform-origin", "");
                    jQuery(this).css("transform", "");
                    if (jQuery(this).parent().hasClass("responsive-zoom-wrapper")) {
                        var parentToRemove = jQuery(this).parent();
                        jQuery(this).css("margin-top", "");
                        jQuery(this).css("margin-bottom", "");
                        parentToRemove.after(jQuery(this));
                        parentToRemove.remove();
                    }
                }
                jQuery(this).css("width", jQuery(this).data("original-width-string"));
            }

            if (settings.hideBeforeResized) { jQuery(this).css("opacity", 1); }
        });
    };
}(jQuery));
/* Examples:
jQuery( ".responsivezoom" ).responsiveZoom ({
    hideBeforeResized: false
});
*/


// Scroll Page v1.1.1 (c) Paul Richards & Jesse Fowler, Fiserv 2015.  All rights reserved.
// Code dependencies:  Scroll To;
// Code Usage: Site Slideshow;
(function (jQuery) {
    jQuery.fn.scrollPage = function (options) {
        var settings = jQuery.extend({
            duration: 5000, // Milliseconds of delay before scrolling to next section.
            autoScroll: false,
            login: jQuery('.onlinebanking input'), //login parent - initiate Pause and Restart
            debug: false
        }, options);

        var $this = this,
            cycleTimer;

        if (jQuery('body').hasClass('desktop')) {
            var lastScrollTop = 0;
            var scrollToNext = function () {
                if (settings.debug) { console.log('lastScrollTop:' + lastScrollTop + ' jQuery(document).scrollTop():' + jQuery(document).scrollTop()) };
                if (lastScrollTop == jQuery(document).scrollTop() || jQuery(document).scrollTop() == 0) {
                    //Activates Pause
                    if ((settings.autoScroll) && !settings.login.is(':focus')) {
                        $this.eq(0).click();
                        window.setTimeout(function () {
                            lastScrollTop = jQuery(document).scrollTop();
                        }, 2100);  // Set this to the delay of Scroll To's animate of the body plus 100 milliseconds.
                    }
                }
            }

            cycleTimer = window.setInterval(scrollToNext, settings.duration);

            //Restart Interval				
            settings.login.on('blur', function () {
                clearInterval(cycleTimer);
                cycleTimer = window.setInterval(scrollToNext, settings.duration);
            });

            jQuery(window).bind('scroll', function () {
                clearInterval(cycleTimer);
                cycleTimer = window.setInterval(scrollToNext, settings.duration);
                jQuery('.scroll-to').each(function () {
                    var post = jQuery(this);
                    var position = post.position().top - jQuery(window).scrollTop();
                    if (position <= 40 || jQuery(window).scrollTop() + jQuery(window).height() == jQuery(document).height()) {
                        post.addClass('scroll-to-current');
                        if (post === jQuery('.scroll-to').eq(0)) {
                            post.last().removeClass("scroll-to-current");
                        } else {
                            post.prev().removeClass("scroll-to-current");
                        }
                    } else {
                        post.removeClass('scroll-to-current');
                    }
                });
            });

        }
    }
}(jQuery));


// Scroll Trigger 1.2.0 (c) Kristen Rogers & Jesse Fowler, Fiserv 2015.  All rights reserved.
// Code dependencies: none;
// Code Usage: Side Nav Generator, Site Slideshow;
(function (jQuery) {

    jQuery.fn.scrollTrigger = function (options) {

        var settings = jQuery.extend({
            triggerClass: "scroll-active",
            scrollMin: 0,
            elementOffset: 1, //percentage of window height if scrollMin not defined.
            resetOnScrollUp: true,
            target: this
        }, options);

        var $this = this,
            height = jQuery(window).scrollTop(),
            scrollMinProvided = true,
            targetProvided = true;

        if (settings.scrollMin == 0) {
            scrollMinProvided = false;
        }
        if (settings.target === this) {
            targetProvided = false;
        }

        $this.each(function (index) {
            if (!scrollMinProvided) {
                settings.scrollMin = jQuery(this).offset().top - (jQuery(window).innerHeight() * settings.elementOffset);
            }
            if (height >= settings.scrollMin) {
                if (targetProvided) {
                    settings.target.addClass(settings.triggerClass);
                } else {
                    jQuery(this).addClass(settings.triggerClass);
                }
            } else if (height < settings.scrollMin && settings.resetOnScrollUp) {
                if (targetProvided) {
                    settings.target.removeClass(settings.triggerClass);
                } else {
                    jQuery(this).removeClass(settings.triggerClass);
                }
            }
        });
        return $this;
    }
}(jQuery));


// Scroll To 1.1.0 (c) Jesse Fowler, Fiserv 2015.  All rights reserved.
// Code dependencies: none;
// Code Usage: Site Slideshow;
(function (jQuery) {
    jQuery.fn.scrollTo = function (options) {
        var settings = jQuery.extend({
            skipInitial: 0,
            trigger: jQuery(".scroll-trigger")
        }, options);
        var $this = this,
            currentElement = 0 + settings.skipInitial;

        jQuery(this).addClass('scroll-to');
        jQuery(this).eq(0).addClass('scroll-to-current');

        if (this.length > 0 + settings.skipInitial) {
            settings.trigger.addClass("active");
            if (currentElement >= $this.length) {
                currentElement = 0;
            }
            settings.trigger.click(function () {
                var scrollPos = jQuery(document).scrollTop();
                $this.each(function (index) {
                    if (jQuery(this).is(jQuery('.scroll-to-current').eq(0))) {
                        if (index >= ($this.length - 1)) {
                            currentElement = 0;
                        } else {
                            currentElement = index + 1;
                        }
                        //console.log(currentElement);
                    }
                });
                if ($this.eq(currentElement).offset().top != scrollPos) {
                    jQuery('html, body').animate({
                        scrollTop: $this.eq(currentElement).offset().top
                    }, 2000);
                    jQuery('.scroll-to-current').removeClass('scroll-to-current');
                    $this.eq(currentElement).addClass('scroll-to-current');
                }
                if (currentElement >= ($this.length - 1)) {
                    currentElement = 0;
                } else {
                    currentElement++;
                }
            });
        }
        return $this;
    }
}(jQuery));


// sideNavGenerator v2.2.1 Copyright (c) 2014 Jesse Fowler, Fiserv 
// Code dependencies: Scroll Trigger, Anchor Link (not a plugin);
// Code Usage: none;
var sideNavGeneratorInstance = 0;
(function (jQuery) {
    jQuery.fn.sideNavGenerator = function (options) {
        var settings = jQuery.extend({
            contentArea: jQuery('body'),
            excludedPageClass: 'no-sidenav',
            addToSideNavClassName: 'Side-Navigation',
            fullURLEnable: false,
            includeCurrentPageSiblings: false,
            debug: false,
            toggleOnScroll: true,
            toggleOnScrollClass: 'active'
        }, options);

        var $this = jQuery(this),
            $body = jQuery("body");

        if (settings.debug) { console.log($this) };

        sideNavGeneratorInstance++

        if (settings.contentArea) {
            // Grabs additional content to the sideNav using table class="addtosidenav"
            var additionalContent = settings.contentArea.find('.' + settings.addToSideNavClassName + '>tbody>tr>td');
            var tableContent = '';
            for (i = 0; i < additionalContent.length; i++) {
                tableContent = tableContent + additionalContent[i].innerHTML;
                additionalContent[i].parentNode.removeChild(additionalContent[i]);
            }

            if (($this.length > 1 && !$body.hasClass(settings.excludedPageClass)) || (tableContent.length > 1 && !$body.hasClass(settings.excludedPageClass)) || (settings.includeCurrentPageSiblings && !$body.hasClass(settings.excludedPageClass))) {
                $body.addClass('sideNavPresent');
                var sideContainer = jQuery('<div />');
                sideContainer.attr('class', 'sideNav');

                if ($this.length > 1 || settings.includeCurrentPageSiblings) {
                    var sideContainerList;
                    var founda = false;
                    if (settings.includeCurrentPageSiblings) {
                        var generateSiblingList = function () {
                            var locationStr = location.toString();
                            if (locationStr.indexOf("#") > 0) {
                                hash = locationStr.substring(0, locationStr.indexOf("#"));
                            } else {
                                hash = locationStr;
                            }
                            if (location.host == 'whstage1.secureinternetbank.com' || location.host == 'whstage2.secureinternetbank.com') {
                                var locationHost = jQuery(location).prop('pathname').split('/')[1];
                            } else {
                                var locationHost = '';
                            }
                            var siblingSideNavUl = jQuery('<ul />');
                            jQuery('ul a').each(function () {
                                currentLink = jQuery(this);
                                if (hash == (location.protocol + '//' + location.host + '/' + locationHost + '/' + currentLink.attr('href')) || hash == (location.protocol + '//' + location.host + '/' + currentLink.attr('href'))) {
                                    if (!founda) {
                                        if (!$body.hasClass('category')) {
                                            founda = true;
                                            siblingSideNavUl.addClass('w-siblings');
                                            var currentLinkParent = currentLink.parent('li').parent('ul');
                                            currentLink.parent('li').addClass('current');
                                            var siblings = currentLinkParent.find('li');
                                            if (siblings.length > 0) {
                                                siblings.each(function () {
                                                    if (jQuery(this).css('display') != 'none') {
                                                        var sibling = jQuery(this).clone();
                                                        sibling.find('ul').remove();
                                                        siblingSideNavUl.append(sibling);
                                                    }
                                                });
                                            }
                                        }
                                    }
                                }
                            });
                            if (settings.debug) { console.log('siblingSideNavUl returned'); };
                            return siblingSideNavUl;
                        };
                        sideContainerList = generateSiblingList();
                    } else {
                        sideContainerList = jQuery('<ul />');
                    }
                    if (settings.debug) { console.log(sideContainerList); };
                    if ($this.length > 0) {
                        var anchorLinksUl = jQuery('<ul />');
                        sideContainerList.find('.current').append(anchorLinksUl);
                    }

                    $this.each(function (index) {
                        var sideContainerListItem = jQuery('<li />');
                        if (settings.includeCurrentPageSiblings && sideContainerList.find('.current').length > 0) {
                            anchorLinksUl.append(sideContainerListItem);
                        } else {
                            sideContainerList.append(sideContainerListItem);
                        }
                        var anchorLinkURL = '';
                        if (settings.fullURLEnable) {
                            anchorLinkURL = location.protocol + '//' + location.host + location.pathname + '#sideNavGeneratorAnchor' + sideNavGeneratorInstance + '-' + index;
                        } else {
                            anchorLinkURL = '#sideNavGeneratorAnchor' + sideNavGeneratorInstance + '-' + index;
                        }

                        var sideContainerListItemLink = jQuery('<a />');
                        if (window.location.toString().match(/\bSiteContent\b/)) {
                            sideContainerListItemLink.attr('href', 'javascript:anchorLink("' + anchorLinkURL + '")');
                        } else {
                            sideContainerListItemLink.attr('href', anchorLinkURL);
                        }
                        //sideContainerListItemLink.text(jQuery(this).text());
                        sideContainerListItemLink.html(jQuery(this).text());
                        sideContainerListItem.append(sideContainerListItemLink);

                        var tagsAnchor = jQuery('<a />');
                        tagsAnchor.attr('id', 'sideNavGeneratorAnchor' + sideNavGeneratorInstance + '-' + index);
                        tagsAnchor.attr('class', 'anchor');
                        tagsAnchor.insertBefore(jQuery(this));

                        if (settings.toggleOnScroll) {
                            jQuery(window).on('scroll', function () {
                                tagsAnchor.scrollTrigger({
                                    triggerClass: settings.toggleOnScrollClass,
                                    elementOffset: .5,
                                    resetOnScrollUp: false,
                                    target: sideContainerListItemLink.parent()
                                });
                            })
                        }
                    });
                    sideContainer.append(sideContainerList);
                }
                settings.contentArea.prepend(sideContainer);

                // Appends additional content
                if (tableContent.length > 1) {
                    var additionalContentContainer = jQuery('<div />');
                    additionalContentContainer.addClass('additionalContentContainer');
                    additionalContentContainer.html(tableContent);
                    sideContainer.append(additionalContentContainer);
                }
            }
        }
        return $this;
    }
}(jQuery));
/*Examples
Normal Implementation:
jQuery(".subpage-container h3").sideNavGenerator();

Custom Implementation:
jQuery(".subpage-container h3").sideNavGenerator({
    contentArea: jQuery('#subpage-container>.inner-content')
});

Include sibling links Implementation:
jQuery(".subpage-container>h2, .subpage-container>form>h2").sideNavGenerator({
	    contentArea: jQuery('#content1'),
	    includeCurrentPageSiblings: true
	});
*/

// Site Notice 3.1.2 Copyright 2015 Jesse Fowler, Fiserv.  All rights reserved.
// Code dependencies: none;
// Code Usage: App Banners;
if (jQuery("body").hasClass("home")) {
    (function (jQuery) {

        jQuery.fn.responsiveSiteNotice = function (options) {

            var settings = $.extend({
                reqLength: 15,
                fixedPosition: false,
                delay: 100
            }, options);

            this.each(function () {
                var $notice = jQuery(this),
                    $noticeHtml = $notice.find('.noticeHtml'),
                    uniqueName = $notice.attr('id') + "NoticeText";
                var bodyClassName;
                if ($notice.hasClass("appbanner")) {
                    bodyClassName = "bannernoticeactive";
                }
                else {
                    bodyClassName = "noticeactive";
                }
                if ($noticeHtml.html().length > settings.reqLength) {

                    var noticeCloser = jQuery('<div class="noticecloser"></div>');

                    var noticeCloserSession = jQuery('<div class="noticeclosersession"></div>');

                    var firstTable = $notice.find('.noticeHtml>table>tbody>tr>td');
                    if (firstTable.length) {
                        noticeCloserSession.prependTo(firstTable);
                        noticeCloser.prependTo(firstTable);
                    } else {
                        noticeCloserSession.prependTo($noticeHtml);
                        noticeCloser.prependTo($noticeHtml);
                    }

                    var bypassNotice = localStorage.getItem(uniqueName),
                        noticeHtmlNow = $noticeHtml.html();
                    if (bypassNotice) {
                        sessionStorage.setItem(uniqueName, bypassNotice);
                    }
                    var bypassNoticeSession = sessionStorage.getItem(uniqueName);

                    if (settings.fixedPosition) {
                        var newId = $notice.prop('id') + '-clone';
                        $notice.clone().prop('id', newId).prependTo(jQuery('body'));
                    }
                    function noticeOpen() {
                        $notice.addClass('active');
                        jQuery('body').addClass(bodyClassName);
                    }
                    function noticeClose() {
                        $notice.removeClass('active');
                        jQuery('body').removeClass(bodyClassName);
                    }
                    try {
                        if (bypassNotice != noticeHtmlNow && bypassNoticeSession != noticeHtmlNow) {
                            setTimeout(noticeOpen, settings.delay);
                            localStorage.removeItem(uniqueName);
                            sessionStorage.removeItem(uniqueName);
                        } else if (bypassNoticeSession != noticeHtmlNow) {
                            setTimeout(noticeOpen, settings.delay);
                            localStorage.removeItem(uniqueName);
                            sessionStorage.removeItem(uniqueName);
                        }
                    } catch (e) {
                        setTimeout(noticeOpen, settings.delay);
                    }

                    noticeCloser.on('click', function () {
                        noticeClose();
                        try {
                            localStorage.setItem(uniqueName, noticeHtmlNow);
                            sessionStorage.setItem(uniqueName, noticeHtmlNow);
                        } catch (e) {
                            console.log('You are in Privacy Mode. Please deactivate Privacy Mode and then reload the page.');
                        }

                    });

                    noticeCloserSession.on('click', function () {
                        noticeClose();
                        try {
                            sessionStorage.setItem(uniqueName, noticeHtmlNow);
                        } catch (e) {
                            console.log('You are in Privacy Mode. Please deactivate Privacy Mode and then reload the page.');
                        }

                    });

                } else if ($noticeHtml.html().length < settings.reqLength) {
                    localStorage.removeItem(uniqueName);
                    sessionStorage.removeItem(uniqueName);
                }
            });

            return this;

        };

    }(jQuery));

    // Removes the blank paragraphs from the bottom of site notice.
    jQuery("#noticeHtml>p:last-of-type").filter(function () {
        return jQuery.trim(jQuery(this).html()) == '&nbsp;';
    }).remove();

}

// Table to Div Conversion 1.3.0 (c) Jesse Fowler, Fiserv 2015.  All rights reserved.
// Code dependencies: none;
// Code Usage: Site Slideshow;
(function (jQuery) {

    jQuery.fn.tableWrapper = function (options) {

        // This is the easiest way to have default options.
        var settings = jQuery.extend({
            // These are the defaults.
            wrapperClass: "subsection",
            wrapperContentClass: "inner-content",
            structure: "section"
        }, options);

        var $this = jQuery(this);

        if (settings.wrapperContentClass != "") {
            var wrapperContentClass = settings.wrapperContentClass;
        } else {
            var wrapperContentClass = settings.wrapperClass + '-content';
        }

        $this.each(function () {
            //console.warn(jQuery(this));
            var wrapper = jQuery('<' + settings.structure + ' class="' + settings.wrapperClass + '"></' + settings.structure + '>'),
                wrapperID = jQuery(this).attr('id');
            if (typeof jQuery(this).attr("style") != "undefined" && jQuery(this).attr("style").indexOf("url") >= 0) {
                wrapper.css("background-image", jQuery(this).css('background-image'));
            }
            if (typeof jQuery(this).attr("id") != "undefined") {
                wrapper.attr("id", jQuery(this).attr('id'));
            }
            jQuery(this).children("tbody").children("tr").each(function () {
                var subsectionContent = jQuery('<div class="' + wrapperContentClass + '"></div>');
                jQuery("td:first", this).each(function () {
                    //subsectionContent += jQuery(this).html();
                    subsectionContent.append(jQuery(this).children());
                });
                wrapper.append(subsectionContent);
            });
            jQuery(this).replaceWith(wrapper);
        });
    }
}(jQuery));

// Take a Tour 2.1.1 Copyright 2017 JP Larson, Fiserv.  All rights reserved.
// Requires tour.css and include
// The include name is determined by the id used within the selector. Example: #tour needs inc_tour.aspx.
(function (jQuery) {
    jQuery.fn.tour = function (options) {
        var settings = jQuery.extend({
            tour: jQuery(this), //The object brought in by the selector in dom ready.
            disabledOnLoad: false, //Disables auto play on DOM ready. Added: 2.1.1
            exitStorage: "local", //Storage method of the exit event. Only applies if disabledOnload is false. Either local or session can be used. Added: 2.1.1
            dataset: 'tour', //The name of the sections dataset. This will be used for all selectors.
            intro: 'intro', //The value used for the intro dataset
            offset: 25, //The offset of the tour section (in pixels) to prevent overlap of the feature.
            scrollOffset: 0.25, //The percentage of the view height left above the tour after scrolling.
            url: "inc_tour.aspx", //The url for the tour include. Changed: 2.0.2
            css: false, //The url for the style sheet. Changed: 2.1.1
            controls: {
                continue: '[data-control=Continue]', //The selector used for the continue buttons.
                exit: '[data-control=Exit]' //The selector used for the exit buttons.
            },
            classes: {
                open: 'open', //The class applied when the tour is opened.
                play: 'play', //The class applied after the slide is continued.
                active: 'active', //The class applied to the active tour section.
                fixed: 'fixed' //The class applied to the tour section when the target is fixed position. Added: 2.1.0
            },
            resetToTop: true, //Scrolls to the top of the page on exit. Can be set to true or false. Added: 2.1.0
            loadDelay: 0 //Delays the loading of the tour in 1/1000 of a second. Can be used for timing issues such as DOM thrashing. Added: 2.1.1
        }, options),
            sections = '[data-' + settings.dataset + ']',
            appendCSS = function () { //Appends the head with the tour CSS if set in the settings.
                if (jQuery('#tour-styles').length < 1 && settings.css) {
                    jQuery('head').append(jQuery('<link id="tour-styles" rel="stylesheet" href="' + settings.css + '">'));
                }
            };

        try {
            var tour,
                tourInit = settings.tour,
                includeFile = jQuery.ajax({ //Ajax function to load the include
                    async: true,
                    type: "GET",
                    url: settings.url,
                    success: function (result) {
                        if (result.length > 5) {
                            appendCSS();
                            var delay = setTimeout(function () {
                                jQuery('body').append(result);
                                tour = jQuery(tourInit.eq(0).attr('href'));
                                init();
                            }, settings.loadDelay);
                        } else {
                            throw (settings.url + " does not exist");
                        }
                    }
                }),
                positionFeatures = function (tourSections) { //Positions each section based on the top position of the featured ID.
                    try {
                        for (i = 0; i < tourSections.length; i++) {
                            feature = tourSections.eq(i);
                            if (feature.data(settings.dataset) != settings.intro) {
                                target = jQuery('#' + feature.data(settings.dataset));
                                try {
                                    if (target.length > 0) {
                                        window.scrollTo(0, window.pageYOffset - 1);
                                        var theOffset = parseInt(target.offset().top),
                                            theNewOffset;
                                        window.scrollTo(0, window.pageYOffset + 1);
                                        theNewOffset = parseInt(target.offset().top);
                                        if (theOffset != theNewOffset) {
                                            feature.css({
                                                top: parseInt(theOffset) - feature.height() - settings.offset
                                            }).addClass(settings.classes.fixed);
                                        } else {
                                            feature.css('top', theOffset - feature.height() - settings.offset);
                                        }

                                    } else {
                                        feature.remove();
                                        throw "The ID '" + feature.data(settings.dataset) + "' does not exist.";
                                    }
                                } catch (err) {
                                    console.log(err);
                                }
                            }
                        }
                    } catch (err) {
                        console.log(err);
                    }
                },
                reset = function () { //Resets the tour to the start position
                    tour.removeClass(settings.classes.open);
                    tour.removeClass(settings.classes.play);
                    tour.find(sections.toString()).removeClass(settings.classes.active);
                    if (settings.resetToTop) {
                        jQuery('html,body').stop().animate({
                            scrollTop: 0,
                        }, 850, 'swing');
                    }

                },
                moveToFeature = function (feature) { //Increments the tour to the next feature.
                    try {
                        feature.removeClass(settings.classes.active);
                        var target = feature.next(),
                            scrollTo = parseInt(target.css('top')) - (jQuery(window).height() * settings.scrollOffset);
                        target.addClass(settings.classes.active);
                        if (!target.hasClass(settings.classes.fixed)) {
                            jQuery('html,body').stop().animate({
                                scrollTop: scrollTo > 0 ? scrollTo : 0,
                            }, 850, 'swing');
                        }
                    } catch (err) {
                        console.log(err);
                    }
                },
                init = function () { //initializes the tour by calling the required functions and assigning even handlers.
                    if (settings.disabledOnLoad == false && window.localStorage.getItem("tourOnLoad" + tour.attr('id')) !== "false" && window.sessionStorage.getItem("tourOnLoad" + tour.attr('id')) !== "false") {
                        tour.addClass(settings.classes.open);
                    }
                    tourInit.click(function (e) {
                        if (e.currentTarget.nodeName == "A") {
                            e.preventDefault();
                        }
                        reset();
                        tour.addClass(settings.classes.open);
                    });
                    jQuery(window).resize(function () {
                        var delay = setTimeout(function () {
                            positionFeatures(tour.find(sections.toString()));
                        }, 500);
                    })
                    tour.find(settings.controls.exit.toString()).click(function () {
                        switch (settings.exitStorage) {
                            case "local":
                                localStorage.setItem("tourOnLoad" + tour.attr('id'), false);
                                break;
                            case "session":
                                sessionStorage.setItem("tourOnLoad" + tour.attr('id'), false);
                                break;
                        }
                        reset();
                    });
                    tour.find(settings.controls.continue.toString()).click(function () {
                        tour.addClass(settings.classes.play);
                        positionFeatures(tour.find(sections.toString()));
                        moveToFeature(jQuery(this).closest(sections.toString()));
                    });
                };
        } catch (err) {
            console.log(err);
        }
    }
}(jQuery));