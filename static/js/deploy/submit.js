$(document).ready(function() {
    $('.form-submit').each(function(i, e) {
        e.onsubmit = function() { return false; };
        var form = $(e);
        form.find('.submitter').click(function(e) {
            var btn = $(this);
            btn.attr('disabled', 'disabled');
            form.find('.error-reason').text('');
            form.find('.error-detail').text('');
            $.ajax({
                url: form.data('url'),
                type: form.data('method') || 'GET',
                data: form.serialize(),
                success: function() {
                    btn.removeAttr('disabled')[0].success();
                },
                error: function(r) {
                    btn.removeAttr('disabled');
                    var c = JSON.parse(r.responseText);
                    form.find('.error-reason').text('出错原因: ' + c.reason);
                    if (c.detail) {
                        form.find('.error-detail').text('详细信息: ' + c.detail);
                    }
                }
            });
        });
    });
});