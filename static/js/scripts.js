function clearText(thefield) {
    if (thefield.defaultValue == thefield.value)
        thefield.value = ""
}
function restoreText(theField) {
    if (theField.value == "") {
        theField.value = theField.defaultValue;
    }
}
// Online Banking
function doLoginRefresh() {
    var x = document.forms.Remote;

    if (x.username.value != "" && x.password.value != "") {
        x.action = 'https://web2.secureinternetbank.com/pbi_pbi1151/login/remote/265371121';
        return true;

    } else {
        //alert("\nPlease enter a valid Access ID and Password.\nThank you."); 
        //return false;
    }
}

// Add custom HTML5 validation
(function () {
    jQuery.fn.customError = function (options) {
        var settings = jQuery.extend({
            field: jQuery(this),
            dataset: "data-error"
        }, options);
        for (i = 0; i < settings.field.length; i++) {
            settings.field.eq(i).on('invalid', function () {
                var message = jQuery(this).attr(settings.dataset);
                this.setCustomValidity(message);
            }).on('change keydown blur', function () {
                this.setCustomValidity('');
            });
        }
        return this;
    }
}(jQuery));

// Replace with checkmarks v1.0.0 Copyright 2017 Jesse Fowler, Fiserv.  All rights reserved.
(function (jQuery) {
    jQuery.fn.replaceWithCheckmarks = function (options) {
        var settings = jQuery.extend({
            findThis: 'x',
            htmlReplacement: '<span class="checkmark"><span class="visuallyhidden">x</span></span>'
        }, options);
        this.each(function () {
            if (jQuery(this).html() == settings.findThis) {
                jQuery(this).html(settings.htmlReplacement);
            }
        });
        return this;
    };
}(jQuery));


var links = document.getElementsByTagName("a");
for (var i = 0; i < links.length; i++) {
    if (links[i].href.match(/speedbump/i) && links[i].href.match(/\?link\=/i) && !links[i].target) {
        links[i].target = '_blank';
    }
}
// Navigation panel fix 1.1.0 Copyright 2018 Jesse Fowler, Fiserv.  All rights reserved.
(function (jQuery) {
    jQuery.fn.navigationPanelFix = function (options) {
        var settings = jQuery.extend(true, {
            tooWideClass: 'edge'
        }, options),
            init = function (obj) {
                obj.off('mouseenter');
                obj.on('mouseenter', function (e) {
                    try {
                        var parentElm = $(this),
                            combinedWidth = Math.abs($('div:first', parentElm).offset().left) + $('div:first', parentElm).width(),
                            bodyWidth = jQuery('body').width();

                        //parentElm.removeClass(settings.tooWideClass);
                        if (jQuery('div', parentElm).length) {
                            if (combinedWidth > bodyWidth) {
                                parentElm.addClass(settings.tooWideClass);
                            }
                        }
                    } catch (e) {
                        // log errors
                    }
                });
                jQuery(window).resize(function () {
                    obj.removeClass(settings.tooWideClass);
                })
            };
        init(this);
        return this;
    };
}(jQuery));

    //Animation on scroll
    (function (jQuery) {
        jQuery.fn.isInViewport = function () {
            var elementTop = jQuery(this).offset().top;
            var elementBottom = elementTop + jQuery(this).outerHeight();
            var viewportTop = jQuery(window).scrollTop();
            var viewportBottom = viewportTop + jQuery(window).height();
            return elementBottom > viewportTop && elementTop < viewportBottom;
        };
    }(jQuery));

