
var MBAViewer = {
    init: function(options) {
        var bitDepth = options['bitDepth'];
        var nSections = options['nSections'];

        var sectionId = options['sectionId'];
        var sectionOrder = options['sectionOrder'];
	var showNissl = options['showNissl'];
	var screen = options['screen'];
        var image = 'brainimg:64/0068';
        var iip = new IIP( "targetframe", {
                    image: options['image'],
                    server: options['server'],
                    credit: '',
                    zoom: 1,
                    bitDepth: bitDepth,
                    render: 'random',
                    showNavButtons: true,
                    crossSiteTest: true
                });
        this.initColorSliders(iip, bitDepth);

        var panel = new Fx.Slide('panel', {mode: 'horizontal'});
        panel.hide();
        $('panel').setStyle('z-index','1');
        $('trigger').addEvent('click', function(event) {
            event.stop();
            panel.toggle();
        });
        var helpPanelViewer = new Fx.Slide('helpPanelViewer', {mode: 'horizontal'});
        helpPanelViewer.hide();
        $('helpPanelViewer').setStyle('z-index','1');
        $('helpTriggerViewer').addEvent('click', function(event) {
            event.stop();
            helpPanelViewer.toggle();
        });
        if($('filmstrip')) {
	    this.initSectionNav(iip,nSections, sectionId, sectionOrder, showNissl, screen);
        }
    },

    initSectionNav: function(iip, nSections, sectionId, sectionOrder, showNissl, screen) {
        var filmstrip = new slideGallery($('filmstrip'), {
                    steps: 4,
                    mode: "line"
                });
        var setSagittalX = function(x) {
            $('sagittal_pos').setStyle('left', x);
        };
        var highlightSection = function(elem) {
            elem.getSiblings().setStyle('border-top','');
            elem.setStyle('border-top','3px solid #FFFFFF');
        };
        // position for any offset
        var offsetValue = 10 + Math.round(sectionOrder-1)/ (2*nSections) * 200;
	setSagittalX(offsetValue);
	 var y_pos = Math.round((sectionOrder-10) / 200 * nSections) + 1;
         filmstrip.jump(y_pos);
        //  highlightSection( $('section-' + sectionId + '-'+ sectionOrder +'-' + showNissl + '-' + screen ).getParent('li'));
        $('sagittal').addEvent('click', function(event) {
            setSagittalX(event.page.x);
            //y_pos = 5.762 - 0.067*(event.page.x-10);
            var y_pos = Math.round((event.page.x-10) / 200 * nSections) + 1;
            filmstrip.jump(y_pos);
            var section = $$('img[id$='+y_pos+']');
            highlightSection(section[0].getParent('li'));
        });
        $$('#filmstrip img').each(function(elem) {
            elem.addEvent('click', function(){
                var parts = elem.id.split('-');
                highlightSection(elem.getParent('li'));
		if (parts[3] == '0') {
		    setSagittalX(10 + Math.round((parts[2]-1) / (2*nSections) * 200));
		}
		else{ 
		    setSagittalX(10 + Math.round((parts[2]-1) / nSections * 200));
		}
                new Request.HTML({
                            url: '/seriesbrowser/ajax/section/' + parts[1] + '/' + parts[3] + '/' + parts[4] + '/',
                            method: 'get',
                            onComplete: function(response) {
                                $('panel_content').empty().adopt(response);
                            }
                        }).send();
                //var path = elem.get('src');
                //var file = path.split('/').pop();
                //var pieces = file.split('_');
                //iip.changeImage(imageBase + pieces[0] + '/' + pieces[0] + '_' + pieces[1] + '.jp2');
            });
        });
    },
    initColorSliders: function(iip, bitDepth) {
        var colors = ['r','g','b'];
        var low_sliders = [0,0,0];
        var high_sliders = [0,0,0];
        $$('.value input').each(function (elem) {
            elem.addEvent('change', function() {
                var new_step = elem.value;
                var re = /^\d*$/;
                if(!re.test(new_step) || new_step < 0 || new_step == '') {
                    new_step = elem.value = 0;
                }
                if(new_step > bitDepth) {
                    new_step = elem.value = bitDepth;
                }
                var id = elem.id;
                var color = id.substring(0,1);
                var group = id.substring(1);

                if (group == 'min') {
                    low_sliders[colors.indexOf(color)].set(new_step);
                }
                else if (group == 'max') {
                    high_sliders[colors.indexOf(color)].set(new_step);
                }
            });
        });

        var updateColorRange = function(group, index, step) {
            $(colors[index]+group).value = step;
        };
        $$('.slider.low').each(function(slider, i){
            low_sliders[i] = new Slider(slider, slider.getElement('.knob'), {
                        range: [0,bitDepth],
                        onChange: function() {
                            if(this.step >= high_sliders[i].step) {
                                high_sliders[i].set(this.step);
                            }
                            updateColorRange('min',i,this.step);
                        }
                    });
        });
        $$('.slider.high').each(function(slider, i){
            high_sliders[i] = new Slider(slider, slider.getElement('.knob'), {
                        range: [0,bitDepth],
                        initialStep: bitDepth,
                        onChange: function(){
                            if(this.step <= low_sliders[i].step) {
                                low_sliders[i].set(this.step);
                            }
                            updateColorRange('max',i,this.step);
                        }
                    });
        });
        var gamma = $('gamma_slider');
        new Slider(gamma, gamma.getElement('.knob'), {
                    range: [1, 20],
                    initialStep: 10,
                    steps: 22,
                    onChange: function() {
                        $('gamma').value = this.step/10;
                    }
                });
    }
};



