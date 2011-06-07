//var pdfImageUrl = "";		
var MBAViewer = {
    init: function(options) {
        var bitDepth = options['bitDepth'];
        var nSections = options['nSections'];

        var sectionId = options['sectionId'];
        var sectionOrder = options['sectionOrder'];
        var showNissl = options['showNissl'];
        var screen = options['screen'];
        var image = options['image'];
        var iip = new IIP( "targetframe", {
                    image: image,
                    server: options['server'],
                    credit: '',
                    zoom: 1,
                    bitDepth: bitDepth,
                    render: 'random',
                    showNavButtons: true,
                    crossSiteTest: true
                });
        //alert("**********YYYYYYYYYYYY");
        //pdfImageUrl = iip.getOpenUrl();
        //alert(pdfImageUrl);
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
            this.initSectionNav(iip,image, nSections, sectionId, sectionOrder, showNissl, screen);
        }
    },

    initSectionNav: function(iip, image, nSections, sectionId, sectionOrder, showNissl, screen) {
        var filmstrip = new slideGallery($('filmstrip'), {
                    steps: 4,
                    mode: "line"
                });
        var setSagittalX = function(x) {
            $('sagittal_pos').setStyle('left', x);
        };
        var highlightSection = function(elem) {
            elem.getSiblings().setStyle('border-top','');
            elem.setStyle('border-top','3px solid #FF4500');
        };
	// position for any offset
	var offsetValue = 0;
	if (showNissl == '0')
	    offsetValue = 10 + Math.round(sectionOrder-1)/ (2*nSections) * 200;
	else
	    offsetValue = 10 + Math.round(sectionOrder-1)/ (nSections) * 200;
	setSagittalX(offsetValue);
	var y_pos = Math.round((sectionOrder-10) / 200 * nSections) + 1;
	filmstrip.jump(y_pos);
        $('sagittal').addEvent('click', function(event) {
            //  highlightSection( $('section-' + sectionId + '-'+ sectionOrder +'-' + showNissl + '-' + screen ).getParent('li'));
            setSagittalX(event.page.x);
            //y_pos = 5.762 - 0.067*(event.page.x-10);
            var y_pos = Math.ceil((event.page.x-10) / 180 * nSections);
            var section = $$('img[id*=-'+y_pos+'-]');
            highlightSection(section[0].getParent('li'));
            filmstrip.jump(y_pos);
        });

        $$('#filmstrip img').each(function(elem) {
            elem.addEvent('click', function(){
                var parts = elem.id.split('-');
                highlightSection(elem.getParent('li'));
                if (parts[3] == '0') {
                    setSagittalX(10 + Math.round((parts[2]-1) / nSections * 180));
                }
                else{
                    setSagittalX(10 + Math.round((parts[2]-1) / (2*nSections) * 180));
                }
                new Request.HTML({
                            url: '/seriesbrowser/ajax/section/' + parts[1] + '/' + parts[3] + '/' + parts[4] + '/',
                            method: 'get',
                            onComplete: function(response) {
                                $('panel_content').empty().adopt(response);
                            }
                        }).send();
                var imageParts = image.split("/");
                var imageParts2 = imageParts[1].split("_");
                var sectionOrderVal = parts[2] + '';
                while(sectionOrderVal.length < 4) {
                    sectionOrderVal  = "0" + sectionOrderVal;
                }
                var imageName = 'PMD/'+ imageParts2[0]+ "_"+sectionOrderVal;
                //                alert(imageName);
                iip.changeImage(imageName);
                iip.requestImages();
            });
        });

        var initSection = $$('img[id*=-1-]');
        highlightSection(initSection[0].getParent('li'));
    }
};