jQuery(document).ready(function () {
    jQuery('input[data-error], select[data-error], textarea[data-error]').customError();

    // Replace with checkmarks v1.0.0 Copyright 2017 Fiserv.  All rights reserved.
    jQuery(".Table-Product tbody>tr>td>p").replaceWithCheckmarks({
        findThis: 'X',
        htmlReplacement: '<span class="checkmark"><span class="visuallyhidden">Check</span></span>'
    });

    jQuery(".Table-Product tbody>tr>td").replaceWithCheckmarks({
        findThis: 'X',
        htmlReplacement: '<span class="checkmark"><span class="visuallyhidden">Check</span></span>'
    });
    jQuery(".Table-Style tbody>tr>td>p").replaceWithCheckmarks({
        findThis: 'X',
        htmlReplacement: '<span class="checkmark"><span class="visuallyhidden">Check</span></span>'
    });

    jQuery(".Table-Style tbody>tr>td").replaceWithCheckmarks({
        findThis: 'X',
        htmlReplacement: '<span class="checkmark"><span class="visuallyhidden">Check</span></span>'
    });

    // Replaces Subsection Table with a Div Wrapper 
    // 1.1.0 (c) Fiserv 2015.  All rights reserved.
    jQuery("table.Subsection-Table").tableWrapper();
    jQuery("table.Subsection-Table-Promo").tableWrapper({
        wrapperClass: "subsection-promo"
    });
    jQuery("table.Subsection-Table-Promo-Blue").tableWrapper({
        wrapperClass: "subsection-promo-blue",
    });
    jQuery("table.Subsection-Table-Promo-White").tableWrapper({
        wrapperClass: "subsection-promo-white",
    });
    jQuery("table.Subsection-Promo-Table-Half").tableWrapper({
        wrapperClass: "subsection-promo-half"
    });
    // Responsive Zoom 2.2.1 Copyright (c) 2014 Fiserv.  All rights reserved.
    // Requires Modernizr, jQuery			
    var windowWidth = jQuery(window).width();
    var onWinResizer = debounce(function () {
        if (jQuery(window).width() != windowWidth) {
            onWinResize();
            windowWidth = jQuery(window).width();
        }
    }, 500);

    jQuery(window).on('resize', onWinResizer);

    function onWinResize() {
        var windowSize = jQuery(window).width();
        // Set page width maximums and minimums
        pageWidth = parseFloat(windowSize);
        if (pageWidth < 990) {
            try {
                jQuery("body").addClass("mobile");
                jQuery("body").removeClass("desktop");
            } catch (err) { }
        } else {
            try {
                jQuery("body").removeClass("mobile");
                jQuery("body").addClass("desktop");
            } catch (err) { }
        }
        jQuery(".responsivezoom").responsiveZoom();
        jQuery(".Table-Style").responsiveZoom();
        jQuery(".Table-Product").responsiveZoom();
        onWinResizeInitalized = true;
    }

    onWinResize();

    // Slideshow
    jQuery('#hero-main').slideShow({
        randomSelect: false,
    });

    // Responsive Nav
    jQuery("#menuopen").click(function () {
        jQuery("body").toggleClass("opennav");
        jQuery("body"
        ).removeClass("openob"); //Hide login
        jQuery("nav ul li").each(function () {
            jQuery(this).removeClass('active');
        });
    });
    jQuery("nav ul li").click(function () {
        jQuery(this).toggleClass("active");
        //jQuery(this).siblings().removeClass("active"); //closes other tabs
    });
    // Navigation panel fix to stay in view with wide panels
    jQuery("#primary > div > ul > li").navigationPanelFix();

    // Homenav door navigation
    jQuery("ul.nav2 li").click(function () {
        jQuery(this).toggleClass("active");
        //jQuery(this).siblings().removeClass("active"); //closes other tabs
    });
    jQuery("ul.panelnav li").click(function () {
        jQuery(this).toggleClass("active");
        //jQuery(this).siblings().removeClass("active"); //closes other tabs
    });

    // Login Show/Hide
    jQuery(".login-button").click(function () { // Login Show/Hide
        jQuery("body").toggleClass("openob");
        jQuery("body").removeClass("opennav"); //Hide Responsive Nav    
    });	
    // Site Search
    jQuery('.search-btn').click(function () {
        jQuery(this).parent().toggleClass('searchopen');
        jQuery('#searchField').focus();
    });
    jQuery('#nav-search input').click(function () {
        jQuery(this).toggleClass('active');
    });	
    // Detect TD has Content
    jQuery("[class*=subsection] .inner-content > table:not('[class*=Table]') td, .Subsection-Table > tbody > tr > td:first-of-type > table:not('[class*=Table]') td").each(function () {
        var $this = jQuery(this);

        if (($this.html().length > 25) || ($this.find('h1,h2,h3,h4,h5').length)) {
            $this.addClass("show");
        }
    });

    // Add overlay (fade) based on content location
    // Detect TD has Content required
    jQuery(".subsection[style*='url'] .inner-content > table:not('[class*=Table]') > tbody > tr, .Subsection-Table[style*='url'] > tbody > tr > td:first-of-type > table:not('[class*=Table]') > tbody > tr").each(function () {
        var $this = jQuery(this);

        if (jQuery(this).find("td:first-child").hasClass("show") && jQuery(this).find("td:last-child").hasClass("show")) {
        } else if (jQuery(this).find("td:first-child").hasClass("show")) {
            $this.parents(".subsection, .Subsection-Table").addClass("fade-left");
        } else if (jQuery(this).find("td:last-child").hasClass("show")) {
            $this.parents(".subsection, .Subsection-Table").addClass("fade-right");
        }
    });

    // Remove unwanted spaces
    jQuery('p').each(function () {
        var $this = jQuery(this);
        if ($this.html().replace(/\s|&nbsp;/g, '').length == 0)
            $this.remove();
    });

    // Smooth Scroll 	
    jQuery(function () {
        jQuery('a[href*=#]:not([href=#])').click(function () {
            if (location.pathname.replace(/^\//, '') == this.pathname.replace(/^\//, '') && location.hostname == this.hostname) {
                var target = jQuery(this.hash);
                target = target.length ? target : jQuery('[name=' + this.hash.slice(1) + ']');
                if (target.length) {
                    jQuery('html,body').animate({
                        scrollTop: target.offset().top
                    }, 850, 'swing');
                    return false;
                }
            }
        });
    });
    // Count Up
    function countUp() {
        jQuery('.count').each(function () {
            jQuery(this).prop('Counter', 0).animate({
                Counter: jQuery(this).text()
            }, {
                    duration: 3000,
                    easing: 'swing',
                    step: function (now) {
                        jQuery(this).text(Math.ceil(now));
                    }
                });
        });
    }
    //Animate homepage on scroll
    if (jQuery("body").hasClass("home")) {
        jQuery(window).on("load resize scroll", promo1Animate);
    }
    //Animate homepage on scroll
    function promo1Animate() {
        if (jQuery(".subsection-promo-white h3").isInViewport()) {
            countUp();
            jQuery(window).off("load resize scroll", promo1Animate);
        }

    };
    //jQuery Weather
    // Place before/outside of your jQuery(document).ready function
    var loadWeather = function () {
        // Change Location 
        var weatherloc = jQuery('.weatherLocation'),
            changeloc = jQuery('#changeloc'),
            xy1 = jQuery('#weatherXY1'),
            forecast = jQuery('#forecast'),
            documentbody = jQuery('body');
        changeloc.clone().appendTo(xy1);
        changeloc.remove();
        changeloc = jQuery('#changeloc');
        if (!documentbody.hasClass('custom')) {
            function initializeChangeLocation() {
                changeloc.click(function () {
                    if (changeloc.hasClass('active')) {
                        weatherloc.css('display', 'none');
                        changeloc.css('display', 'block');
                        changeloc.removeClass('active');
                    } else {
                        weatherloc.css('display', 'block');
                        changeloc.css('display', 'none');
                        changeloc.addClass('active');
                    }
                });

            };
            initializeChangeLocation();
        };

    }
    // Weather 2.0.0 -------------------------------------*/
    jQuery('#weather').load('inc_weather.aspx', function () {
        var initWeather = function () {
            loadWeather();
            jQuery('#weatherwidget').ajaxPost({
                url: "inc_weather.aspx",
                postContainer: jQuery('#weather'),
                success: function () {
                    return initWeather();
                },
            });
        }
        initWeather();
    });

});
jQuery(window).scroll(function () {

    jQuery('body').scrollTrigger({
        triggerClass: "showtop",
        scrollMin: 350
    });
    jQuery('body').scrollTrigger({
        triggerClass: "scroll",
        scrollMin: 1
    });

});
jQuery(window).load(function () {
    if (jQuery("body").hasClass("home")) {
        jQuery(".notice").responsiveSiteNotice({
        //    fixedPosition: true
        });
    }

    // Place directly after the Site Notice 3.1.0 script
    var $body = jQuery("body");
    // Smart App Banners 1.1.0 
    var ua = navigator.userAgent;
    var kindleStrings = ["KFAPWA", "KFAPWI", "KFARWI", "KFASWI", "KFFOWI", "KFGIWI", "KFJWA", "KFJWI", "KFMEWI", "KFOT", "KFSAWA", "KFSAWI", "KFSOWI", "KFTBWI", "KFTHWA", "KFTHWI", "KFTT", "Kindle", "Silk"];
    var isKindle = false;

    for (index = 0; index < kindleStrings.length; index++) {
        var matchRegExp = new RegExp(kindleStrings[index]);
        if (matchRegExp.test(ua)) {
            isKindle = true;
            break;
        }
    }

    var mobile = (/iphone|ipad|ipod|android|blackberry|mini|windows\sce|palm/i.test(navigator.userAgent.toLowerCase()));
    if (mobile) {
        var userAgent = navigator.userAgent.toLowerCase();
        if ((userAgent.search("android") > -1) && (userAgent.search("mobile") > -1) && !isKindle) {
            $body.addClass("android");
        } else if ((userAgent.search("android") > -1) && (userAgent.search("mobile") <= -1) && !isKindle) {
            $body.addClass("android-tablet");
        } else if ((userAgent.search("android") > -1) && (userAgent.search("mobile") > -1) && isKindle) {
            $body.addClass("android-fire");
        } else if ((userAgent.search("android") > -1) && (userAgent.search("mobile") <= -1) && isKindle) {
            $body.addClass("android-tablet-fire");
        } else if (userAgent.search("ipad") > -1) {
            $body.addClass("ipad");
        } else if ((userAgent.search("iphone") > -1) || (userAgent.search("ipod") > -1)) {
            $body.addClass("iphone");
        }
    }
})