var MBAViewer = {
    init: function(options) {
        var image = options['image'];
        var nSections = options['nSections'];
	var isAuxiliary = options['isAuxiliary'];

        var iip = new IIP("targetframe", {
            image: image,
            sectionId: options['sectionId'],
            server: options['server'],
            credit: '',
            zoom: 1,
            scale: options['scale'],
            bitDepth: options['bitDepth'],
            render: 'random',
            showNavButtons: true,
            crossSiteTest: false
        });

        var panel = new Fx.Slide('panel', {mode: 'horizontal'});
        panel.hide();
        $('panel').setStyle('z-index','1');
        $('trigger').addEvent('click', function(event) {
            event.stop();
            panel.toggle();
        });

        if($('filmstrip')) {
            this.initSectionNav(iip, image, nSections, options['sectionId'],isAuxiliary);
        }
    },

    initSectionNav: function(iip, image, nSections, sampleSection, isAuxiliary) {
        var filmstrip = new slideGallery($('filmstrip'), {
            steps: 4,
            mode: "line"
        });

        var highlightSection = function(elem) {
            elem.getSiblings().setStyle('border-top','');
            elem.setStyle('border-top','3px solid #FF4500');
        };

	if (!isAuxiliary)
        {
	    // Leave these pieces out if there is no clickable sag view
            var setSagittalX = function(x) {
              $('sagittal_pos').setStyle('left', x);
            };
        
            $('sagittal').addEvent('click', function(event) {
              setSagittalX(event.page.x);
              var y_pos = Math.ceil((event.page.x-10) / 180 * nSections);
              filmstrip.jump(y_pos);
            });
        }

        var sections = [];
	var sampleSectionIdx = 0;
        $$('#filmstrip img').each(function(elem, i) {
            sections.push(elem.getParent('li'));
            var parts = elem.id.split('-');
	    if (parts[1]==sampleSection) {
		sampleSectionIdx = i;
	    }
            elem.addEvent('click', function(){
                highlightSection(sections[i]);
                if (!isAuxiliary) {
		  setSagittalX(10 + Math.round(i / nSections * 180));
                }
                new Request.HTML({
                    url: '/seriesbrowser/ajax/section/' + parts[1] + '/',
                    method: 'get',
                    onSuccess: function(response) {
                        $('panel_content').empty().adopt(response);
                    }
                }).send();
                var imageParts = image.split("/");
                var sectionOrderVal = parts[2] + '';
                while(sectionOrderVal.length < 4) {
                    sectionOrderVal  = "0" + sectionOrderVal;
                }
		//var imageName = 'MouseBrain/' + sectionOrderVal;
		var imageName = 'MouseBrain/' + parts[1];
                iip.changeImage(imageName, parts[1]);
            });
        });

	// Need to send an AJAX request even for the first section
        new Request.HTML({
            url: '/seriesbrowser/ajax/section/' + sampleSection + '/',
                 method: 'get',
                 onSuccess: function(response) {
                     $('panel_content').empty().adopt(response);
                 }
            }).send();

	// And make the filmstrip / sagittal section reflect initial section
        highlightSection(sections[sampleSectionIdx]);
	filmstrip.jump(sampleSectionIdx);
	if (!isAuxiliary) {
	  setSagittalX(10 + Math.round(sampleSectionIdx / nSections * 180));
        }
    }
};



