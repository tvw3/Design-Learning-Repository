//Change active tab, and load content based on selected tab
    $("#tabs li").on('click',function() {
 	    if(!($(this).hasClass('active'))) {
            //Get current tab for fade out
            var currentContentId = '#' + $('#tabs .active').attr('id') + 'content';
            //Clear active tab
            $('#tabs .active').removeClass('active');
            //fade out the current content
            $(currentContentId).fadeOut(.05);
            //Set the clicked tab to active
            $(this).addClass('active');

            //Get the id of the appropriate content based on the tab selected
            //fade in the new content
            $('#' + this.id + 'content').fadeIn('slow');
	    }
    });