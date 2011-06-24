var MBAViewer = {
    init: function(options) {
        var bitDepth = options['bitDepth'];
        var nSections = options['nSections'];
        var sectionId = options['sectionId'];
        var sectionOrder = options['sectionOrder'];
        var image = options['image'];

        var iip = new IIP("targetframe", {
            image: image,
            server: options['server'],
            credit: '',
            zoom: 1,
            bitDepth: bitDepth,
            render: 'random',
            showNavButtons: true,
            crossSiteTest: false,
            scale: 2174
        });

        var panel = new Fx.Slide('panel', {mode: 'horizontal'});
        panel.hide();
        $('panel').setStyle('z-index','1');
        $('trigger').addEvent('click', function(event) {
            event.stop();
            panel.toggle();
        });

        if($('filmstrip')) {
            this.initSectionNav(iip,image, nSections, sectionId, sectionOrder);
        }
    },

    initSectionNav: function(iip, image, nSections, sectionId, sectionOrder) {
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
        
        $('sagittal').addEvent('click', function(event) {
            setSagittalX(event.page.x);
            //y_pos = 5.762 - 0.067*(event.page.x-10);
            var y_pos = Math.ceil((event.page.x-10) / 180 * nSections);
            filmstrip.jump(y_pos);
        });

        var sections = [];
        $$('#filmstrip img').each(function(elem, i) {
            sections.push(elem.getParent('li'));
            elem.addEvent('click', function(){
                var parts = elem.id.split('-');
                highlightSection(sections[i]);
                setSagittalX(10 + Math.round(i / nSections * 180));
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
                var imageName = 'PMD/'+ imageParts[0]+ "_"+sectionOrderVal;
                iip.changeImage(imageName);
            });
        });

        highlightSection(sections[0]);
    }
};



